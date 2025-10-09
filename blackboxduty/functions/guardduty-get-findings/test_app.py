import pytest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime
from botocore.exceptions import ClientError, BotoCoreError
import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import lambda_handler, serialize_datetime, convert_findings_to_serializable


@pytest.fixture
def valid_event():
    """Fixture for valid event data"""
    return {
        'DetectorId': 'test-detector-123',
        'FindingRegion': 'us-east-1',
        'FindingIds': ['finding-1', 'finding-2']
    }


@pytest.fixture
def sample_finding():
    """Fixture for sample GuardDuty finding"""
    return {
        'Id': 'finding-1',
        'Arn': 'arn:aws:guardduty:us-east-1:123456789012:detector/test-detector-123/finding/finding-1',
        'Type': 'Recon:EC2/PortProbeUnprotectedPort',
        'SchemaVersion': '2.0',
        'Severity': 5.0,
        'Title': 'Port scan detected',
        'Description': 'Unprotected port being probed.',
        'CreatedAt': datetime(2023, 10, 9, 12, 0, 0),
        'UpdatedAt': datetime(2023, 10, 9, 12, 30, 0),
        'Region': 'us-east-1',
        'Confidence': 8.5
    }


@pytest.fixture
def mock_guardduty_response(sample_finding):
    """Fixture for mock GuardDuty API response"""
    return {
        'Findings': [sample_finding]
    }


class TestUtilityFunctions:
    """Test utility functions"""

    def test_serialize_datetime_success(self):
        """Test datetime serialization"""
        test_datetime = datetime(2023, 10, 9, 12, 0, 0)
        result = serialize_datetime(test_datetime)
        assert result == '2023-10-09T12:00:00'

    def test_serialize_datetime_invalid_type(self):
        """Test datetime serialization with invalid type"""
        with pytest.raises(TypeError):
            serialize_datetime("not a datetime")

    def test_convert_findings_to_serializable(self, sample_finding):
        """Test findings conversion to serializable format"""
        findings = [sample_finding]
        result = convert_findings_to_serializable(findings)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['Id'] == 'finding-1'
        # Check that datetime objects were converted to strings
        assert isinstance(result[0]['CreatedAt'], str)
        assert isinstance(result[0]['UpdatedAt'], str)


class TestLambdaHandlerSuccess:
    """Test successful lambda handler scenarios"""

    @patch('app.boto3.client')
    def test_lambda_handler_success(self, mock_boto3_client, valid_event, mock_guardduty_response):
        """Test successful lambda handler execution"""
        # Mock the GuardDuty client
        mock_client = MagicMock()
        mock_client.get_findings.return_value = mock_guardduty_response
        mock_boto3_client.return_value = mock_client
        
        # Execute the lambda handler
        result = lambda_handler(valid_event, {})
        
        # Verify the result
        assert 'Findings' in result
        assert len(result['Findings']) == 1
        assert result['Findings'][0]['Id'] == 'finding-1'
        
        # Verify boto3 client was called correctly
        mock_boto3_client.assert_called_once_with('guardduty', region_name='us-east-1')
        mock_client.get_findings.assert_called_once_with(
            DetectorId='test-detector-123',
            FindingIds=['finding-1', 'finding-2']
        )

    @patch('app.boto3.client')
    def test_lambda_handler_empty_findings_response(self, mock_boto3_client, valid_event):
        """Test lambda handler with empty findings response"""
        # Mock the GuardDuty client with empty response
        mock_client = MagicMock()
        mock_client.get_findings.return_value = {'Findings': []}
        mock_boto3_client.return_value = mock_client
        
        result = lambda_handler(valid_event, {})
        
        assert 'Findings' in result
        assert len(result['Findings']) == 0

    @patch('app.boto3.client')
    @pytest.mark.parametrize('region', ['us-west-2', 'eu-west-1', 'ap-southeast-1'])
    def test_lambda_handler_multiple_regions(self, mock_boto3_client, valid_event, mock_guardduty_response, region):
        """Test lambda handler with different regions"""
        # Mock the GuardDuty client
        mock_client = MagicMock()
        mock_client.get_findings.return_value = mock_guardduty_response
        mock_boto3_client.return_value = mock_client
        
        event = valid_event.copy()
        event['FindingRegion'] = region
        
        result = lambda_handler(event, {})
        
        # Verify the result
        assert 'Findings' in result
        
        # Verify boto3 client was called with correct region
        mock_boto3_client.assert_called_with('guardduty', region_name=region)

    @patch('app.boto3.client')
    def test_lambda_handler_large_finding_ids_list(self, mock_boto3_client, valid_event, mock_guardduty_response):
        """Test lambda handler with large list of finding IDs"""
        # Mock the GuardDuty client
        mock_client = MagicMock()
        mock_client.get_findings.return_value = mock_guardduty_response
        mock_boto3_client.return_value = mock_client
        
        # Create event with many finding IDs
        large_finding_ids = [f'finding-{i}' for i in range(50)]
        event = valid_event.copy()
        event['FindingIds'] = large_finding_ids
        
        result = lambda_handler(event, {})
        
        # Verify the result
        assert 'Findings' in result
        
        # Verify boto3 client was called with all finding IDs
        mock_client.get_findings.assert_called_once_with(
            DetectorId='test-detector-123',
            FindingIds=large_finding_ids
        )


