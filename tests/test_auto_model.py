import pytest
from unittest.mock import patch, MagicMock
import json

from models.auto import AutoModel, ModelSelection
from models import SoftwareLicenseAgreement, EmploymentContract


class TestAutoModel:
    @patch('models.auto.cached_llm_invoke')
    def test_auto_model_selection(self, mock_llm_invoke, mock_pdf_path):
        """Test that AutoModel correctly selects the appropriate model."""
        # Create a ModelSelection instance for the mock response
        mock_response = ModelSelection(model_name="SoftwareLicenseAgreement")
        
        # Setup mock
        mock_llm_invoke.return_value = mock_response
        
        # Define available models
        available_models = {
            "software_license_agreement": SoftwareLicenseAgreement,
            "employment_contract": EmploymentContract
        }
        
        # Test the from_pdf method
        auto_model = AutoModel.from_pdf(mock_pdf_path, available_models)
        
        # Assertions
        assert auto_model.chosen_model_name == "software_license_agreement"
        assert auto_model.chosen_model_result is None
        
        # Make sure the LLM was called correctly
        mock_llm_invoke.assert_called_once()
    
    @patch('models.auto.cached_llm_invoke')
    def test_auto_model_with_class_name(self, mock_llm_invoke, mock_pdf_path):
        """Test that AutoModel correctly handles class name instead of dict key."""
        # Create a ModelSelection instance with the class name instead of the dict key
        mock_response = ModelSelection(model_name="EmploymentContract")
        
        # Setup mock
        mock_llm_invoke.return_value = mock_response
        
        # Define available models
        available_models = {
            "software_license_agreement": SoftwareLicenseAgreement,
            "employment_contract": EmploymentContract
        }
        
        # Test the from_pdf method
        auto_model = AutoModel.from_pdf(mock_pdf_path, available_models)
        
        # Assertions - should match the dict key, not the class name
        assert auto_model.chosen_model_name == "employment_contract"
        assert auto_model.chosen_model_result is None
        
        # Make sure the LLM was called correctly
        mock_llm_invoke.assert_called_once()
    
    @patch('models.auto.cached_llm_invoke')
    def test_auto_model_with_invalid_model(self, mock_llm_invoke, mock_pdf_path):
        """Test AutoModel behavior when an invalid model is selected."""
        # Create a ModelSelection instance with an invalid model name
        mock_response = ModelSelection(model_name="InvalidModel")
        
        # Setup mock
        mock_llm_invoke.return_value = mock_response
        
        # Define available models
        available_models = {
            "software_license_agreement": SoftwareLicenseAgreement,
            "employment_contract": EmploymentContract
        }
        
        # Test with invalid model name - should raise ValueError
        with pytest.raises(ValueError) as excinfo:
            auto_model = AutoModel.from_pdf(mock_pdf_path, available_models)
        
        # Check error message
        assert "LLM selected invalid model: InvalidModel" in str(excinfo.value)
        assert "Valid options are: software_license_agreement, employment_contract" in str(excinfo.value)
