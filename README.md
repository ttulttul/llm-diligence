# Diligentizer

Diligentizer is a powerful utility designed to help you collect and organize due diligence material for your company. It automates the extraction of key information from various documents like contracts, financial reports, and legal agreements, producing structured data that's easy to analyze and review.

## Features

- **Document Analysis**: Feed PDFs of contracts, financial reports, legal agreements, and other due diligence materials
- **Intelligent Extraction**: Uses AI to extract relevant information based on document type
- **Structured Data**: Converts unstructured document content into well-organized Pydantic models
- **Auto-Detection**: Can automatically identify document types and apply the appropriate extraction model
- **Extensive Model Library**: Supports numerous document types across various domains:
  - Legal documents (software agreements, employment contracts)
  - Financial statements
  - Corporate structure information
  - Intellectual property documents
  - SaaS metrics and agreements
  - Technical documentation
  - And many more

## How It Works

Diligentizer uses large language models to analyze document content and extract structured information. The process works as follows:

1. You provide a PDF document to analyze
2. Either select a specific extraction model or let the system auto-detect the document type
3. The system analyzes the document content and extracts relevant fields
4. Results are displayed as structured JSON data that matches the corresponding Pydantic model

## Installation

```bash
# Clone the repository
git clone [repository-url]
cd diligentizer

# Run the setup script
./setup.sh
```

The setup script will:
- Create a virtual environment
- Install all dependencies
- Set up a .env file for your API keys

## Usage

List all available models:
```bash
python diligentizer.py --list
```

Analyze a document with automatic model detection:
```bash
python diligentizer.py --auto --pdf path/to/your/document.pdf
```

Analyze a document with a specific model:
```bash
python diligentizer.py --model legal_SoftwareLicenseAgreement --pdf path/to/your/document.pdf
```

## Supported Document Types

Diligentizer supports a wide range of document types, including:

- Software License Agreements
- Employment Contracts
- Financial Statements
- Income Statements
- Service Level Agreements
- Security Compliance Documents
- Corporate Structure Documents
- Intellectual Property Inventories
- Network Architecture Documents
- And many more

You can view the full list of supported models by running `python diligentizer.py --list`

## Future Work

Future development will focus on:

- Exporting extracted data to CSV files
- Database integration for storing and querying extracted information
- Batch processing of multiple documents
- Custom model creation based on your specific document types
- Web interface for document upload and analysis
- API for integrating with other systems

## Contributing

Contributions are welcome! Feel free to submit pull requests or open issues for new features or bug fixes.

## License

[License information]
