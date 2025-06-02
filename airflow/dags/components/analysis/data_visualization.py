import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, Optional
from airflow.decorators import task

UPLOAD_DIR = "/shared_data/"

@task
def data_visualization(data: Dict[str, Any], chart_type: str, x_column: Optional[str] = None,
                      y_column: Optional[str] = None, color_column: Optional[str] = None,
                      title: Optional[str] = None, save_format: str = "png") -> Dict[str, Any]:
    """
    Create data visualizations.
    
    Args:
        data: Input data from extraction or transformation task
        chart_type: Type of visualization (scatter, line, bar, histogram, box, heatmap, pie)
        x_column: Column for X-axis
        y_column: Column for Y-axis
        color_column: Column for color grouping
        title: Chart title
        save_format: Output format (png, jpg, svg, pdf, html)
    
    Returns:
        Dictionary containing visualization results and metadata
    """
    try:
        # Extract data
        input_data = data.get('data', [])
        if not input_data:
            raise ValueError("No data provided for visualization")
        
        # Convert to DataFrame
        df = pd.DataFrame(input_data)
        
        print(f"Starting data visualization. Data shape: {df.shape}")
        print(f"Chart type: {chart_type}")
        
        # Validate and prepare columns
        x_col, y_col, color_col = _validate_columns(df, x_column, y_column, color_column, chart_type)
        
        # Set default title
        if not title:
            title = f"{chart_type.title()} Chart"
            if x_col and y_col:
                title = f"{y_col} vs {x_col}"
        
        # Create plots directory
        plots_dir = os.path.join(UPLOAD_DIR, "plots")
        os.makedirs(plots_dir, exist_ok=True)
        
        # Generate visualization
        plot_file = _create_visualization(df, chart_type, x_col, y_col, color_col, title, 
                                        save_format, data.get('filename', 'data'))
        
        # Generate summary statistics for the visualization
        viz_stats = _generate_viz_stats(df, x_col, y_col, color_col, chart_type)
        
        # Prepare results data
        results_data = [{
            'chart_type': chart_type,
            'x_column': x_col,
            'y_column': y_col,
            'color_column': color_col,
            'title': title,
            'plot_file': plot_file,
            'data_points': len(df),
            'save_format': save_format
        }]
        
        print(f"Visualization completed. Generated: {plot_file}")
        
        return {
            "data": results_data,
            "filename": f"visualization_{data.get('filename', 'data')}.csv",
            "plot_file": plot_file,
            "chart_type": chart_type,
            "visualization_stats": viz_stats,
            "columns_used": {"x": x_col, "y": y_col, "color": color_col},
            "data_points": len(df)
        }
        
    except Exception as e:
        raise ValueError(f"Data visualization failed: {e}")

def _validate_columns(df: pd.DataFrame, x_column: Optional[str], y_column: Optional[str], 
                     color_column: Optional[str], chart_type: str) -> tuple:
    """Validate and select appropriate columns for visualization"""
    
    # Get available columns by type
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
    all_cols = df.columns.tolist()
    
    x_col = x_column
    y_col = y_column
    color_col = color_column
    
    # Auto-select columns if not provided based on chart type
    if chart_type.lower() == "histogram":
        if not x_col:
            x_col = numeric_cols[0] if numeric_cols else all_cols[0]
        y_col = None  # Histograms don't need y column
        
    elif chart_type.lower() == "box":
        if not x_col:
            x_col = numeric_cols[0] if numeric_cols else all_cols[0]
        y_col = None  # Box plots don't need y column for single variable
        
    elif chart_type.lower() == "pie":
        if not x_col:
            x_col = categorical_cols[0] if categorical_cols else all_cols[0]
        y_col = None  # Pie charts use value counts
        
    elif chart_type.lower() == "heatmap":
        # For heatmap, use correlation matrix of numeric columns
        x_col = None
        y_col = None
        
    else:
        # For scatter, line, bar charts
        if not x_col:
            x_col = all_cols[0] if all_cols else None
        if not y_col and len(all_cols) > 1:
            # Prefer numeric columns for y-axis
            remaining_cols = [col for col in all_cols if col != x_col]
            y_col = next((col for col in remaining_cols if col in numeric_cols), remaining_cols[0])
    
    # Validate color column
    if color_col and color_col not in df.columns:
        print(f"Warning: Color column '{color_col}' not found, ignoring")
        color_col = None
    
    # Validate x and y columns exist
    if x_col and x_col not in df.columns:
        raise ValueError(f"X column '{x_col}' not found in data")
    if y_col and y_col not in df.columns:
        raise ValueError(f"Y column '{y_col}' not found in data")
    
    return x_col, y_col, color_col

