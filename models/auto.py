from typing import Dict, Type, Any, List, Union, Optional, Set
import os
import inspect
from .base import DiligentizerModel, Agreement, FinancialDocument, DueDiligenceDocument
from pydantic import Field, BaseModel
import json
import instructor
from anthropic import Anthropic
from instructor.multimodal import PDF
import sys

from utils.llm import cached_llm_invoke
from utils import logger

class AutoDocumentClassification(DiligentizerModel):
    """Model used to receive the selected model name from the LLM."""
    model_name: str = Field(..., description="The name of the most appropriate model for this document")

class AutoModel(DiligentizerModel):
    """Automatically selects the most appropriate model to analyze the document."""
    
    chosen_model_name: str = Field(..., description="The name of the model chosen by the LLM")
    chosen_model_description: str = Field("", description="The description of the chosen model")
    chosen_model_result: Any = Field(None, description="The result from the chosen model")
    selection_path: List[str] = Field(default_factory=list, description="The hierarchical path of model selection")
    
    @staticmethod
    def _get_model_descriptions(models_dict: Dict[str, Type[DiligentizerModel]]) -> Dict[str, Dict[str, Any]]:
        """Generate descriptions for a set of models."""
        model_descriptions = {}
        for name, model_class in models_dict.items():
            if name == "auto_AutoModel":  # Skip the auto model itself
                continue
            doc_string = model_class.__doc__ or "No description available"
            field_descriptions = []
            for field_name, field_info in model_class.model_fields.items():
                if field_info.description:
                    field_descriptions.append(f"- {field_name}: {field_info.description}")
            
            model_descriptions[name] = {
                "description": doc_string,
                "class_name": model_class.__name__,
                "fields": field_descriptions
            }
        return model_descriptions
    
    @staticmethod
    def _filter_models_by_parent(available_models: Dict[str, Type[DiligentizerModel]], 
                                parent_class: Type[DiligentizerModel]) -> Dict[str, Type[DiligentizerModel]]:
        """Filter models to only include those that directly inherit from the specified parent class."""
        filtered_models = {}
        for name, model_class in available_models.items():
            # Skip models defined within the auto model module
            if model_class.__module__ == __name__:
                continue
            
            # Check if this model directly inherits from the parent class
            if inspect.getmro(model_class)[1] == parent_class:
                filtered_models[name] = model_class
        
        return filtered_models
    
    @staticmethod
    def _get_base_models(available_models: Dict[str, Type[DiligentizerModel]]) -> Dict[str, Type[DiligentizerModel]]:
        """Get models that directly inherit from DiligentizerModel."""
        base_models = {}
        for name, model_class in available_models.items():
            if name == "auto_AutoModel":  # Skip the auto model itself
                continue
            
            # Check if this model directly inherits from DiligentizerModel
            if DiligentizerModel in model_class.__bases__:
                logger.info(f"BASE_MODEL: {name} {model_class}")
                base_models[name] = model_class
        
        return base_models
    
    @staticmethod
    def _select_model_with_llm(pdf_input: Any, models_dict: Dict[str, Type[DiligentizerModel]], 
                              phase_description: str) -> AutoDocumentClassification:
        """Use LLM to select the most appropriate model from the provided models."""
        model_descriptions = AutoModel._get_model_descriptions(models_dict)
        
        prompt = f"""
You are an expert document analyzer. I have a PDF document that I need to analyze and extract information from.
I want you to review the document and choose the most appropriate model based on its content.

{phase_description}

Here are the available models:
{json.dumps(model_descriptions, indent=2)}

Based on the document content, which model would be most appropriate to use?
Respond with only the exact model name (one of the keys from the available models list).
"""
        
        # Create message content with both text and PDF
        message_content = [
            {"type": "text", "text": prompt},
            pdf_input  # instructor's PDF class handles formatting correctly
        ]

        logger.debug(f"Calling LLM from AutoModel for phase: {phase_description}")
        
        # Make the API call with cached instructor
        response = cached_llm_invoke(
            system_message="You are a document analysis assistant.",
            user_content=message_content,
            max_tokens=500,
            response_model=AutoDocumentClassification
        )
        
        return response
    
    @staticmethod
    def _find_model_key(chosen_model_name: str, available_models: Dict[str, Type[DiligentizerModel]]) -> Optional[str]:
        """Find the correct model key based on the model name."""
        # Try exact match first
        if chosen_model_name in available_models:
            return chosen_model_name
        
        # Try case-insensitive match and class name match
        for key in available_models.keys():
            # Check if the key matches the chosen model name (case-insensitive)
            if key.lower() == chosen_model_name.lower():
                return key
            # Check if the key matches the class name of any model (case-insensitive)
            model_class_name = available_models[key].__name__.lower()
            if model_class_name == chosen_model_name.lower():
                return key
        
        return None
    
    @classmethod
    def from_pdf(cls, pdf_path: str,
                 available_models: Dict[str, Type[DiligentizerModel]],
                 classify_only: bool = False) -> Union["AutoModel", AutoDocumentClassification]:
        """Use LLM to select and apply the most appropriate model for the document through a hierarchical process."""
        # Load the PDF for analysis
        pdf_input = PDF.from_path(pdf_path)
        
        # Track the selection path
        selection_path = []
        
        # Phase 1: Select from base models (those directly inheriting from DiligentizerModel)
        base_models = cls._get_base_models(available_models)
        if not base_models:
            logger.warning("No base models found that directly inherit from DiligentizerModel")
            # Fall back to using all models
            base_models = {k: v for k, v in available_models.items() if k != "auto_AutoModel"}

        logger.info(f"base models: {base_models}")
        
        phase1_description = "PHASE 1: First, select the broad category that best matches this document."
        phase1_response = cls._select_model_with_llm(pdf_input, base_models, phase1_description)
        
        base_model_name = phase1_response.model_name
        base_model_key = cls._find_model_key(base_model_name, base_models)
        
        if not base_model_key:
            raise ValueError(f"LLM selected invalid base model: {base_model_name}. Valid options are: {', '.join(base_models.keys())}")
        
        base_model_class = base_models[base_model_key]
        selection_path.append(base_model_key)
        logger.info(f"Phase 1 selected base model: {base_model_key} ({base_model_class.__name__})")
        
        # Current model is the base model selected in phase 1
        current_model_key = base_model_key
        current_model_class = base_model_class
        
        # Continue with additional phases as long as there are derived models
        phase_num = 2
        while True:
            # Get models that directly inherit from the current model
            derived_models = cls._filter_models_by_parent(available_models, current_model_class)
            
            if not derived_models:
                # No more derived models, we've reached a leaf model
                logger.info(f"No more derived models from {current_model_class.__name__}, selection complete")
                break
            
            # Select from derived models
            phase_description = f"PHASE {phase_num}: Now, select the specific type of {current_model_class.__name__} that best matches this document."
            phase_response = cls._select_model_with_llm(pdf_input, derived_models, phase_description)
            
            derived_model_name = phase_response.model_name
            derived_model_key = cls._find_model_key(derived_model_name, derived_models)
            
            if not derived_model_key:
                logger.warning(f"LLM selected invalid derived model: {derived_model_name}. Stopping at {current_model_key}")
                break
            
            # Update current model to the selected derived model
            current_model_key = derived_model_key
            current_model_class = derived_models[derived_model_key]
            selection_path.append(current_model_key)
            
            logger.info(f"Phase {phase_num} selected derived model: {current_model_key} ({current_model_class.__name__})")
            phase_num += 1
        
        # Final selected model
        chosen_model_name = current_model_key
        model_class = current_model_class
        
        # If we are asked only to return the document classification, then do so
        if classify_only:
            return AutoDocumentClassification(model_name=chosen_model_name)
        
        # Get the description of the chosen model
        chosen_model_description = model_class.__doc__ or "No description available"
        
        return cls(
            chosen_model_name=chosen_model_name,
            chosen_model_description=chosen_model_description,
            chosen_model_result=None,  # Will be populated by the caller
            selection_path=selection_path
        )
