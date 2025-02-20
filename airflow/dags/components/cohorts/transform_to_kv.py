import pandas as pd
import numpy as np
from airflow.decorators import task

@task
def transform_to_kv(data: dict,
                    fixed_columns: list[str], 
                    measurement_columns: list[str]) -> dict:
    """Transforms a DataFrame into a key-value structure."""

    df = pd.DataFrame.from_dict(data["data"])
    print(f"Original df: {df}")
    df.columns = df.columns.str.strip()

    print(f"df[column]: {df[fixed_columns]}")
    print(f"df.reset_index: {df.reset_index(fixed_columns)}")
    df_headers = df.reindex(columns=fixed_columns)
    print(f"df_headers: {df_headers}")

    return None
    df_measures = df.reindex(measurement_columns)
    
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

    return {"data": df_output.to_dict(), "filename": data["filename"]}
    
