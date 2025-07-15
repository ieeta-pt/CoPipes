import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import tempfile
import sys
from typing import Dict, Any, Optional
from airflow.decorators import task

# Add utils to path for imports
if '/opt/airflow/dags' not in sys.path:
    sys.path.insert(0, '/opt/airflow/dags')

from components.utils.supabase_storage import storage

@task
def data_visualization(data: Dict[str, Any], chart_type: str, x_column: Optional[str] = None,
                      y_column: Optional[str] = None, color_column: Optional[str] = None,
                      title: Optional[str] = None, save_format: str = "png") -> Dict[str, Any]:
    """
    Create data visualizations.
    
    Args:
        data: Input data from extraction or transformation task
        chart_type: Type of visualization (scatter, line, bar, histogram, box, heatmap, pie, category_demand, monthly_heatmap, demand_ranking, trend_analysis)
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
        
        # Generate visualization and save to Supabase Storage
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
    
    # Handle business chart types that auto-detect columns
    business_chart_types = ['category_demand', 'monthly_heatmap', 'demand_ranking', 'trend_analysis']
    if chart_type.lower() in business_chart_types:
        return None, None, None
    
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


def _decode_categorical_features(df: pd.DataFrame) -> pd.DataFrame:
    """Decode one-hot encoded categorical features back to original categories"""
    df_decoded = df.copy()
    
    print(f"DEBUG: Input DataFrame columns: {list(df.columns)}")
    print(f"DEBUG: DataFrame shape: {df.shape}")
    
    # Generic decoder for common prefixes
    prefixes_to_decode = ['Product_Category_', 'Gender_', 'Category_', 'Type_', 'Class_']
    
    for prefix in prefixes_to_decode:
        encoded_cols = [col for col in df.columns if col.startswith(prefix)]
        if encoded_cols:
            print(f"DEBUG: Found encoded columns for {prefix}: {encoded_cols}")
            decoded_col_name = prefix.rstrip('_')
            
            # Check sample values to understand the encoding
            for col in encoded_cols[:2]:  # Check first 2 columns
                sample_values = df[col].unique()[:5]
                print(f"DEBUG: Sample values in {col}: {sample_values}")
            
            def get_category(row, cols=encoded_cols, prefix=prefix):
                # Handle scaled/normalized values - find the column with highest value
                max_val = float('-inf')
                max_col = None
                
                for col in cols:
                    if row[col] > max_val:
                        max_val = row[col]
                        max_col = col
                
                if max_col:
                    return max_col.replace(prefix, '')
                return 'Unknown'
            
            df_decoded[decoded_col_name] = df.apply(lambda row: get_category(row), axis=1)
            print(f"DEBUG: Created decoded column '{decoded_col_name}' with unique values: {df_decoded[decoded_col_name].unique()}")
    
    print(f"DEBUG: Final DataFrame columns: {list(df_decoded.columns)}")
    return df_decoded

def _find_column_by_keywords(df: pd.DataFrame, keywords: list) -> Optional[str]:
    """Find column by matching keywords"""
    print(f"DEBUG: Looking for keywords {keywords} in columns: {list(df.columns)}")
    
    # Prioritize exact matches and decoded columns
    matches = []
    for col in df.columns:
        if any(keyword in col.lower() for keyword in keywords):
            matches.append(col)
    
    if matches:
        print(f"DEBUG: All matches found: {matches}")
        
        # Prefer decoded columns (without underscore prefixes) over encoded ones
        for match in matches:
            if not any(match.startswith(prefix) for prefix in ['Product_Category_', 'Gender_', 'Category_']):
                print(f"DEBUG: Using decoded column: {match}")
                return match
        
        # If no decoded column, use the first match
        print(f"DEBUG: Using first match: {matches[0]}")
        return matches[0]
    
    print(f"DEBUG: No match found for keywords {keywords}")
    return None

def _create_visualization(df: pd.DataFrame, chart_type: str, x_col: Optional[str], 
                         y_col: Optional[str], color_col: Optional[str], title: str,
                         save_format: str, data_name: str) -> str:
    """Create the actual visualization and save to Supabase Storage"""
    
    # Set plot style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create figure
    plt.figure(figsize=(12, 8))
    
    chart_type_lower = chart_type.lower()
    
    try:
        if chart_type_lower == "scatter":
            if color_col and color_col in df.columns:
                scatter = plt.scatter(df[x_col], df[y_col], c=df[color_col], alpha=0.6, s=50)
                plt.colorbar(scatter, label=color_col)
            else:
                plt.scatter(df[x_col], df[y_col], alpha=0.6, s=50)
            plt.xlabel(x_col)
            plt.ylabel(y_col)
            
        elif chart_type_lower == "line":
            if color_col and color_col in df.columns:
                for group in df[color_col].unique():
                    group_data = df[df[color_col] == group]
                    plt.plot(group_data[x_col], group_data[y_col], label=str(group), marker='o')
                plt.legend()
            else:
                plt.plot(df[x_col], df[y_col], marker='o')
            plt.xlabel(x_col)
            plt.ylabel(y_col)
            
        elif chart_type_lower == "bar":
            if color_col and color_col in df.columns:
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
            if color_col and color_col in df.columns:
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
            if color_col and color_col in df.columns:
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
            
        elif chart_type_lower == "category_demand":
            _create_category_demand_chart(df)
            
        elif chart_type_lower == "monthly_heatmap":
            _create_monthly_heatmap(df)
            
        elif chart_type_lower == "demand_ranking":
            _create_demand_ranking_chart(df)
            
        elif chart_type_lower == "trend_analysis":
            _create_trend_analysis_chart(df)
            
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")
        
        plt.title(title, fontsize=16, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save plot to temporary file, then upload to Supabase Storage
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_')).replace(' ', '_')
        plot_filename = f"{chart_type_lower}_{data_name}_{safe_title}.{save_format}"
        storage_path = f"plots/{plot_filename}"
        
        with tempfile.NamedTemporaryFile(suffix=f".{save_format}") as tmp_file:
            # Save plot to temporary file
            if save_format.lower() == 'svg':
                plt.savefig(tmp_file.name, format='svg', bbox_inches='tight')
            elif save_format.lower() == 'pdf':
                plt.savefig(tmp_file.name, format='pdf', bbox_inches='tight')
            else:
                plt.savefig(tmp_file.name, dpi=150, bbox_inches='tight', format=save_format)
            
            plt.close()
            
            # Read the file and upload to Supabase Storage
            with open(tmp_file.name, 'rb') as f:
                plot_content = f.read()
            
            # Determine content type
            content_type_map = {
                'png': 'image/png',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'svg': 'image/svg+xml',
                'pdf': 'application/pdf'
            }
            content_type = content_type_map.get(save_format.lower(), 'application/octet-stream')
            
            # Upload to Supabase Storage
            try:
                if storage.file_exists(storage_path):
                    storage.client.storage.from_(storage.bucket_name).update(
                        path=storage_path,
                        file=plot_content,
                        file_options={"content-type": content_type}
                    )
                else:
                    storage.client.storage.from_(storage.bucket_name).upload(
                        path=storage_path,
                        file=plot_content,
                        file_options={"content-type": content_type}
                    )
                print(f"Plot saved to Supabase Storage: {storage_path}")
                return storage_path
            except Exception as e:
                print(f"Failed to save plot to Supabase Storage: {e}")
                return plot_filename  # Return filename even if upload fails
        
    except Exception as e:
        plt.close()
        raise ValueError(f"Failed to create {chart_type} visualization: {e}")

def _create_category_demand_chart(df: pd.DataFrame):
    """Create category demand bar chart"""
    df_decoded = _decode_categorical_features(df)
    
    demand_col = _find_column_by_keywords(df_decoded, ['predicted_demand', 'predicted', 'prediction', 'demand', 'quantity'])
    category_col = _find_column_by_keywords(df_decoded, ['category', 'product_category', 'type'])
    
    if demand_col and category_col:
        # Ensure we're using decoded category names
        category_totals = df_decoded.groupby(category_col)[demand_col].sum().sort_values(ascending=False)
        
        # Create more distinct colors for better readability
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98FB98', '#F0E68C']
        bars = plt.bar(range(len(category_totals)), category_totals.values, 
                      color=colors[:len(category_totals)])
        
        # Set category names as x-tick labels
        plt.xticks(range(len(category_totals)), category_totals.index, rotation=45, ha='right')
        
        # Add value labels on bars
        for i, (category, value) in enumerate(category_totals.items()):
            plt.text(i, value + max(category_totals.values) * 0.01,
                    f'{value:.0f}', ha='center', va='bottom', fontweight='bold')
        
        plt.xlabel('Product Category', fontweight='bold')
        plt.ylabel('Total Predicted Demand', fontweight='bold')
        plt.grid(True, alpha=0.3, axis='y')
    else:
        plt.text(0.5, 0.5, 'No suitable data found for category demand analysis', 
                ha='center', va='center', transform=plt.gca().transAxes)

def _create_monthly_heatmap(df: pd.DataFrame):
    """Create monthly category demand heatmap"""
    df_decoded = _decode_categorical_features(df)
    
    demand_col = _find_column_by_keywords(df_decoded, ['predicted_demand', 'predicted', 'prediction', 'demand', 'quantity'])
    category_col = _find_column_by_keywords(df_decoded, ['category', 'product_category', 'type'])
    date_col = _find_column_by_keywords(df_decoded, ['date', 'time', 'timestamp'])
    
    if demand_col and category_col and date_col:
        # Create month labels with proper formatting
        df_decoded['Month'] = pd.to_datetime(df_decoded[date_col]).dt.strftime('%b %Y')
        pivot_df = df_decoded.groupby([category_col, 'Month'])[demand_col].mean().unstack(fill_value=0)
        
        if not pivot_df.empty:
            # Create heatmap with better formatting
            plt.figure(figsize=(12, 6))
            sns.heatmap(pivot_df, annot=True, cmap='YlOrRd', fmt='.1f',
                       cbar_kws={'label': 'Average Demand'}, 
                       linewidths=0.5, linecolor='white')
            
            # Format labels
            plt.ylabel('Product Category', fontweight='bold')
            plt.xlabel('Month', fontweight='bold')
            
            # Rotate y-axis labels for better readability
            plt.yticks(rotation=0)
            plt.xticks(rotation=45, ha='right')
        else:
            plt.text(0.5, 0.5, 'Insufficient data for monthly heatmap', 
                    ha='center', va='center', transform=plt.gca().transAxes)
    else:
        plt.text(0.5, 0.5, 'No suitable data found for monthly analysis', 
                ha='center', va='center', transform=plt.gca().transAxes)

def _create_demand_ranking_chart(df: pd.DataFrame):
    """Create horizontal bar chart ranking categories by demand"""
    df_decoded = _decode_categorical_features(df)
    
    demand_col = _find_column_by_keywords(df_decoded, ['predicted_demand', 'predicted', 'prediction', 'demand', 'quantity'])
    category_col = _find_column_by_keywords(df_decoded, ['category', 'product_category', 'type'])
    
    print(f"DEBUG: Found demand_col: {demand_col}")
    print(f"DEBUG: Found category_col: {category_col}")
    
    if demand_col and category_col:
        print(f"DEBUG: Sample data from category column: {df_decoded[category_col].value_counts()}")
        # Sort categories by demand (ascending for horizontal bar chart)
        category_totals = df_decoded.groupby(category_col)[demand_col].sum().sort_values(ascending=True)
        
        # Use gradient colors from low to high demand
        colors = plt.cm.RdYlBu_r(np.linspace(0.2, 0.8, len(category_totals)))
        bars = plt.barh(range(len(category_totals)), category_totals.values, color=colors)
        
        # Set category names as y-tick labels
        plt.yticks(range(len(category_totals)), category_totals.index)
        
        # Format labels
        plt.xlabel('Total Predicted Demand', fontweight='bold')
        plt.ylabel('Product Category', fontweight='bold')
        
        # Add value labels at the end of bars
        for i, value in enumerate(category_totals.values):
            plt.text(value + max(category_totals.values) * 0.02, i, 
                    f'{value:.0f}', va='center', ha='left', fontweight='bold')
        
        # Add grid for better readability
        plt.grid(True, alpha=0.3, axis='x')
        
        # Highlight the top category
        top_idx = len(category_totals) - 1
        bars[top_idx].set_edgecolor('black')
        bars[top_idx].set_linewidth(2)
    else:
        plt.text(0.5, 0.5, 'No suitable data found for demand ranking', 
                ha='center', va='center', transform=plt.gca().transAxes)

def _create_trend_analysis_chart(df: pd.DataFrame):
    """Create trend analysis line chart"""
    df_decoded = _decode_categorical_features(df)
    
    demand_col = _find_column_by_keywords(df_decoded, ['predicted_demand', 'predicted', 'prediction', 'demand', 'quantity'])
    date_col = _find_column_by_keywords(df_decoded, ['date', 'time', 'timestamp'])
    category_col = _find_column_by_keywords(df_decoded, ['category', 'product_category', 'type'])
    
    if demand_col and date_col:
        df_decoded['Date_parsed'] = pd.to_datetime(df_decoded[date_col])
        
        if category_col:
            # Create distinct colors and markers for each category
            categories = df_decoded[category_col].unique()
            colors = plt.cm.Set3(np.linspace(0, 1, len(categories)))
            markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h']
            
            for i, category in enumerate(categories):
                category_data = df_decoded[df_decoded[category_col] == category].sort_values('Date_parsed')
                plt.plot(category_data['Date_parsed'], category_data[demand_col], 
                        label=category, marker=markers[i % len(markers)], 
                        color=colors[i], linewidth=2, markersize=6)
            
            # Format legend
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
        else:
            df_sorted = df_decoded.sort_values('Date_parsed')
            plt.plot(df_sorted['Date_parsed'], df_sorted[demand_col], 
                    marker='o', linewidth=2, markersize=6, color='#2E86AB')
        
        # Format labels and axes
        plt.xlabel('Date', fontweight='bold')
        plt.ylabel('Predicted Demand', fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        
        # Add grid for better readability
        plt.grid(True, alpha=0.3)
        
        # Format dates on x-axis
        plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%b %Y'))
        plt.gca().xaxis.set_major_locator(plt.matplotlib.dates.MonthLocator(interval=1))
    else:
        plt.text(0.5, 0.5, 'No suitable data found for trend analysis', 
                ha='center', va='center', transform=plt.gca().transAxes)

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