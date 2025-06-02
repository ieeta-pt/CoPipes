import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, Optional
from airflow.decorators import task

UPLOAD_DIR = "/shared_data/"

@task
def descriptive_statistics(data: Dict[str, Any], target_columns: Optional[str] = None,
                          include: str = "all", percentiles: str = "0.25,0.5,0.75",
                          generate_plots: bool = True) -> Dict[str, Any]:
    """
    Generate descriptive statistics for data.
    
    Args:
        data: Input data from extraction or transformation task
        target_columns: Columns to analyze (separated by commas, leave empty for all numeric)
        include: Data types to include (all, number, object, datetime)
        percentiles: Percentiles to calculate (separated by commas)
        generate_plots: Generate distribution plots
    
    Returns:
        Dictionary containing statistics and metadata
    """
    try:
        # Extract data
        input_data = data.get('data', [])
        if not input_data:
            raise ValueError("No data provided for descriptive statistics")
        
        # Convert to DataFrame
        df = pd.DataFrame(input_data)
        
        print(f"Starting descriptive statistics. Data shape: {df.shape}")
        
        # Parse target columns
        if target_columns and target_columns.strip():
            target_cols = [col.strip() for col in target_columns.split(',')]
            # Filter to existing columns
            target_cols = [col for col in target_cols if col in df.columns]
            if target_cols:
                df_analysis = df[target_cols]
            else:
                print("Warning: None of the specified columns exist, using all columns")
                df_analysis = df
        else:
            df_analysis = df
        
        # Parse percentiles
        try:
            percentile_list = [float(p.strip()) for p in percentiles.split(',')]
        except ValueError:
            percentile_list = [0.25, 0.5, 0.75]  # Default
        
        # Filter by data types
        if include.lower() == "number":
            df_analysis = df_analysis.select_dtypes(include=[np.number])
        elif include.lower() == "object":
            df_analysis = df_analysis.select_dtypes(include=['object', 'string'])
        elif include.lower() == "datetime":
            df_analysis = df_analysis.select_dtypes(include=['datetime64'])
        # For "all", use the DataFrame as is
        
        print(f"Analyzing {len(df_analysis.columns)} columns: {df_analysis.columns.tolist()}")
        
        # Generate basic statistics
        stats_results = {}
        
        # Overall dataset info
        stats_results['dataset_info'] = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'analyzed_columns': len(df_analysis.columns),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'missing_values_total': df.isnull().sum().sum()
        }
        
        # Column-wise statistics
        column_stats = []
        
        for col in df_analysis.columns:
            col_data = df_analysis[col]
            col_stats = {
                'column': col,
                'dtype': str(col_data.dtype),
                'count': col_data.count(),
                'missing': col_data.isnull().sum(),
                'missing_percentage': (col_data.isnull().sum() / len(col_data)) * 100
            }
            
            if pd.api.types.is_numeric_dtype(col_data):
                # Numeric statistics
                col_stats.update({
                    'mean': col_data.mean(),
                    'std': col_data.std(),
                    'min': col_data.min(),
                    'max': col_data.max(),
                    'range': col_data.max() - col_data.min(),
                    'skewness': col_data.skew(),
                    'kurtosis': col_data.kurtosis()
                })
                
                # Add percentiles
                for p in percentile_list:
                    col_stats[f'p{int(p*100)}'] = col_data.quantile(p)
                
            elif pd.api.types.is_string_dtype(col_data) or pd.api.types.is_object_dtype(col_data):
                # String/categorical statistics
                value_counts = col_data.value_counts()
                col_stats.update({
                    'unique_values': col_data.nunique(),
                    'most_frequent': value_counts.index[0] if len(value_counts) > 0 else None,
                    'most_frequent_count': value_counts.iloc[0] if len(value_counts) > 0 else 0,
                    'least_frequent': value_counts.index[-1] if len(value_counts) > 0 else None,
                    'least_frequent_count': value_counts.iloc[-1] if len(value_counts) > 0 else 0
                })
                
            elif pd.api.types.is_datetime64_any_dtype(col_data):
                # Datetime statistics
                col_stats.update({
                    'earliest': col_data.min(),
                    'latest': col_data.max(),
                    'range_days': (col_data.max() - col_data.min()).days if col_data.min() and col_data.max() else None
                })
            
            column_stats.append(col_stats)
        
        stats_results['column_statistics'] = column_stats
        
        # Generate correlation matrix for numeric columns
        numeric_cols = df_analysis.select_dtypes(include=[np.number])
        if len(numeric_cols.columns) > 1:
            correlation_matrix = numeric_cols.corr()
            stats_results['correlation_matrix'] = correlation_matrix.to_dict()
        
        # Generate plots if requested
        plot_files = []
        if generate_plots and len(df_analysis.columns) > 0:
            plot_files = _generate_distribution_plots(df_analysis, data.get('filename', 'data'))
        
        # Convert results to DataFrame for consistent output
        results_data = []
        
        # Add dataset summary
        results_data.append({
            'metric_type': 'dataset_summary',
            'metric_name': 'total_rows',
            'value': stats_results['dataset_info']['total_rows']
        })
        
        # Add column statistics
        for col_stat in column_stats:
            for key, value in col_stat.items():
                if key != 'column':
                    results_data.append({
                        'metric_type': 'column_statistic',
                        'column': col_stat['column'],
                        'metric_name': key,
                        'value': value
                    })
        
        print(f"Descriptive statistics completed. {len(column_stats)} columns analyzed")
        
        return {
            "data": results_data,
            "filename": f"stats_{data.get('filename', 'data')}.csv",
            "statistics": stats_results,
            "plot_files": plot_files,
            "columns_analyzed": len(df_analysis.columns),
            "percentiles_used": percentile_list
        }
        
    except Exception as e:
        raise ValueError(f"Descriptive statistics failed: {e}")

