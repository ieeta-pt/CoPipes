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
    
    df_read = pd.read_csv(
        filename, 
        na_values='null', 
        sep=file_sep, 
        dtype=str, 
        encoding=result['encoding']
    )

    # print("CSV Columns:", df_read.columns.tolist())

    # # df_read.columns = [col.encode('ISO-8859-1').decode('utf-8', 'ignore') for col in df_read.columns]
    # df_read.columns = df_read.columns.str.encode('latin1').str.decode('utf-8', errors='ignore')
    # df_read.columns = df_read.columns.str.strip().str.normalize("NFKC")

    # print("CSV Columns:", df_read.columns.tolist())

    df_read = df_read.where(pd.notna(df_read), None)

    data_file = filename.split("/")[-1]

    return {"data": df_read.to_dict(orient="records"), "filename": data_file}

