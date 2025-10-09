import logging
import boto3
import json
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """Function to list GuardDuty detectors with multi-region support.

    Parameters
    ----------
    event : dict
        Event payload containing:
        - FindingRegion: AWS region to list detectors from

    Returns
    ------
        dict: Object containing the GuardDuty detector IDs
    """
    logger.info("Received event: %s", event)
    
    try:
        region = event.get('FindingRegion')
        
        logger.info(f"Listing detectors in region: {region or 'current region'}")
        
        if region:
            guardduty_client = boto3.client('guardduty', region_name=region)
        else:
            guardduty_client = boto3.client('guardduty')
        
        response = guardduty_client.list_detectors()
        
        detector_ids = response.get('DetectorIds', [])
        logger.info(f"Successfully retrieved {len(detector_ids)} detectors")
        
        # Return detector IDs in the same format as GuardDuty API response
        return {
            'DetectorIds': detector_ids
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