def _generate_distribution_plots(df: pd.DataFrame, data_name: str) -> list:
    """Generate distribution plots for numeric columns"""
    plot_files = []
    
    try:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return plot_files
        
        # Set plot style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create plots directory
        plots_dir = os.path.join(UPLOAD_DIR, "plots")
        os.makedirs(plots_dir, exist_ok=True)
        
        # Generate histogram for each numeric column
        for col in numeric_cols[:10]:  # Limit to first 10 columns
            try:
                plt.figure(figsize=(10, 6))
                
                # Create subplot with histogram and box plot
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
                
                # Histogram
                df[col].hist(bins=30, ax=ax1, alpha=0.7, edgecolor='black')
                ax1.set_title(f'Distribution of {col}')
                ax1.set_xlabel(col)
                ax1.set_ylabel('Frequency')
                ax1.grid(True, alpha=0.3)
                
                # Box plot
                df[col].plot(kind='box', ax=ax2)
                ax2.set_title(f'Box Plot of {col}')
                ax2.set_ylabel(col)
                
                plt.tight_layout()
                
                # Save plot
                plot_filename = f"distribution_{data_name}_{col.replace(' ', '_')}.png"
                plot_path = os.path.join(plots_dir, plot_filename)
                plt.savefig(plot_path, dpi=150, bbox_inches='tight')
                plt.close()
                
                plot_files.append(plot_filename)
                print(f"Generated plot: {plot_filename}")
                
            except Exception as e:
                print(f"Warning: Could not generate plot for column {col}: {e}")
                plt.close()
        
        # Generate correlation heatmap if multiple numeric columns
        if len(numeric_cols) > 1:
            try:
                plt.figure(figsize=(12, 8))
                correlation_matrix = df[numeric_cols].corr()
                
                sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                           square=True, linewidths=0.5)
                plt.title(f'Correlation Matrix - {data_name}')
                plt.tight_layout()
                
                plot_filename = f"correlation_heatmap_{data_name}.png"
                plot_path = os.path.join(plots_dir, plot_filename)
                plt.savefig(plot_path, dpi=150, bbox_inches='tight')
                plt.close()
                
                plot_files.append(plot_filename)
                print(f"Generated correlation heatmap: {plot_filename}")
                
            except Exception as e:
                print(f"Warning: Could not generate correlation heatmap: {e}")
                plt.close()
        
    except Exception as e:
        print(f"Warning: Plot generation failed: {e}")
    
    return plot_files