import pandas as pd
import numpy as np
import chardet
from airflow.decorators import task

@task
def transform_csv(csv_filename: str, 
                  fixed_columns: list[str], 
                  measurement_columns: list[str], 
                  cohort_sep: str = ',') -> pd.DataFrame:
    """Transforms a CSV file into a key-value structure."""

    # Detect encoding
    with open(csv_filename, 'rb') as f:
        result = chardet.detect(f.read())
    
    df_read = pd.read_csv(
        csv_filename, 
        na_values='null', 
        sep=cohort_sep, 
        dtype=str, 
        encoding=result['encoding']
    )

    df_read.columns = df_read.columns.str.strip()

    df_headers = df_read[fixed_columns]
    df_measures = df_read[measurement_columns]
    
    # Repeat static columns for each measurement
    df_processed = pd.DataFrame(
        np.repeat(df_headers.values, len(measurement_columns), axis=0),
        columns=df_headers.columns
    )
    
    # Convert matrix to key-value DataFrame
    list_dict_measures = df_measures.to_dict(orient='records')
    df_kv_measures = pd.DataFrame(
        [(i, j) for row in list_dict_measures for i, j in row.items()],
        columns=["Variable", "Measure"]
    )

    # Merge data
    df_output = df_processed.reset_index(drop=True).merge(
        df_kv_measures.reset_index(drop=True), 
        left_index=True, right_index=True
    )

    return df_output
    
