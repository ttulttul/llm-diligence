import pytest
from unittest.mock import patch, MagicMock
import json
import os
from pathlib import Path

from analysis.analyzer import run_analysis
from models import SoftwareLicenseAgreement, EmploymentContract


@pytest.mark.integration
class TestIntegration:
    
    @patch('utils.llm.cached_llm_invoke')
    def test_end_to_end_workflow(self, mock_llm_invoke, mock_llm_response_license, 
                                  mock_document_content, tmp_path):
        """Test an end-to-end document analysis workflow with mocked LLM."""
        # Create a test document in the temp directory
        test_doc_path = tmp_path / "test_doc.pdf"
        with open(test_doc_path, "w") as f:
            f.write(mock_document_content)
        
        # Setup the mock LLM
        mock_llm_invoke.return_value = mock_llm_response_license
        
        # Run the analysis
        result = run_analysis(SoftwareLicenseAgreement, str(test_doc_path))
        
        # Check the result
        assert isinstance(result, SoftwareLicenseAgreement)
        assert result.license_type == "Perpetual"
        assert result.licensor == "TechCorp Inc."
        assert result.licensee == "Client XYZ"
        
        # Check LLM was called with correct parameters
        mock_llm_invoke.assert_called_once()
        
        # Test JSON serialization to file
        output_path = tmp_path / "result.json"
        with open(output_path, "w") as f:
            json.dump(result.model_dump(), f, cls=MagicMock(side_effect=lambda obj: obj))
            
        # Verify file was created
        assert output_path.exists()
        
        # Verify content can be deserialized
        with open(output_path, "r") as f:
            loaded_data = json.load(f)
        
        assert loaded_data["license_type"] == "Perpetual"
        assert loaded_data["licensor"] == "TechCorp Inc."
