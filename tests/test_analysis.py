import pytest
from unittest.mock import patch, MagicMock
import json

from analysis.analyzer import run_analysis, get_available_models
from models import SoftwareLicenseAgreement, EmploymentContract, AutoModel


class TestAnalyzer:
    
    @patch('analysis.analyzer.cached_llm_invoke')
    def test_run_analysis_software_license(self, mock_llm_invoke, mock_llm_response_license, mock_pdf_path):
        """Test analyzing a software license agreement."""
        # Setup the mock to return the parsed JSON instead of a raw string
        # This avoids the error when the analyzer tries to set attributes on the response
        if isinstance(mock_llm_response_license, str):
            mock_response = json.loads(mock_llm_response_license)
        else:
            mock_response = mock_llm_response_license
            
        mock_llm_invoke.return_value = mock_response
        
        # Run the analysis
        result = run_analysis(SoftwareLicenseAgreement, mock_pdf_path)
        
        # Assertions
        assert isinstance(result, SoftwareLicenseAgreement)
        assert result.license_type == "Perpetual"
        assert result.licensor == "TechCorp Inc."
        assert result.licensee == "Client XYZ"
        assert result.governing_law == "California"
        assert result.limitations_of_liability is True
        
        # Verify LLM was called with correct parameters
        mock_llm_invoke.assert_called_once()
        
    @patch('analysis.analyzer.cached_llm_invoke')
    def test_run_analysis_employment_contract(self, mock_llm_invoke, mock_llm_response_employment, mock_pdf_path):
        """Test analyzing an employment contract."""
        # Setup the mock to return the parsed JSON instead of a raw string
        if isinstance(mock_llm_response_employment, str):
            mock_response = json.loads(mock_llm_response_employment)
        else:
            mock_response = mock_llm_response_employment
            
        mock_llm_invoke.return_value = mock_response
        
        # Run the analysis
        result = run_analysis(EmploymentContract, mock_pdf_path)
        
        # Assertions
        assert isinstance(result, EmploymentContract)
        assert result.employer == "ABC Corporation"
        assert result.employee == "Jane Doe"
        assert result.position == "Senior Software Engineer"
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
