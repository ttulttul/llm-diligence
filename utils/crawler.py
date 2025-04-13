import json
from pathlib import Path
from typing import Type, List, Optional

from models import ModelEncoder
from models.base import DiligentizerModel
from analysis import run_analysis
from utils import logger

def process_directory(
    crawl_dir: str,
    model_class: Type[DiligentizerModel],
    selected_model: str,
    json_output_dir: Optional[Path] = None,
    sqlite_path: Optional[str] = None
) -> int:
    """
    Recursively process all PDF files in the specified directory.
    
    Args:
        crawl_dir: Directory to crawl for PDF files
        model_class: The model class to use for analysis
        selected_model: Name of the selected model (for output filenames)
        json_output_dir: Optional directory to save JSON output
        sqlite_path: Optional path to SQLite database
        
    Returns:
        int: 0 for success, 1 for failure
    """
    # Get all PDF files in the directory and subdirectories
    crawl_path = Path(crawl_dir)
    if not crawl_path.exists() or not crawl_path.is_dir():
        logger.error(f"Directory not found: {crawl_dir}")
        return 1
        
    pdf_files = list(crawl_path.glob('**/*.pdf'))
    if not pdf_files:
        logger.warning(f"No PDF files found in {crawl_dir}")
        return 0
        
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    print(f"Processing {len(pdf_files)} PDF files from {crawl_dir}...")
    
    # Process each PDF file
    for pdf_path in pdf_files:
        relative_path = pdf_path.relative_to(crawl_path)
        print(f"\nProcessing: {relative_path}")
        logger.info(f"Processing file: {pdf_path}")
        
        try:
            # Run analysis on this file
            result = run_analysis(model_class, str(pdf_path), sqlite_path)
            
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
                        json.dump(result.model_dump(), f, cls=ModelEncoder, indent=2)
                    print(f"JSON output saved to: {output_path}")
                    logger.info(f"JSON output saved to: {output_path}")
                except Exception as e:
                    logger.error(f"Failed to save JSON output for {pdf_path}: {e}")
                    print(f"Error saving JSON output: {e}")
        except Exception as e:
            logger.error(f"Failed to process {pdf_path}: {e}")
            print(f"Error processing {pdf_path}: {e}")
    
    return 0
