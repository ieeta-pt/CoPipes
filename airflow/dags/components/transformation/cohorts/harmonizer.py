import pandas as pd
from typing import Dict
from airflow.decorators import task
import components.utils.cohorts.ad_hoc as ad_hoc

@task
def harmonize(data: dict, mappings: dict, adhoc_harmonization: bool = False) -> Dict[dict, str]:
    print(f"\nHarmonizing {data['filename']}\n")

    df = pd.DataFrame.from_dict(data["data"])
    data_file = data["filename"]

    mappings_df = pd.DataFrame.from_dict(mappings["data"])

    harmonized_data = harmonize_data(df, data_file, mappings_df, adhoc_harmonization)

    harmonized_data = harmonized_data.to_dict(orient="records")
    harmonized_data = replace_nan_with_none(harmonized_data)

    return {"data": harmonized_data, "filename": data["filename"]}


def harmonize_data(data: pd.DataFrame, data_file: str, mappings: pd.DataFrame, adhoc_harmonization: bool = False):
    data = filter_data(data)
    data = harmonize_variable_concept(data, data_file, mappings)
    data = harmonize_measure_concept(data, mappings, data_file)
    data = harmonize_measure_number(data)
    data = harmonize_measure_string(data)
    # Ad hoc specific functions
    if adhoc_harmonization:
        data = harmonize_measure_adhoc(data)

    # data = clean_empty_measure(data)
    return data

def filter_data(data):
    return data[pd.notnull(data["Measure"])]


def harmonize_variable_concept(data: pd.DataFrame, data_file: str, mappings: pd.DataFrame) -> pd.DataFrame:
    df_mapping = get_content_mapping_by_file(mappings, data_file)
    df_mapping = df_mapping.reindex(columns=["sourceName", "targetConceptId"])

    mappings_list = df_mapping.to_dict(orient="records")
    data_dict = data.to_dict(orient="records")
    output_data = []

    for row in data_dict:
        added = False
        for mapping in mappings_list:
            if mapping["sourceName"].strip() == row["Variable"].strip():
                temp_row = row.copy()
                temp_row["VariableConcept"] = mapping["targetConceptId"]
                if mapping["targetConceptId"] != '0':
                    output_data.append(temp_row)
                added = True
        if not added:
            output_data.append(row)

    result = pd.DataFrame(output_data, columns=data.columns.to_list() + ["VariableConcept"])
    return result

def get_content_mapping_by_file(mappings: pd.DataFrame, data_file: str) -> pd.DataFrame:
    if not mappings.empty:
        filtered_mapping = mappings[mappings["sourceCode"].str.contains(data_file)]
        return filtered_mapping[["sourceCode", "sourceName", "targetConceptId"]]
    return None


def harmonize_measure_concept(data: pd.DataFrame, mappings: pd.DataFrame, fname: str) -> pd.DataFrame:
    df_mapping = get_content_mapping(mappings, fname)
    key_mapping_series = df_mapping[["sourceCode", "sourceName"]].apply(tuple, axis=1)
    key_mapping = pd.concat([key_mapping_series, df_mapping["targetConceptId"]], axis=1)
    key_mapping = key_mapping.rename(columns={0: 'source'})
    content_mapping = key_mapping.set_index("source")["targetConceptId"].to_dict()

    data["MeasureConcept"] = data[["Variable", "Measure"]].apply(tuple, axis=1).map(content_mapping)
    return data

def get_content_mapping(mappings: pd.DataFrame, fname: str) -> pd.DataFrame:
    if not mappings.empty:
        filtered_mapping = mappings 
        filtered_mapping = filtered_mapping[~filtered_mapping["sourceCode"].str.contains(fname)]
        return filtered_mapping[["sourceCode", "sourceName", "targetConceptId"]]
    return None


def harmonize_measure_number(data):
    data["MeasureNumber"] = data["Measure"]
    data["MeasureNumber"] = data["MeasureNumber"].astype(str).str.replace(",", ".")
    data["MeasureNumber"] = pd.to_numeric(data["MeasureNumber"], errors='coerce')

    data["MeasureNumber"] = data["MeasureNumber"][data["MeasureConcept"].isnull()]
    return data

def harmonize_measure_string(data):
    data["MeasureString"] = data["Measure"]
    data["MeasureString"] = data["MeasureString"][data["MeasureConcept"].isnull()]
    data["MeasureString"] = data["MeasureString"][data["MeasureNumber"].isnull()]
    return data

def harmonize_measure_adhoc(data):
    data_dict = data.to_dict('records')
    output_data = []
    for row in data_dict:
        harmonized_data = ad_hoc.harmonizer(row)
        if isinstance(harmonized_data, list):
            output_data += harmonized_data
        else:
            output_data += [harmonized_data]
    if hasattr(ad_hoc, "add_missing_rows"):
        output_data += ad_hoc.add_missing_rows()
    return pd.DataFrame(output_data, columns=data.columns.values)

def clean_empty_measure(data):
    data = data[data["MeasureString"] != "n.a."]
    return data.dropna(how='all', subset=["MeasureConcept", "MeasureNumber", "MeasureString"])

def replace_nan_with_none(obj):
    if isinstance(obj, dict):
        return {k: replace_nan_with_none(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_nan_with_none(item) for item in obj]
    elif isinstance(obj, float) and pd.isna(obj):
        return None
    else:
        return obj