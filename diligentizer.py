import sys
import argparse
import os
import json
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import from the analysis module
from analysis import get_available_models, list_available_models, run_analysis
from utils import logger, configure_logger


def process_csv_file(csv_input_path, csv_input_column, csv_output_path, column_prefix, model_class):
    """Process a CSV file, analyzing text in the specified column and outputting results.
    
    Args:
        csv_input_path: Path to the input CSV file
        csv_input_column: Name of the column containing text to analyze
        csv_output_path: Path to save the output CSV file
        column_prefix: Prefix for output columns
        model_class: The model class to use for analysis
        
    Returns:
        bool: True if processing was successful, False otherwise
    """
    try:
        # Try to read the CSV file with pandas, which automatically handles encoding detection
        try:
            df = pd.read_csv(csv_input_path)
        except UnicodeDecodeError:
            # If UTF-8 fails, try with cp1252 encoding
            logger.info("UTF-8 encoding failed, trying with cp1252 encoding")
            df = pd.read_csv(csv_input_path, encoding='cp1252')
        
        # Check if the specified column exists
        if csv_input_column not in df.columns:
            print(f"Error: Column '{csv_input_column}' not found in CSV file")
            return False
        
        # Get model fields to create output columns
        model_fields = list(model_class.model_fields.keys())
        output_columns = [f"{column_prefix}{field}" for field in model_fields]
        
        # Initialize output columns with empty values
        for col in output_columns:
            df[col] = ""
        
        # Process each row in the dataframe
        for i, row in df.iterrows():
            print(f"Processing row {i+1}...")
            logger.info(f"Processing row {i+1}")
            
            # Get the text to analyze
            text_to_analyze = row[csv_input_column]
            
            # Skip empty text
            if pd.isna(text_to_analyze) or text_to_analyze == "":
                logger.warning(f"Empty text in row {i+1}, skipping")
                continue
            
            try:
                # Create a system message for text analysis
                system_message = (
                    "You are a document analysis assistant that extracts structured information from text. "
                    "Analyze the provided text and extract key details according to the specified schema."
                )
                
                # Create a prompt based on the model fields
                field_descriptions = []
                for field_name, field_info in model_class.model_fields.items():
                    desc = field_info.description or f"the {field_name}"
                    field_descriptions.append(f'  "{field_name}": "<string: {desc}>"')
                
                fields_json = ",\n".join(field_descriptions)
                
                prompt = (
                    f"Analyze the following text and extract the key details. "
                    f"Your output must be valid JSON matching this exact schema: "
                    f"{{\n{fields_json}\n}}. "
                    f"Output only the JSON."
                )
                
                # Use cached LLM invoke for text analysis
                from utils.llm import cached_llm_invoke
                
                message_content = [
                    {"type": "text", "text": prompt},
                    {"type": "text", "text": text_to_analyze}
                ]
                
                response = cached_llm_invoke(
                    system_message=system_message,
                    user_content=message_content,
                    max_tokens=2000,
                    response_model=model_class
                )
                
                # Add analysis results to the dataframe
                result_dict = response.model_dump()
                
                # Add analysis results with prefixed column names
                for field_name in model_fields:
                    output_column = f"{column_prefix}{field_name}"
                    if field_name in result_dict:
                        # Convert complex objects to strings
                        if isinstance(result_dict[field_name], (dict, list)):
                            df.at[i, output_column] = json.dumps(result_dict[field_name])
                        else:
                            df.at[i, output_column] = str(result_dict[field_name])
                
                logger.info(f"Successfully processed row {i+1}")
                
            except Exception as e:
                logger.error(f"Error processing row {i+1}: {e}", exc_info=True)
                print(f"Error processing row {i+1}: {e}")
                # Row will keep empty values for analysis columns
        
        # Write the dataframe to the output CSV
        df.to_csv(csv_output_path, index=False)
        
        print(f"Analysis complete. Results written to {csv_output_path}")
        logger.info(f"CSV processing complete. Output saved to {csv_output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing CSV file: {e}", exc_info=True)
        print(f"Error processing CSV file: {e}")
        return False

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
        parser.add_argument("--crawl-dir", type=str,
                           help="Recursively process all PDF files in the specified directory")
        parser.add_argument("--sqlite", type=str, help="Path to SQLite database for storing results")
        parser.add_argument("--json-output", type=str, metavar="DIR",
                           help="Output results as JSON files to specified directory")
        parser.add_argument("--csv-input", type=str, help="Path to CSV file for batch processing")
        parser.add_argument("--csv-input-column", type=str, help="Column name in CSV containing text to analyze")
        parser.add_argument("--csv-output", type=str, help="Path to output CSV file with analysis results")
        parser.add_argument("--csv-output-column-prefix", type=str, default="analysis_",
                           help="Prefix for output columns in CSV (default: analysis_)")
        parser.add_argument("--log-level", type=str, default="WARNING", 
                           choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                           help="Set the logging level (default: WARNING)")
        parser.add_argument("--log-file", type=str, help="Path to the log file")
        parser.add_argument("--verbose", action="store_true", help="Be verbose about everything")
        
        args = parser.parse_args()

        # If verbose is configured, override the log level
        if args.verbose:
            args.log_level = "INFO"
        
        # Configure logger with command line arguments
        configure_logger(args.log_level, args.log_file)
        logger.debug("Diligentizer starting up")
        
        # Get all available models
        models_dict = get_available_models()
        
        if not models_dict:
            logger.error("No models found in the models directory.")
            return 1
            
        if args.list:
            list_available_models(models_dict, verbose=args.verbose)
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
        json_output_dir = None
        if args.json_output:
            json_output_dir = Path(args.json_output)
            json_output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"JSON output will be saved to: {json_output_dir}")
        
        # Process a CSV file if specified
        if args.csv_input:
            if not args.csv_input_column:
                print("Error: --csv-input-column is required when using --csv-input")
                return 1
            
            if not args.csv_output:
                print("Error: --csv-output is required when using --csv-input")
                return 1
                
            # Process the CSV file
            logger.info(f"Processing CSV file: {args.csv_input}")
            print(f"Processing CSV file: {args.csv_input}")
            
            success = process_csv_file(
                args.csv_input,
                args.csv_input_column,
                args.csv_output,
                args.csv_output_column_prefix,
                model_class
            )
            
            if not success:
                return 1
                
        # Process a directory of files
        elif args.crawl_dir:
            # Get all PDF files in the directory and subdirectories
            crawl_path = Path(args.crawl_dir)
            if not crawl_path.exists() or not crawl_path.is_dir():
                logger.error(f"Directory not found: {args.crawl_dir}")
                return 1
                
            pdf_files = list(crawl_path.glob('**/*.pdf'))
            if not pdf_files:
                logger.warning(f"No PDF files found in {args.crawl_dir}")
                return 0
                
            logger.info(f"Found {len(pdf_files)} PDF files to process")
            print(f"Processing {len(pdf_files)} PDF files from {args.crawl_dir}...")
            
            # Process each PDF file
            for pdf_path in pdf_files:
                relative_path = pdf_path.relative_to(crawl_path)
                print(f"\nProcessing: {relative_path}")
                logger.info(f"Processing file: {pdf_path}")
                
                try:
                    # Run analysis on this file
                    result = run_analysis(model_class, str(pdf_path), args.sqlite)
                    
                    # Save result as JSON if requested
                    if json_output_dir and result:
                        # Create subdirectories in the output dir to match the input structure
                        if len(relative_path.parts) > 1:
                            output_subdir = json_output_dir / Path(*relative_path.parts[:-1])
                            output_subdir.mkdir(parents=True, exist_ok=True)
                        else:
                            output_subdir = json_output_dir
                            
                        # Use the filename as part of the output filename
                        output_filename = f"{relative_path.stem}_{selected_model}.json"
                        output_path = output_subdir / output_filename
                        
                        try:
                            with open(output_path, 'w') as f:
                                # Use the ModelEncoder to handle datetime objects
                                from models import ModelEncoder
                                json.dump(result.model_dump(), f, cls=ModelEncoder, indent=2)
                            print(f"JSON output saved to: {output_path}")
                            logger.info(f"JSON output saved to: {output_path}")
                        except Exception as e:
                            logger.error(f"Failed to save JSON output for {pdf_path}: {e}")
                            print(f"Error saving JSON output: {e}")
                except Exception as e:
                    logger.error(f"Failed to process {pdf_path}: {e}")
                    print(f"Error processing {pdf_path}: {e}")
        else:
            # Process a single file
            result = run_analysis(model_class, args.pdf, args.sqlite)
            
            # Save result as JSON if requested
            if json_output_dir and result:
                output_path = json_output_dir / f"{Path(args.pdf).stem}_{selected_model}.json"
                try:
                    with open(output_path, 'w') as f:
                        # Use the ModelEncoder to handle datetime objects
                        from models import ModelEncoder
                        json.dump(result.model_dump(), f, cls=ModelEncoder, indent=2)
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
