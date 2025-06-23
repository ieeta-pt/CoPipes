import os
import pandas as pd
from typing import Dict, Any
from airflow.decorators import task
import json
import gzip
import bz2

UPLOAD_DIR = "/tmp/airflow_exports/"

@task
def file_export(data: Dict[str, Any], file_path: str, file_format: str = "csv",
                compression: str = "none", include_header: bool = True) -> Dict[str, Any]:
    """
    Export data to file in various formats.
    Files are stored in a local directory (/tmp/airflow_exports/) regardless of user input.
    
    Args:
        data: Input data from transformation task
        file_path: User-specified file path (filename or path - will be stored locally)
        file_format: Export file format (csv, json, parquet, xlsx, xml)
        compression: File compression (none, gzip, bzip2, snappy)
        include_header: Include column headers (for CSV)
    
    Returns:
        Dictionary containing export results and metadata
    """
    try:
        # Extract data
        input_data = data.get('data', [])
        if not input_data:
            raise ValueError("No data provided for file export")
        
        # Convert to DataFrame
        df = pd.DataFrame(input_data)
        total_rows = len(df)
        
        print(f"Starting file export. Rows: {total_rows}, Format: {file_format}")
        print(f"User specified path: {file_path}")
        
        # Always store in local directory, abstract user from underlying path
        # User provides filename or relative path, we store in UPLOAD_DIR
        if file_path.startswith('/'):
            # If user provides absolute path, extract just the filename
            file_path = os.path.basename(file_path)
        
        output_path = os.path.join(UPLOAD_DIR, file_path)
        print(f"Actual storage path: {output_path}")
        
        # Ensure directory exists with proper permissions
        output_dir = os.path.dirname(output_path) if os.path.dirname(output_path) else UPLOAD_DIR
        os.makedirs(output_dir, exist_ok=True, mode=0o755)
        
        # Export based on format
        exported_file = _export_to_format(df, output_path, file_format, include_header)
        
        # Apply compression if requested
        final_file = _apply_compression(exported_file, compression)
        
        # Get file size
        file_size = os.path.getsize(final_file)
        
        print(f"File export completed. Output: {final_file}, Size: {file_size} bytes")
        
        return {
            "data": [{"message": f"Successfully exported {total_rows} rows to {os.path.basename(final_file)}"}],
            "filename": f"export_{os.path.basename(final_file)}",
            "export_path": final_file,
            "user_specified_path": file_path,
            "rows_exported": total_rows,
            "columns_exported": len(df.columns),
            "file_format": file_format,
            "compression": compression,
            "file_size": file_size,
            "include_header": include_header
        }
        
    except Exception as e:
        raise ValueError(f"File export failed: {e}")

def _export_to_format(df: pd.DataFrame, output_path: str, file_format: str, include_header: bool) -> str:
    """Export DataFrame to specified format"""
    
    # Ensure file extension matches format
    base_path = os.path.splitext(output_path)[0]
    
    if file_format.lower() == "csv":
        file_path = f"{base_path}.csv"
        df.to_csv(file_path, index=False, header=include_header)
        os.chmod(file_path, 0o644)
        
    elif file_format.lower() == "json":
        file_path = f"{base_path}.json"
        df.to_json(file_path, orient='records', indent=2)
        os.chmod(file_path, 0o644)
        
    elif file_format.lower() == "parquet":
        file_path = f"{base_path}.parquet"
        df.to_parquet(file_path, index=False)
        os.chmod(file_path, 0o644)
        
    elif file_format.lower() == "xlsx":
        file_path = f"{base_path}.xlsx"
        df.to_excel(file_path, index=False, header=include_header)
        os.chmod(file_path, 0o644)
        
    elif file_format.lower() == "xml":
        file_path = f"{base_path}.xml"
        _export_to_xml(df, file_path)
        os.chmod(file_path, 0o644)
        
    else:
        # Default to CSV
        file_path = f"{base_path}.csv"
        df.to_csv(file_path, index=False, header=include_header)
        os.chmod(file_path, 0o644)
        print(f"Warning: Unsupported format '{file_format}', defaulting to CSV")
    
    return file_path

def _export_to_xml(df: pd.DataFrame, file_path: str):
    """Export DataFrame to XML format"""
    try:
        # Use pandas to_xml if available (pandas >= 1.3.0)
        df.to_xml(file_path, index=False)
    except AttributeError:
        # Fallback manual XML creation
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<data>\n')
            
            for _, row in df.iterrows():
                f.write('  <record>\n')
                for col, value in row.items():
                    # Escape XML special characters
                    escaped_value = str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    escaped_col = str(col).replace(' ', '_').replace('-', '_')
                    f.write(f'    <{escaped_col}>{escaped_value}</{escaped_col}>\n')
                f.write('  </record>\n')
            
            f.write('</data>\n')

def _apply_compression(file_path: str, compression: str) -> str:
    """Apply compression to exported file"""
    
    if compression.lower() == "none":
        return file_path
    
    elif compression.lower() == "gzip":
        compressed_path = f"{file_path}.gz"
        with open(file_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                f_out.writelines(f_in)
        
        # Remove original file
        os.remove(file_path)
        print(f"Applied gzip compression: {compressed_path}")
        return compressed_path
    
    elif compression.lower() == "bzip2":
        compressed_path = f"{file_path}.bz2"
        with open(file_path, 'rb') as f_in:
            with bz2.open(compressed_path, 'wb') as f_out:
                f_out.writelines(f_in)
        
        # Remove original file
        os.remove(file_path)
        print(f"Applied bzip2 compression: {compressed_path}")
        return compressed_path
    
    elif compression.lower() == "snappy":
        try:
            import snappy
            compressed_path = f"{file_path}.snappy"
            with open(file_path, 'rb') as f_in:
                compressed_data = snappy.compress(f_in.read())
                with open(compressed_path, 'wb') as f_out:
                    f_out.write(compressed_data)
            
            # Remove original file
            os.remove(file_path)
            print(f"Applied snappy compression: {compressed_path}")
            return compressed_path
        except ImportError:
            print("Warning: Snappy compression not available, skipping compression")
            return file_path
    
    else:
        print(f"Warning: Unsupported compression '{compression}', skipping compression")
        return file_path