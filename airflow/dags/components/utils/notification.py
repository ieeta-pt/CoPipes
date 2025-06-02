import logging
from typing import Dict, Optional, Any
from airflow.decorators import task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task
def send_notification(
    message: Optional[str] = None,
    status: str = "SUCCESS",
    pipeline_name: Optional[str] = None,
    additional_info: Optional[Dict[str, Any]] = None,
    notification_type: str = "log",
    **context
) -> Dict[str, Any]:
    """
    Send configurable pipeline notifications.
    
    Args:
        message: Custom notification message
        status: Pipeline status (SUCCESS, FAILED, WARNING)
        pipeline_name: Name of the pipeline for context
        additional_info: Additional information to include
        notification_type: Type of notification (log, email, slack, etc.)
        **context: Airflow context
    
    Returns:
        Dict containing notification results
    """
    logger.info(f"Sending {notification_type} notification...")
    
    # Get pipeline info from context
    dag_id = context.get('dag', {}).dag_id if hasattr(context.get('dag', {}), 'dag_id') else 'unknown'
    execution_date = context.get('execution_date', 'unknown')
    next_execution_date = context.get('next_execution_date', 'unknown')
    
    # Use provided pipeline name or fall back to DAG ID
    pipeline_display_name = pipeline_name or dag_id
    
    # Build notification message
    if message:
        notification_message = message
    else:
        notification_message = f"""
    Pipeline: {pipeline_display_name}
    Status: {status}
    Execution Date: {execution_date}
    Next scheduled run: {next_execution_date}
    """
    
    # Add additional information if provided
    if additional_info:
        notification_message += "\n\nAdditional Information:\n"
        for key, value in additional_info.items():
            notification_message += f"  {key}: {value}\n"
    
    # Send notification based on type
    if notification_type == "log":
        if status == "SUCCESS":
            logger.info(notification_message)
        elif status == "FAILED":
            logger.error(notification_message)
        elif status == "WARNING":
            logger.warning(notification_message)
        else:
            logger.info(notification_message)
    
    # In production, add other notification types:
    # elif notification_type == "email":
    #     send_email_notification(notification_message)
    # elif notification_type == "slack":
    #     send_slack_notification(notification_message)
    
    logger.info(f"Notification sent successfully via {notification_type}")
    
    return {
        "status": "success",
        "notification_type": notification_type,
        "pipeline_name": pipeline_display_name,
        "pipeline_status": status,
        "execution_date": str(execution_date),
        "message_sent": notification_message.strip()
    }