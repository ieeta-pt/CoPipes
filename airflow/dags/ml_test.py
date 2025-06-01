from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.utils.dates import days_ago
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default arguments for the DAG
default_args = {
    'owner': 'ml-team',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'catchup': False
}

# Initialize the DAG
dag = DAG(
    'demand_forecasting_pipeline',
    default_args=default_args,
    description='End-to-end ML pipeline for demand forecasting',
    schedule_interval='@daily',  # Run daily
    max_active_runs=1,
    tags=['ml', 'forecasting', 'retail']
)

def data_ingestion(**context):
    """
    Ingest data from various sources (sales, weather, marketing)
    In production, this would connect to actual databases/APIs
    """
    logger.info("Starting data ingestion...")
    
    # Simulate data ingestion from multiple sources
    # In reality, you'd connect to databases, APIs, or file systems
    
    # Generate sample sales data
    dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
    sales_data = pd.DataFrame({
        'date': dates,
        'sales': np.random.normal(1000, 200, len(dates)) + 
                np.sin(np.arange(len(dates)) * 2 * np.pi / 365) * 100,  # Seasonal pattern
        'product_id': np.random.choice(['A', 'B', 'C'], len(dates))
    })
    
    # Generate sample weather data
    weather_data = pd.DataFrame({
        'date': dates,
        'temperature': np.random.normal(20, 10, len(dates)),
        'humidity': np.random.normal(60, 15, len(dates)),
        'rainfall': np.random.exponential(2, len(dates))
    })
    
    # Generate sample marketing data
    marketing_data = pd.DataFrame({
        'date': dates,
        'marketing_spend': np.random.exponential(500, len(dates)),
        'campaign_type': np.random.choice(['online', 'tv', 'radio', 'none'], len(dates))
    })
    
    # Create data directory if it doesn't exist
    os.makedirs('/tmp/ml_pipeline_data', exist_ok=True)
    
    # Save raw data
    sales_data.to_csv('/tmp/ml_pipeline_data/sales_raw.csv', index=False)
    weather_data.to_csv('/tmp/ml_pipeline_data/weather_raw.csv', index=False)
    marketing_data.to_csv('/tmp/ml_pipeline_data/marketing_raw.csv', index=False)
    
    logger.info(f"Ingested {len(sales_data)} sales records")
    logger.info(f"Ingested {len(weather_data)} weather records")
    logger.info(f"Ingested {len(marketing_data)} marketing records")
    
    return "Data ingestion completed successfully"

def data_preprocessing(**context):
    """
    Clean, transform, and feature engineer the data
    """
    logger.info("Starting data preprocessing...")
    
    # Load raw data
    sales_df = pd.read_csv('/tmp/ml_pipeline_data/sales_raw.csv')
    weather_df = pd.read_csv('/tmp/ml_pipeline_data/weather_raw.csv')
    marketing_df = pd.read_csv('/tmp/ml_pipeline_data/marketing_raw.csv')
    
    # Convert date columns
    for df in [sales_df, weather_df, marketing_df]:
        df['date'] = pd.to_datetime(df['date'])
    
    # Merge all data on date
    merged_df = sales_df.merge(weather_df, on='date', how='left')
    merged_df = merged_df.merge(marketing_df, on='date', how='left')
    
    # Feature engineering
    merged_df['day_of_week'] = merged_df['date'].dt.dayofweek
    merged_df['month'] = merged_df['date'].dt.month
    merged_df['quarter'] = merged_df['date'].dt.quarter
    merged_df['is_weekend'] = (merged_df['day_of_week'] >= 5).astype(int)
    
    # Create lagged features
    merged_df['sales_lag_1'] = merged_df.groupby('product_id')['sales'].shift(1)
    merged_df['sales_lag_7'] = merged_df.groupby('product_id')['sales'].shift(7)
    merged_df['sales_rolling_7'] = merged_df.groupby('product_id')['sales'].rolling(7).mean().reset_index(0, drop=True)
    
    # One-hot encode categorical variables
    merged_df = pd.get_dummies(merged_df, columns=['product_id', 'campaign_type'])
    
    # Handle missing values
    merged_df = merged_df.fillna(merged_df.mean())
    
    # Remove first few rows with NaN due to lagging
    merged_df = merged_df.dropna()
    
    # Save processed data
    merged_df.to_csv('/tmp/ml_pipeline_data/processed_data.csv', index=False)
    
    logger.info(f"Processed data shape: {merged_df.shape}")
    logger.info("Data preprocessing completed successfully")
    
    return f"Processed {len(merged_df)} records"

def model_training(**context):
    """
    Train the machine learning model
    """
    logger.info("Starting model training...")
    
    # Load processed data
    df = pd.read_csv('/tmp/ml_pipeline_data/processed_data.csv')
    
    # Prepare features and target
    target_col = 'sales'
    feature_cols = [col for col in df.columns if col not in ['date', target_col]]
    
    X = df[feature_cols]
    y = df[target_col]
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=False
    )
    
    # Train model
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    # Calculate metrics
    train_mae = mean_absolute_error(y_train, y_pred_train)
    test_mae = mean_absolute_error(y_test, y_pred_test)
    train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    
    # Log metrics
    logger.info(f"Training MAE: {train_mae:.2f}")
    logger.info(f"Test MAE: {test_mae:.2f}")
    logger.info(f"Training RMSE: {train_rmse:.2f}")
    logger.info(f"Test RMSE: {test_rmse:.2f}")
    
    # Save model and metrics
    os.makedirs('/tmp/ml_pipeline_models', exist_ok=True)
    joblib.dump(model, '/tmp/ml_pipeline_models/demand_forecast_model.pkl')
    
    # Save feature names
    with open('/tmp/ml_pipeline_models/feature_names.txt', 'w') as f:
        f.write('\n'.join(feature_cols))
    
    # Save metrics
    metrics = {
        'train_mae': train_mae,
        'test_mae': test_mae,
        'train_rmse': train_rmse,
        'test_rmse': test_rmse,
        'feature_count': len(feature_cols),
        'training_samples': len(X_train),
        'test_samples': len(X_test)
    }
    
    pd.DataFrame([metrics]).to_csv('/tmp/ml_pipeline_models/model_metrics.csv', index=False)
    
    logger.info("Model training completed successfully")
    
    return f"Model trained with Test MAE: {test_mae:.2f}"

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
    import shutil
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

# Define tasks
start_task = DummyOperator(
    task_id='start_pipeline',
    dag=dag
)

data_ingestion_task = PythonOperator(
    task_id='data_ingestion',
    python_callable=data_ingestion,
    dag=dag
)

data_preprocessing_task = PythonOperator(
    task_id='data_preprocessing',
    python_callable=data_preprocessing,
    dag=dag
)

model_training_task = PythonOperator(
    task_id='model_training',
    python_callable=model_training,
    dag=dag
)

model_evaluation_task = PythonOperator(
    task_id='model_evaluation',
    python_callable=model_evaluation,
    dag=dag
)

model_deployment_task = PythonOperator(
    task_id='model_deployment',
    python_callable=model_deployment,
    dag=dag
)

notification_task = PythonOperator(
    task_id='send_notification',
    python_callable=send_notification,
    dag=dag,
    trigger_rule='all_done'  # Run regardless of upstream success/failure
)

end_task = DummyOperator(
    task_id='end_pipeline',
    dag=dag
)

# Define task dependencies
start_task >> data_ingestion_task >> data_preprocessing_task >> model_training_task
model_training_task >> model_evaluation_task >> model_deployment_task >> notification_task >> end_task