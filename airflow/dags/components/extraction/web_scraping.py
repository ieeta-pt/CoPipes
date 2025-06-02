import requests
import pandas as pd
from typing import Dict, Optional
from airflow.decorators import task
from bs4 import BeautifulSoup
import time
import re

@task
def web_scraping(url: str, css_selector: Optional[str] = None, xpath: Optional[str] = None,
                wait_time: int = 3, use_browser: bool = False) -> Dict[str, str]:
    """
    Scrape data from web pages.
    
    Args:
        url: Website URL to scrape
        css_selector: CSS selector for target elements
        xpath: XPath expression for target elements (basic support)
        wait_time: Seconds to wait for page load
        use_browser: Use headless browser for JavaScript content (limited implementation)
    
    Returns:
        Dictionary containing scraped data and metadata
    """
    try:
        # Add delay before request
        time.sleep(wait_time)
        
        # Set headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Make request
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract data based on selectors
        extracted_data = []
        
        if css_selector:
            # Use CSS selector
            elements = soup.select(css_selector)
            for i, element in enumerate(elements):
                data = _extract_element_data(element, i, 'css_selector')
                extracted_data.append(data)
                
        elif xpath:
            # Basic XPath support (convert to CSS selector where possible)
            css_equiv = _xpath_to_css(xpath)
            if css_equiv:
                elements = soup.select(css_equiv)
                for i, element in enumerate(elements):
                    data = _extract_element_data(element, i, 'xpath_converted')
                    extracted_data.append(data)
            else:
                # Fallback: extract all text content
                text_content = soup.get_text(strip=True)
                extracted_data.append({
                    'content': text_content,
                    'selector_type': 'xpath_fallback',
                    'element_index': 0
                })
        else:
            # No selector provided - extract common content
            extracted_data = _extract_common_content(soup)
        
        # Create DataFrame
        if extracted_data:
            df = pd.DataFrame(extracted_data)
        else:
            df = pd.DataFrame([{
                'content': 'No data extracted',
                'url': url,
                'message': 'No matching elements found'
            }])
        
        # Add URL to all records
        df['source_url'] = url
        
        # Replace NaN with None for consistent handling
        df = df.where(pd.notna(df), None)
        
        url_name = url.split("/")[-1] or url.split("://")[-1].split("/")[0]
        print(f"Successfully scraped data from: {url}")
        print(f"Elements found: {len(extracted_data)}, Shape: {df.shape}")
        
        return {
            "data": df.to_dict(orient="records"),
            "filename": f"scraped_{url_name}.csv",
            "source_url": url,
            "elements_found": len(extracted_data),
            "selector_used": css_selector or xpath or "auto"
        }
        
    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch webpage '{url}': {e}")
    except Exception as e:
        raise ValueError(f"Error scraping data from '{url}': {e}")

def _extract_element_data(element, index: int, selector_type: str) -> Dict[str, str]:
    """Extract comprehensive data from a BeautifulSoup element"""
    data = {
        'element_index': index,
        'selector_type': selector_type,
        'tag': element.name,
        'text': element.get_text(strip=True) if element.get_text(strip=True) else None
    }
    
    # Add attributes
    if element.attrs:
        for attr, value in element.attrs.items():
            if attr in ['href', 'src', 'alt', 'title', 'class', 'id']:
                if isinstance(value, list):
                    data[f'attr_{attr}'] = ' '.join(value)
                else:
                    data[f'attr_{attr}'] = value
    
    # Extract links
    links = element.find_all('a', href=True)
    if links:
        data['links'] = '; '.join([link['href'] for link in links[:5]])  # Limit to first 5
    
    # Extract images
    images = element.find_all('img', src=True)
    if images:
        data['images'] = '; '.join([img['src'] for img in images[:3]])  # Limit to first 3
    
    return data

def _extract_common_content(soup) -> list:
    """Extract common webpage content when no selector is provided"""
    extracted_data = []
    
    # Extract title
    title = soup.find('title')
    if title:
        extracted_data.append({
            'content_type': 'title',
            'text': title.get_text(strip=True),
            'tag': 'title',
            'element_index': 0
        })
    
    # Extract headings
    for i, heading in enumerate(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])):
        extracted_data.append({
            'content_type': 'heading',
            'text': heading.get_text(strip=True),
            'tag': heading.name,
            'element_index': i
        })
    
    # Extract paragraphs
    for i, paragraph in enumerate(soup.find_all('p')):
        text = paragraph.get_text(strip=True)
        if text and len(text) > 10:  # Only meaningful paragraphs
            extracted_data.append({
                'content_type': 'paragraph',
                'text': text,
                'tag': 'p',
                'element_index': i
            })
    
    # Extract lists
    for i, list_item in enumerate(soup.find_all('li')):
        text = list_item.get_text(strip=True)
        if text:
            extracted_data.append({
                'content_type': 'list_item',
                'text': text,
                'tag': 'li',
                'element_index': i
            })
    
    # Extract table data
    for i, table in enumerate(soup.find_all('table')):
        rows = table.find_all('tr')
        for j, row in enumerate(rows):
            cells = row.find_all(['td', 'th'])
            if cells:
                row_data = [cell.get_text(strip=True) for cell in cells]
                extracted_data.append({
                    'content_type': 'table_row',
                    'text': ' | '.join(row_data),
                    'tag': 'tr',
                    'element_index': f"{i}_{j}",
                    'table_index': i,
                    'row_index': j
                })
    
    return extracted_data

def _xpath_to_css(xpath: str) -> Optional[str]:
    """Convert basic XPath expressions to CSS selectors"""
    # Very basic XPath to CSS conversion
    # This is a simplified implementation
    
    xpath = xpath.strip()
    
    # Simple tag selection
    if xpath.startswith('//') and '[' not in xpath and '@' not in xpath:
        return xpath[2:]  # Remove // prefix
    
    # Element with attribute
    if xpath.startswith('//') and '[@' in xpath:
        match = re.match(r'//(\w+)\[@(\w+)="([^"]+)"\]', xpath)
        if match:
            tag, attr, value = match.groups()
            return f"{tag}[{attr}='{value}']"
    
    # Element with class
    if '[@class=' in xpath:
        match = re.match(r'//(\w+)\[@class="([^"]+)"\]', xpath)
        if match:
            tag, class_name = match.groups()
            return f"{tag}.{class_name.replace(' ', '.')}"
    
    # Element with id
    if '[@id=' in xpath:
        match = re.match(r'//(\w+)\[@id="([^"]+)"\]', xpath)
        if match:
            tag, id_name = match.groups()
            return f"{tag}#{id_name}"
    
    return None  # Cannot convert, will use fallback