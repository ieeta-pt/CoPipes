import pandas as pd
import logging
from typing import Dict, Optional, Union
from airflow.decorators import task
import components.utils.cohorts.ad_hoc as ad_hoc
from components.extraction.csv import csv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task
def harmonize(
    data: Dict, 
    mappings: Union[Dict, str],
    adhoc_harmonization: bool = False,
    source_column: str = "Variable",
    measure_column: str = "Measure",
    identifier_columns: Optional[list] = None,
    **context
) -> Dict:
    """
    Harmonize data using configurable mapping rules.
    
    Args:
        data: Input data dictionary with 'data' key containing records
        mappings: Mapping dictionary or file path to mapping CSV
        adhoc_harmonization: Whether to apply domain-specific ad-hoc harmonization
        source_column: Name of the column containing source variable names
        measure_column: Name of the column containing measurements
        identifier_columns: List of columns that identify unique records
        **context: Airflow context
    
    Returns:
        Dict containing harmonized data
    """
    logger.info(f"Harmonizing data from {data.get('filename', 'unknown source')}")

    # Load mappings if provided as file path
    if isinstance(mappings, str):
        logger.info(f"Loading mappings from file: {mappings}")
        mappings = csv(mappings)

    if not data or 'data' not in data:
        logger.error("No valid data received for harmonization.")
        raise ValueError("No valid data received for harmonization.")

    df = pd.DataFrame.from_dict(data["data"])
    data_file = data.get("filename", "unknown")
    
    logger.info(f"Processing {len(df)} records for harmonization")

    if not mappings or 'data' not in mappings:
        logger.warning("No mappings provided, returning original data")
        return data

    mappings_df = pd.DataFrame.from_dict(mappings["data"])
    logger.info(f"Using {len(mappings_df)} mapping rules")

    # Auto-detect identifier columns if not provided
    if identifier_columns is None:
        # Assume columns other than source and measure are identifiers
        all_columns = set(df.columns)
        identifier_columns = list(all_columns - {source_column, measure_column})
        logger.info(f"Auto-detected identifier columns: {identifier_columns}")

    harmonized_data = harmonize_data(
        df, data_file, mappings_df, adhoc_harmonization,
        source_column, measure_column, identifier_columns
    )

    harmonized_data = harmonized_data.to_dict(orient="records")
    harmonized_data = replace_nan_with_none(harmonized_data)

    logger.info(f"Harmonization completed: {len(harmonized_data)} records")
    
    return {
        "data": harmonized_data, 
        "filename": data.get("filename", "unknown"),
        "mappings_applied": len(mappings_df),
        "adhoc_harmonization": adhoc_harmonization
    }


def harmonize_data(
    data: pd.DataFrame, 
    data_file: str, 
    mappings: pd.DataFrame, 
    adhoc_harmonization: bool = False,
    source_column: str = "Variable",
    measure_column: str = "Measure",
    identifier_columns: list = None
):
    """Apply harmonization transformations to the data"""
    data = filter_data(data, measure_column)
    data = harmonize_variable_concept(data, data_file, mappings, source_column)
    data = harmonize_measure_concept(data, mappings, data_file, measure_column)
    data = harmonize_measure_number(data, measure_column)
    data = harmonize_measure_string(data, measure_column)
    # Ad hoc specific functions
    if adhoc_harmonization:
        data = harmonize_measure_adhoc(data, measure_column)

    # data = clean_empty_measure(data)
    return data

def filter_data(data, measure_column="Measure"):
    """Filter out rows with null measures"""
    return data[pd.notnull(data[measure_column])]


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