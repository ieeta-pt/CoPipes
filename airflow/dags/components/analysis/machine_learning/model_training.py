import pandas as pd
import numpy as np
import joblib
import logging
import os
import sys
from typing import Dict, List, Any, Optional
from airflow.decorators import task

# Add utils to path for imports
if '/opt/airflow/dags' not in sys.path:
    sys.path.insert(0, '/opt/airflow/dags')

from components.utils.supabase_storage import storage
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.svm import SVC, SVR
from sklearn.metrics import accuracy_score, r2_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task
def model_training(
    data: Dict[str, Any],
    target_column: str,
    feature_columns: Optional[List[str]] = None,
    model_type: str = "random_forest",
    task_type: str = "classification",
    test_size: float | str = 0.2,
    random_state: int | str = 42,
    hyperparameter_tuning: bool = False,
    cross_validation: bool = True,
    cv_folds: int | str = 5,
    model_name: Optional[str] = None,
    **context
) -> Dict[str, Any]:
    """
    Train a machine learning model with configurable options.
    
    Args:
        data: Input data dictionary with 'data' key containing records
        target_column: Name of the target variable column
        feature_columns: List of feature column names (auto-detect if None)
        model_type: Type of model ('random_forest', 'logistic_regression', 'svm', 'linear_regression')
        task_type: 'classification' or 'regression'
        test_size: Proportion of data for testing
        random_state: Random seed for reproducibility
        hyperparameter_tuning: Whether to perform hyperparameter tuning
        cross_validation: Whether to perform cross-validation
        cv_folds: Number of folds for cross-validation
        output_directory: Directory to save trained model
        model_name: Custom name for the model file
        **context: Airflow context
    
    Returns:
        Dict containing training results and model metadata
    """
    if not data or 'data' not in data:
        logger.error("No valid data received for model training.")
        raise ValueError("No valid data received for model training.")

    df = pd.DataFrame(data['data'])
    logger.info(f"Training model on {len(df)} samples with {len(df.columns)} features")

    # Validate target column
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found in data")

    # Auto-detect feature columns if not provided
    if feature_columns is None:
        feature_columns = [col for col in df.columns if col != target_column]
        logger.info(f"Auto-detected {len(feature_columns)} feature columns")
    
    # Validate feature columns
    missing_features = [col for col in feature_columns if col not in df.columns]
    if missing_features:
        raise ValueError(f"Feature columns not found in data: {missing_features}")
    
    if isinstance(test_size, str):
        test_size = float(test_size)
    if isinstance(random_state, str):
        random_state = int(random_state)
    if isinstance(cv_folds, str):
        cv_folds = int(cv_folds)

    # Prepare features and target
    X = df[feature_columns].copy()
    y = df[target_column].copy()
    
    logger.info(f"Features shape: {X.shape}, Target shape: {y.shape}")

    # Handle missing values
    # For numeric features
    numeric_features = X.select_dtypes(include=[np.number]).columns
    if len(numeric_features) > 0:
        imputer_numeric = SimpleImputer(strategy='median')
        X[numeric_features] = imputer_numeric.fit_transform(X[numeric_features])
    
    # For categorical features
    categorical_features = X.select_dtypes(include=['object']).columns
    if len(categorical_features) > 0:
        imputer_categorical = SimpleImputer(strategy='most_frequent')
        X[categorical_features] = imputer_categorical.fit_transform(X[categorical_features])
        
        # Encode categorical features
        label_encoders = {}
        for col in categorical_features:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            label_encoders[col] = le

    # Handle missing values in target
    if y.isnull().any():
        if task_type == "classification":
            y = y.fillna(y.mode()[0] if not y.mode().empty else 0)
        else:
            y = y.fillna(y.median())

    # Encode target if it's categorical for classification
    target_encoder = None
    if task_type == "classification" and y.dtype == 'object':
        target_encoder = LabelEncoder()
        y = target_encoder.fit_transform(y.astype(str))

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y if task_type == "classification" else None
    )
    
    logger.info(f"Training set: {X_train.shape}, Test set: {X_test.shape}")

    # Scale features for some models
    scaler = None
    if model_type in ['logistic_regression', 'svm']:
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
    else:
        X_train_scaled = X_train
        X_test_scaled = X_test

    # Initialize model
    model = _get_model(model_type, task_type, random_state)
    
    # Hyperparameter tuning
    if hyperparameter_tuning:
        logger.info("Performing hyperparameter tuning...")
        param_grid = _get_param_grid(model_type, task_type)
        
        scoring = 'accuracy' if task_type == "classification" else 'r2'
        grid_search = GridSearchCV(
            model, param_grid, cv=cv_folds, scoring=scoring, n_jobs=-1, verbose=1
        )
        grid_search.fit(X_train_scaled, y_train)
        model = grid_search.best_estimator_
        best_params = grid_search.best_params_
        logger.info(f"Best parameters: {best_params}")
    else:
        best_params = None

    # Train model
    logger.info(f"Training {model_type} model...")
    model.fit(X_train_scaled, y_train)

    # Cross-validation
    cv_scores = None
    if cross_validation:
        logger.info("Performing cross-validation...")
        scoring = 'accuracy' if task_type == "classification" else 'r2'
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=cv_folds, scoring=scoring)
        logger.info(f"CV Score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")

    # Evaluate on test set
    y_pred = model.predict(X_test_scaled)
    
    if task_type == "classification":
        test_score = accuracy_score(y_test, y_pred)
        metric_name = "accuracy"
    else:
        test_score = r2_score(y_test, y_pred)
        metric_name = "r2_score"
    
    logger.info(f"Test {metric_name}: {test_score:.4f}")

    # Save model and preprocessing objects to Supabase Storage
    execution_date = context.get('ds', 'unknown')
    model_filename = model_name or f"{model_type}_{task_type}_{execution_date}.joblib"
    storage_path = f"models/{model_filename}"
    
    # Save all necessary objects
    model_objects = {
        'model': model,
        'scaler': scaler,
        'label_encoders': label_encoders if categorical_features.any() else None,
        'target_encoder': target_encoder,
        'feature_columns': feature_columns,
        'target_column': target_column,
        'model_type': model_type,
        'task_type': task_type
    }
    
    try:
        model_path = storage.save_joblib(model_objects, storage_path)
        logger.info(f"Model saved to Supabase Storage: {model_path}")
    except Exception as e:
        logger.error(f"Failed to save model to Supabase Storage: {e}")
        raise

    return {
        "status": "success",
        "model_path": model_path,
        "model_type": model_type,
        "task_type": task_type,
        "feature_columns": feature_columns,
        "target_column": target_column,
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "test_score": test_score,
        "metric_name": metric_name,
        "cv_scores": cv_scores.tolist() if cv_scores is not None else None,
        "cv_mean": cv_scores.mean() if cv_scores is not None else None,
        "cv_std": cv_scores.std() if cv_scores is not None else None,
        "best_params": best_params,
        "execution_date": execution_date
    }


