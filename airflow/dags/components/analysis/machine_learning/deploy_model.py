import joblib
import json
import os
import shutil
import logging
import sys
from typing import Dict, Any, Optional
from datetime import datetime
from airflow.decorators import task

# Add utils to path for imports
if '/opt/airflow/dags' not in sys.path:
    sys.path.insert(0, '/opt/airflow/dags')

from components.utils.supabase_storage import storage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task
def deploy_model(
    model_training_result: Dict[str, Any],
    evaluation_results: Dict[str, Any],
    model_name: Optional[str] = None,
    performance_threshold: Optional[float] = None,
    metric_name: str = "accuracy",
    backup_existing: bool = True,
    **context
) -> Dict[str, Any]:
    """
    Deploy a trained model to production environment with validation checks.
    
    Args:
        model_training_result: Result dictionary from model training task
        evaluation_results: Results from model evaluation
        model_name: Name for the deployed model (auto-generated if None)
        performance_threshold: Minimum performance threshold for deployment
        metric_name: Name of the metric to check against threshold
        backup_existing: Whether to backup existing production model
        **context: Airflow context
    
    Returns:
        Dict containing deployment results and metadata
    """
    # Extract model path from training result
    if isinstance(model_training_result, dict) and 'model_path' in model_training_result:
        model_path = model_training_result['model_path']
    else:
        raise ValueError(f"Invalid model training result format: {model_training_result}")
    
    logger.info(f"Deploying model from Supabase Storage: {model_path}")
    
    # Load model metadata from Supabase Storage
    try:
        model_objects = storage.load_joblib(model_path)
    except Exception as e:
        raise FileNotFoundError(f"Model file not found in Supabase Storage: {model_path}. Error: {e}")
    model_type = model_objects.get('model_type', 'unknown')
    task_type = model_objects.get('task_type', 'unknown')
    
    # Validate model performance
    if performance_threshold is not None:
        model_performance = evaluation_results.get('evaluation_metrics', {}).get(metric_name)
        
        if model_performance is None:
            raise ValueError(f"Metric '{metric_name}' not found in evaluation results")
        
        if model_performance < performance_threshold:
            raise ValueError(
                f"Model performance ({model_performance:.4f}) below threshold "
                f"({performance_threshold:.4f}) for {metric_name}"
            )
        
        logger.info(f"Model performance check passed: {metric_name} = {model_performance:.4f}")
    
    # Generate deployment name
    execution_date = context.get('ds', datetime.now().strftime('%Y-%m-%d'))
    if model_name is None:
        model_name = f"{model_type}_{task_type}_production"
    
    deployed_storage_path = f"production_models/{model_name}.joblib"
    
    # Backup existing model if it exists
    backup_path = None
    if backup_existing and storage.file_exists(deployed_storage_path):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_storage_path = f"production_models/backups/{model_name}_backup_{timestamp}.joblib"
        
        # Load existing model and save as backup
        try:
            existing_model = storage.load_joblib(deployed_storage_path)
            backup_path = storage.save_joblib(existing_model, backup_storage_path)
            logger.info(f"Existing model backed up to Supabase Storage: {backup_path}")
        except Exception as e:
            logger.warning(f"Failed to backup existing model: {e}")
    
    # Copy model to production location in Supabase Storage
    try:
        # Load the model and save it to production location
        deployed_model_path = storage.save_joblib(model_objects, deployed_storage_path)
        logger.info(f"Model deployed to Supabase Storage: {deployed_model_path}")
    except Exception as e:
        logger.error(f"Failed to deploy model to Supabase Storage: {e}")
        raise
    
    # Create deployment metadata
    deployment_metadata = {
        "deployment_date": execution_date,
        "deployment_timestamp": datetime.now().isoformat(),
        "model_name": model_name,
        "model_type": model_type,
        "task_type": task_type,
        "source_model_path": model_path,
        "deployed_model_path": deployed_model_path,
        "backup_path": backup_path,
        "performance_metrics": evaluation_results.get('evaluation_metrics', {}),
        "performance_threshold": performance_threshold,
        "metric_checked": metric_name,
        "deployment_status": "success"
    }
    
    # Save deployment metadata to Supabase Storage
    metadata_storage_path = f"production_models/metadata/{model_name}_metadata.json"
    try:
        metadata_path = storage.save_json(deployment_metadata, metadata_storage_path)
        logger.info(f"Deployment metadata saved to Supabase Storage: {metadata_path}")
    except Exception as e:
        logger.warning(f"Failed to save deployment metadata: {e}")
        metadata_path = None
    
    # Create model info file for easy access
    model_info = {
        "model_name": model_name,
        "model_path": deployed_model_path,
        "model_type": model_type,
        "task_type": task_type,
        "feature_columns": model_objects.get('feature_columns', []),
        "target_column": model_objects.get('target_column', ''),
        "deployment_date": execution_date,
        "last_updated": datetime.now().isoformat()
    }
    
    info_storage_path = f"production_models/info/{model_name}_info.json"
    try:
        info_path = storage.save_json(model_info, info_storage_path)
        logger.info(f"Model info saved to Supabase Storage: {info_path}")
    except Exception as e:
        logger.warning(f"Failed to save model info: {e}")
        info_path = None
    
    return {
        "status": "success",
        "model_name": model_name,
        "deployed_model_path": deployed_model_path,
        "metadata_path": metadata_path,
        "info_path": info_path,
        "backup_path": backup_path,
        "deployment_date": execution_date,
        "performance_validated": performance_threshold is not None,
        "deployment_metadata": deployment_metadata
    }