def _create_visualization(df: pd.DataFrame, chart_type: str, x_col: Optional[str], 
                         y_col: Optional[str], color_col: Optional[str], title: str,
                         save_format: str, data_name: str) -> str:
    """Create the actual visualization"""
    
    # Set plot style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create figure
    plt.figure(figsize=(12, 8))
    
    chart_type_lower = chart_type.lower()
    
    try:
        if chart_type_lower == "scatter":
            if color_col:
                scatter = plt.scatter(df[x_col], df[y_col], c=df[color_col], alpha=0.6, s=50)
                plt.colorbar(scatter, label=color_col)
            else:
                plt.scatter(df[x_col], df[y_col], alpha=0.6, s=50)
            plt.xlabel(x_col)
            plt.ylabel(y_col)
            
        elif chart_type_lower == "line":
            if color_col:
                for group in df[color_col].unique():
                    group_data = df[df[color_col] == group]
                    plt.plot(group_data[x_col], group_data[y_col], label=str(group), marker='o')
                plt.legend()
            else:
                plt.plot(df[x_col], df[y_col], marker='o')
            plt.xlabel(x_col)
            plt.ylabel(y_col)
            
        elif chart_type_lower == "bar":
            if color_col:
                # Group by color column and aggregate
                grouped = df.groupby([x_col, color_col])[y_col].sum().unstack(fill_value=0)
                grouped.plot(kind='bar', stacked=False, ax=plt.gca())
                plt.legend(title=color_col)
            else:
                # Simple aggregation by x column
                aggregated = df.groupby(x_col)[y_col].sum()
                aggregated.plot(kind='bar', ax=plt.gca())
            plt.xlabel(x_col)
            plt.ylabel(y_col)
            plt.xticks(rotation=45)
            
        elif chart_type_lower == "histogram":
            if color_col:
                # Multiple histograms by color
                for group in df[color_col].unique():
                    group_data = df[df[color_col] == group][x_col]
                    plt.hist(group_data, alpha=0.7, label=str(group), bins=30)
                plt.legend()
            else:
                plt.hist(df[x_col], bins=30, alpha=0.7, edgecolor='black')
            plt.xlabel(x_col)
            plt.ylabel('Frequency')
            
        elif chart_type_lower == "box":
            if color_col:
                # Box plot by color groups
                df.boxplot(column=x_col, by=color_col, ax=plt.gca())
                plt.suptitle('')  # Remove auto-generated title
            else:
                df[x_col].plot(kind='box', ax=plt.gca())
            plt.ylabel(x_col)
            
        elif chart_type_lower == "heatmap":
            # Create correlation heatmap of numeric columns
            numeric_df = df.select_dtypes(include=[np.number])
            if len(numeric_df.columns) < 2:
                raise ValueError("Need at least 2 numeric columns for heatmap")
            
            correlation_matrix = numeric_df.corr()
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                       square=True, linewidths=0.5)
            
        elif chart_type_lower == "pie":
            # Pie chart of value counts
            value_counts = df[x_col].value_counts()
            # Limit to top 10 categories for readability
            if len(value_counts) > 10:
                value_counts = value_counts.head(10)
            
            plt.pie(value_counts.values, labels=value_counts.index, autopct='%1.1f%%')
            plt.axis('equal')
            
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")
        
        plt.title(title, fontsize=16, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save plot
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_')).replace(' ', '_')
        plot_filename = f"{chart_type_lower}_{data_name}_{safe_title}.{save_format}"
        plot_path = os.path.join(UPLOAD_DIR, "plots", plot_filename)
        
        # Save with appropriate DPI and format
        if save_format.lower() == 'svg':
            plt.savefig(plot_path, format='svg', bbox_inches='tight')
        elif save_format.lower() == 'pdf':
            plt.savefig(plot_path, format='pdf', bbox_inches='tight')
        else:
            plt.savefig(plot_path, dpi=150, bbox_inches='tight', format=save_format)
        
        plt.close()
        
        return plot_filename
        
    except Exception as e:
        plt.close()
        raise ValueError(f"Failed to create {chart_type} visualization: {e}")

def _generate_viz_stats(df: pd.DataFrame, x_col: Optional[str], y_col: Optional[str], 
                       color_col: Optional[str], chart_type: str) -> dict:
    """Generate statistics about the visualization"""
    
    stats = {
        'chart_type': chart_type,
        'data_points': len(df),
        'columns_used': []
    }
    
    if x_col:
        stats['columns_used'].append(x_col)
        if x_col in df.select_dtypes(include=[np.number]).columns:
            stats['x_min'] = df[x_col].min()
            stats['x_max'] = df[x_col].max()
            stats['x_mean'] = df[x_col].mean()
        else:
            stats['x_unique_values'] = df[x_col].nunique()
    
    if y_col:
        stats['columns_used'].append(y_col)
        if y_col in df.select_dtypes(include=[np.number]).columns:
            stats['y_min'] = df[y_col].min()
            stats['y_max'] = df[y_col].max()
            stats['y_mean'] = df[y_col].mean()
        else:
            stats['y_unique_values'] = df[y_col].nunique()
    
    if color_col:
        stats['columns_used'].append(color_col)
        stats['color_groups'] = df[color_col].nunique()
        stats['color_values'] = df[color_col].unique().tolist()[:10]  # Limit to 10
    
    return stats