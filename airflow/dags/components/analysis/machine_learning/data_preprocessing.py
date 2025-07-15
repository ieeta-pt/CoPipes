import json
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Union
from airflow.decorators import task
from sklearn.preprocessing import (
    StandardScaler, MinMaxScaler, RobustScaler, LabelEncoder, 
    OneHotEncoder, OrdinalEncoder
)
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.feature_selection import (
    SelectKBest, SelectFromModel, VarianceThreshold, f_classif, f_regression
)
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import joblib
import os
import sys

# Add utils to path for imports
if '/opt/airflow/dags' not in sys.path:
    sys.path.insert(0, '/opt/airflow/dags')

from components.utils.supabase_storage import storage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task
def data_preprocessing(
    data: Dict[str, Any],
    target_column: Optional[str] = None,
    feature_columns: Optional[List[str]] = None,
    preprocessing_config: Optional[Dict[str, Any]] | str= None,
    save_preprocessors: bool = True,
    **context
) -> Dict[str, Any]:
    """
    Comprehensive data preprocessing for machine learning pipelines.
    
    Args:
        data: Input data dictionary with 'data' key containing records
        target_column: Name of the target variable column
        feature_columns: List of feature column names (auto-detect if None)
        preprocessing_config: Configuration for preprocessing steps
        output_directory: Directory to save preprocessing objects
        save_preprocessors: Whether to save preprocessing objects for later use
        **context: Airflow context
    
    Returns:
        Dict containing preprocessed data and preprocessing metadata
    """
    if not data or 'data' not in data:
        logger.error("No valid data received for preprocessing.")
        raise ValueError("No valid data received for preprocessing.")

    df = pd.DataFrame(data['data'])
    logger.info(f"Preprocessing {len(df)} samples with {len(df.columns)} features")

    # Default preprocessing configuration
    if isinstance(preprocessing_config, str):
        try:
            preprocessing_config = json.loads(preprocessing_config)
        except json.JSONDecodeError:
            logger.error("Invalid JSON string for preprocessing configuration.")
            raise ValueError("Invalid JSON string for preprocessing configuration.")
        
    if preprocessing_config is None:
        preprocessing_config = {
            "handle_missing": True,
            "scale_features": True,
            "encode_categorical": True,
            "feature_selection": False,
            "remove_outliers": False,
            "create_features": False
        }

    # Auto-detect feature and target columns
    if target_column and target_column in df.columns:
        if feature_columns is None:
            feature_columns = [col for col in df.columns if col != target_column]
    else:
        if feature_columns is None:
            feature_columns = list(df.columns)
    
    logger.info(f"Processing {len(feature_columns)} feature columns")
    
    # Separate features and target
    X = df[feature_columns].copy()
    y = df[target_column].copy() if target_column and target_column in df.columns else None
    
    # Identify column types
    numeric_columns = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_columns = X.select_dtypes(include=['object', 'category']).columns.tolist()
    boolean_columns = X.select_dtypes(include=['bool']).columns.tolist()
    
    logger.info(f"Identified {len(numeric_columns)} numeric, {len(categorical_columns)} categorical, "
                f"and {len(boolean_columns)} boolean columns")
    
    # Store preprocessing objects
    preprocessors = {}
    
    # 1. Handle Missing Values
    if preprocessing_config.get("handle_missing", True):
        X, missing_preprocessors = _handle_missing_values(
            X, numeric_columns, categorical_columns, preprocessing_config
        )
        preprocessors.update(missing_preprocessors)
    
    # 2. Encode Categorical Variables
    if preprocessing_config.get("encode_categorical", True):
        X, encoding_preprocessors = _encode_categorical_features(
            X, categorical_columns, preprocessing_config
        )
        preprocessors.update(encoding_preprocessors)
        # Update numeric columns after encoding
        numeric_columns = X.select_dtypes(include=[np.number]).columns.tolist()
    
    # 3. Handle Boolean Columns
    if boolean_columns:
        X[boolean_columns] = X[boolean_columns].astype(int)
        logger.info(f"Converted {len(boolean_columns)} boolean columns to integer")
    
    # 4. Scale Features
    if preprocessing_config.get("scale_features", True):
        X, scaling_preprocessors = _scale_features(
            X, numeric_columns, preprocessing_config
        )
        preprocessors.update(scaling_preprocessors)
    
    # 5. Feature Selection
    if preprocessing_config.get("feature_selection", False) and y is not None:
        X, selection_preprocessors = _select_features(
            X, y, preprocessing_config
        )
        preprocessors.update(selection_preprocessors)
    
    # 6. Remove Outliers
    if preprocessing_config.get("remove_outliers", False):
        X, clean_indices = _remove_outliers(X, preprocessing_config)
        if y is not None:
            y = y[clean_indices]
        logger.info(f"Outlier removal: {len(X)} samples remaining")
    
    # 7. Feature Engineering
    if preprocessing_config.get("create_features", False):
        X = _create_features(X, preprocessing_config)
    
    # Save preprocessors to Supabase Storage
    preprocessor_path = None
    if save_preprocessors:
        execution_date = context.get('ds', 'unknown')
        storage_path = f"preprocessors/preprocessors_{execution_date}.joblib"
        
        preprocessor_metadata = {
            'preprocessors': preprocessors,
            'feature_columns': feature_columns,
            'target_column': target_column,
            'numeric_columns': numeric_columns,
            'categorical_columns': categorical_columns,
            'boolean_columns': boolean_columns,
            'final_feature_names': list(X.columns),
            'preprocessing_config': preprocessing_config
        }
        
        try:
            preprocessor_path = storage.save_joblib(preprocessor_metadata, storage_path)
            logger.info(f"Preprocessors saved to Supabase Storage: {preprocessor_path}")
        except Exception as e:
            logger.warning(f"Failed to save preprocessors to Supabase Storage: {e}")
            preprocessor_path = None
    
    # Prepare output
    result_data = X.copy()
    if y is not None:
        result_data[target_column] = y
    
    return {
        "data": result_data.to_dict(orient='records'),
        "filename": data.get('filename', 'preprocessed_data'),
        "original_columns": feature_columns,
        "final_columns": list(X.columns),
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "boolean_columns": boolean_columns,
        "target_column": target_column,
        "original_samples": len(df),
        "final_samples": len(X),
        "preprocessing_config": preprocessing_config,
        "preprocessor_path": preprocessor_path if save_preprocessors else None
    }


