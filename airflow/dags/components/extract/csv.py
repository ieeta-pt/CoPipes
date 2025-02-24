import pandas as pd
import chardet
from typing import Dict
from airflow.decorators import task

@task
def extract_csv(filename: str, 
                file_sep: str = ',') -> Dict[dict, str]:
    """Load a CSV file into a DataFrame."""

    with open(filename, 'rb') as f:
        result = chardet.detect(f.read())
        f.close()
    
    df_read = pd.read_csv(
        filename, 
        na_values='null', 
        sep=file_sep, 
        dtype=str, 
        encoding=result['encoding']
    )

    df_read = df_read.where(pd.notna(df_read), None)

    data_file = filename.split("/")[-1]

    return {"data": df_read.to_dict(orient="records"), "filename": data_file}

