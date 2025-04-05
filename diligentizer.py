import os
import sys
import argparse
import importlib
import inspect
import pkgutil
from typing import Dict, Type, Optional, List
import instructor
from anthropic import Anthropic
from instructor.multimodal import PDF
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import the models package
import models
from models.base import DiligentizerModel

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

def run_analysis(model_class: Type[DiligentizerModel], pdf_path: str = "software_license.pdf") -> None:
    """Run the analysis with the selected model."""
    # Retrieve your Anthropic API key from .env file
    API_KEY = os.environ.get("ANTHROPIC_API_KEY")
    if not API_KEY:
        print("Error: ANTHROPIC_API_KEY environment variable not found.")
        print("Please set it in your .env file or environment variables.")
        sys.exit(1)

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
            run_analysis(selected_model_class, pdf_path)
            
            # Set the analysis result in auto_model if needed for further processing
            return
        except Exception as e:
            print(f"An error occurred during auto model selection: {e}")
            return
    
    # Regular model analysis (not auto)
    # Initialize the Anthropic client and Instructor with tool support
    anthropic_client = Anthropic(api_key=API_KEY)
    client = instructor.from_anthropic(
        anthropic_client,
        mode=instructor.Mode.ANTHROPIC_TOOLS
    )

    # Load the PDF file for analysis
    pdf_input = PDF.from_path(pdf_path)
    
    # Create a dynamic prompt based on the model fields
    field_descriptions = []
    for field_name, field_info in model_class.model_fields.items():
        desc = field_info.description or f"the {field_name}"
        field_descriptions.append(f'  "{field_name}": "<string: {desc}>"')
    
    fields_json = ",\n".join(field_descriptions)
    
    prompt = (
        f"You are a document analyst. Analyze the following document "
        f"and extract the key details. Your output must be valid JSON matching this exact schema: "
        f"{{\n{fields_json}\n}}. "
        f"Output only the JSON."
    )

    try:
        # Call Claude with the prompt and the PDF content
        response = client.chat.completions.create(
            model="claude-3-7-sonnet-20250219",
            messages=[
                {"role": "system", "content": "You are a document analyst."},
                {"role": "user", "content": [prompt, pdf_input]},
            ],
            max_tokens=1000,
            response_model=model_class,
        )

        # Print the structured result
        print(f"\nExtracted {model_class.__name__} Details:")
        print(response.model_dump_json(indent=2))
    except Exception as e:
        print(f"An error occurred during analysis: {e}")

def main():
    """Main entry point with command line argument parsing."""
    parser = argparse.ArgumentParser(description="Diligentizer - Extract structured data from documents")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--list", action="store_true", help="List all available models")
    group.add_argument("--model", type=str, help="Specify the model to use")
    parser.add_argument("--pdf", type=str, default="software_license.pdf", 
                       help="Path to the PDF file (default: software_license.pdf)")
    
    args = parser.parse_args()
    
    # Get all available models
    models_dict = get_available_models()
    
    if not models_dict:
        print("Error: No models found in the models directory.")
        return 1
        
    if args.list:
        list_available_models(models_dict)
        return 0
        
    # If no model specified, allow interactive selection
    selected_model = args.model
    if not selected_model:
        list_available_models(models_dict)
        print("\nSelect a model by number or name (or 'q' to quit):")
        choice = input("> ").strip()
        
        if choice.lower() == 'q':
            return 0
            
        # Check if user entered a number
        if choice.isdigit() and 1 <= int(choice) <= len(models_dict):
            selected_model = list(models_dict.keys())[int(choice) - 1]
        else:
            selected_model = choice
    
    # Validate the selected model exists
    if selected_model not in models_dict:
        print(f"Error: Model '{selected_model}' not found. Use --list to see available models.")
        return 1
        
    # Run the analysis with the selected model
    model_class = models_dict[selected_model]
    print(f"Using model: {selected_model} ({model_class.__name__})")
    run_analysis(model_class, args.pdf)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
