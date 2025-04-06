#!/bin/bash

# parallel_diligentizer.sh - Process PDF files recursively in a directory using diligentizer.py
# 
# Usage: ./parallel_diligentizer.sh [options] <directory>
#
# This script finds all PDF files in the specified directory (recursively)
# and processes them in parallel using diligentizer.py with find and xargs.

set -e

# Default values
MAX_JOBS=32
MODEL_TYPE="auto"
MODEL_NAME=""
DATABASE_FILE=""
VERBOSE=0
LOG_LEVEL="INFO"
LOG_FILE=""
ERROR_LOG_FILE=""
TOTAL_PROCESSED=0
TOTAL_FILES=0

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
    echo "  -l, --log-level LEVEL    Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    echo "  -f, --log-file FILE      Write logs to file"
    echo "  -e, --error-log FILE     Write stderr from subprocesses to file"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Example:"
    echo "  $(basename $0) --auto --db results.db ./documents"
    echo ""
}

# Create a function to process a PDF file
process_pdf() {
    local pdf_file="$1"
    local model_arg="$2"
    local db_arg="$3"
    local verbose="$4"
    local log_level="$5"
    local log_file_arg="$6"
    local error_log_file="$7"
    
    if [[ $verbose -eq 1 ]]; then
        echo "Processing: $pdf_file"
        python diligentizer.py $model_arg --pdf "$pdf_file" $db_arg --log-level "$log_level" $log_file_arg
        echo "Completed: $pdf_file"
    else
        if [[ -n "$error_log_file" ]]; then
            # Prefix errors with filename and timestamp for context
            python diligentizer.py $model_arg --pdf "$pdf_file" $db_arg --log-level "$log_level" $log_file_arg >/dev/null 2>> >(sed "s/^/$(date '+%Y-%m-%d %H:%M:%S') - $pdf_file: /" >> "$error_log_file")
        else
            python diligentizer.py $model_arg --pdf "$pdf_file" $db_arg --log-level "$log_level" $log_file_arg >/dev/null 2>&1
        fi
        # Update progress (safely for concurrent processes)
        local tmp_count
        tmp_count=$(cat /tmp/diligentizer_count 2>/dev/null || echo 0)
        echo $((tmp_count + 1)) > /tmp/diligentizer_count
        local current=$(cat /tmp/diligentizer_count 2>/dev/null || echo 0)
        if [[ $TOTAL_FILES -gt 0 ]]; then
            printf "\rProcessed %d/%d files (%.1f%%)" $current $TOTAL_FILES $(echo "scale=1; $current*100/$TOTAL_FILES" | bc)
        else
            printf "\rProcessed %d files" $current
        fi
    fi
}
export -f process_pdf

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
        -l|--log-level)
            LOG_LEVEL="$2"
            shift 2
            ;;
        -f|--log-file)
            LOG_FILE="$2"
            shift 2
            ;;
        -e|--error-log)
            ERROR_LOG_FILE="$2"
            shift 2
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

# Prepare log file argument
if [[ -n "$LOG_FILE" ]]; then
    LOG_FILE_ARG="--log-file $LOG_FILE"
else
    LOG_FILE_ARG=""
fi

# Initialize error log file if specified
if [[ -n "$ERROR_LOG_FILE" ]]; then
    # Create directory if it doesn't exist
    ERROR_LOG_DIR=$(dirname "$ERROR_LOG_FILE")
    if [[ -n "$ERROR_LOG_DIR" && "$ERROR_LOG_DIR" != "." ]]; then
        mkdir -p "$ERROR_LOG_DIR"
    fi
    
    # Initialize with header
    echo "# Diligentizer Error Log - Started $(date)" > "$ERROR_LOG_FILE"
    echo "# Command: $0 $*" >> "$ERROR_LOG_FILE"
    echo "# -------------------------------------------------" >> "$ERROR_LOG_FILE"
fi

# Find all PDF files in the target directory and count them
echo "Finding PDF files in '$TARGET_DIR'..."
TOTAL_FILES=$(find "$TARGET_DIR" -type f -iname "*.pdf" | wc -l | tr -d ' ')

if [[ $TOTAL_FILES -eq 0 ]]; then
    echo "No PDF files found in '$TARGET_DIR'."
    exit 0
fi

echo "Found $TOTAL_FILES PDF files to process."
echo "Processing with $MAX_JOBS parallel jobs..."

# Initialize counter file
echo 0 > /tmp/diligentizer_count

# Process files in parallel using find and xargs with null delimiter
if [[ $VERBOSE -eq 1 ]]; then
    # Verbose: Show output from each job
    find "$TARGET_DIR" -type f -iname "*.pdf" -print0 | \
    xargs -0 -P "$MAX_JOBS" -n 1 bash -c "export TOTAL_FILES=$TOTAL_FILES; process_pdf \"\$1\" '$MODEL_ARG' '$DB_ARG' 1 '$LOG_LEVEL' '$LOG_FILE_ARG' '$ERROR_LOG_FILE'" {} 
else
    # Silent: Show progress counter
    find "$TARGET_DIR" -type f -iname "*.pdf" -print0 | \
    xargs -0 -P "$MAX_JOBS" -n 1 bash -c "export TOTAL_FILES=$TOTAL_FILES; process_pdf \"\$1\" '$MODEL_ARG' '$DB_ARG' 0 '$LOG_LEVEL' '$LOG_FILE_ARG' '$ERROR_LOG_FILE'" {}
    echo # Print newline after progress display
fi

# Clean up
rm -f /tmp/diligentizer_count

echo "All done! Processed $TOTAL_FILES PDF files."
