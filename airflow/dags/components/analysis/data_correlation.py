import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, Optional
from airflow.decorators import task

UPLOAD_DIR = "/shared_data/"

@task
def data_correlation(data: Dict[str, Any], method: str = "pearson",
                    target_columns: Optional[str] = None, threshold: float = 0.5,
                    generate_heatmap: bool = True) -> Dict[str, Any]:
    """
    Calculate correlation matrix and identify relationships between variables.
    
    Args:
        data: Input data from extraction or transformation task
        method: Correlation method (pearson, kendall, spearman)
        target_columns: Columns to include (separated by commas, leave empty for all numeric)
        threshold: Correlation threshold for highlighting
        generate_heatmap: Generate correlation heatmap
    
    Returns:
        Dictionary containing correlation results and metadata
    """
    try:
        # Extract data
        input_data = data.get('data', [])
        if not input_data:
            raise ValueError("No data provided for correlation analysis")
        
        # Convert to DataFrame
        df = pd.DataFrame(input_data)
        
        print(f"Starting correlation analysis. Data shape: {df.shape}")
        print(f"Method: {method}, Threshold: {threshold}")
        
        # Parse target columns
        if target_columns and target_columns.strip():
            target_cols = [col.strip() for col in target_columns.split(',')]
            # Filter to existing columns
            target_cols = [col for col in target_cols if col in df.columns]
            if target_cols:
                df_analysis = df[target_cols]
            else:
                print("Warning: None of the specified columns exist, using all numeric columns")
                df_analysis = df.select_dtypes(include=[np.number])
        else:
            # Use all numeric columns
            df_analysis = df.select_dtypes(include=[np.number])
        
        if len(df_analysis.columns) < 2:
            raise ValueError("Need at least 2 numeric columns for correlation analysis")
        
        print(f"Analyzing correlations for {len(df_analysis.columns)} columns: {df_analysis.columns.tolist()}")
        
        # Calculate correlation matrix
        correlation_methods = {
            'pearson': 'pearson',
            'spearman': 'spearman',
            'kendall': 'kendall'
        }
        
        corr_method = correlation_methods.get(method.lower(), 'pearson')
        correlation_matrix = df_analysis.corr(method=corr_method)
        
        # Handle NaN values in correlation matrix
        correlation_matrix = correlation_matrix.fillna(0)
        
        # Find high correlations
        high_correlations = []
        strong_correlations = []
        
        for i, col1 in enumerate(correlation_matrix.columns):
            for j, col2 in enumerate(correlation_matrix.columns):
                if i < j:  # Avoid duplicates and self-correlation
                    corr_value = correlation_matrix.loc[col1, col2]
                    
                    correlation_entry = {
                        'variable_1': col1,
                        'variable_2': col2,
                        'correlation': corr_value,
                        'absolute_correlation': abs(corr_value),
                        'strength': _get_correlation_strength(abs(corr_value)),
                        'direction': 'positive' if corr_value > 0 else 'negative'
                    }
                    
                    if abs(corr_value) >= threshold:
                        high_correlations.append(correlation_entry)
                    
                    if abs(corr_value) >= 0.7:  # Strong correlations
                        strong_correlations.append(correlation_entry)
        
        # Sort correlations by absolute value
        high_correlations.sort(key=lambda x: x['absolute_correlation'], reverse=True)
        strong_correlations.sort(key=lambda x: x['absolute_correlation'], reverse=True)
        
        # Generate summary statistics
        correlation_stats = {
            'total_pairs': len(correlation_matrix.columns) * (len(correlation_matrix.columns) - 1) // 2,
            'high_correlations_count': len(high_correlations),
            'strong_correlations_count': len(strong_correlations),
            'method': corr_method,
            'threshold': threshold,
            'max_correlation': correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].max(),
            'min_correlation': correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].min(),
            'mean_correlation': np.mean(np.abs(correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)]))
        }
        
        # Generate heatmap if requested
        plot_files = []
        if generate_heatmap:
            plot_files = _generate_correlation_heatmap(correlation_matrix, method, data.get('filename', 'data'))
        
        # Prepare results data
        results_data = []
        
        # Add correlation matrix as flattened data
        for col1 in correlation_matrix.columns:
            for col2 in correlation_matrix.columns:
                results_data.append({
                    'variable_1': col1,
                    'variable_2': col2,
                    'correlation': correlation_matrix.loc[col1, col2],
                    'is_self_correlation': col1 == col2,
                    'above_threshold': abs(correlation_matrix.loc[col1, col2]) >= threshold
                })
        
        print(f"Correlation analysis completed. Found {len(high_correlations)} high correlations (>={threshold})")
        
        return {
            "data": results_data,
            "filename": f"correlation_{data.get('filename', 'data')}.csv",
            "correlation_matrix": correlation_matrix.to_dict(),
            "high_correlations": high_correlations,
            "strong_correlations": strong_correlations,
            "correlation_stats": correlation_stats,
            "plot_files": plot_files,
            "columns_analyzed": len(df_analysis.columns)
        }
        
    except Exception as e:
        raise ValueError(f"Correlation analysis failed: {e}")

def _get_correlation_strength(abs_correlation: float) -> str:
    """Classify correlation strength"""
    if abs_correlation >= 0.9:
        return "very_strong"
    elif abs_correlation >= 0.7:
        return "strong"
    elif abs_correlation >= 0.5:
        return "moderate"
    elif abs_correlation >= 0.3:
        return "weak"
    else:
        return "very_weak"

def _generate_correlation_heatmap(correlation_matrix: pd.DataFrame, method: str, data_name: str) -> list:
    """Generate correlation heatmap"""
    plot_files = []
    
    try:
        # Create plots directory
        plots_dir = os.path.join(UPLOAD_DIR, "plots")
        os.makedirs(plots_dir, exist_ok=True)
        
        # Generate heatmap
        plt.figure(figsize=(12, 10))
        
        # Create mask for upper triangle
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
        
        # Generate heatmap
        sns.heatmap(correlation_matrix, 
                   annot=True, 
                   cmap='RdBu_r', 
                   center=0,
                   square=True, 
                   linewidths=0.5,
                   mask=mask,
                   fmt='.2f',
                   cbar_kws={"shrink": .8})
        
        plt.title(f'Correlation Matrix ({method.title()}) - {data_name}', fontsize=16)
        plt.tight_layout()
        
        # Save plot
        plot_filename = f"correlation_heatmap_{method}_{data_name}.png"
        plot_path = os.path.join(plots_dir, plot_filename)
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        plot_files.append(plot_filename)
        print(f"Generated correlation heatmap: {plot_filename}")
        
        # Generate clustermap if enough variables
        if len(correlation_matrix.columns) >= 3:
            plt.figure(figsize=(12, 10))
            
            # Generate clustermap
            clustermap = sns.clustermap(correlation_matrix, 
                                      annot=True, 
                                      cmap='RdBu_r', 
                                      center=0,
                                      square=True, 
                                      linewidths=0.5,
                                      fmt='.2f',
                                      figsize=(12, 10))
            
            clustermap.fig.suptitle(f'Clustered Correlation Matrix ({method.title()}) - {data_name}', 
                                  fontsize=16, y=1.02)
            
            # Save clustermap
            cluster_filename = f"correlation_clustermap_{method}_{data_name}.png"
            cluster_path = os.path.join(plots_dir, cluster_filename)
            clustermap.savefig(cluster_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            plot_files.append(cluster_filename)
            print(f"Generated correlation clustermap: {cluster_filename}")
        
    except Exception as e:
        print(f"Warning: Could not generate correlation plots: {e}")
        plt.close()
    
    return plot_files