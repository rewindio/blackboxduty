import logging
import boto3
import json
from datetime import datetime
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def serialize_datetime(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def convert_findings_to_serializable(findings):
    """Convert GuardDuty findings to JSON serializable format"""
    return json.loads(json.dumps(findings, default=serialize_datetime))

def lambda_handler(event, context):
    """Function to get GuardDuty findings with multi-region support.

    Parameters
    ----------
    event : dict
        Event payload containing:
        - DetectorId: GuardDuty detector ID
        - FindingRegion: AWS region where the finding is located
        - FindingIds: List of finding IDs to retrieve

    Returns
    ------
        dict: Object containing the GuardDuty findings
    """
    logger.info("Received event: %s", event)
    
    try:
        detector_id = event.get('DetectorId')
        finding_region = event.get('FindingRegion')
        finding_ids = event.get('FindingIds')
        
        if not detector_id:
            raise ValueError("DetectorId is required")
        if not finding_region:
            raise ValueError("FindingRegion is required")
        if not finding_ids or not isinstance(finding_ids, list):
            raise ValueError("FindingIds must be a non-empty list")
        
        logger.info(f"Getting findings for detector {detector_id} in region {finding_region}")
        logger.info(f"Finding IDs: {finding_ids}")
        
        guardduty_client = boto3.client('guardduty', region_name=finding_region)
        
        response = guardduty_client.get_findings(
            DetectorId=detector_id,
            FindingIds=finding_ids
        )
        
        logger.info(f"Successfully retrieved {len(response.get('Findings', []))} findings")
        
        findings = response.get('Findings', [])
        serializable_findings = convert_findings_to_serializable(findings)
        
        # Return findings in the same format as GuardDuty API response
        return {
            'Findings': serializable_findings
        }
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return {
            'statusCode': 400,
            'error': 'ValidationError',
            'message': str(e)
        }
    
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"AWS ClientError: {error_code} - {error_message}")
        return {
            'statusCode': 500,
            'error': error_code,
            'message': error_message
        }
    
    except BotoCoreError as e:
        logger.error(f"BotoCore error: {str(e)}")
        return {
            'statusCode': 500,
            'error': 'BotoCoreError',
            'message': str(e)
        }
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'error': 'UnexpectedError',
            'message': str(e)
        }
