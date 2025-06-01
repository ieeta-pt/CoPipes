import pandas as pd
import numpy as np
import os
import logging
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
from airflow.decorators import task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task
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