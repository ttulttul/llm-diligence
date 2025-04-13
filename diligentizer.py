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
from utils.crawler import process_directory
from utils.db import setup_database, save_model_to_db

# Cache for database setup
_db_cache = {}

def save_to_db(db_path, response): 
    logger.info(f"Attempting to save response to database at {db_path}: {response}")
    
    # Check if we've already set up this database
    if db_path not in _db_cache:
        try:
            # Set up the database with all available models
            logger.info(f"Setting up database for the first time: {db_path}")
            models_dict = get_available_models()
            model_classes = list(models_dict.values())
            engine, Session, sa_models = setup_database(db_path, model_classes)
            
            # Cache the setup
            _db_cache[db_path] = (engine, Session, sa_models)
        except Exception as e:
            logger.error(f"Error setting up database: {e}", exc_info=True)
            return
    else:
        # Use cached setup
        logger.debug(f"Using cached database setup for: {db_path}")
        engine, Session, sa_models = _db_cache[db_path]
   
    try:
        # Create a session and save the model
        with Session() as session:
            # Convert the model to a JSON-compatible dict
            json_compatible_data = json.loads(response.model_dump_json())
        
            # Create a new instance with the JSON data
            json_safe_response = type(response).model_validate(json_compatible_data)
        
            sa_instance = save_model_to_db(json_safe_response, sa_models, session)
            # Explicitly commit the transaction
            session.commit()
            logger.info(f"Saved to database: {db_path}, table: {sa_instance.__tablename__}, ID: {sa_instance.id}")
    except Exception as e:
        logger.error(f"Error saving to database: {e}", exc_info=True)

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
        parser.add_argument("--classify-only", action="store_true", help="Return the auto-selected model rather than applying that model to the document. This is useful for pre-classification. (default: False)", default=False)
        parser.add_argument("--classify-to-csv", type=str, help="Path to CSV file to save classification results when using --classify-only")
        parser.add_argument("--pdf", type=str, help="Path to the PDF file")
        parser.add_argument("--crawl-dir", type=str,
                           help="Recursively process all PDF files in the specified directory")
        parser.add_argument("--parallel", type=int, default=0, metavar="N",
                           help="Process files in parallel using N processes (0 for sequential processing)")
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
            print("Error: you must provide a model using --model or --auto")
            return 1
        else:
            # If args.model is provided, use it directly
            selected_model = args.model

        # By default, if the auto model is specified either using --model auto_AutoModel
        # or through the shortcut --auto, then the analysis will first use the auto model
        # to find the right diligence model to use. Then, it will analyze the document using
        # that automatically selected model. If classify_only is True, then we skip the second
        # step and simply return the result from the auto model, which is effectively a classification.
        classify_only = False

        # The --auto-only switch disables running the model that the auto model selected.
        if args.classify_only:
            classify_only = True
        
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
            
        # Validate PDF file if specified
        if args.pdf and not args.crawl_dir and not args.csv_input:
            pdf_path = Path(args.pdf)
            if not pdf_path.exists():
                print(f"Error: PDF file not found: {args.pdf}")
                logger.error(f"PDF file not found: {args.pdf}")
                return 1
            if not pdf_path.is_file():
                print(f"Error: Not a file: {args.pdf}")
                logger.error(f"Not a file: {args.pdf}")
                return 1
            if not os.access(pdf_path, os.R_OK):
                print(f"Error: PDF file is not readable: {args.pdf}")
                logger.error(f"PDF file is not readable: {args.pdf}")
                return 1
        
        # Validate that we have a source to process (PDF, directory, or CSV)
        if not (args.pdf or args.crawl_dir or args.csv_input):
            print("Error: You must specify either --pdf, --crawl-dir, or --csv-input")
            logger.error("No input source specified (PDF, directory, or CSV)")
            return 1
            
        # Validate that --classify-to-csv is only used with --classify-only
        if args.classify_to_csv and not args.classify_only:
            print("Error: --classify-to-csv can only be used with --classify-only")
            logger.error("--classify-to-csv used without --classify-only")
            return 1
            
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
                
        # Process a directory of files or a single file
        if args.crawl_dir:
            # Use the crawler to process a directory
            results_generator = process_directory(
                args.crawl_dir,
                model_class,
                selected_model,
                json_output_dir,
                args.sqlite,
                args.parallel,
                classify_only
            )
        else:
            # Process a single file
            if not args.pdf:
                print("Error: --pdf is required when not using --crawl-dir or --csv-input")
                logger.error("No PDF file specified")
                return 1
            
            # Create a generator that yields a single result for the single PDF
            def single_pdf_generator():
                try:
                    pdf_path = Path(args.pdf)
                    result = run_analysis(model_class, args.pdf, None, classify_only)
                    yield (True, str(pdf_path), result, None)
                except Exception as e:
                    logger.error(f"Failed to process {args.pdf}: {e}")
                    yield (False, str(pdf_path), None, e)
            
            results_generator = single_pdf_generator()
        
        # Process all results from the generator
        success_count = 0
        failure_count = 0
        
        # Set up CSV output for classification results if requested
        csv_file = None
        csv_writer = None
        if args.classify_only and args.classify_to_csv:
            import csv
            try:
                csv_file = open(args.classify_to_csv, 'w', newline='')
                csv_writer = csv.writer(csv_file)
                # Write header row
                csv_writer.writerow(['file_path', 'model_name'])
                logger.info(f"Classification results will be saved to: {args.classify_to_csv}")
                print(f"Classification results will be saved to: {args.classify_to_csv}")
            except Exception as e:
                logger.error(f"Failed to create CSV file: {e}")
                print(f"Error creating CSV file: {e}")
                if csv_file:
                    csv_file.close()
                csv_file = None
                csv_writer = None
        
        for success, file_path, result, exception in results_generator:
            if success:
                logger.info(f"result: SUCCESS {file_path} -> {result}")
                success_count += 1
                
                # Save result as JSON if requested (only if not already done by process_directory)
                if json_output_dir and result and not args.crawl_dir:
                    pdf_path = Path(file_path)
                    output_path = json_output_dir / f"{pdf_path.stem}_{selected_model}.json"
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
                
                # Save to db if requested (only if not already done by process_directory)
                if args.sqlite and result:
                    logger.info(f"Saving to db: {result}")
                    save_to_db(args.sqlite, result)
                
                # Write classification result to CSV if requested
                if args.classify_only and csv_writer and hasattr(result, 'model_name'):
                    csv_writer.writerow([file_path, result.model_name])
                # If this is an AutoModel result with a selection path, log it
                elif hasattr(result, 'selection_path') and result.selection_path:
                    path_str = " -> ".join(result.selection_path)
                    logger.info(f"Model selection path: {path_str}")
                    print(f"Model selection path: {path_str}")
            else:
                logger.info(f"result: FAILURE {file_path} -> exception={exception}")
                failure_count += 1
        
        # Print summary if processing multiple files
        if args.crawl_dir:
            total = success_count + failure_count
            print(f"\nCompleted processing {total} files.")
            print(f"Success: {success_count}, Failures: {failure_count}")
        
        # Close CSV file if it was opened
        if csv_file:
            csv_file.close()
            logger.info(f"Classification CSV file closed: {args.classify_to_csv}")
        
        return 0
    except KeyboardInterrupt:
        print("\nProcess interrupted by user (CTRL-C)")
        logger.info("Process terminated by keyboard interrupt")
        return 130  # Standard exit code for SIGINT

if __name__ == "__main__":
    sys.exit(main())
