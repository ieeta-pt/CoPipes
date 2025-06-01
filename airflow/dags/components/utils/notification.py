import logging
from airflow.decorators import task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task
def send_notification(**context):
    """
    Send notification about pipeline completion
    """
    logger.info("Sending pipeline completion notification...")
    
    # In production, this would send emails, Slack messages, etc.
    # For demo, we'll just log the notification
    
    pipeline_status = "SUCCESS"
    
    notification_message = f"""
    Demand Forecasting Pipeline Completed Successfully!
    
    Execution Date: {context['execution_date']}
    Pipeline Status: {pipeline_status}
    
    Next scheduled run: {context['next_execution_date']}
    """
    
    logger.info(notification_message)
    
    return "Notification sent successfully"