class TestLambdaHandlerValidation:
    """Test validation error scenarios"""

    def test_lambda_handler_missing_detector_id(self):
        """Test lambda handler with missing DetectorId"""
        event = {
            'FindingRegion': 'us-east-1',
            'FindingIds': ['finding-1']
        }
        
        result = lambda_handler(event, {})
        
        assert result['statusCode'] == 400
        assert result['error'] == 'ValidationError'
        assert 'DetectorId is required' in result['message']

    def test_lambda_handler_missing_finding_region(self):
        """Test lambda handler with missing FindingRegion"""
        event = {
            'DetectorId': 'test-detector-123',
            'FindingIds': ['finding-1']
        }
        
        result = lambda_handler(event, {})
        
        assert result['statusCode'] == 400
        assert result['error'] == 'ValidationError'
        assert 'FindingRegion is required' in result['message']

    def test_lambda_handler_missing_finding_ids(self):
        """Test lambda handler with missing FindingIds"""
        event = {
            'DetectorId': 'test-detector-123',
            'FindingRegion': 'us-east-1'
        }
        
        result = lambda_handler(event, {})
        
        assert result['statusCode'] == 400
        assert result['error'] == 'ValidationError'
        assert 'FindingIds must be a non-empty list' in result['message']

    def test_lambda_handler_empty_finding_ids(self):
        """Test lambda handler with empty FindingIds list"""
        event = {
            'DetectorId': 'test-detector-123',
            'FindingRegion': 'us-east-1',
            'FindingIds': []
        }
        
        result = lambda_handler(event, {})
        
        assert result['statusCode'] == 400
        assert result['error'] == 'ValidationError'
        assert 'FindingIds must be a non-empty list' in result['message']

    def test_lambda_handler_invalid_finding_ids_type(self):
        """Test lambda handler with invalid FindingIds type"""
        event = {
            'DetectorId': 'test-detector-123',
            'FindingRegion': 'us-east-1',
            'FindingIds': 'not-a-list'
        }
        
        result = lambda_handler(event, {})
        
        assert result['statusCode'] == 400
        assert result['error'] == 'ValidationError'
        assert 'FindingIds must be a non-empty list' in result['message']


class TestLambdaHandlerErrors:
    """Test error handling scenarios"""

    @patch('app.boto3.client')
    def test_lambda_handler_client_error(self, mock_boto3_client, valid_event):
        """Test lambda handler with AWS ClientError"""
        # Mock the GuardDuty client to raise ClientError
        mock_client = MagicMock()
        error_response = {
            'Error': {
                'Code': 'DetectorNotFound',
                'Message': 'The detector does not exist'
            }
        }
        mock_client.get_findings.side_effect = ClientError(error_response, 'GetFindings')
        mock_boto3_client.return_value = mock_client
        
        result = lambda_handler(valid_event, {})
        
        assert result['statusCode'] == 500
        assert result['error'] == 'DetectorNotFound'
        assert result['message'] == 'The detector does not exist'

    @patch('app.boto3.client')
    def test_lambda_handler_botocore_error(self, mock_boto3_client, valid_event):
        """Test lambda handler with BotoCoreError"""
        # Mock the GuardDuty client to raise BotoCoreError
        mock_client = MagicMock()
        mock_client.get_findings.side_effect = BotoCoreError()
        mock_boto3_client.return_value = mock_client
        
        result = lambda_handler(valid_event, {})
        
        assert result['statusCode'] == 500
        assert result['error'] == 'BotoCoreError'

    @patch('app.boto3.client')
    def test_lambda_handler_unexpected_error(self, mock_boto3_client, valid_event):
        """Test lambda handler with unexpected error"""
        # Mock the GuardDuty client to raise unexpected error
        mock_boto3_client.side_effect = Exception("Unexpected error occurred")
        
        result = lambda_handler(valid_event, {})
        
        assert result['statusCode'] == 500
        assert result['error'] == 'UnexpectedError'
        assert result['message'] == 'Unexpected error occurred'
