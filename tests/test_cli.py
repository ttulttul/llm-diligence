import pytest
import sys
import os
import tempfile
import json
import csv
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from argparse import Namespace

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import diligentizer
from models.legal import SoftwareLicenseAgreement
from models.contracts import EmploymentContract
from models.auto import AutoModel


class TestDiligentizerCLI:
    """Test suite for diligentizer.py command line interface."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_pdf = os.path.join(self.temp_dir, "test.pdf")
        self.temp_csv = os.path.join(self.temp_dir, "test.csv")
        self.temp_output = os.path.join(self.temp_dir, "output.csv")
        self.temp_json_dir = os.path.join(self.temp_dir, "json_output")
        self.temp_db = os.path.join(self.temp_dir, "test.db")
        
        # Create test files
        with open(self.temp_pdf, 'w') as f:
            f.write("Mock PDF content")
        
        # Create test CSV
        with open(self.temp_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'text_content'])
            writer.writerow(['1', 'This is a software license agreement'])
            writer.writerow(['2', 'This is an employment contract'])

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('diligentizer.get_available_models')
    @patch('diligentizer.list_available_models')
    def test_list_argument(self, mock_list_models, mock_get_models):
        """Test --list argument."""
        mock_models = {
            "legal_SoftwareLicenseAgreement": SoftwareLicenseAgreement,
            "contracts_EmploymentContract": EmploymentContract
        }
        mock_get_models.return_value = mock_models
        
        with patch('sys.argv', ['diligentizer.py', '--list']):
            result = diligentizer.main()
            assert result == 0
        
        mock_list_models.assert_called_once_with(mock_models, verbose=False)

    @patch('diligentizer.get_available_models')
    @patch('diligentizer.list_available_models')
    def test_list_verbose_argument(self, mock_list_models, mock_get_models):
        """Test --list with --verbose argument."""
        mock_models = {
            "legal_SoftwareLicenseAgreement": SoftwareLicenseAgreement,
            "contracts_EmploymentContract": EmploymentContract
        }
        mock_get_models.return_value = mock_models
        
        with patch('sys.argv', ['diligentizer.py', '--list', '--verbose']):
            result = diligentizer.main()
            assert result == 0
        
        mock_list_models.assert_called_once_with(mock_models, verbose=True)

    @patch('diligentizer.get_available_models')
    @patch('diligentizer.run_analysis')
    def test_model_argument(self, mock_run_analysis, mock_get_models):
        """Test --model argument."""
        mock_models = {
            "legal_SoftwareLicenseAgreement": SoftwareLicenseAgreement,
            "contracts_EmploymentContract": EmploymentContract
        }
        mock_get_models.return_value = mock_models
        
        # Just use a MagicMock for the test result to avoid validation complexity
        mock_result = MagicMock()
        mock_run_analysis.return_value = mock_result
        
        with patch('sys.argv', ['diligentizer.py', '--model', 'legal_SoftwareLicenseAgreement', '--pdf', self.temp_pdf]):
            result = diligentizer.main()
            assert result == 0
        
        mock_run_analysis.assert_called_once()

    @patch('diligentizer.get_available_models')
    @patch('diligentizer.run_analysis')
    def test_auto_argument(self, mock_run_analysis, mock_get_models):
        """Test --auto argument."""
        mock_models = {
            "auto_AutoModel": AutoModel,
            "legal_SoftwareLicenseAgreement": SoftwareLicenseAgreement
        }
        mock_get_models.return_value = mock_models
        mock_run_analysis.return_value = MagicMock()
        
        with patch('sys.argv', ['diligentizer.py', '--auto', '--pdf', self.temp_pdf]):
            result = diligentizer.main()
            assert result == 0

    @patch('diligentizer.get_available_models')
    @patch('diligentizer.run_analysis')
    def test_classify_only_argument(self, mock_run_analysis, mock_get_models):
        """Test --classify-only argument."""
        mock_models = {
            "auto_AutoModel": AutoModel,
            "legal_SoftwareLicenseAgreement": SoftwareLicenseAgreement
        }
        mock_get_models.return_value = mock_models
        
        mock_result = MagicMock()
        mock_result.model_name = "SoftwareLicenseAgreement"
        mock_run_analysis.return_value = mock_result
        
        with patch('sys.argv', ['diligentizer.py', '--auto', '--classify-only', '--pdf', self.temp_pdf]):
            result = diligentizer.main()
            assert result == 0

    @patch('diligentizer.get_available_models')
    @patch('diligentizer.run_analysis')
    def test_classify_to_csv_argument(self, mock_run_analysis, mock_get_models):
        """Test --classify-to-csv argument."""
        mock_models = {
            "auto_AutoModel": AutoModel,
            "legal_SoftwareLicenseAgreement": SoftwareLicenseAgreement
        }
        mock_get_models.return_value = mock_models
        
        csv_output = os.path.join(self.temp_dir, "classification.csv")
        
        mock_result = MagicMock()
        mock_result.model_name = "SoftwareLicenseAgreement"
        mock_result.selection_path = ["Agreement", "SoftwareLicenseAgreement"]
        mock_run_analysis.return_value = mock_result
        
        with patch('sys.argv', ['diligentizer.py', '--auto', '--classify-only', '--classify-to-csv', csv_output, '--pdf', self.temp_pdf]):
            result = diligentizer.main()
            assert result == 0
            
            # Check that CSV file was created
            assert os.path.exists(csv_output)

    @patch('diligentizer.get_available_models')
    @patch('diligentizer.process_directory')
    def test_crawl_dir_argument(self, mock_process_dir, mock_get_models):
        """Test --crawl-dir argument."""
        mock_models = {
            "legal_SoftwareLicenseAgreement": SoftwareLicenseAgreement
        }
        mock_get_models.return_value = mock_models
        mock_process_dir.return_value = iter([(True, self.temp_pdf, MagicMock(), None)])
        
        with patch('sys.argv', ['diligentizer.py', '--model', 'legal_SoftwareLicenseAgreement', '--crawl-dir', self.temp_dir]):
            result = diligentizer.main()
            assert result == 0
        
        mock_process_dir.assert_called_once()

    @patch('diligentizer.get_available_models')
    @patch('diligentizer.process_directory')
    def test_crawl_limit_argument(self, mock_process_dir, mock_get_models):
        """Test --crawl-limit argument."""
        mock_models = {
            "legal_SoftwareLicenseAgreement": SoftwareLicenseAgreement
        }
        mock_get_models.return_value = mock_models
        mock_process_dir.return_value = iter([(True, self.temp_pdf, MagicMock(), None)])
        
        with patch('sys.argv', ['diligentizer.py', '--model', 'legal_SoftwareLicenseAgreement', '--crawl-dir', self.temp_dir, '--crawl-limit', '5']):
            result = diligentizer.main()
            assert result == 0
        
        # Check that crawl_limit was passed to process_directory
        args, kwargs = mock_process_dir.call_args
        assert kwargs['crawl_limit'] == 5

    @patch('diligentizer.get_available_models')
    @patch('diligentizer.process_directory')
    def test_parallel_argument(self, mock_process_dir, mock_get_models):
        """Test --parallel argument."""
        mock_models = {
            "legal_SoftwareLicenseAgreement": SoftwareLicenseAgreement
        }
        mock_get_models.return_value = mock_models
        mock_process_dir.return_value = iter([(True, self.temp_pdf, MagicMock(), None)])
        
        with patch('sys.argv', ['diligentizer.py', '--model', 'legal_SoftwareLicenseAgreement', '--crawl-dir', self.temp_dir, '--parallel', '4']):
            result = diligentizer.main()
            assert result == 0
        
        # Check that parallel was passed to process_directory as 6th positional argument
        args, kwargs = mock_process_dir.call_args
        assert args[5] == 4  # parallel is the 6th argument (0-indexed)

    @patch('diligentizer.get_available_models')
    @patch('diligentizer.run_analysis')
    @patch('diligentizer.save_to_db')
    def test_sqlite_argument(self, mock_save_db, mock_run_analysis, mock_get_models):
        """Test --sqlite argument."""
        mock_models = {
            "legal_SoftwareLicenseAgreement": SoftwareLicenseAgreement
        }
        mock_get_models.return_value = mock_models
        
        mock_result = MagicMock()
        mock_run_analysis.return_value = mock_result
        
        with patch('sys.argv', ['diligentizer.py', '--model', 'legal_SoftwareLicenseAgreement', '--pdf', self.temp_pdf, '--sqlite', self.temp_db]):
            result = diligentizer.main()
            assert result == 0
        
        mock_save_db.assert_called_once_with(self.temp_db, mock_result)

    @patch('diligentizer.get_available_models')
    @patch('diligentizer.run_analysis')
    def test_json_output_argument(self, mock_run_analysis, mock_get_models):
        """Test --json-output argument."""
        mock_models = {
            "legal_SoftwareLicenseAgreement": SoftwareLicenseAgreement
        }
        mock_get_models.return_value = mock_models
        
        mock_result = MagicMock()
        mock_result.model_dump.return_value = {"test": "data"}
        mock_run_analysis.return_value = mock_result
        
        os.makedirs(self.temp_json_dir, exist_ok=True)
        
        with patch('sys.argv', ['diligentizer.py', '--model', 'legal_SoftwareLicenseAgreement', '--pdf', self.temp_pdf, '--json-output', self.temp_json_dir]):
            with patch('builtins.open', mock_open()) as mock_file:
                result = diligentizer.main()
                assert result == 0
                
                # Check that file was opened for writing
                mock_file.assert_called()

    @patch('diligentizer.get_available_models')
    @patch('diligentizer.process_csv_file')
    @patch('diligentizer.run_analysis')  # Mock to prevent PDF processing
    def test_csv_input_arguments(self, mock_run_analysis, mock_process_csv, mock_get_models):
        """Test CSV input related arguments."""
        mock_models = {
            "legal_SoftwareLicenseAgreement": SoftwareLicenseAgreement
        }
        mock_get_models.return_value = mock_models
        mock_process_csv.return_value = True
        mock_run_analysis.return_value = MagicMock()  # Mock PDF processing
        
        with patch('sys.argv', [
            'diligentizer.py', 
            '--model', 'legal_SoftwareLicenseAgreement',
            '--csv-input', self.temp_csv,
            '--csv-input-column', 'text_content',
            '--csv-output', self.temp_output,
            '--csv-output-column-prefix', 'analysis_',
            '--pdf', self.temp_pdf  # Include PDF to satisfy validation
        ]):
            result = diligentizer.main()
            assert result == 0
        
        mock_process_csv.assert_called_once()

    @patch('diligentizer.get_available_models')
    @patch('diligentizer.configure_logger')
    @patch('diligentizer.run_analysis')
    def test_log_level_argument(self, mock_run_analysis, mock_configure_logger, mock_get_models):
        """Test --log-level argument."""
        mock_models = {
            "legal_SoftwareLicenseAgreement": SoftwareLicenseAgreement
        }
        mock_get_models.return_value = mock_models
        mock_run_analysis.return_value = MagicMock()
        
        with patch('sys.argv', ['diligentizer.py', '--model', 'legal_SoftwareLicenseAgreement', '--pdf', self.temp_pdf, '--log-level', 'DEBUG']):
            result = diligentizer.main()
            assert result == 0
        
        mock_configure_logger.assert_called_with('DEBUG', None)

    @patch('diligentizer.get_available_models')
    @patch('diligentizer.configure_logger')
    @patch('diligentizer.run_analysis')
    def test_verbose_argument(self, mock_run_analysis, mock_configure_logger, mock_get_models):
        """Test --verbose argument."""
        mock_models = {
            "legal_SoftwareLicenseAgreement": SoftwareLicenseAgreement
        }
        mock_get_models.return_value = mock_models
        mock_run_analysis.return_value = MagicMock()
        
        with patch('sys.argv', ['diligentizer.py', '--model', 'legal_SoftwareLicenseAgreement', '--pdf', self.temp_pdf, '--verbose']):
            result = diligentizer.main()
            assert result == 0
        
        # Verbose should override log level to INFO
        mock_configure_logger.assert_called_with('INFO', None)

    @patch('diligentizer.get_available_models')
    @patch('diligentizer.run_analysis')
    def test_prompt_extra_argument(self, mock_run_analysis, mock_get_models):
        """Test --prompt-extra argument."""
        mock_models = {
            "legal_SoftwareLicenseAgreement": SoftwareLicenseAgreement
        }
        mock_get_models.return_value = mock_models
        mock_run_analysis.return_value = MagicMock()
        
        with patch('sys.argv', ['diligentizer.py', '--model', 'legal_SoftwareLicenseAgreement', '--pdf', self.temp_pdf, '--prompt-extra', 'Additional context']):
            result = diligentizer.main()
            assert result == 0
        
        # Check that prompt_extra was passed to run_analysis
        args, kwargs = mock_run_analysis.call_args
        assert kwargs['prompt_extra'] == 'Additional context'

    @patch('diligentizer.get_available_models')
    @patch('diligentizer.run_analysis')
    def test_provider_argument(self, mock_run_analysis, mock_get_models):
        """Test --provider argument."""
        mock_models = {
            "legal_SoftwareLicenseAgreement": SoftwareLicenseAgreement
        }
        mock_get_models.return_value = mock_models
        mock_run_analysis.return_value = MagicMock()
        
        with patch('sys.argv', ['diligentizer.py', '--model', 'legal_SoftwareLicenseAgreement', '--pdf', self.temp_pdf, '--provider', 'openai']):
            result = diligentizer.main()
            assert result == 0
        
        # Check that provider was passed to run_analysis
        args, kwargs = mock_run_analysis.call_args
        assert kwargs['provider'] == 'openai'

    @patch('diligentizer.get_available_models')
    @patch('diligentizer.run_analysis')
    def test_provider_model_argument(self, mock_run_analysis, mock_get_models):
        """Test --provider-model argument."""
        mock_models = {
            "legal_SoftwareLicenseAgreement": SoftwareLicenseAgreement
        }
        mock_get_models.return_value = mock_models
        mock_run_analysis.return_value = MagicMock()
        
        with patch('sys.argv', ['diligentizer.py', '--model', 'legal_SoftwareLicenseAgreement', '--pdf', self.temp_pdf, '--provider-model', 'gpt-4']):
            result = diligentizer.main()
            assert result == 0
        
        # Check that provider_model was passed to run_analysis
        args, kwargs = mock_run_analysis.call_args
        assert kwargs['provider_model'] == 'gpt-4'

    @patch('diligentizer.get_available_models')
    @patch('diligentizer.run_analysis')
    def test_chunk_size_argument(self, mock_run_analysis, mock_get_models):
        """Test --chunk-size argument."""
        mock_models = {
            "legal_SoftwareLicenseAgreement": SoftwareLicenseAgreement
        }
        mock_get_models.return_value = mock_models
        mock_run_analysis.return_value = MagicMock()
        
        with patch('sys.argv', ['diligentizer.py', '--model', 'legal_SoftwareLicenseAgreement', '--pdf', self.temp_pdf, '--chunk-size', '4']):
            result = diligentizer.main()
            assert result == 0
        
        # Check that chunk_size was passed to run_analysis
        args, kwargs = mock_run_analysis.call_args
        assert kwargs['chunk_size'] == 4

    @patch('diligentizer.get_available_models')
    def test_error_conditions(self, mock_get_models):
        """Test various error conditions."""
        mock_models = {
            "legal_SoftwareLicenseAgreement": SoftwareLicenseAgreement
        }
        mock_get_models.return_value = mock_models
        
        # Test missing model
        with patch('sys.argv', ['diligentizer.py']):
            result = diligentizer.main()
            assert result == 1
        
        # Test invalid model
        with patch('sys.argv', ['diligentizer.py', '--model', 'invalid_model', '--pdf', self.temp_pdf]):
            result = diligentizer.main()
            assert result == 1
        
        # Test missing PDF file
        with patch('sys.argv', ['diligentizer.py', '--model', 'legal_SoftwareLicenseAgreement', '--pdf', '/nonexistent/file.pdf']):
            result = diligentizer.main()
            assert result == 1
        
        # Test --classify-to-csv without --classify-only
        with patch('sys.argv', ['diligentizer.py', '--model', 'legal_SoftwareLicenseAgreement', '--pdf', self.temp_pdf, '--classify-to-csv', '/tmp/output.csv']):
            result = diligentizer.main()
            assert result == 1

    @patch('diligentizer.get_available_models')
    def test_no_models_available(self, mock_get_models):
        """Test behavior when no models are available."""
        mock_get_models.return_value = {}
        
        with patch('sys.argv', ['diligentizer.py', '--list']):
            result = diligentizer.main()
            assert result == 1

    @patch('diligentizer.get_available_models')
    def test_auto_model_not_found(self, mock_get_models):
        """Test --auto when AutoModel is not available."""
        mock_models = {
            "legal_SoftwareLicenseAgreement": SoftwareLicenseAgreement
        }
        mock_get_models.return_value = mock_models
        
        with patch('sys.argv', ['diligentizer.py', '--auto', '--pdf', self.temp_pdf]):
            result = diligentizer.main()
            assert result == 1

    def test_keyboard_interrupt(self):
        """Test handling of keyboard interrupt."""
        with patch('diligentizer.get_available_models') as mock_get_models:
            mock_get_models.side_effect = KeyboardInterrupt()
            
            with patch('sys.argv', ['diligentizer.py', '--list']):
                result = diligentizer.main()
                assert result == 130

    @patch('diligentizer.get_available_models')
    @patch('diligentizer.process_csv_file')
    def test_csv_processing_failure(self, mock_process_csv, mock_get_models):
        """Test CSV processing failure handling."""
        mock_models = {
            "legal_SoftwareLicenseAgreement": SoftwareLicenseAgreement
        }
        mock_get_models.return_value = mock_models
        mock_process_csv.return_value = False  # Simulate failure
        
        with patch('sys.argv', [
            'diligentizer.py', 
            '--model', 'legal_SoftwareLicenseAgreement',
            '--csv-input', self.temp_csv,
            '--csv-input-column', 'text_content',
            '--csv-output', self.temp_output
        ]):
            result = diligentizer.main()
            assert result == 1

    @patch('diligentizer.get_available_models')
    @patch('diligentizer.run_analysis')
    def test_provider_max_tokens_argument(self, mock_run_analysis, mock_get_models):
        """Test --provider-max-tokens argument."""
        mock_models = {
            "legal_SoftwareLicenseAgreement": SoftwareLicenseAgreement
        }
        mock_get_models.return_value = mock_models
        mock_run_analysis.return_value = MagicMock()
        
        with patch('sys.argv', ['diligentizer.py', '--model', 'legal_SoftwareLicenseAgreement', '--pdf', self.temp_pdf, '--provider-max-tokens', '4096']):
            result = diligentizer.main()
            assert result == 0
        
        # Check that provider_max_tokens was passed to run_analysis
        args, kwargs = mock_run_analysis.call_args
        assert kwargs['provider_max_tokens'] == 4096

    @patch.dict(os.environ, {}, clear=True)
    @patch('diligentizer.get_available_models')
    @patch('diligentizer.run_analysis')
    def test_provider_reasoning_effort_argument(self, mock_run_analysis, mock_get_models):
        """Test --provider-reasoning-effort argument."""
        mock_models = {
            "legal_SoftwareLicenseAgreement": SoftwareLicenseAgreement
        }
        mock_get_models.return_value = mock_models
        mock_run_analysis.return_value = MagicMock()
        
        with patch('sys.argv', ['diligentizer.py', '--model', 'legal_SoftwareLicenseAgreement', '--pdf', self.temp_pdf, '--provider-reasoning-effort', 'high']):
            result = diligentizer.main()
            assert result == 0
        
        # Check that environment variable was set
        assert os.environ.get("LLM_REASONING_EFFORT") == "high"

    @patch.dict(os.environ, {}, clear=True)
    @patch('diligentizer.get_available_models')
    @patch('diligentizer.run_analysis')
    def test_provider_small_model_argument(self, mock_run_analysis, mock_get_models):
        """Test --provider-small-model argument."""
        mock_models = {
            "legal_SoftwareLicenseAgreement": SoftwareLicenseAgreement
        }
        mock_get_models.return_value = mock_models
        mock_run_analysis.return_value = MagicMock()
        
        with patch('sys.argv', ['diligentizer.py', '--model', 'legal_SoftwareLicenseAgreement', '--pdf', self.temp_pdf, '--provider-small-model', 'gpt-3.5-turbo']):
            result = diligentizer.main()
            assert result == 0
        
        # Check that environment variable was set
        assert os.environ.get("LLM_SMALL_MODEL_NAME") == "gpt-3.5-turbo"