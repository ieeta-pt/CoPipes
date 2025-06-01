import pandas as pd
import logging
from airflow.decorators import task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task
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