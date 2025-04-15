import pandas as pd
import numpy as np
from typing import Dict
from airflow.decorators import task

HEADERS_FILE = "/opt/airflow/data/input_data/4_Content_Organized/headers.txt"
MEASURES_FILE = "/opt/airflow/data/input_data/4_Content_Organized/measures.txt"

@task
def to_key_value(data: dict,
                    fixed_columns: list[str] = None, 
                    measurement_columns: list[str] = None) -> Dict[dict, str]:
    """Transforms a DataFrame into a key-value structure."""

    file = data["filename"]

    if not (fixed_columns or measurement_columns):
        column_mappings = parse_column_files(HEADERS_FILE, MEASURES_FILE)

        fixed_columns = column_mappings[file]["fixed_columns"]
        measurement_columns = column_mappings[file]["measurement_columns"]

    df = pd.DataFrame(data["data"])
    df.columns = df.columns.str.strip()

    df_headers = df[fixed_columns]
    df_measures = df[measurement_columns]

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

    return {"data": df_output.to_dict(orient="records"), "filename": data["filename"]}
    
##### UTILS FUNCTIONS #####

def parse_column_files(headers_path, measures_path):
    """Parse the .txt files to extract fixed and measurement columns for each file."""
    column_mappings = {}

    with open(headers_path, "r") as headers, open(measures_path, "r") as measures:
        for line in headers:
            file_name, columns = line.strip().split("=")
            columns = columns.split("\t")
            column_mappings[file_name] = {"fixed_columns" : [col.strip() for col in columns]}


        for line in measures:
            file_name, columns = line.strip().split("=")
            if file_name in column_mappings:
                columns = columns.split("\t")
                column_mappings[file_name]["measurement_columns"] = [col.strip() for col in columns]

    return column_mappings
