import pytest
from unittest.mock import patch, MagicMock
import json

from analysis.analyzer import run_analysis, get_available_models
from models import SoftwareLicenseAgreement, EmploymentContract, AutoModel


class TestAnalyzer:
    
    # Helper class for tests
    class AttributeDict(dict):
        """A dictionary that allows attribute access to its keys and simulates Pydantic model methods."""
        def __init__(self, *args, **kwargs):
            super(TestAnalyzer.AttributeDict, self).__init__(*args, **kwargs)
            self.__dict__ = self
            
        def model_dump_json(self, **kwargs):
            """Simulate Pydantic's model_dump_json method."""
            import json
            from datetime import datetime, date
            
            def json_serializer(obj):
                if isinstance(obj, (datetime, date)):
                    return obj.isoformat()
                raise TypeError(f"Type {type(obj)} not serializable")
                
            return json.dumps(self, default=json_serializer, **kwargs)
            
        def model_dump(self, **kwargs):
            """Simulate Pydantic's model_dump method."""
            return dict(self)
    
    @patch('analysis.analyzer.cached_llm_invoke')
    def test_run_analysis_software_license(self, mock_llm_invoke, mock_llm_response_license, mock_pdf_path):
        """Test analyzing a software license agreement."""
        # Parse the mock response
        if isinstance(mock_llm_response_license, str):
            mock_data = json.loads(mock_llm_response_license)
        else:
            mock_data = mock_llm_response_license
        
        # Create a dict that can also have attributes set
        mock_response = self.AttributeDict(mock_data)
        
        # Add datetime field to simulate what happens in the real code
        from datetime import datetime
        mock_response.analyzed_at = datetime.now()
        
        # Add required fields that might be missing in the mock response
        required_fields = {
            "start_date": "2023-01-01",
            "end_date": "2025-12-31",
            "auto_renews": "Yes",
            "license_grant": "perpetual license",  # Valid enum value
            "license_scope": "entire enterprise",  # Valid enum value
            "minimum_price": "10000.00",
            "price_period": "annually",  # Valid enum value
            "warranty_type": "limited warranty",  # Valid enum value
            "liability_limit": "limited to fees paid",  # Valid enum value
            "governing_law_jurisdiction": "California",
            "dispute_resolution": "arbitration",  # Valid enum value
            "change_of_control": "customer consent required",  # Valid enum value
            "termination_provisions": "can terminate for breach after cure period",  # Valid enum value
            "acceptance_mechanism": "signature required",  # Valid enum value
            "licensor": "TechCorp Inc.",
            "licensee": "Client XYZ"
        }
        
        # Only add fields that don't already exist
        for field, value in required_fields.items():
            if field not in mock_response:
                mock_response[field] = value
        
        # Make sure the mock response has all required fields
        mock_llm_invoke.return_value = mock_response
        
        # Run the analysis
        result = run_analysis(SoftwareLicenseAgreement, mock_pdf_path)
        
        # Assertions
        assert isinstance(result, SoftwareLicenseAgreement)
        assert result.license_grant == "perpetual license"
        assert result.licensor == "TechCorp Inc."
        assert result.licensee == "Client XYZ"
        assert result.governing_law_jurisdiction == "California"
        # Check other fields that exist in the model
        assert result.source_filename == mock_pdf_path
        
        # Verify LLM was called with correct parameters
        mock_llm_invoke.assert_called_once()
        
    @patch('analysis.analyzer.cached_llm_invoke')
    def test_run_analysis_employment_contract(self, mock_llm_invoke, mock_llm_response_employment, mock_pdf_path):
        """Test analyzing an employment contract."""
        # Parse the mock response
        if isinstance(mock_llm_response_employment, str):
            mock_data = json.loads(mock_llm_response_employment)
        else:
            mock_data = mock_llm_response_employment
        
        # Create a dict that can also have attributes set
        mock_response = self.AttributeDict(mock_data)
        
        # Add datetime field to simulate what happens in the real code
        from datetime import datetime
        mock_response.analyzed_at = datetime.now()
        
        # Add any required fields that might be missing in the mock response
        # This ensures the model validation will succeed
        required_fields = {
            "agreement_date": "2023-01-01",
            "effective_start_date": "2023-01-15",
            "term_type": "indefinite",  # Use lowercase to match enum values
            "governing_law": "California",
            "employer_name": "ABC Corporation",
            "employee_name": "Jane Doe",
            "job_title": "Senior Software Engineer",
            "at_will": True,
            "salary": {"base_amount": 120000.00, "currency": "USD"}
        }
        
        # Only add fields that don't already exist
        for field, value in required_fields.items():
            if field not in mock_response:
                mock_response[field] = value
        
        mock_llm_invoke.return_value = mock_response
        
        # Run the analysis
        result = run_analysis(EmploymentContract, mock_pdf_path)
        
        # Assertions
        assert isinstance(result, EmploymentContract)
        assert result.employer_name == "ABC Corporation"  # Changed from employer to employer_name
        assert result.employee_name == "Jane Doe"  # Changed from employee to employee_name
        assert result.job_title == "Senior Software Engineer"  # Changed from position to job_title
        assert result.at_will is True
        assert result.salary.base_amount == 120000.00
        assert result.salary.currency == "USD"
        
    @patch('analysis.analyzer.get_available_models')
    def test_get_available_models(self, mock_get_models):
        """Test that available models are retrieved correctly."""
        # Setup mock return value
        mock_models = {
            "software_license_agreement": SoftwareLicenseAgreement,
            "employment_contract": EmploymentContract,
            "auto": AutoModel
        }
        mock_get_models.return_value = mock_models
        
        # Get models
        models = get_available_models()
        
        # Assertions
        assert "software_license_agreement" in models
        assert "employment_contract" in models
        assert "auto" in models
        assert models["software_license_agreement"] == SoftwareLicenseAgreement
