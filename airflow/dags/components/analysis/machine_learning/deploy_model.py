import joblib
import json
import os
import shutil
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from airflow.decorators import task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task
def deploy_model(
    model_path: str,
    evaluation_results: Dict[str, Any],
    deployment_directory: str = "/shared_data/production_models",
    model_name: Optional[str] = None,
    performance_threshold: Optional[float] = None,
    metric_name: str = "accuracy",
    backup_existing: bool = True,
    **context
) -> Dict[str, Any]:
    """
    Deploy a trained model to production environment with validation checks.
    
    Args:
        model_path: Path to the trained model file
        evaluation_results: Results from model evaluation
        deployment_directory: Directory for production models
        model_name: Name for the deployed model (auto-generated if None)
        performance_threshold: Minimum performance threshold for deployment
        metric_name: Name of the metric to check against threshold
        backup_existing: Whether to backup existing production model
        **context: Airflow context
    
    Returns:
        Dict containing deployment results and metadata
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    logger.info(f"Deploying model from: {model_path}")
    
    # Load model metadata
    model_objects = joblib.load(model_path)
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
    
    # Create deployment directory
    os.makedirs(deployment_directory, exist_ok=True)
    
    # Generate deployment name
    execution_date = context.get('ds', datetime.now().strftime('%Y-%m-%d'))
    if model_name is None:
        model_name = f"{model_type}_{task_type}_production"
    
    deployed_model_path = os.path.join(deployment_directory, f"{model_name}.joblib")
    
    # Backup existing model if it exists
    backup_path = None
    if backup_existing and os.path.exists(deployed_model_path):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(deployment_directory, f"{model_name}_backup_{timestamp}.joblib")
        shutil.copy2(deployed_model_path, backup_path)
        logger.info(f"Existing model backed up to: {backup_path}")
    
    # Copy model to production location
    shutil.copy2(model_path, deployed_model_path)
    logger.info(f"Model deployed to: {deployed_model_path}")
    
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
    
    # Save deployment metadata
    metadata_path = os.path.join(deployment_directory, f"{model_name}_metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(deployment_metadata, f, indent=2, default=str)
    
    logger.info(f"Deployment metadata saved to: {metadata_path}")
    
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
    
    info_path = os.path.join(deployment_directory, f"{model_name}_info.json")
    with open(info_path, 'w') as f:
        json.dump(model_info, f, indent=2)
    
    logger.info(f"Model info saved to: {info_path}")
    
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