import os
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from models import (
    DiligentizerModel, 
    SoftwareLicenseAgreement,
    EmploymentContract,
    AutoModel
)

@pytest.fixture
def mock_pdf_path():
    """Fixture for a mock PDF path."""
    return "tests/data/mock_document.pdf"

@pytest.fixture
def mock_license_data():
    """Fixture for mock software license data."""
    return {
        "license_type": "Perpetual",
        "licensor": "TechCorp Inc.",
        "licensee": "Client XYZ",
        "effective_date": "2023-01-01",
        "license_fee": 10000.00,
        "termination_date": "2025-12-31",
        "governing_law": "California",
        "limitations_of_liability": True,
        "warranty_period": 90,
        "maintenance_included": True
    }

@pytest.fixture
def mock_employment_data():
    """Fixture for mock employment contract data."""
    return {
        "employer": "ABC Corporation",
        "employee": "Jane Doe",
        "position": "Senior Software Engineer",
        "agreement_date": "2023-02-15",
        "effective_start_date": "2023-03-01",
        "salary": {
            "base_amount": 120000.00,
            "currency": "USD",
            "payment_frequency": "Bi-weekly"
        },
        "term_length": 12,
        "at_will": True,
        "non_compete_months": 6
    }

@pytest.fixture
def mock_llm_response_license():
    """Fixture that mocks a license agreement analysis response from LLM."""
    return json.dumps({
        "license_type": "Perpetual",
        "licensor": "TechCorp Inc.",
        "licensee": "Client XYZ",
        "effective_date": "2023-01-01",
        "license_fee": 10000.00,
        "termination_date": "2025-12-31",
        "governing_law": "California",
        "limitations_of_liability": True,
        "warranty_period": 90,
        "maintenance_included": True
    })

@pytest.fixture
def mock_llm_response_employment():
    """Fixture that mocks an employment contract analysis response from LLM."""
    return json.dumps({
        "employer": "ABC Corporation",
        "employee": "Jane Doe",
        "position": "Senior Software Engineer",
        "agreement_date": "2023-02-15",
        "effective_start_date": "2023-03-01",
        "salary": {
            "base_amount": 120000.00,
            "currency": "USD",
            "payment_frequency": "Bi-weekly"
        },
        "term_length": 12,
        "at_will": True,
        "non_compete_months": 6
    })

@pytest.fixture
def mock_auto_model_response():
    """Fixture that mocks an auto model classification response."""
    return json.dumps({
        "model_type": "SoftwareLicenseAgreement",
        "confidence_score": 0.92,
        "alternate_models": [
            {"model_type": "ServiceLevelAgreement", "confidence_score": 0.45}
        ]
    })

@pytest.fixture
def mock_document_content():
    """Fixture that returns mock content for a document."""
    return """SOFTWARE LICENSE AGREEMENT
    
    This Software License Agreement ("Agreement") is made by and between TechCorp Inc. ("Licensor") 
    and Client XYZ ("Licensee"), effective as of January 1, 2023 ("Effective Date").
    
    1. LICENSE GRANT: Licensor hereby grants to Licensee a perpetual, non-exclusive, non-transferable 
       license to use the Software subject to the terms and conditions of this Agreement.
       
    2. LICENSE FEE: Licensee agrees to pay Licensor a one-time license fee of $10,000.00.
    
    3. WARRANTY: Licensor warrants the Software will operate substantially in accordance with its 
       documentation for a period of ninety (90) days from the Effective Date.
       
    4. LIMITATION OF LIABILITY: IN NO EVENT SHALL LICENSOR BE LIABLE FOR ANY CONSEQUENTIAL, 
       INCIDENTAL, OR INDIRECT DAMAGES.
       
    5. GOVERNING LAW: This Agreement shall be governed by the laws of the State of California.
    
    6. TERMINATION: This Agreement shall terminate on December 31, 2025, unless terminated earlier.
    """

# Create the test directory structure
@pytest.fixture(scope="session", autouse=True)
def create_test_dirs():
    """Create test data directories needed for testing."""
    Path("tests/data").mkdir(parents=True, exist_ok=True)
    # Create a simple mock PDF-like file (just a text file with .pdf extension)
    with open("tests/data/mock_document.pdf", "w") as f:
        f.write("This is a mock PDF document for testing purposes.")
    with open("tests/data/mock_license.pdf", "w") as f:
        f.write("This is a mock software license agreement for testing.")
    with open("tests/data/mock_employment.pdf", "w") as f:
        f.write("This is a mock employment contract for testing.")
    yield
    # Optional cleanup if needed
