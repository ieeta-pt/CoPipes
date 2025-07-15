from airflow import DAG
from datetime import datetime
import sys
import os

# Add the DAGs folder to the Python path for subfolder imports
if '/opt/airflow/dags' not in sys.path:
    sys.path.insert(0, '/opt/airflow/dags')

from components.transformation.data_aggregation import data_aggregation
from components.analysis.machine_learning.model_evaluation import model_evaluation
from components.transformation.data_cleaning import data_cleaning
from components.extraction.csv import csv
from components.analysis.machine_learning.data_preprocessing import data_preprocessing
from components.analysis.machine_learning.model_training import model_training
from components.analysis.data_visualization import data_visualization

with DAG (
    dag_id="user_8a7f57f9_99e4_4171_b992_ab6f2bd1328a_Product_demand_prediction",
    schedule=None,
    start_date=None,
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    csv_f3e = csv(filename='retail_sales_dataset.csv', file_separation=',')
    data_cleaning_eks = data_cleaning(data=csv_f3e, remove_duplicates='True', handle_missing_values='mean', outlier_detection='iqr', outlier_threshold='1.5')
    data_aggregation_mmf = data_aggregation(data=data_cleaning_eks, group_by_columns='Product_Category, Date, Age, Gender', aggregation_functions='sum(Quantity) as total_quantity, avg(Price_per_Unit) as avg_price, count(*) as transaction_count, avg(Total_Amount) as avg_total_amount', having_conditions=None)
    data_preprocessing_fmu = data_preprocessing(data=data_aggregation_mmf, target_column='total_quantity', feature_columns=None, preprocessing_config='{"handle_missing": true,"scale_features": true,"encode_categorical": true,"feature_selection": true,"create_features": true,"feature_engineering": {"polynomial_features": false,"interaction_features": true}}', save_preprocessors='True')
    model_training_uus = model_training(data=data_preprocessing_fmu, target_column='total_quantity', feature_columns=None, model_type='random_forest', task_type='regression', test_size='0.2', random_state='42', hyperparameter_tuning='True', cross_validation='True', cv_folds='5', model_name=None)
    model_evaluation_1j1 = model_evaluation(model_training_result=model_training_uus, test_data=data_preprocessing_fmu, generate_plots='True', save_predictions='True')
    data_visualization_arh = data_visualization(data=model_evaluation_1j1, chart_type='demand_ranking', x_column=None, y_column=None, color_column=None, title='Which Categories Should I Stock More?', save_format='png')
    data_visualization_fde = data_visualization(data=model_evaluation_1j1, chart_type='category_demand', x_column=None, y_column=None, color_column=None, title='Total Demand by Category', save_format='png')
    data_visualization_nq4 = data_visualization(data=model_evaluation_1j1, chart_type='monthly_heatmap', x_column=None, y_column=None, color_column=None, title='Monthly Stocking Recommendations', save_format='png')

    csv_f3e >> data_cleaning_eks
    data_cleaning_eks >> data_aggregation_mmf
    data_aggregation_mmf >> data_preprocessing_fmu
    data_preprocessing_fmu >> model_training_uus
    model_training_uus >> model_evaluation_1j1
    model_evaluation_1j1 >> data_visualization_arh
    data_visualization_arh >> data_visualization_fde
    data_visualization_fde >> data_visualization_nq4