def _get_model(model_type: str, task_type: str, random_state: int):
    """Get model instance based on type and task"""
    if task_type == "classification":
        if model_type == "random_forest":
            return RandomForestClassifier(random_state=random_state, n_jobs=-1)
        elif model_type == "logistic_regression":
            return LogisticRegression(random_state=random_state, max_iter=1000)
        elif model_type == "svm":
            return SVC(random_state=random_state)
        else:
            raise ValueError(f"Unsupported classification model: {model_type}")
    else:  # regression
        if model_type == "random_forest":
            return RandomForestRegressor(random_state=random_state, n_jobs=-1)
        elif model_type == "linear_regression":
            return LinearRegression()
        elif model_type == "svm":
            return SVR()
        else:
            raise ValueError(f"Unsupported regression model: {model_type}")


def _get_param_grid(model_type: str, task_type: str) -> Dict:
    """Get parameter grid for hyperparameter tuning"""
    if task_type == "classification":
        if model_type == "random_forest":
            return {
                'n_estimators': [50, 100, 200],
                'max_depth': [None, 10, 20],
                'min_samples_split': [2, 5, 10]
            }
        elif model_type == "logistic_regression":
            return {
                'C': [0.1, 1.0, 10.0],
                'penalty': ['l1', 'l2'],
                'solver': ['liblinear']
            }
        elif model_type == "svm":
            return {
                'C': [0.1, 1.0, 10.0],
                'kernel': ['linear', 'rbf'],
                'gamma': ['scale', 'auto']
            }
    else:  # regression
        if model_type == "random_forest":
            return {
                'n_estimators': [50, 100, 200],
                'max_depth': [None, 10, 20],
                'min_samples_split': [2, 5, 10]
            }
        elif model_type == "svm":
            return {
                'C': [0.1, 1.0, 10.0],
                'kernel': ['linear', 'rbf'],
                'gamma': ['scale', 'auto']
            }
    
    return {}