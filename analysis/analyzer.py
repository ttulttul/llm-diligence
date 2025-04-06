import os
import sys
import importlib
import inspect
import pkgutil
from typing import Dict, Type, Optional, List
from instructor.multimodal import PDF

# Import the models package
import models
from models.base import DiligentizerModel
from utils.llm import cached_llm_invoke
from utils.db import setup_database, save_model_to_db

def get_available_models() -> Dict[str, Type[DiligentizerModel]]:
    """Discover all available models in the models package."""
    models_dict = {}
    
    # Walk through all modules in the models package
    for _, module_name, _ in pkgutil.iter_modules(models.__path__, models.__name__ + '.'):
        # Skip the base module
        if module_name.endswith('.base'):
            continue
            
        # Import the module
        module = importlib.import_module(module_name)
        
        # Find all DiligentizerModel subclasses in the module
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, DiligentizerModel) and 
                obj != DiligentizerModel):
                # Store the model with a friendly name: module_modelname
                friendly_name = f"{module_name.split('.')[-1]}_{name}"
                models_dict[friendly_name] = obj
                
    return models_dict

def list_available_models(models_dict: Dict[str, Type[DiligentizerModel]]) -> None:
    """Print a formatted list of all available models."""
    print("\nAvailable Models:")
    print("=" * 60)
    for i, (name, model_class) in enumerate(models_dict.items(), 1):
        print(f"{i}. {name}")
        # Get model fields with descriptions
        for field_name, field in model_class.__annotations__.items():
            field_info = model_class.model_fields.get(field_name)
            if field_info and field_info.description:
                print(f"   - {field_name}: {field_info.description}")
        print("-" * 60)

def run_analysis(model_class: Type[DiligentizerModel], pdf_path: str = "software_license.pdf", db_path: Optional[str] = None) -> None:
    """Run the analysis with the selected model."""

    # Check if this is the auto model
    if model_class.__name__ == "AutoModel":
        # Get all available models to pass to AutoModel
        models_dict = get_available_models()
        
        try:
            # Use the auto model to select the appropriate model
            auto_model = model_class.from_pdf(pdf_path, models_dict)
            
            # Get the selected model and run the analysis with it
            selected_model_name = auto_model.chosen_model_name
            selected_model_class = models_dict[selected_model_name]
            
            # Now run the analysis with the selected model
            run_analysis(selected_model_class, pdf_path, db_path)
            
            # Set the analysis result in auto_model if needed for further processing
            return
        except Exception as e:
            print(f"An error occurred during auto model selection: {e}")
            return
    
    # Load the PDF file for analysis
    pdf_input = PDF.from_path(pdf_path)
    
    # Create a dynamic prompt based on the model fields
    field_descriptions = []
    for field_name, field_info in model_class.model_fields.items():
        desc = field_info.description or f"the {field_name}"
        field_descriptions.append(f'  "{field_name}": "<string: {desc}>"')
    
    fields_json = ",\n".join(field_descriptions)
    
    prompt = (
        f"Analyze the following document and extract the key details. "
        f"Your output must be valid JSON matching this exact schema: "
        f"{{\n{fields_json}\n}}. "
        f"Output only the JSON."
    )

    try:
        # Create message content with both text and PDF
        message_content = [
            {"type": "text", "text": prompt},
            pdf_input  # instructor's PDF class handles formatting correctly
        ]
        
        # Use cached LLM invoke instead of direct API call
        response = cached_llm_invoke(
            system_message="You are a document analysis assistant that extracts structured information from documents.",
            user_content=message_content,
            max_tokens=1000,
            response_model=model_class
        )

        # Print the structured result
        print(f"\nExtracted {model_class.__name__} Details:")
        print(response.model_dump_json(indent=2))
        
        # Save to database if requested
        if db_path:
            try:
                # Set up the database with all available models
                models_dict = get_available_models()
                model_classes = list(models_dict.values())
                engine, Session, sa_models = setup_database(db_path, model_classes)
                
                # Create a session and save the model
                with Session() as session:
                    sa_instance = save_model_to_db(response, sa_models, session)
                    print(f"\nSaved to database: {db_path}, table: {sa_instance.__tablename__}, ID: {sa_instance.id}")
            except Exception as e:
                print(f"Error saving to database: {e}")
    except Exception as e:
        print(f"An error occurred during analysis: {e}")
