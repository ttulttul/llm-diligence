import pytest
from unittest.mock import patch, MagicMock
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from analysis.analyzer import run_analysis
from models import SoftwareLicenseAgreement, EmploymentContract


@pytest.mark.integration
class TestIntegration:
    # Helper class for tests
    class AttributeDict(dict):
        """A dictionary that allows attribute access to its keys and simulates Pydantic model methods."""
        def __init__(self, *args, **kwargs):
            super(TestIntegration.AttributeDict, self).__init__(*args, **kwargs)
            self.__dict__ = self
            
        def model_dump_json(self, **kwargs):
            """Simulate Pydantic's model_dump_json method."""
            import json
            return json.dumps(self, **kwargs)
            
        def model_dump(self, **kwargs):
            """Simulate Pydantic's model_dump method."""
            return dict(self)
    
    @patch('utils.llm.cached_llm_invoke')
    @patch('analysis.analyzer.extract_text_from_pdf')
    def test_end_to_end_workflow(self, mock_extract_text, mock_llm_invoke, 
                                 mock_llm_response_license, mock_document_content, tmp_path):
        """Test an end-to-end document analysis workflow with mocked LLM."""
        # Create a test document in the temp directory
        test_doc_path = tmp_path / "test_doc.pdf"
        with open(test_doc_path, "w") as f:
            f.write(mock_document_content)
        
        # Mock the PDF text extraction
        mock_extract_text.return_value = mock_document_content
        
        # Parse the mock response
        if isinstance(mock_llm_response_license, str):
            mock_data = json.loads(mock_llm_response_license)
        else:
            mock_data = mock_llm_response_license
        
        # Create a dict that can also have attributes set
        mock_response = self.AttributeDict(mock_data)
        
        # Setup the mock LLM
        mock_llm_invoke.return_value = mock_response
        
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
