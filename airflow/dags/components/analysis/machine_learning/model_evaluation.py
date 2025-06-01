import pandas as pd
import logging
from airflow.decorators import task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task
def model_evaluation(**context):
    """
    Evaluate model performance and decide if it should be deployed
    """
    logger.info("Starting model evaluation...")
    
    # Load metrics
    metrics_df = pd.read_csv('/tmp/ml_pipeline_models/model_metrics.csv')
    test_mae = metrics_df['test_mae'].iloc[0]
    
    # Define acceptance criteria
    MAE_THRESHOLD = 150  # Acceptable MAE threshold
    
    if test_mae <= MAE_THRESHOLD:
        logger.info(f"Model passed evaluation. MAE {test_mae:.2f} <= {MAE_THRESHOLD}")
        evaluation_result = "PASS"
    else:
        logger.warning(f"Model failed evaluation. MAE {test_mae:.2f} > {MAE_THRESHOLD}")
        evaluation_result = "FAIL"
    
    # Save evaluation result
    with open('/tmp/ml_pipeline_models/evaluation_result.txt', 'w') as f:
        f.write(evaluation_result)
    
    logger.info("Model evaluation completed")
    
    return f"Model evaluation: {evaluation_result} (MAE: {test_mae:.2f})"