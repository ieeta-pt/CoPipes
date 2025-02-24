import pandas as pd
from typing import Dict
from airflow.decorators import task

@task
def harmonize(data: dict, mappings: dict, args = None, adhoc_harmonization=None) -> Dict[dict, str]:
    df = pd.DataFrame.from_dict(data["data"])
    data_file = data["filename"]

    mappings_df = pd.DataFrame.from_dict(mappings["data"])

    harmonized_data = harmonize_data(df, data_file, mappings_df, args, adhoc_harmonization)

    harmonized_data = harmonized_data.where(pd.notna(harmonized_data), None)

    # final_stage(harmonized_data, args) 

    return {"data": harmonized_data.to_dict(orient="records"), "filename": data["filename"]}



def harmonize_data(data: pd.DataFrame, data_file: str, mappings: pd.DataFrame, args = None, adhoc_harmonization=None):
    data = filter_data(data)
    data = harmonize_variable_concept(data, data_file, mappings)
    data = harmonize_measure_concept(data, mappings)
    data = harmonize_measure_number(data)

    data = harmonize_measure_string(data)

    ## Ad hoc specific functions
    # data = harmonize_measure_adhoc(data, adhoc_harmonization)
    # patient_id_label = get_patient_id_label(file, args)
    # load_new_measures(data, patient_id_label, args, adhoc_harmonization)

    data = clean_empty_measure(data)
    return data


# def final_stage(data, data_file, dest_dir, file_sep, file_manager, args):
#     source_code = file.split(CSV_MARK)[1]
#     patient_id_label = get_patient_id_label(file, args)
#     data = calculate_new_measures(data, patient_id_label, args, adhoc_harmonization)
#     file_manager.toCsv(data, dest_dir, f"{CSV_MARK}{source_code}", file_sep)


def filter_data(data):
    return data[pd.notnull(data["Measure"])]


def harmonize_variable_concept(data, data_file, mappings):
    data_mapping = mappings[mappings["sourceCode"].str.contains(data_file)]
    data_mapping = data_mapping.reindex(columns=["sourceName", "targetConceptId"])
    mappings_list = data_mapping.to_dict('records')

    data = data.copy()
    data.loc[:, "VariableConcept"] = data["Variable"].map(
        lambda var: next(
            (m["targetConceptId"] for m in mappings_list if m["sourceName"].strip() == var.strip()), 
            None
        )
    )

    data["VariableConcept"] = data["VariableConcept"].where(pd.notna(data["VariableConcept"]), None)
    return data


def harmonize_measure_concept(data, mappings):
    filtered_mapping = mappings[~mappings["sourceCode"].str.contains(".csv")]
    filtered_mapping = filtered_mapping.reindex(columns=["sourceCode", "sourceName", "targetConceptId"])

    key_mapping_series = filtered_mapping[["sourceCode", "sourceName"]].apply(tuple, axis=1)
    key_mapping = pd.concat([key_mapping_series, filtered_mapping["targetConceptId"]], axis=1)
    key_mapping = key_mapping.rename(columns={0: 'source'})
    key_mapping = key_mapping.set_index("source")["targetConceptId"].to_dict()

    data["MeasureConcept"] = data[["Variable", "Measure"]].apply(tuple, axis=1).map(key_mapping)
    return data


def harmonize_measure_number(data):
    data["MeasureNumber"] = data["Measure"].astype(str).str.replace(",", ".")
    data["MeasureNumber"] = pd.to_numeric(data["MeasureNumber"], errors='coerce')

    data["MeasureNumber"] = data["MeasureNumber"].astype(object)
    data.loc[data["MeasureConcept"].notnull(), "MeasureNumber"] = None
    
    return data


def harmonize_measure_string(data):
    data["MeasureString"] = data["Measure"]
    data.loc[data["MeasureConcept"].notnull() | data["MeasureNumber"].notnull(), "MeasureString"] = None
    return data


def harmonize_measure_adhoc(data, adhoc_harmonization):
    if adhoc_harmonization:
        output_data = [adhoc_harmonization.harmonizer(row) for row in data.to_dict('records')]
        if hasattr(adhoc_harmonization, "addMissingRows"):
            output_data += adhoc_harmonization.addMissingRows()
        data = pd.DataFrame(output_data)
    return data


def clean_empty_measure(data):
    data = data[data["MeasureString"] != "n.a."]
    return data.dropna(how='all', subset=["MeasureConcept", "MeasureNumber", "MeasureString"])


# def load_new_measures(data, patient_id_label, args, adhoc_harmonization):
#     if args.adhocmethods:
#         sah = StandardAdHoc(adhoc_harmonization.cutOff if adhoc_harmonization else None)
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
