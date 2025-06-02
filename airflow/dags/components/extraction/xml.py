import os
import json
import requests
import pandas as pd
from typing import Dict, Optional
from airflow.decorators import task
import xml.etree.ElementTree as ET
from lxml import etree, html

UPLOAD_DIR = "/shared_data/"

@task
def xml_extract(source: str, xpath: Optional[str] = None, namespaces: Optional[str] = None) -> Dict[str, str]:
    """
    Extract data from XML file or URL.
    
    Args:
        source: XML file path or URL
        xpath: XPath expression to extract specific elements
        namespaces: XML namespaces in JSON format (e.g., {"ns": "http://example.com"})
    
    Returns:
        Dictionary containing extracted data and metadata
    """
    try:
        # Parse namespaces if provided
        ns_dict = {}
        if namespaces:
            try:
                ns_dict = json.loads(namespaces)
            except json.JSONDecodeError:
                print(f"Warning: Invalid namespaces JSON format: {namespaces}")
        
        # Determine if source is a URL or file path
        if source.startswith(('http://', 'https://')):
            # Fetch from URL
            response = requests.get(source, timeout=30)
            response.raise_for_status()
            xml_content = response.content
            source_type = "url"
            source_name = source.split("/")[-1] or "xml_response"
        else:
            # Read from file
            file_path = os.path.join(UPLOAD_DIR, source) if not source.startswith('/') else source
            with open(file_path, 'rb') as f:
                xml_content = f.read()
            source_type = "file"
            source_name = os.path.basename(source)
        
        # Parse XML content
        try:
            # Try lxml first for better XPath support
            root = etree.fromstring(xml_content)
            use_lxml = True
        except:
            # Fallback to ElementTree
            root = ET.fromstring(xml_content.decode('utf-8'))
            use_lxml = False
        
        # Extract data using XPath if provided
        if xpath:
            try:
                if use_lxml:
                    elements = root.xpath(xpath, namespaces=ns_dict)
                else:
                    # ElementTree has limited XPath support
                    elements = root.findall(xpath, ns_dict)
            except Exception as e:
                print(f"Warning: XPath expression failed '{xpath}': {e}")
                elements = [root]  # Use root element as fallback
        else:
            # Extract all child elements if no XPath provided
            if use_lxml:
                elements = root.xpath(".//*[not(*)]")  # All leaf elements
            else:
                elements = list(root.iter())
        
        # Convert elements to structured data
        records = []
        
        def element_to_dict(elem):
            """Convert XML element to dictionary"""
            result = {}
            
            # Add element tag and text
            if use_lxml:
                tag = etree.QName(elem).localname if elem.tag else 'element'
                text = elem.text.strip() if elem.text else None
            else:
                tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                text = elem.text.strip() if elem.text else None
            
            result['tag'] = tag
            if text:
                result['text'] = text
            
            # Add attributes
            if elem.attrib:
                for key, value in elem.attrib.items():
                    attr_key = key.split('}')[-1] if '}' in key else key
                    result[f"@{attr_key}"] = value
            
            # Add child elements (non-recursive for flat structure)
            for child in elem:
                if use_lxml:
                    child_tag = etree.QName(child).localname if child.tag else 'child'
                    child_text = child.text.strip() if child.text else None
                else:
                    child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                    child_text = child.text.strip() if child.text else None
                
                if child_text:
                    result[child_tag] = child_text
            
            return result
        
        # Process elements
        if isinstance(elements, list):
            for elem in elements:
                if hasattr(elem, 'tag'):  # Valid XML element
                    record = element_to_dict(elem)
                    if any(v for v in record.values() if v):  # Only add non-empty records
                        records.append(record)
        else:
            # Single element
            if hasattr(elements, 'tag'):
                record = element_to_dict(elements)
                if any(v for v in record.values() if v):
                    records.append(record)
        
        # Create DataFrame
        if records:
            df = pd.DataFrame(records)
        else:
            # Create minimal DataFrame if no data extracted
            df = pd.DataFrame([{'tag': 'root', 'text': 'No data extracted'}])
        
        # Replace NaN with None for consistent handling
        df = df.where(pd.notna(df), None)
        
        print(f"Successfully extracted XML data from {source_type}: {source_name}")
        print(f"Shape: {df.shape}, Columns: {df.columns.tolist()}")
        
        return {
            "data": df.to_dict(orient="records"),
            "filename": source_name,
            "source_type": source_type
        }
        
    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch XML from URL '{source}': {e}")
    except FileNotFoundError:
        raise ValueError(f"XML file not found: {source}")
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML format in '{source}': {e}")
    except Exception as e:
        raise ValueError(f"Error processing XML data from '{source}': {e}")