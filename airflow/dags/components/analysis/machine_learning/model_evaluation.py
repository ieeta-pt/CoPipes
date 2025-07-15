import pandas as pd
import numpy as np
import joblib
import logging
import os
import json
import sys
from typing import Dict, Any
from airflow.decorators import task

# Add utils to path for imports
if '/opt/airflow/dags' not in sys.path:
    sys.path.insert(0, '/opt/airflow/dags')

from components.utils.supabase_storage import storage
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, classification_report, mean_squared_error, 
    mean_absolute_error, r2_score, explained_variance_score
)
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task
def model_evaluation(
    model_training_result: Dict[str, Any],
    test_data: Dict[str, Any],
    generate_plots: bool = True,
    save_predictions: bool = True,
    **context
) -> Dict[str, Any]:
    """
    Evaluate a trained machine learning model with comprehensive metrics.
    
    Args:
        model_training_result: Result dictionary from model training task
        test_data: Test data dictionary with 'data' key containing records
        generate_plots: Whether to generate evaluation plots
        save_predictions: Whether to save predictions to file
        **context: Airflow context
    
    Returns:
        Dict containing comprehensive evaluation metrics and results
    """
    if not test_data or 'data' not in test_data:
        logger.error("No valid test data received for model evaluation.")
        raise ValueError("No valid test data received for model evaluation.")

    # Extract model path from training result
    if isinstance(model_training_result, dict) and 'model_path' in model_training_result:
        model_path = model_training_result['model_path']
    else:
        raise ValueError(f"Invalid model training result format: {model_training_result}")

    # Load model and preprocessing objects from Supabase Storage
    logger.info(f"Loading model from Supabase Storage: {model_path}")
    try:
        model_objects = storage.load_joblib(model_path)
    except Exception as e:
        raise FileNotFoundError(f"Model file not found in Supabase Storage: {model_path}. Error: {e}")
    
    model = model_objects['model']
    scaler = model_objects.get('scaler')
    label_encoders = model_objects.get('label_encoders', {})
    target_encoder = model_objects.get('target_encoder')
    feature_columns = model_objects['feature_columns']
    target_column = model_objects['target_column']
    model_type = model_objects['model_type']
    task_type = model_objects['task_type']
    
    logger.info(f"Evaluating {model_type} model for {task_type} task")

    # Prepare test data
    df_test = pd.DataFrame(test_data['data'])
    logger.info(f"Evaluating on {len(df_test)} test samples")

    # Validate columns
    if target_column not in df_test.columns:
        raise ValueError(f"Target column '{target_column}' not found in test data")
    
    missing_features = [col for col in feature_columns if col not in df_test.columns]
    if missing_features:
        raise ValueError(f"Feature columns not found in test data: {missing_features}")

    # Prepare features and target
    X_test = df_test[feature_columns].copy()
    y_test = df_test[target_column].copy()

    # Apply preprocessing
    # Handle categorical features
    if label_encoders:
        for col, encoder in label_encoders.items():
            if col in X_test.columns:
                # Handle unseen categories
                X_test[col] = X_test[col].astype(str)
                known_classes = set(encoder.classes_)
                X_test[col] = X_test[col].apply(
                    lambda x: x if x in known_classes else encoder.classes_[0]
                )
                X_test[col] = encoder.transform(X_test[col])

    # Apply scaling
    if scaler is not None:
        X_test_scaled = scaler.transform(X_test)
    else:
        X_test_scaled = X_test

    # Handle target encoding
    if target_encoder is not None:
        y_test_encoded = target_encoder.transform(y_test.astype(str))
    else:
        y_test_encoded = y_test

    # Make predictions
    logger.info("Making predictions...")
    y_pred = model.predict(X_test_scaled)
    
    # Get prediction probabilities for classification
    y_pred_proba = None
    if task_type == "classification" and hasattr(model, 'predict_proba'):
        y_pred_proba = model.predict_proba(X_test_scaled)

    # Calculate metrics
    evaluation_results = {}
    
    if task_type == "classification":
        evaluation_results = _calculate_classification_metrics(
            y_test_encoded, y_pred, y_pred_proba, target_encoder
        )
    else:
        evaluation_results = _calculate_regression_metrics(y_test_encoded, y_pred)

    # Save evaluation results to Supabase Storage
    execution_date = context.get('ds', 'unknown')
    
    # Save evaluation report
    report_storage_path = f"evaluations/evaluation_report_{execution_date}.json"
    try:
        report_path = storage.save_json(evaluation_results, report_storage_path)
        logger.info(f"Evaluation report saved to Supabase Storage: {report_path}")
    except Exception as e:
        logger.warning(f"Failed to save evaluation report: {e}")
        report_path = None

    # Save predictions
    predictions_path = None
    if save_predictions:
        predictions_df = df_test.copy()
        predictions_df['predictions'] = y_pred
        
        if y_pred_proba is not None:
            # Add probability columns for each class
            classes = model.classes_ if hasattr(model, 'classes_') else range(y_pred_proba.shape[1])
            for i, cls in enumerate(classes):
                predictions_df[f'prob_class_{cls}'] = y_pred_proba[:, i]
        
        # Convert DataFrame to JSON for storage
        predictions_data = predictions_df.to_dict(orient='records')
        predictions_storage_path = f"predictions/predictions_{execution_date}.json"
        try:
            predictions_path = storage.save_json({"predictions": predictions_data}, predictions_storage_path)
            logger.info(f"Predictions saved to Supabase Storage: {predictions_path}")
        except Exception as e:
            logger.warning(f"Failed to save predictions: {e}")
            predictions_path = None

    # Generate plots (skip for now due to complexity of storing images in Supabase)
    plot_paths = []
    if generate_plots:
        logger.info("Plot generation temporarily disabled for Supabase Storage integration")
        # plot_paths = _generate_evaluation_plots(
        #     y_test_encoded, y_pred, y_pred_proba, task_type, 
        #     execution_date, target_encoder
        # )

    # Prepare prediction data for visualization
    prediction_data = []
    if save_predictions:
        predictions_df = df_test.copy()
        predictions_df['predictions'] = y_pred
        predictions_df['actual_demand'] = y_test_encoded
        predictions_df['predicted_demand'] = y_pred
        
        # Add probability columns for classification if available
        if y_pred_proba is not None:
            classes = model.classes_ if hasattr(model, 'classes_') else range(y_pred_proba.shape[1])
            for i, cls in enumerate(classes):
                predictions_df[f'prob_class_{cls}'] = y_pred_proba[:, i]
        
        prediction_data = predictions_df.to_dict(orient='records')

    return {
        "status": "success",
        "model_path": model_path,
        "model_type": model_type,
        "task_type": task_type,
        "test_samples": len(df_test),
        "evaluation_metrics": evaluation_results,
        "report_path": report_path,
        "predictions_path": predictions_path if save_predictions else None,
        "plot_paths": plot_paths,
        "execution_date": execution_date,
        "data": prediction_data  # Add prediction data for visualization
    }


