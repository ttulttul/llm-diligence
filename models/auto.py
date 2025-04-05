from typing import Dict, Type, Any, List
import os
from .base import DiligentizerModel
from pydantic import Field, BaseModel
import json
from instructor.multimodal import PDF
import sys
from utils.llm import cached_llm_invoke

class ModelSelection(DiligentizerModel):
    """Model used to receive the selected model name from the LLM."""
    model_name: str = Field(..., description="The name of the most appropriate model for this document")

class AutoModel(DiligentizerModel):
    """Automatically selects the most appropriate model to analyze the document."""
    
    chosen_model_name: str = Field(..., description="The name of the model chosen by the LLM")
    chosen_model_result: Any = Field(None, description="The result from the chosen model")
    
    @classmethod
    def from_pdf(cls, pdf_path: str, available_models: Dict[str, Type[DiligentizerModel]]) -> "AutoModel":
        """Use LLM to select and apply the most appropriate model for the document."""
        # Get API key
        API_KEY = os.environ.get("ANTHROPIC_API_KEY")
        if not API_KEY:
            raise ValueError("ANTHROPIC_API_KEY environment variable not found")
        
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
        
        # Create properly formatted message content - use the same pattern as in diligentizer.py
        user_content = [
            {"type": "text", "text": prompt},
            pdf_input  # instructor's PDF class handles formatting correctly
        ]
        
        from utils.llm import get_claude_model_name
        model_selection = cached_llm_invoke(
            model_name=get_claude_model_name(),
            system_message=system_message,
            user_content=user_content,
            max_tokens=50,
            response_model=ModelSelection,
            api_key=API_KEY
        )
        
        chosen_model_name = model_selection.model_name
        
        # Validate the chosen model exists
        if chosen_model_name not in available_models:
            raise ValueError(f"LLM selected invalid model: {chosen_model_name}. Valid options are: {', '.join(available_models.keys())}")
        
        print(f"\nAuto model selection result: '{chosen_model_name}'")
        
        # Now use the selected model to analyze the document
        model_class = available_models[chosen_model_name]
        
        return cls(
            chosen_model_name=chosen_model_name,
            chosen_model_result=None  # Will be populated by the caller
        )