def _handle_missing_values(X, numeric_columns, categorical_columns, config):
    """Handle missing values in the dataset"""
    preprocessors = {}
    
    missing_strategy = config.get("missing_strategy", "auto")
    
    # Handle numeric columns
    if numeric_columns:
        if missing_strategy == "auto":
            # Use median for numeric columns
            imputer_numeric = SimpleImputer(strategy='median')
        elif missing_strategy == "knn":
            imputer_numeric = KNNImputer(n_neighbors=5)
        else:
            imputer_numeric = SimpleImputer(strategy=missing_strategy)
        
        X[numeric_columns] = imputer_numeric.fit_transform(X[numeric_columns])
        preprocessors['imputer_numeric'] = imputer_numeric
        logger.info(f"Imputed missing values in {len(numeric_columns)} numeric columns")
    
    # Handle categorical columns
    if categorical_columns:
        imputer_categorical = SimpleImputer(strategy='most_frequent')
        X[categorical_columns] = imputer_categorical.fit_transform(X[categorical_columns])
        preprocessors['imputer_categorical'] = imputer_categorical
        logger.info(f"Imputed missing values in {len(categorical_columns)} categorical columns")
    
    return X, preprocessors


def _encode_categorical_features(X, categorical_columns, config):
    """Encode categorical features"""
    preprocessors = {}
    
    if not categorical_columns:
        return X, preprocessors
    
    encoding_method = config.get("categorical_encoding", "auto")
    
    for col in categorical_columns:
        unique_values = X[col].nunique()
        
        if encoding_method == "auto":
            # Use one-hot for low cardinality, label encoding for high cardinality
            if unique_values <= 10:
                method = "onehot"
            else:
                method = "label"
        else:
            method = encoding_method
        
        if method == "onehot":
            encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
            encoded_cols = encoder.fit_transform(X[[col]])
            
            # Create column names
            feature_names = [f"{col}_{cat}" for cat in encoder.categories_[0]]
            encoded_df = pd.DataFrame(encoded_cols, columns=feature_names, index=X.index)
            
            # Replace original column
            X = X.drop(columns=[col])
            X = pd.concat([X, encoded_df], axis=1)
            
            preprocessors[f'encoder_{col}'] = encoder
            logger.info(f"One-hot encoded {col} into {len(feature_names)} columns")
            
        elif method == "label":
            encoder = LabelEncoder()
            X[col] = encoder.fit_transform(X[col].astype(str))
            preprocessors[f'encoder_{col}'] = encoder
            logger.info(f"Label encoded {col} with {unique_values} unique values")
            
        elif method == "ordinal":
            encoder = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
            X[col] = encoder.fit_transform(X[[col]]).ravel()
            preprocessors[f'encoder_{col}'] = encoder
            logger.info(f"Ordinal encoded {col}")
    
    return X, preprocessors


def _scale_features(X, numeric_columns, config):
    """Scale numeric features"""
    preprocessors = {}
    
    if not numeric_columns:
        return X, preprocessors
    
    scaling_method = config.get("scaling_method", "standard")
    
    if scaling_method == "standard":
        scaler = StandardScaler()
    elif scaling_method == "minmax":
        scaler = MinMaxScaler()
    elif scaling_method == "robust":
        scaler = RobustScaler()
    else:
        logger.warning(f"Unknown scaling method: {scaling_method}, using standard")
        scaler = StandardScaler()
    
    X[numeric_columns] = scaler.fit_transform(X[numeric_columns])
    preprocessors['scaler'] = scaler
    
    logger.info(f"Applied {scaling_method} scaling to {len(numeric_columns)} numeric columns")
    
    return X, preprocessors


