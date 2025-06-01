import pandas as pd
import numpy as np
import os
import logging
from airflow.decorators import task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task
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