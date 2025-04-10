import pytest
from datetime import datetime, date
import json
from pathlib import Path

from models import (
    DiligentizerModel, 
    SoftwareLicenseAgreement,
    EmploymentContract,
    ModelEncoder
)
from models.auto import AutoModel


class TestModelClasses:
    
    def test_software_license_agreement(self, mock_license_data):
        """Test creating and validating a SoftwareLicenseAgreement."""
        license_model = SoftwareLicenseAgreement(**mock_license_data)
        
        assert license_model.licensor == "TechCorp Inc."
        assert license_model.licensee == "Client XYZ"
        assert license_model.start_date == "2023-01-01"
        assert license_model.minimum_price == 10000.00
        
        # Test the JSON serialization
        json_data = license_model.model_dump()
        assert "licensor" in json_data
        assert "licensee" in json_data
        assert "start_date" in json_data
        assert "analyzed_at" in json_data
        
    def test_employment_contract(self, mock_employment_data):
        """Test creating and validating an EmploymentContract."""
        employment_model = EmploymentContract(**mock_employment_data)
        
        assert employment_model.employer == "ABC Corporation"
        assert employment_model.employee == "Jane Doe"
        assert employment_model.job_title == "Senior Software Engineer"
        assert employment_model.agreement_date == date(2023, 2, 15)
        assert employment_model.salary.annual_amount == 120000.00
        assert employment_model.salary.currency == "USD"
        assert len(employment_model.bonuses) == 1
        
        # Test the JSON serialization
        json_data = employment_model.model_dump()
        assert "employer" in json_data
        assert "employee" in json_data
        assert "job_title" in json_data
        assert "salary" in json_data
        assert "annual_amount" in json_data["salary"]
        
    def test_model_encoder(self):
        """Test the ModelEncoder for JSON serialization."""
        # Create a model with date/datetime fields
        test_model = SoftwareLicenseAgreement(
            licensor="Test Corp",
            licensee="Test Client",
            start_date="2023-01-01",
            end_date="2025-12-31",
            auto_renews=False,
            license_grant="perpetual license",
            license_scope="unlimited",
            minimum_price=10000.00,
            price_period="one-time",
            warranty_type="limited warranty",
            liability_limit="fixed monetary amount",
            governing_law_jurisdiction="California",
            dispute_resolution="litigation",
            change_of_control="no restrictions",
            termination_provisions="can only terminate for material breach",
            acceptance_mechanism="signature required",
            analyzed_at=datetime(2023, 1, 1, 12, 0, 0)
        )
        
        # Convert to JSON using the encoder
        json_str = json.dumps(test_model.model_dump(), cls=ModelEncoder)
        json_data = json.loads(json_str)
        
        # Check that dates are properly serialized
        assert json_data["analyzed_at"] == "2023-01-01T12:00:00"
        
        # Ensure we can deserialize back
        deserialized = SoftwareLicenseAgreement.model_validate(json_data)
        assert deserialized.licensor == "Test Corp"
        assert deserialized.start_date == "2023-01-01"
