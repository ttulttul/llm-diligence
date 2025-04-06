#!/bin/bash

# parallel_diligentizer.sh - Process PDF files recursively in a directory using diligentizer.py
# 
# Usage: ./parallel_diligentizer.sh [options] <directory>
#
# This script finds all PDF files in the specified directory (recursively)
# and processes them in parallel using diligentizer.py.

set -e

# Default values
MAX_JOBS=32
MODEL_TYPE="auto"
MODEL_NAME=""
DATABASE_FILE=""
VERBOSE=0

# Function to display usage information
function show_usage {
    echo "Usage: $(basename $0) [options] <directory>"
    echo ""
    echo "Options:"
    echo "  -j, --jobs N             Maximum number of parallel jobs (default: 32)"
    echo "  -m, --model MODEL_NAME   Use specific model for all files"
    echo "  -a, --auto               Use auto model detection (default)"
    echo "  -d, --db DATABASE_FILE   Save results to SQLite database"
    echo "  -v, --verbose            Show verbose output"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Example:"
    echo "  $(basename $0) --auto --db results.db ./documents"
    echo ""
}

# Check if GNU Parallel is installed
if ! command -v parallel &> /dev/null; then
    echo "Error: This script requires GNU Parallel."
    echo "Please install it with one of the following commands:"
    echo "  - macOS:   brew install parallel"
    echo "  - Ubuntu:  sudo apt-get install parallel"
    echo "  - CentOS:  sudo yum install parallel"
    exit 1
fi

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -j|--jobs)
            MAX_JOBS="$2"
            shift 2
            ;;
        -m|--model)
            MODEL_TYPE="specific"
            MODEL_NAME="$2"
            shift 2
            ;;
        -a|--auto)
            MODEL_TYPE="auto"
            shift
            ;;
        -d|--db)
            DATABASE_FILE="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=1
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        -*)
            echo "Error: Unknown option: $1"
            show_usage
            exit 1
            ;;
        *)
            if [[ -z "$TARGET_DIR" ]]; then
                TARGET_DIR="$1"
            else
                echo "Error: Multiple directory arguments provided."
                show_usage
                exit 1
            fi
            shift
            ;;
    esac
done

# Check if a directory was provided
if [[ -z "$TARGET_DIR" ]]; then
    echo "Error: No directory specified."
    show_usage
    exit 1
fi

# Check if the directory exists
if [[ ! -d "$TARGET_DIR" ]]; then
    echo "Error: Directory '$TARGET_DIR' does not exist."
    exit 1
fi

# Prepare model arguments
if [[ "$MODEL_TYPE" == "auto" ]]; then
    MODEL_ARG="--auto"
elif [[ "$MODEL_TYPE" == "specific" ]]; then
    MODEL_ARG="--model $MODEL_NAME"
else
    echo "Error: Invalid model type: $MODEL_TYPE"
    exit 1
fi

# Prepare database argument
if [[ -n "$DATABASE_FILE" ]]; then
    DB_ARG="--sqlite $DATABASE_FILE"
else
    DB_ARG=""
fi

# Find all PDF files in the target directory
echo "Finding PDF files in '$TARGET_DIR'..."
PDF_FILES=$(find "$TARGET_DIR" -type f -iname "*.pdf" | sort)

# Count how many files we found
FILE_COUNT=$(echo "$PDF_FILES" | wc -l | tr -d ' ')
if [[ $FILE_COUNT -eq 0 ]]; then
    echo "No PDF files found in '$TARGET_DIR'."
    exit 0
fi

echo "Found $FILE_COUNT PDF files to process."
echo "Processing with $MAX_JOBS parallel jobs..."

# Process each PDF file in parallel
if [[ $VERBOSE -eq 1 ]]; then
    # Verbose: Show output from each job
    echo "$PDF_FILES" | parallel -j $MAX_JOBS "echo 'Processing: {}'; python diligentizer.py $MODEL_ARG --pdf {} $DB_ARG; echo 'Completed: {}';"
else
    # Silent: Show progress bar only
    echo "$PDF_FILES" | parallel -j $MAX_JOBS --bar "python diligentizer.py $MODEL_ARG --pdf {} $DB_ARG"
fi

echo "All done! Processed $FILE_COUNT PDF files."
