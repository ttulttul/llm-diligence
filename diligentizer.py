import sys
import argparse
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import from the analysis module
from analysis import get_available_models, list_available_models, run_analysis
from utils import logger, configure_logger


def main():
    """Main entry point with command line argument parsing."""
    parser = argparse.ArgumentParser(description="Diligentizer - Extract structured data from documents")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--list", action="store_true", help="List all available models")
    group.add_argument("--model", type=str, help="Specify the model to use")
    group.add_argument("--auto", action="store_true", help="Automatically select the most appropriate model")
    parser.add_argument("--pdf", type=str, default="software_license.pdf", 
                       help="Path to the PDF file (default: software_license.pdf)")
    parser.add_argument("--sqlite", type=str, help="Path to SQLite database for storing results")
    parser.add_argument("--log-level", type=str, default="INFO", 
                       choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                       help="Set the logging level (default: INFO)")
    parser.add_argument("--log-file", type=str, help="Path to the log file")
    
    args = parser.parse_args()
    
    # Configure logger with command line arguments
    configure_logger(args.log_level, args.log_file)
    logger.debug("Diligentizer starting up")
    
    # Get all available models
    models_dict = get_available_models()
    
    if not models_dict:
        logger.error("No models found in the models directory.")
        return 1
        
    if args.list:
        list_available_models(models_dict)
        return 0
        
    # Handle automatic model selection
    if args.auto:
        auto_model_key = None
        for key, model_class in models_dict.items():
            if model_class.__name__ == "AutoModel":
                auto_model_key = key
                break
        
        if auto_model_key:
            selected_model = auto_model_key
        else:
            print("Error: AutoModel not found in available models.")
            return 1
    # If no model specified and not using auto, allow interactive selection
    elif not args.model:
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
    else:
        # If args.model is provided, use it directly
        selected_model = args.model
    
    # Validate the selected model exists
    if selected_model not in models_dict:
        print(f"Error: Model '{selected_model}' not found. Use --list to see available models.")
        return 1
        
    # Run the analysis with the selected model
    model_class = models_dict[selected_model]
    print(f"Using model: {selected_model} ({model_class.__name__})")
    run_analysis(model_class, args.pdf, args.sqlite)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
