import pytest
from unittest.mock import patch, MagicMock
import json

from models.auto import AutoModel
from models import SoftwareLicenseAgreement, EmploymentContract


class TestAutoModel:
    
    @patch('models.auto.cached_llm_invoke')
    def test_auto_model_selection(self, mock_llm_invoke, mock_auto_model_response, mock_pdf_path):
        """Test that AutoModel correctly selects the appropriate model."""
        # Setup mock
        mock_llm_invoke.return_value = mock_auto_model_response
        
        # Define available models
        available_models = {
            "software_license_agreement": SoftwareLicenseAgreement,
            "employment_contract": EmploymentContract
        }
        
        # Test the from_pdf method
        auto_model = AutoModel.from_pdf(mock_pdf_path, available_models)
        
        # Assertions
        assert auto_model.selected_model_type == "SoftwareLicenseAgreement"
        assert auto_model.confidence_score == 0.92
        assert len(auto_model.alternate_models) == 1
        assert auto_model.alternate_models[0]["model_type"] == "ServiceLevelAgreement"
        
        # Make sure the LLM was called correctly
        mock_llm_invoke.assert_called_once()
    
    @patch('models.auto.cached_llm_invoke')
    def test_auto_model_with_low_confidence(self, mock_llm_invoke, mock_pdf_path):
        """Test AutoModel behavior when confidence is below threshold."""
        # Setup mock to return low confidence
        mock_llm_invoke.return_value = json.dumps({
            "model_type": "SoftwareLicenseAgreement",
            "confidence_score": 0.32,  # Below default threshold
            "alternate_models": [
                {"model_type": "ServiceLevelAgreement", "confidence_score": 0.30}
            ]
        })
        
        # Define available models
        available_models = {
            "software_license_agreement": SoftwareLicenseAgreement,
            "employment_contract": EmploymentContract
        }
        
        # Test with default threshold
        auto_model = AutoModel.from_pdf(mock_pdf_path, available_models)
        
        # Assertions - should still select even with low confidence
        assert auto_model.selected_model_type == "SoftwareLicenseAgreement"
        assert auto_model.confidence_score == 0.32
        # Flag should indicate low confidence
        assert auto_model.below_confidence_threshold is True
