import json
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Type, List, Optional, Tuple

from models import ModelEncoder
from models.base import DiligentizerModel
from analysis import run_analysis
from utils import logger

def process_file(args: Tuple) -> Tuple[bool, str, Optional[DiligentizerModel], Optional[Exception]]:
    """
    Process a single PDF file.
    
    Args:
        args: Tuple containing (pdf_path, model_class, sqlite_path, json_output_dir, 
                               selected_model, crawl_path, classify_only, prompt_extra, provider)
        
    Returns:
        Tuple of (success, file_path, result, exception)
    """
    pdf_path, model_class, sqlite_path, json_output_dir, selected_model, crawl_path, classify_only, prompt_extra, provider = args
    
    try:
        # Calculate relative path for output
        relative_path = pdf_path.relative_to(crawl_path)
        
        # Run analysis on this file
        result = run_analysis(model_class, str(pdf_path), sqlite_path, classify_only, prompt_extra, provider=provider)
        
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
                logger.info(f"JSON output saved to: {output_path}")
            except Exception as e:
                logger.error(f"Failed to save JSON output for {pdf_path}: {e}")
                return False, str(pdf_path), result, e
                
        return True, str(pdf_path), result, None
    except Exception as e:
        logger.error(f"Failed to process {pdf_path}: {e}")
        return False, str(pdf_path), None, e

def process_directory(
    crawl_dir: str,
    model_class: Type[DiligentizerModel],
    selected_model: str,
    json_output_dir: Optional[Path] = None,
    sqlite_path: Optional[str] = None,
    parallel: int = 0,
    classify_only: bool = False,
    prompt_extra: Optional[str] = None,
    crawl_limit: Optional[int] = None,
    provider: str = "anthropic"
):
    """
    Recursively process all PDF files in the specified directory.
    
    Args:
        crawl_dir: Directory to crawl for PDF files
        model_class: The model class to use for analysis
        selected_model: Name of the selected model (for output filenames)
        json_output_dir: Optional directory to save JSON output
        sqlite_path: Optional path to SQLite database
        parallel: Number of parallel processes to run
        classify_only: Will be passed to run_analysis()
        prompt_extra: Will be passed to run_analysis()
        
    Yields:
        Tuple containing (success: bool, file_path: str, result: Optional[DiligentizerModel], 
                          exception: Optional[Exception])
    """
    # Get all PDF files in the directory and subdirectories
    crawl_path = Path(crawl_dir)
    if not crawl_path.exists() or not crawl_path.is_dir():
        logger.error(f"Directory not found: {crawl_dir}")
        yield (False, crawl_dir, None, ValueError(f"Directory not found: {crawl_dir}"))
        return
        
    pdf_files = list(crawl_path.glob('**/*.pdf'))
    if not pdf_files:
        logger.warning(f"No PDF files found in {crawl_dir}")
        yield (False, crawl_dir, None, ValueError(f"No PDF files found in {crawl_dir}"))
        return
    
    # Apply crawl limit if specified
    if crawl_limit and crawl_limit > 0 and len(pdf_files) > crawl_limit:
        logger.info(f"Limiting crawl to {crawl_limit} of {len(pdf_files)} PDF files found")
        pdf_files = pdf_files[:crawl_limit]
    else:
        logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    # Determine whether to use parallel processing
    if parallel > 0:
        logger.info(f"Using parallel processing with {parallel} processes")
        
        # Prepare arguments for each file
        process_args = [
            (pdf_path, model_class, sqlite_path, json_output_dir, selected_model, crawl_path, classify_only, prompt_extra, provider)
            for pdf_path in pdf_files
        ]
        
        # Process files in parallel
        with ProcessPoolExecutor(max_workers=parallel) as executor:
            for i, (success, file_path, result, exception) in enumerate(executor.map(process_file, process_args)):
                relative_path = Path(file_path).relative_to(crawl_path)
                
                # Yield the result to the caller
                yield (success, file_path, result, exception)
        
    else:
        # Process files sequentially
        for i, pdf_path in enumerate(pdf_files):
            relative_path = pdf_path.relative_to(crawl_path)
            logger.info(f"Processing file: {pdf_path}")
            
            success, file_path, result, exception = process_file((pdf_path, model_class, sqlite_path, json_output_dir, selected_model, crawl_path, classify_only, prompt_extra, provider))
            
            # Yield the result to the caller
            yield (success, file_path, result, exception)