def _calculate_classification_metrics(y_true, y_pred, y_pred_proba, target_encoder):
    """Calculate comprehensive classification metrics"""
    metrics = {}
    
    # Basic metrics
    metrics['accuracy'] = float(accuracy_score(y_true, y_pred))
    
    # Handle multiclass vs binary
    average_method = 'weighted' if len(np.unique(y_true)) > 2 else 'binary'
    
    metrics['precision'] = float(precision_score(y_true, y_pred, average=average_method, zero_division=0))
    metrics['recall'] = float(recall_score(y_true, y_pred, average=average_method, zero_division=0))
    metrics['f1_score'] = float(f1_score(y_true, y_pred, average=average_method, zero_division=0))
    
    # ROC AUC (if probabilities available)
    if y_pred_proba is not None:
        try:
            if len(np.unique(y_true)) == 2:
                # Binary classification
                metrics['roc_auc'] = float(roc_auc_score(y_true, y_pred_proba[:, 1]))
            else:
                # Multiclass
                metrics['roc_auc'] = float(roc_auc_score(y_true, y_pred_proba, multi_class='ovr'))
        except Exception as e:
            logger.warning(f"Could not calculate ROC AUC: {e}")
            metrics['roc_auc'] = None
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    metrics['confusion_matrix'] = cm.tolist()
    
    # Classification report
    if target_encoder:
        target_names = target_encoder.classes_
    else:
        target_names = None
    
    report = classification_report(y_true, y_pred, target_names=target_names, output_dict=True, zero_division=0)
    metrics['classification_report'] = report
    
    # Class-wise metrics
    unique_classes = np.unique(y_true)
    metrics['class_metrics'] = {}
    for cls in unique_classes:
        cls_name = target_encoder.inverse_transform([cls])[0] if target_encoder else str(cls)
        metrics['class_metrics'][cls_name] = {
            'precision': float(precision_score(y_true == cls, y_pred == cls, zero_division=0)),
            'recall': float(recall_score(y_true == cls, y_pred == cls, zero_division=0)),
            'f1_score': float(f1_score(y_true == cls, y_pred == cls, zero_division=0))
        }
    
    return metrics


