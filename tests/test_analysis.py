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
        
        # Create a proper model-like response
        from datetime import datetime, date
        
        # Ensure all required fields are present with proper types
        mock_data.update({
            "source_filename": mock_pdf_path,
            "analyzed_at": datetime.now(),
            "llm_model": "claude-3-opus-20240229",
            "licensor": "TechCorp Inc.",
            "licensee": "Client XYZ",
            "effective_date": date(2023, 1, 1),
            "expiration_date": date(2025, 12, 31),
            "license_type": "Perpetual",
            "license_fee": 10000.00,
            "license_grant": "PERPETUAL",  # Enum value
            "license_scope": "ENTERPRISE",  # Enum value
            "warranty_type": "LIMITED",  # Enum value
            "liability_limit": "FEES_PAID",  # Enum value
            "governing_law_jurisdiction": "California",
            "dispute_resolution": "ARBITRATION",  # Enum value
            "change_of_control": "CONSENT_REQUIRED",  # Enum value
            "termination_provisions": "BREACH_WITH_CURE",  # Enum value
            "acceptance_mechanism": "SIGNATURE",  # Enum value
            "price_period": "ANNUAL"  # Enum value
        })
        
        # Create a model-like object that will be returned by the mock
        mock_response = self.AttributeDict(mock_data)
        
        # Set up the mock to return our properly formatted response
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
        
        # Create a proper model-like response with all required fields
        from datetime import datetime, date
        
        # Create the nested objects with proper structure
        salary_data = {
            "annual_amount": 120000.00,
            "currency": "USD",
            "payment_frequency": "Bi-weekly"
        }
        
        termination_clauses = {
            "for_cause": "Immediate termination for gross misconduct",
            "without_cause_employer": "Two weeks notice required",
            "resignation_employee": "Two weeks notice required"
        }
        
        restrictive_covenants = {
            "non_solicitation_duration_months": 12,
            "non_solicitation_scope": "Employees and clients",
            "non_competition_duration_months": 6,
            "non_competition_scope": "Software industry within 50 miles",
            "confidentiality_clause_present": True,
            "intellectual_property_assignment": True
        }
        
        # Update the mock data with properly structured fields
        mock_data.update({
            "source_filename": mock_pdf_path,
            "analyzed_at": datetime.now(),
            "llm_model": "claude-3-opus-20240229",
            "employer": "ABC Corporation",
            "employee": "Jane Doe",
            "job_title": "Senior Software Engineer",
            "agreement_date": date(2023, 1, 1),
            "effective_start_date": date(2023, 1, 15),
            "salary": salary_data,
            "bonuses": [],
            "benefits_description": "Standard company benefits package",
            "vacation_policy_description": "15 days paid vacation annually",
            "termination_clauses": termination_clauses,
            "restrictive_covenants": restrictive_covenants,
            "governing_law": "California",
            "on_call_requirements": None,
            "appendices_referenced": ["Employee Handbook", "Confidentiality Agreement"]
        })
        
        # Create a model-like object that will be returned by the mock
        mock_response = self.AttributeDict(mock_data)
        
        # Set up the mock to return our properly formatted response
        mock_llm_invoke.return_value = mock_response
        
        # Run the analysis
        result = run_analysis(EmploymentContract, mock_pdf_path)
        
        # Assertions
        assert isinstance(result, EmploymentContract)
        assert result.employer == "ABC Corporation"
        assert result.employee == "Jane Doe"
        assert result.job_title == "Senior Software Engineer"
        assert result.salary.annual_amount == 120000.00
        assert result.salary.currency == "USD"
        assert result.salary.payment_frequency == "Bi-weekly"
        assert result.governing_law == "California"
        assert result.termination_clauses.for_cause == "Immediate termination for gross misconduct"
        assert result.restrictive_covenants.confidentiality_clause_present is True
        assert len(result.appendices_referenced) == 2
        
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
