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
        # Required Agreement fields
        "agreement_title": "Software License Agreement",
        "agreement_date": "2023-01-01",
        "effective_date": "2023-01-01",
        "governing_law": "California",
        "term_description": "3 year term from 2023-01-01 to 2025-12-31",
        # License-specific fields
        "licensor": "TechCorp Inc.",
        "licensee": "Client XYZ",
        "start_date": "2023-01-01",
        "end_date": "2025-12-31",
        "auto_renews": False,
        "license_grant": "perpetual license",
        "license_scope": "unlimited",
        "minimum_price": 10000.00,
        "price_period": "one-time",
        "warranty_type": "limited warranty",
        "liability_limit": "fixed monetary amount",
        "governing_law_jurisdiction": "California",
        "dispute_resolution": "litigation",
        "change_of_control": "no restrictions",
        "termination_provisions": "can only terminate for material breach",
        "acceptance_mechanism": "signature required",
        "maintenance_included": True
    }

@pytest.fixture
def mock_employment_data():
    """Fixture for mock employment contract data."""
    return {
        # Required Agreement fields
        "agreement_title": "Employment Agreement",
        "agreement_date": "2023-02-15",
        "effective_date": "2023-03-01",
        "governing_law": "California",
        "term_description": "Indefinite employment term",
        # Required EmploymentAgreement fields
        "employer": "ABC Corporation",
        "employee": "Jane Doe",
        "compensation_description": "Annual salary of $120,000 USD paid bi-weekly",
        # Required EmploymentContract fields
        "termination_for_cause": "Immediate termination for misconduct",
        "termination_without_cause_employer": "30 days notice required",
        # Optional EmploymentContract fields
        "job_title": "Senior Software Engineer",
        "effective_start_date": "2023-03-01",
        "salary_amount": 120000.00,
        "salary_currency": "USD",
        "salary_payment_frequency": "bi-weekly",
        "bonuses": ["Performance bonus up to $20,000 annually"],
        "benefits_description": "Standard company benefits package",
        "vacation_policy_description": "15 days paid vacation annually",
        "non_competition_duration_months": 6,
        "non_competition_scope": "Software industry within 50 miles",
        "non_solicitation_duration_months": 12,
        "non_solicitation_scope": "Company clients and employees",
        "confidentiality_clause_present": True,
        "intellectual_property_assignment": True
    }

@pytest.fixture
def mock_llm_response_license():
    """Fixture that mocks a license agreement analysis response from LLM."""
    return json.dumps({
        "licensor": "TechCorp Inc.",
        "licensee": "Client XYZ",
        "start_date": "2023-01-01",
        "end_date": "2025-12-31",
        "auto_renews": False,
        "license_grant": "perpetual license",
        "license_scope": "unlimited",
        "minimum_price": 10000.00,
        "price_period": "one-time",
        "warranty_type": "limited warranty",
        "liability_limit": "fixed monetary amount",
        "governing_law_jurisdiction": "California",
        "dispute_resolution": "litigation",
        "change_of_control": "no restrictions",
        "termination_provisions": "can only terminate for material breach",
        "acceptance_mechanism": "signature required",
        "maintenance_included": True,
        "source_filename": None,
        "analyzed_at": "2023-01-01T12:00:00"
    })

@pytest.fixture
def mock_llm_response_employment():
    """Fixture that mocks an employment contract analysis response from LLM."""
    return json.dumps({
        "employer": "ABC Corporation",
        "employee": "Jane Doe",
        "job_title": "Senior Software Engineer",
        "agreement_date": "2023-02-15",
        "effective_start_date": "2023-03-01",
        "salary_amount": 120000.00,
        "salary_currency": "USD",
        "salary_payment_frequency": "bi-weekly",
        "bonuses": [
            {
                "description": "Performance bonus",
                "max_amount": 20000.00,
                "currency": "USD",
                "timing": "annually",
                "conditions": "Based on company and individual performance"
            }
        ],
        "benefits_description": "Standard company benefits package",
        "vacation_policy_description": "15 days paid vacation annually",
        "termination_clauses": {
            "for_cause": "Immediate termination for misconduct",
            "without_cause_employer": "30 days notice required",
            "resignation_employee": "30 days notice required"
        },
        "restrictive_covenants": {
            "non_competition_duration_months": 6,
            "non_competition_scope": "Software industry within 50 miles",
            "non_solicitation_duration_months": 12,
            "non_solicitation_scope": "Company clients and employees",
            "confidentiality_clause_present": True,
            "intellectual_property_assignment": True
        },
        "governing_law": "California",
        "source_filename": None,
        "analyzed_at": "2023-02-15T10:00:00"
    })

@pytest.fixture
def mock_auto_model_response():
    """Fixture that mocks an auto model classification response."""
    return json.dumps({
        "model_name": "SoftwareLicenseAgreement"
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