def _calculate_regression_metrics(y_true, y_pred):
    """Calculate comprehensive regression metrics"""
    metrics = {}
    
    # Basic metrics
    metrics['mean_squared_error'] = float(mean_squared_error(y_true, y_pred))
    metrics['root_mean_squared_error'] = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    metrics['mean_absolute_error'] = float(mean_absolute_error(y_true, y_pred))
    metrics['r2_score'] = float(r2_score(y_true, y_pred))
    metrics['explained_variance_score'] = float(explained_variance_score(y_true, y_pred))
    
    # Additional metrics
    residuals = y_true - y_pred
    metrics['mean_residual'] = float(np.mean(residuals))
    metrics['std_residual'] = float(np.std(residuals))
    
    # Percentage errors
    percentage_errors = np.abs((y_true - y_pred) / y_true) * 100
    percentage_errors = percentage_errors[np.isfinite(percentage_errors)]  # Remove inf/nan
    if len(percentage_errors) > 0:
        metrics['mean_absolute_percentage_error'] = float(np.mean(percentage_errors))
        metrics['median_absolute_percentage_error'] = float(np.median(percentage_errors))
    
    return metrics


def _generate_evaluation_plots(y_true, y_pred, y_pred_proba, task_type, output_dir, execution_date, target_encoder):
    """Generate evaluation plots"""
    plot_paths = []
    
    try:
        if task_type == "classification":
            # Confusion Matrix
            plt.figure(figsize=(8, 6))
            cm = confusion_matrix(y_true, y_pred)
            
            if target_encoder:
                labels = target_encoder.classes_
            else:
                labels = np.unique(y_true)
            
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                       xticklabels=labels, yticklabels=labels)
            plt.title('Confusion Matrix')
            plt.ylabel('True Label')
            plt.xlabel('Predicted Label')
            
            cm_path = os.path.join(output_dir, f"confusion_matrix_{execution_date}.png")
            plt.savefig(cm_path, dpi=300, bbox_inches='tight')
            plt.close()
            plot_paths.append(cm_path)
            
            # ROC Curve (for binary classification with probabilities)
            if y_pred_proba is not None and len(np.unique(y_true)) == 2:
                from sklearn.metrics import roc_curve
                fpr, tpr, _ = roc_curve(y_true, y_pred_proba[:, 1])
                
                plt.figure(figsize=(8, 6))
                plt.plot(fpr, tpr, linewidth=2)
                plt.plot([0, 1], [0, 1], 'k--')
                plt.xlim([0.0, 1.0])
                plt.ylim([0.0, 1.05])
                plt.xlabel('False Positive Rate')
                plt.ylabel('True Positive Rate')
                plt.title('ROC Curve')
                plt.grid(True)
                
                roc_path = os.path.join(output_dir, f"roc_curve_{execution_date}.png")
                plt.savefig(roc_path, dpi=300, bbox_inches='tight')
                plt.close()
                plot_paths.append(roc_path)
        
        else:  # regression
            # Actual vs Predicted
            plt.figure(figsize=(10, 8))
            
            plt.subplot(2, 2, 1)
            plt.scatter(y_true, y_pred, alpha=0.6)
            plt.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2)
            plt.xlabel('Actual')
            plt.ylabel('Predicted')
            plt.title('Actual vs Predicted')
            
            # Residuals plot
            plt.subplot(2, 2, 2)
            residuals = y_true - y_pred
            plt.scatter(y_pred, residuals, alpha=0.6)
            plt.axhline(y=0, color='r', linestyle='--')
            plt.xlabel('Predicted')
            plt.ylabel('Residuals')
            plt.title('Residuals Plot')
            
            # Residuals histogram
            plt.subplot(2, 2, 3)
            plt.hist(residuals, bins=30, alpha=0.7)
            plt.xlabel('Residuals')
            plt.ylabel('Frequency')
            plt.title('Residuals Distribution')
            
            # Q-Q plot
            plt.subplot(2, 2, 4)
            from scipy import stats
            stats.probplot(residuals, dist="norm", plot=plt)
            plt.title('Q-Q Plot')
            
            plt.tight_layout()
            
            regression_path = os.path.join(output_dir, f"regression_analysis_{execution_date}.png")
            plt.savefig(regression_path, dpi=300, bbox_inches='tight')
            plt.close()
            plot_paths.append(regression_path)
    
    except Exception as e:
        logger.warning(f"Error generating plots: {e}")
    
    return plot_paths