from typing import Dict, Type, Any, List, Union, Optional, Set
import os
import inspect
from .base import DiligentizerModel
from pydantic import Field, BaseModel
import json
import instructor
from anthropic import Anthropic
from instructor.multimodal import PDF
import sys

from utils.llm import cached_llm_invoke
from utils import logger

class AutoDocumentClassification(DiligentizerModel):
    """Model used to receive the selected model name from the LLM.
    This model serves as an interface for the document classification process, capturing the LLM's
    determination of the most appropriate document model to use for a given document. It enables
    the automatic routing of documents to specialized analysis models based on their content and structure."""
    model_name: str = Field(..., description="The name of the most appropriate model for this document")

    class Config:
        extra = 'allow'

class AutoModel(DiligentizerModel):
    """Automatically selects the most appropriate model to analyze the document.
    This intelligent model implements a hierarchical document classification system that progressively
    narrows down the document type through multiple phases of analysis. It manages the selection process,
    tracks the decision path, and coordinates with the chosen specialized model to perform the final
    document analysis, enabling accurate and efficient automated document processing."""
    
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
            # Find direct subclasses of this model_class in models_dict
            derived_models = [
                child_key
                for child_key, child_cls in models_dict.items()
                if model_class in child_cls.__bases__
            ]
            if derived_models:
                # join with comma and space; replace last comma with " and " for nicer grammar
                if len(derived_models) > 1:
                    derived_str = ", ".join(derived_models[:-1]) + " and " + derived_models[-1]
                else:
                    derived_str = derived_models[0]
                doc_string = doc_string.rstrip() + f" More specific models like {derived_str} derive from this model type."
            
            model_descriptions[name] = {
                "description": doc_string,
                "class_name": model_class.__name__,
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
            if name.startswith("auto"):  # Skip all models in the auto module
                continue
            
            # Check if this model directly inherits from DiligentizerModel
            if DiligentizerModel in model_class.__bases__:
                base_models[name] = model_class
        
        return base_models
    
    @staticmethod
    def _select_model_with_llm(pdf_input: Any, models_dict: Dict[str, Type[DiligentizerModel]], 
                              phase_description: str, prompt_extra: Optional[str] = None) -> AutoDocumentClassification:
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
        
        # Add extra prompt text if provided
        if prompt_extra:
            message_content.append({"type": "text", "text": prompt_extra})

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
                 classify_only: bool = False,
                 prompt_extra: Optional[str] = None) -> Union["AutoModel", AutoDocumentClassification]:
        """Use LLM to select and apply the most appropriate model for the document through a hierarchical process."""
        # Load the PDF for analysis
        pdf_input = PDF.from_path(pdf_path)
        
        # Track the selection path
        selection_path = []
        
        # Initialize with base models (those directly inheriting from DiligentizerModel)
        current_models = cls._get_base_models(available_models)
        if not current_models:
            raise Exception("No available models: something is wrong with the installation")

        logger.info(f"Starting with models: {current_models}")
        
        # Current model starts as None
        current_model_key = None
        current_model_class = None
        
        # Single loop for all phases
        phase_num = 1
        while current_models:
            # Create appropriate phase description
            if phase_num == 1:
                phase_description = "PHASE 1: First, select the broad category that best matches this document."
            else:
                phase_description = f"PHASE {phase_num}: Now, select the specific type of {current_model_class.__name__} that best matches this document."
            
            # Select model with LLM
            phase_response = cls._select_model_with_llm(pdf_input, current_models, phase_description, prompt_extra)
            
            # Get model name and find corresponding key
            model_name = phase_response.model_name
            model_key = cls._find_model_key(model_name, current_models)
            
            if not model_key:
                if phase_num == 1:
                    # If we fail at phase 1, we have no valid model
                    raise ValueError(f"LLM selected invalid model: {model_name}. Valid options are: {', '.join(current_models.keys())}")
                else:
                    # If we fail at a later phase, we can use the last valid model
                    logger.warning(f"LLM selected invalid model: {model_name}. Stopping at {current_model_key}")
                    break
            
            # Update current model
            current_model_key = model_key
            current_model_class = current_models[model_key]
            selection_path.append(current_model_key)
            
            logger.info(f"Phase {phase_num} selected model: {current_model_key} ({current_model_class.__name__})")
            
            # Get models for next phase (those directly inheriting from current model)
            current_models = cls._filter_models_by_parent(available_models, current_model_class)
            
            if not current_models:
                # No more derived models, we've reached a leaf model
                logger.info(f"No more derived models from {current_model_class.__name__}, selection complete")
                break
            
            phase_num += 1
        
        # Final selected model (if we have one)
        if current_model_key is None:
            raise ValueError("Failed to select any valid model")
            
        chosen_model_name = current_model_key
        model_class = current_model_class
        
        # If we are asked only to return the document classification, then do so
        if classify_only:
            adc = AutoDocumentClassification(model_name=chosen_model_name)
            adc.selection_path = " -> ".join(selection_path)
            return adc
        
        # Get the description of the chosen model
        chosen_model_description = model_class.__doc__ or "No description available"
        
        return cls(
            chosen_model_name=chosen_model_name,
            chosen_model_description=chosen_model_description,
            chosen_model_result=None,  # Will be populated by the caller
            selection_path=selection_path
        )
