#!/bin/bash

# Colors for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Diligentizer Project Setup ===${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Python 3 is not installed. Please install Python 3 to continue.${NC}"
    exit 1
fi

# Create virtual environment
echo -e "${GREEN}Creating virtual environment...${NC}"
python3 -m venv venv

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Install required packages
echo -e "${GREEN}Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}Setup complete!${NC}"
echo -e "${YELLOW}To activate the virtual environment in the future, run:${NC}"
echo -e "source venv/bin/activate"

echo -e "${YELLOW}To run the diligentizer, use:${NC}"
echo -e "python diligentizer.py --list"
