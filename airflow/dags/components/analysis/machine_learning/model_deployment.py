import pandas as pd
import os
import shutil
import logging
from datetime import datetime
from airflow.decorators import task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task
def model_deployment(**context):
    """
    Deploy the model if it passed evaluation
    """
    logger.info("Starting model deployment...")
    
    # Check evaluation result
    with open('/tmp/ml_pipeline_models/evaluation_result.txt', 'r') as f:
        evaluation_result = f.read().strip()
    
    if evaluation_result != "PASS":
        logger.error("Model did not pass evaluation. Skipping deployment.")
        raise ValueError("Model failed evaluation criteria")
    
    # In production, this would:
    # 1. Copy model to production storage (S3, GCS, etc.)
    # 2. Update model registry
    # 3. Deploy to serving infrastructure (SageMaker, Kubernetes, etc.)
    # 4. Update API endpoints
    
    # For demo, we'll simulate deployment
    deployment_path = '/tmp/ml_pipeline_production/'
    os.makedirs(deployment_path, exist_ok=True)
    
    # Copy model to "production" location
    shutil.copy('/tmp/ml_pipeline_models/demand_forecast_model.pkl', 
                f'{deployment_path}/current_model.pkl')
    shutil.copy('/tmp/ml_pipeline_models/feature_names.txt', 
                f'{deployment_path}/feature_names.txt')
    
    # Create deployment metadata
    deployment_info = {
        'deployment_date': datetime.now().isoformat(),
        'model_version': f"v_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        'status': 'deployed'
    }
    
    pd.DataFrame([deployment_info]).to_csv(f'{deployment_path}/deployment_info.csv', index=False)
    
    logger.info("Model deployed successfully to production")
    
    return "Model deployment completed successfully"