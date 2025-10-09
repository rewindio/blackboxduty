import pytest
from unittest.mock import patch, MagicMock
import json
from botocore.exceptions import ClientError, BotoCoreError
import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import lambda_handler


class TestGuardDutyListDetectors:
    """Test class for GuardDuty List Detectors Lambda function."""

    @patch('app.boto3.client')
    def test_lambda_handler_success_with_region(self, mock_boto3_client):
        """Test successful execution with specific region."""
        # Arrange
        mock_guardduty_client = MagicMock()
        mock_boto3_client.return_value = mock_guardduty_client
        mock_guardduty_client.list_detectors.return_value = {
            'DetectorIds': ['detector-id-1', 'detector-id-2', 'detector-id-3']
        }
        
        event = {
            'FindingRegion': 'us-west-2'
        }
        context = {}
        
        # Act
        result = lambda_handler(event, context)
        
        # Assert
        assert result == {
            'DetectorIds': ['detector-id-1', 'detector-id-2', 'detector-id-3']
        }
        mock_boto3_client.assert_called_once_with('guardduty', region_name='us-west-2')
        mock_guardduty_client.list_detectors.assert_called_once()

    @patch('app.boto3.client')
    def test_lambda_handler_success_without_region(self, mock_boto3_client):
        """Test successful execution without specific region (uses default)."""
        # Arrange
        mock_guardduty_client = MagicMock()
        mock_boto3_client.return_value = mock_guardduty_client
        mock_guardduty_client.list_detectors.return_value = {
            'DetectorIds': ['detector-id-1']
        }
        
        event = {}
        context = {}
        
        # Act
        result = lambda_handler(event, context)
        
        # Assert
        assert result == {
            'DetectorIds': ['detector-id-1']
        }
        mock_boto3_client.assert_called_once_with('guardduty')
        mock_guardduty_client.list_detectors.assert_called_once()

    @patch('app.boto3.client')
    def test_lambda_handler_success_empty_detectors(self, mock_boto3_client):
        """Test successful execution with no detectors."""
        # Arrange
        mock_guardduty_client = MagicMock()
        mock_boto3_client.return_value = mock_guardduty_client
        mock_guardduty_client.list_detectors.return_value = {
            'DetectorIds': []
        }
        
        event = {'FindingRegion': 'eu-west-1'}
        context = {}
        
        # Act
        result = lambda_handler(event, context)
        
        # Assert
        assert result == {
            'DetectorIds': []
        }
        mock_boto3_client.assert_called_once_with('guardduty', region_name='eu-west-1')
        mock_guardduty_client.list_detectors.assert_called_once()

    @patch('app.boto3.client')
    def test_lambda_handler_client_error(self, mock_boto3_client):
        """Test handling of AWS ClientError."""
        # Arrange
        mock_guardduty_client = MagicMock()
        mock_boto3_client.return_value = mock_guardduty_client
        
        error_response = {
            'Error': {
                'Code': 'AccessDeniedException',
                'Message': 'User is not authorized to perform: guardduty:ListDetectors'
            }
        }
        mock_guardduty_client.list_detectors.side_effect = ClientError(
            error_response, 'ListDetectors'
        )
        
        event = {'FindingRegion': 'us-east-1'}
        context = {}
        
        # Act
        result = lambda_handler(event, context)
        
        # Assert
        expected_result = {
            'statusCode': 500,
            'error': 'AccessDeniedException',
            'message': 'User is not authorized to perform: guardduty:ListDetectors'
        }
        assert result == expected_result
        mock_boto3_client.assert_called_once_with('guardduty', region_name='us-east-1')
        mock_guardduty_client.list_detectors.assert_called_once()

    @patch('app.boto3.client')
    def test_lambda_handler_botocore_error(self, mock_boto3_client):
        """Test handling of BotoCoreError."""
        # Arrange
        mock_guardduty_client = MagicMock()
        mock_boto3_client.return_value = mock_guardduty_client
        
        mock_guardduty_client.list_detectors.side_effect = BotoCoreError()
        
        event = {}
        context = {}
        
        # Act
        result = lambda_handler(event, context)
        
        # Assert
        assert result['statusCode'] == 500
        assert result['error'] == 'BotoCoreError'
        assert 'message' in result
        mock_boto3_client.assert_called_once_with('guardduty')
        mock_guardduty_client.list_detectors.assert_called_once()

    @patch('app.boto3.client')
    def test_lambda_handler_unexpected_error(self, mock_boto3_client):
        """Test handling of unexpected exceptions."""
        # Arrange
        mock_boto3_client.side_effect = Exception("Unexpected error occurred")
        
        event = {'FindingRegion': 'ap-southeast-1'}
        context = {}
        
        # Act
        result = lambda_handler(event, context)
        
        # Assert
        expected_result = {
            'statusCode': 500,
            'error': 'UnexpectedError',
            'message': 'Unexpected error occurred'
        }
        assert result == expected_result
        mock_boto3_client.assert_called_once_with('guardduty', region_name='ap-southeast-1')

    @patch('app.boto3.client')
    def test_lambda_handler_missing_detector_ids_key(self, mock_boto3_client):
        """Test handling when DetectorIds key is missing from response."""
        # Arrange
        mock_guardduty_client = MagicMock()
        mock_boto3_client.return_value = mock_guardduty_client
        mock_guardduty_client.list_detectors.return_value = {}  # Missing DetectorIds key
        
        event = {}
        context = {}
        
        # Act
        result = lambda_handler(event, context)
        
        # Assert
        assert result == {
            'DetectorIds': []
        }
        mock_boto3_client.assert_called_once_with('guardduty')
        mock_guardduty_client.list_detectors.assert_called_once()

    @patch('app.boto3.client')
    def test_lambda_handler_with_none_region(self, mock_boto3_client):
        """Test execution with explicit None region."""
        # Arrange
        mock_guardduty_client = MagicMock()
        mock_boto3_client.return_value = mock_guardduty_client
        mock_guardduty_client.list_detectors.return_value = {
            'DetectorIds': ['detector-test']
        }
        
        event = {'FindingRegion': None}
        context = {}
        
        # Act
        result = lambda_handler(event, context)
        
        # Assert
        assert result == {
            'DetectorIds': ['detector-test']
        }
        # When region is None, it should call without region_name parameter
        mock_boto3_client.assert_called_once_with('guardduty')
        mock_guardduty_client.list_detectors.assert_called_once()

    @patch('app.boto3.client')
    def test_lambda_handler_with_empty_string_region(self, mock_boto3_client):
        """Test execution with empty string region."""
        # Arrange
        mock_guardduty_client = MagicMock()
        mock_boto3_client.return_value = mock_guardduty_client
        mock_guardduty_client.list_detectors.return_value = {
            'DetectorIds': ['detector-empty-region']
        }
        
        event = {'FindingRegion': ''}
        context = {}
        
        # Act
        result = lambda_handler(event, context)
        
        # Assert
        assert result == {
            'DetectorIds': ['detector-empty-region']
        }
        # When region is empty string, it should call without region_name parameter
        mock_boto3_client.assert_called_once_with('guardduty')
        mock_guardduty_client.list_detectors.assert_called_once()


