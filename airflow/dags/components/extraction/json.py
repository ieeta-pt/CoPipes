import os
import json
import requests
import pandas as pd
from typing import Dict, Optional
from airflow.decorators import task
import jsonpath_ng
from components.utils.resolve_file import resolve_input_file

UPLOAD_DIR = "/shared_data/"

@task
def json_extract(source: str, json_path: Optional[str] = None, flatten_nested: bool = True, user_id: str = None) -> Dict[str, str]:
    """
    Extract data from JSON file or API endpoint.
    
    Args:
        source: JSON file path or API endpoint URL
        json_path: JSONPath expression to extract specific data (e.g., $.data[*])
        flatten_nested: Whether to flatten nested JSON objects
    
    Returns:
        Dictionary containing extracted data and metadata
    """
    try:
        # Determine if source is a URL or file path
        if source.startswith(('http://', 'https://')):
            # Fetch from API endpoint
            response = requests.get(source, timeout=30)
            response.raise_for_status()
            data = response.json()
            source_type = "api"
            source_name = source.split("/")[-1] or "api_response"
        else:
            # Read from file
            if source.startswith('/'):
                file_path = source
            else:
                file_path = resolve_input_file(source, user_id)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            source_type = "file"
            source_name = os.path.basename(source)
        
        # Apply JSONPath filter if provided
        if json_path:
            try:
                jsonpath_expr = jsonpath_ng.parse(json_path)
                matches = [match.value for match in jsonpath_expr.find(data)]
                if matches:
                    data = matches if len(matches) > 1 else matches[0]
                else:
                    print(f"Warning: JSONPath '{json_path}' returned no matches")
            except Exception as e:
                print(f"Warning: Invalid JSONPath expression '{json_path}': {e}")
        
        # Convert to DataFrame for consistent processing
        if isinstance(data, list):
            df = pd.json_normalize(data, max_level=1 if not flatten_nested else None)
        elif isinstance(data, dict):
            df = pd.json_normalize([data], max_level=1 if not flatten_nested else None)
        else:
            # Handle primitive types
            df = pd.DataFrame([{"value": data}])
        
        # Replace NaN with None for consistent handling
        df = df.where(pd.notna(df), None)
        
        print(f"Successfully extracted JSON data from {source_type}: {source_name}")
        print(f"Shape: {df.shape}, Columns: {df.columns.tolist()}")
        
        return {
            "data": df.to_dict(orient="records"),
            "filename": source_name,
            "source_type": source_type
        }
        
    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch data from API endpoint '{source}': {e}")
    except FileNotFoundError:
        raise ValueError(f"JSON file not found: {source}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in '{source}': {e}")
    except Exception as e:
        raise ValueError(f"Error processing JSON data from '{source}': {e}")