def _select_features(X, y, config):
    """Perform feature selection"""
    preprocessors = {}
    
    selection_method = config.get("feature_selection_method", "variance")
    n_features = config.get("n_features_to_select", "auto")
    
    if selection_method == "variance":
        # Remove low variance features
        threshold = config.get("variance_threshold", 0.01)
        selector = VarianceThreshold(threshold=threshold)
        X_selected = selector.fit_transform(X)
        
        # Get selected feature names
        selected_features = X.columns[selector.get_support()]
        X = pd.DataFrame(X_selected, columns=selected_features, index=X.index)
        
        preprocessors['feature_selector'] = selector
        logger.info(f"Variance threshold selection: {len(selected_features)} features selected")
        
    elif selection_method == "univariate":
        # Determine if classification or regression
        if y.dtype == 'object' or len(y.unique()) < 20:
            score_func = f_classif
        else:
            score_func = f_regression
        
        if n_features == "auto":
            n_features = min(50, X.shape[1] // 2)
        
        selector = SelectKBest(score_func=score_func, k=n_features)
        X_selected = selector.fit_transform(X, y)
        
        selected_features = X.columns[selector.get_support()]
        X = pd.DataFrame(X_selected, columns=selected_features, index=X.index)
        
        preprocessors['feature_selector'] = selector
        logger.info(f"Univariate selection: {len(selected_features)} features selected")
        
    elif selection_method == "model_based":
        # Use tree-based feature importance
        if y.dtype == 'object' or len(y.unique()) < 20:
            estimator = RandomForestClassifier(n_estimators=50, random_state=42)
        else:
            estimator = RandomForestRegressor(n_estimators=50, random_state=42)
        
        selector = SelectFromModel(estimator)
        X_selected = selector.fit_transform(X, y)
        
        selected_features = X.columns[selector.get_support()]
        X = pd.DataFrame(X_selected, columns=selected_features, index=X.index)
        
        preprocessors['feature_selector'] = selector
        logger.info(f"Model-based selection: {len(selected_features)} features selected")
    
    return X, preprocessors


def _remove_outliers(X, config):
    """Remove outliers using specified method"""
    outlier_method = config.get("outlier_method", "iqr")
    
    if outlier_method == "iqr":
        # Interquartile Range method
        Q1 = X.quantile(0.25)
        Q3 = X.quantile(0.75)
        IQR = Q3 - Q1
        
        # Define outlier bounds
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # Identify outliers
        outlier_mask = ((X < lower_bound) | (X > upper_bound)).any(axis=1)
        clean_indices = ~outlier_mask
        
        X_clean = X[clean_indices]
        logger.info(f"IQR outlier removal: removed {outlier_mask.sum()} outliers")
        
    elif outlier_method == "zscore":
        # Z-score method
        z_threshold = config.get("zscore_threshold", 3)
        z_scores = np.abs((X - X.mean()) / X.std())
        outlier_mask = (z_scores > z_threshold).any(axis=1)
        clean_indices = ~outlier_mask
        
        X_clean = X[clean_indices]
        logger.info(f"Z-score outlier removal: removed {outlier_mask.sum()} outliers")
    
    else:
        logger.warning(f"Unknown outlier method: {outlier_method}")
        X_clean = X
        clean_indices = X.index
    
    return X_clean, clean_indices


def _create_features(X, config):
    """Create new features through feature engineering"""
    feature_engineering = config.get("feature_engineering", {})
    
    # Polynomial features
    if feature_engineering.get("polynomial_features", False):
        from sklearn.preprocessing import PolynomialFeatures
        
        degree = feature_engineering.get("polynomial_degree", 2)
        numeric_cols = X.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) > 0 and len(numeric_cols) <= 10:  # Avoid explosion
            poly = PolynomialFeatures(degree=degree, interaction_only=True, include_bias=False)
            poly_features = poly.fit_transform(X[numeric_cols])
            
            # Create feature names
            poly_names = [f"poly_{i}" for i in range(poly_features.shape[1])]
            poly_df = pd.DataFrame(poly_features, columns=poly_names, index=X.index)
            
            # Remove original columns and add polynomial features
            X = X.drop(columns=numeric_cols)
            X = pd.concat([X, poly_df], axis=1)
            
            logger.info(f"Created {poly_features.shape[1]} polynomial features")
    
    # Interaction features
    if feature_engineering.get("interaction_features", False):
        numeric_cols = X.select_dtypes(include=[np.number]).columns[:5]  # Limit to avoid explosion
        
        for i, col1 in enumerate(numeric_cols):
            for col2 in numeric_cols[i+1:]:
                X[f"{col1}_x_{col2}"] = X[col1] * X[col2]
        
        logger.info(f"Created interaction features for {len(numeric_cols)} numeric columns")
    
    return X