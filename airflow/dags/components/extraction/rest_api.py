import json
import requests
import pandas as pd
from typing import Dict, Optional
from airflow.decorators import task
import time

@task
def rest_api(endpoint: str, method: str = "GET", headers: Optional[str] = None, 
             auth_token: Optional[str] = None, pagination: bool = False) -> Dict[str, str]:
    """
    Extract data from REST API endpoint.
    
    Args:
        endpoint: API endpoint URL
        method: HTTP method (GET, POST, PUT, DELETE)
        headers: HTTP headers in JSON format
        auth_token: Authorization token
        pagination: Handle paginated responses
    
    Returns:
        Dictionary containing API response data and metadata
    """
    try:
        # Parse headers if provided
        request_headers = {}
        if headers:
            try:
                request_headers = json.loads(headers)
            except json.JSONDecodeError:
                print(f"Warning: Invalid headers JSON format: {headers}")
        
        # Add authorization token if provided
        if auth_token:
            if auth_token.startswith('Bearer '):
                request_headers['Authorization'] = auth_token
            else:
                request_headers['Authorization'] = f'Bearer {auth_token}'
        
        # Set default headers
        if 'Accept' not in request_headers:
            request_headers['Accept'] = 'application/json'
        
        all_data = []
        page = 1
        max_pages = 50  # Safety limit for pagination
        
        while page <= max_pages:
            # Make API request
            if pagination and page > 1:
                # Add pagination parameters (common patterns)
                if '?' in endpoint:
                    url = f"{endpoint}&page={page}"
                else:
                    url = f"{endpoint}?page={page}"
            else:
                url = endpoint
            
            print(f"Making {method} request to: {url}")
            
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=request_headers,
                timeout=30
            )
            
            response.raise_for_status()
            
            # Parse response
            try:
                data = response.json()
            except json.JSONDecodeError:
                # Handle non-JSON responses
                data = {"response": response.text}
            
            # Handle different response structures
            if isinstance(data, dict):
                # Check for common pagination structures
                if pagination:
                    # Common pagination patterns
                    items = None
                    if 'data' in data:
                        items = data['data']
                    elif 'results' in data:
                        items = data['results']
                    elif 'items' in data:
                        items = data['items']
                    else:
                        items = data
                    
                    if isinstance(items, list):
                        all_data.extend(items)
                        
                        # Check if there are more pages
                        has_more = False
                        if 'has_more' in data:
                            has_more = data['has_more']
                        elif 'next' in data and data['next']:
                            has_more = True
                        elif 'pagination' in data:
                            pag = data['pagination']
                            has_more = pag.get('has_more', False) or (
                                pag.get('current_page', 0) < pag.get('total_pages', 0)
                            )
                        elif isinstance(items, list) and len(items) == 0:
                            has_more = False
                        else:
                            # If we got data but no clear pagination info, try one more page
                            has_more = len(items) > 0 and page == 1
                        
                        if not has_more:
                            break
                    else:
                        all_data.append(data)
                        break
                else:
                    # Single page request
                    if 'data' in data and isinstance(data['data'], list):
                        all_data.extend(data['data'])
                    else:
                        all_data.append(data)
                    break
                    
            elif isinstance(data, list):
                all_data.extend(data)
                if not pagination:
                    break
            else:
                # Primitive type
                all_data.append({"value": data})
                break
            
            page += 1
            
            # Add delay between requests to be respectful
            if pagination and page <= max_pages:
                time.sleep(0.5)
        
        # Convert to DataFrame
        if all_data:
            if isinstance(all_data[0], dict):
                df = pd.json_normalize(all_data)
            else:
                df = pd.DataFrame([{"value": item} for item in all_data])
        else:
            df = pd.DataFrame([{"message": "No data returned from API"}])
        
        # Replace NaN with None for consistent handling
        df = df.where(pd.notna(df), None)
        
        endpoint_name = endpoint.split("/")[-1] or "api_response"
        print(f"Successfully extracted data from API: {endpoint}")
        print(f"Method: {method}, Pages: {page-1}, Shape: {df.shape}")
        
        return {
            "data": df.to_dict(orient="records"),
            "filename": f"{endpoint_name}_{method.lower()}.json",
            "endpoint": endpoint,
            "method": method,
            "pages_fetched": page - 1,
            "total_records": len(df)
        }
        
    except requests.RequestException as e:
        raise ValueError(f"API request failed for '{endpoint}': {e}")
    except Exception as e:
        raise ValueError(f"Error processing API response from '{endpoint}': {e}")