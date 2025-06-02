import joblib
import json
import os
import logging
from typing import Dict, Any
from datetime import datetime
from airflow.decorators import task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task
def list_deployed_models(
    deployment_directory: str = "/shared_data/production_models",
    **context
) -> Dict[str, Any]:
    """
    List all deployed models with their metadata.
    
    Args:
        deployment_directory: Directory containing production models
        **context: Airflow context
    
    Returns:
        Dict containing list of deployed models and their info
    """
    if not os.path.exists(deployment_directory):
        logger.warning(f"Deployment directory does not exist: {deployment_directory}")
        return {"status": "success", "deployed_models": [], "count": 0}
    
    deployed_models = []
    
    # Find all .joblib files (excluding backups)
    model_files = [
        f for f in os.listdir(deployment_directory) 
        if f.endswith('.joblib') and 'backup' not in f
    ]
    
    for model_file in model_files:
        model_path = os.path.join(deployment_directory, model_file)
        model_name = model_file.replace('.joblib', '')
        
        # Load model metadata
        try:
            model_objects = joblib.load(model_path)
            
            # Check for corresponding info file
            info_path = os.path.join(deployment_directory, f"{model_name}_info.json")
            if os.path.exists(info_path):
                with open(info_path, 'r') as f:
                    model_info = json.load(f)
            else:
                model_info = {}
            
            # Check for metadata file
            metadata_path = os.path.join(deployment_directory, f"{model_name}_metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    deployment_metadata = json.load(f)
            else:
                deployment_metadata = {}
            
            model_details = {
                "model_name": model_name,
                "model_path": model_path,
                "model_type": model_objects.get('model_type', 'unknown'),
                "task_type": model_objects.get('task_type', 'unknown'),
                "feature_columns": model_objects.get('feature_columns', []),
                "target_column": model_objects.get('target_column', ''),
                "file_size_mb": round(os.path.getsize(model_path) / (1024 * 1024), 2),
                "last_modified": datetime.fromtimestamp(os.path.getmtime(model_path)).isoformat(),
                "model_info": model_info,
                "deployment_metadata": deployment_metadata
            }
            
            deployed_models.append(model_details)
            
        except Exception as e:
            logger.warning(f"Could not load model metadata for {model_file}: {e}")
            continue
    
    # Sort by last modified date
    deployed_models.sort(key=lambda x: x['last_modified'], reverse=True)
    
    logger.info(f"Found {len(deployed_models)} deployed models")
    
    return {
        "status": "success",
        "deployed_models": deployed_models,
        "count": len(deployed_models),
        "deployment_directory": deployment_directory
    }