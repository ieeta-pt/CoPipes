import pandas as pd
import chardet
from airflow.decorators import task

@task
def extract_csv(filename: str, 
                file_sep: str = ',') -> dict:
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

    data_file = filename.split("/")[-1].split(".")[0]

    return {"data": df_read.to_dict(), "filename": data_file}

