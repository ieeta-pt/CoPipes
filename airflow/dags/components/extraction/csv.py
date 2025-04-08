import os
import pandas as pd
import chardet
import unicodedata
from typing import Dict
from airflow.decorators import task

UPLOAD_DIR = "/shared_data/"

@task
def csv(filename: str, file_sep: str = ',') -> Dict[dict, str]:
    """
    Load a CSV file into a DataFrame with robust handling of character encodings.
    Specifically handles special characters like umlauts (ä, ö, ü).
    """

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file = os.path.join(UPLOAD_DIR, filename)
    # First try to detect the encoding
    with open(file, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        print(f"Detected encoding: {result['encoding']} with confidence: {result['confidence']}")
    
    # Try these encodings in order
    encodings_to_try = ['utf-8-sig', 'utf-8', result['encoding'], 'ISO-8859-1', 'latin1', 'cp1252']
    
    # Try each encoding until one works
    for encoding in encodings_to_try:
        try:
            print(f"Attempting to read with encoding: {encoding}")
            df_read = pd.read_csv(
                file,
                na_values='null',
                sep=file_sep,
                dtype=str,
                encoding=encoding
            )
            
            # If we get here, the encoding worked
            print(f"Successfully read CSV with encoding: {encoding}")
            
            # Normalize column names to handle special characters
            df_read.columns = df_read.columns.astype(str)
            df_read.columns = [unicodedata.normalize('NFKC', col) for col in df_read.columns]
            
            # Print column names to verify
            print("CSV Columns after normalization:", df_read.columns.tolist())
            
            # Check if 'Folsäure' is properly encoded
            problem_columns = [col for col in df_read.columns if 'Fols' in col]
            if problem_columns:
                print(f"Found potentially problematic columns: {problem_columns}")
            
            # Replace NaN with None for consistent handling
            df_read = df_read.where(pd.notna(df_read), None)
            
            data_file = filename.split("/")[-1]
            return {"data": df_read.to_dict(orient="records"), "filename": data_file}
        
        except UnicodeDecodeError as e:
            print(f"Failed with encoding {encoding}: {e}")
            continue
    
    # If we get here, none of the encodings worked
    raise ValueError(f"Unable to read CSV file with any of the attempted encodings: {encodings_to_try}")