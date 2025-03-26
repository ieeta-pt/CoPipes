import pandas as pd
from typing import Dict
from airflow.decorators import task
import components.cohorts.ad_hoc as ad_hoc

@task
def harmonize(data: dict, mappings: dict, adhoc_harmonization: bool = False) -> Dict[dict, str]:
    print(f"\nHarmonizing {data['filename']}\n")

    df = pd.DataFrame.from_dict(data["data"])
    data_file = data["filename"]

    mappings_df = pd.DataFrame.from_dict(mappings["data"])

    harmonized_data = harmonize_data(df, data_file, mappings_df, adhoc_harmonization)

    # harmonized_data = harmonized_data.where(pd.notna(harmonized_data), None)

    # final_stage(harmonized_data, args) 

    harmonized_data = harmonized_data.to_dict(orient="records")
    harmonized_data = replace_nan_with_none(harmonized_data)

    return {"data": harmonized_data, "filename": data["filename"]}



def harmonize_data(data: pd.DataFrame, data_file: str, mappings: pd.DataFrame, adhoc_harmonization: bool = False):
    data = filter_data(data)
    data = harmonize_variable_concept(data, data_file, mappings)
    data = harmonize_measure_concept(data, mappings)
    data = harmonize_measure_number(data)
    data = harmonize_measure_string(data)
    # Ad hoc specific functions
    if adhoc_harmonization:
        data = harmonize_measure_adhoc(data)

    patient_id_label = "Patient ID"
    # load_new_measures(data, patient_id_label, adhoc_harmonization)
    data = clean_empty_measure(data)
    return data


# def final_stage(data, data_file, dest_dir, file_sep, file_manager, args):
#     source_code = file.split(CSV_MARK)[1]
#     patient_id_label = get_patient_id_label(file, args)
#     data = calculate_new_measures(data, patient_id_label, args, adhoc_harmonization)
#     file_manager.toCsv(data, dest_dir, f"{CSV_MARK}{source_code}", file_sep)


def filter_data(data):
    return data[pd.notnull(data["Measure"])]


def harmonize_variable_concept(data: pd.DataFrame, data_file: str, mappings: pd.DataFrame) -> pd.DataFrame:
    # Filter the mappings for the given file
    data_mapping = mappings[mappings["sourceCode"].str.contains(data_file, na=False)]
    data_mapping = data_mapping.reindex(columns=["sourceName", "conceptId"])

    # Build lookup dictionary
    lookup = {
        row["sourceName"].strip(): row["conceptId"]
        for _, row in data_mapping.iterrows()
    }

    # Copy input to avoid mutation
    df = data.copy()

    # Apply mapping logic row by row
    def map_variable(row):
        var = row.get("Variable", "")
        concept_id = lookup.get(var.strip())
        if concept_id is None:
            row["VariableConcept"] = None  # no mapping found
            return row
        elif concept_id != '0':
            row["VariableConcept"] = concept_id
            return row
        else:
            return None  # skip rows where conceptId == '0'

    # Map each row, filter out None results
    mapped_rows = [map_variable(row) for _, row in df.iterrows()]
    filtered_rows = [row for row in mapped_rows if row is not None]

    # Rebuild final DataFrame
    result_df = pd.DataFrame(filtered_rows)

    # Ensure VariableConcept column is always present
    if "VariableConcept" not in result_df.columns:
        result_df["VariableConcept"] = None

    return result_df




def harmonize_measure_concept(data, mappings):
    filtered_mapping = mappings[~mappings["sourceCode"].str.contains(".csv")]
    filtered_mapping = filtered_mapping.reindex(columns=["sourceCode", "sourceName", "conceptId"])

    key_mapping_series = filtered_mapping[["sourceCode", "sourceName"]].apply(tuple, axis=1)
    key_mapping = pd.concat([key_mapping_series, filtered_mapping["conceptId"]], axis=1)
    key_mapping = key_mapping.rename(columns={0: 'source'})
    key_mapping = key_mapping.set_index("source")["conceptId"].to_dict()

    data["MeasureConcept"] = data[["Variable", "Measure"]].apply(tuple, axis=1).map(key_mapping)
    return data


def harmonize_measure_number(data):
    data["MeasureNumber"] = data["Measure"].astype(str).str.replace(",", ".")
    data["MeasureNumber"] = pd.to_numeric(data["MeasureNumber"], errors='coerce')

    data["MeasureNumber"] = data["MeasureNumber"].astype(object)
    data.loc[data["MeasureConcept"].notna(), "MeasureNumber"] = None

    return data


def harmonize_measure_string(data):
    data["MeasureString"] = data["Measure"]
    data.loc[data["MeasureConcept"].notnull() | data["MeasureNumber"].notnull(), "MeasureString"] = None
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


# def load_new_measures(data, patient_id_label, adhoc_harmonization):
#     data_dict = data.to_dict(orient='records')
#     if adhoc_harmonization:
#         sah = ad_hoc.cutOff()
#         sah.definePatientIDLabel(patient_id_label)
#         sah.processLoadingStage(data.to_dict('records'))




# def calculate_new_measures(data, patient_id_label, args, adhoc_harmonization):
#     if args.adhocmethods:
#         sah = StandardAdHoc(adhoc_harmonization.cutOff if adhoc_harmonization else None)
#         sah.definePatientIDLabel(patient_id_label)
#         return pd.DataFrame(sah.processCalculationAndAppendingStage(data.to_dict('records')))
#     return data


# def get_patient_id_label(file, args):
#     file_name = file.split(CSV_MARK)[1].replace(" ", "_")
#     return args.settings["patient_ids"].get(file_name, "").strip('"')

def replace_nan_with_none(obj):
    if isinstance(obj, dict):
        return {k: replace_nan_with_none(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_nan_with_none(item) for item in obj]
    elif isinstance(obj, float) and pd.isna(obj):
        return None
    else:
        return obj