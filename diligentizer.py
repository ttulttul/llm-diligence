import sys
import argparse
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import from the analysis module
from analysis import get_available_models, list_available_models, run_analysis
from utils import logger, configure_logger


def main():
    """Main entry point with command line argument parsing."""
    try:
        parser = argparse.ArgumentParser(description="Diligentizer - Extract structured data from documents")
        group = parser.add_mutually_exclusive_group()
        group.add_argument("--list", action="store_true", help="List all available models")
        group.add_argument("--model", type=str, help="Specify the model to use")
        group.add_argument("--auto", action="store_true", help="Automatically select the most appropriate model")
        parser.add_argument("--pdf", type=str, default="software_license.pdf", 
                           help="Path to the PDF file (default: software_license.pdf)")
        parser.add_argument("--sqlite", type=str, help="Path to SQLite database for storing results")
        parser.add_argument("--json-output", action="store_true", 
                           help="Output results as JSON files")
        parser.add_argument("--json-dir", type=str, default="output", 
                           help="Directory for JSON output files (default: output)")
        parser.add_argument("--json-prefix", type=str, default="diligentizer_", 
                           help="Prefix for JSON output filenames (default: diligentizer_)")
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
        
        # Create JSON output directory if needed
        json_output_params = None
        if args.json_output:
            json_dir = Path(args.json_dir)
            json_dir.mkdir(parents=True, exist_ok=True)
            json_output_params = {
                "json_dir": json_dir,
                "json_prefix": args.json_prefix
            }
            logger.info(f"JSON output will be saved to: {json_dir}")
        
        # Run the analysis with the selected model
        result = run_analysis(model_class, args.pdf, args.sqlite)
        
        # Save result as JSON if requested
        if json_output_params and result:
            output_path = json_output_params["json_dir"] / f"{json_output_params['json_prefix']}{selected_model}.json"
            try:
                with open(output_path, 'w') as f:
                    # Use the DateTimeEncoder to handle datetime objects
                    from utils.db import DateTimeEncoder
                    json.dump(result.model_dump(), f, cls=DateTimeEncoder, indent=2)
                print(f"JSON output saved to: {output_path}")
                logger.info(f"JSON output saved to: {output_path}")
            except Exception as e:
                logger.error(f"Failed to save JSON output: {e}")
                print(f"Error saving JSON output: {e}")
        
        return 0
    except KeyboardInterrupt:
        print("\nProcess interrupted by user (CTRL-C)")
        logger.info("Process terminated by keyboard interrupt")
        return 130  # Standard exit code for SIGINT

if __name__ == "__main__":
    sys.exit(main())
