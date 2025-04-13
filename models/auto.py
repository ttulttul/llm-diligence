from typing import Dict, Type, Any, List, Union
import os
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
    """Model used to receive the selected model name from the LLM."""
    model_name: str = Field(..., description="The name of the most appropriate model for this document")

class AutoModel(DiligentizerModel):
    """Automatically selects the most appropriate model to analyze the document."""
    
    chosen_model_name: str = Field(..., description="The name of the model chosen by the LLM")
    chosen_model_description: str = Field("", description="The description of the chosen model")
    chosen_model_result: Any = Field(None, description="The result from the chosen model")
    
    @classmethod
    def from_pdf(cls, pdf_path: str,
                 available_models: Dict[str, Type[DiligentizerModel]],
                 classify_only: bool = False) -> Union["AutoModel", Type[AutoDocumentClassification]]:
        """Use LLM to select and apply the most appropriate model for the document."""
        # Load the PDF for analysis
        pdf_input = PDF.from_path(pdf_path)
        
        # First call: Ask the LLM to choose the best model
        model_descriptions = {}
        for name, model_class in available_models.items():
            if name == "auto_AutoModel":  # Skip the auto model itself
                continue
            doc_string = model_class.__doc__ or "No description available"
            field_descriptions = []
            for field_name, field_info in model_class.model_fields.items():
                if field_info.description:
                    field_descriptions.append(f"- {field_name}: {field_info.description}")
            
            model_descriptions[name] = {
                "description": doc_string,
                "fields": field_descriptions
            }
        
        prompt = f"""
You are an expert document analyzer. I have a PDF document that I need to analyze and extract information from.
I want you to review the document and choose the most appropriate model based on its content.

Here are the available models:
{json.dumps(model_descriptions, indent=2)}

Based on the document content, which model would be most appropriate to use?
Respond with only the exact model name (one of the keys from the available models list).
"""
        
        # Make the first API call to select the model using the cached function
        system_message = "You are a document analysis assistant."
        
        # Create message content with both text and PDF
        message_content = [
            {"type": "text", "text": prompt},
            pdf_input  # instructor's PDF class handles formatting correctly
        ]

        logger.info(f"Calling LLM from AutoModel: {message_content}")
        
        # Make the API call with cached instructor
        response = cached_llm_invoke(
            system_message="You are a document analysis assistant.",
            user_content=message_content,
            max_tokens=500,
            response_model=AutoDocumentClassification
        )
        
        model_selection = response
        logger.info(f"Selected {model_selection.model_name}")

        # If we are asked only to return the document classification, then do so
        if classify_only:
            return model_selection
        
        # Otherwise, carry on building out the chosen model so that it can be filled
        # in by the caller
        chosen_model_name = model_selection.model_name
        
        # Validate the chosen model exists - try exact match first
        if chosen_model_name in available_models:
            model_class = available_models[chosen_model_name]
        else:
            # Try case-insensitive match and snake_case conversion
            chosen_model_key = None
            for key in available_models.keys():
                # Check if the key matches the chosen model name (case-insensitive)
                if key.lower() == chosen_model_name.lower():
                    chosen_model_key = key
                    break
                # Check if the key matches the class name of any model (case-insensitive)
                model_class_name = available_models[key].__name__.lower()
                if model_class_name == chosen_model_name.lower():
                    chosen_model_key = key
                    break
            
            if chosen_model_key is None:
                raise ValueError(f"LLM selected invalid model: {chosen_model_name}. Valid options are: {', '.join(available_models.keys())}")
            
            chosen_model_name = chosen_model_key
            model_class = available_models[chosen_model_key]
        
        # Get the description of the chosen model
        chosen_model_description = model_class.__doc__ or "No description available"
        
        return cls(
            chosen_model_name=chosen_model_name,
            chosen_model_description=chosen_model_description,
            chosen_model_result=None  # Will be populated by the caller
        )
