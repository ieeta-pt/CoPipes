import json
import os
import shutil
import logging
from typing import Dict, Any
from datetime import datetime
from airflow.decorators import task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task
def rollback_model(
    model_name: str,
    deployment_directory: str = "/shared_data/production_models",
    **context
) -> Dict[str, Any]:
    """
    Rollback to the previous version of a deployed model.
    
    Args:
        model_name: Name of the model to rollback
        deployment_directory: Directory containing production models
        **context: Airflow context
    
    Returns:
        Dict containing rollback results
    """
    logger.info(f"Rolling back model: {model_name}")
    
    current_model_path = os.path.join(deployment_directory, f"{model_name}.joblib")
    
    if not os.path.exists(current_model_path):
        raise FileNotFoundError(f"Current model not found: {current_model_path}")
    
    # Find most recent backup
    backup_files = [
        f for f in os.listdir(deployment_directory) 
        if f.startswith(f"{model_name}_backup_") and f.endswith('.joblib')
    ]
    
    if not backup_files:
        raise FileNotFoundError(f"No backup found for model: {model_name}")
    
    # Sort by timestamp (most recent first)
    backup_files.sort(reverse=True)
    latest_backup = backup_files[0]
    backup_path = os.path.join(deployment_directory, latest_backup)
    
    # Create new backup of current model
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    current_backup_path = os.path.join(
        deployment_directory, f"{model_name}_rollback_backup_{timestamp}.joblib"
    )
    shutil.copy2(current_model_path, current_backup_path)
    
    # Restore from backup
    shutil.copy2(backup_path, current_model_path)
    
    logger.info(f"Model rolled back from backup: {latest_backup}")
    logger.info(f"Previous version backed up to: {current_backup_path}")
    
    # Update metadata
    rollback_metadata = {
        "rollback_date": context.get('ds', datetime.now().strftime('%Y-%m-%d')),
        "rollback_timestamp": datetime.now().isoformat(),
        "model_name": model_name,
        "restored_from_backup": backup_path,
        "previous_version_backup": current_backup_path,
        "rollback_status": "success"
    }
    
    metadata_path = os.path.join(deployment_directory, f"{model_name}_rollback_metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(rollback_metadata, f, indent=2, default=str)
    
    return {
        "status": "success",
        "model_name": model_name,
        "restored_from": backup_path,
        "previous_backup": current_backup_path,
        "rollback_metadata": rollback_metadata
    }