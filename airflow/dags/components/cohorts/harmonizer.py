from glob import glob
import pandas as pd
from airflow.decorators import task

@task
def harmonize(data: dict, mappings: dict, args = None, adhoc_harmonization=None):
    df = pd.DataFrame.from_dict(data["data"])
    data_file = data["filename"]

    mappings_df = pd.DataFrame.from_dict(mappings["data"])

    harmonized_data = harmonize_data(df, data_file, mappings_df, args, adhoc_harmonization)

    final_stage(harmonized_data, args)


def harmonize_data(data: pd.DataFrame, data_file: str, mappings: pd.DataFrame, args = None, adhoc_harmonization=None):
    data = filter_data(data)
    data = harmonize_variable_concept(data, data_file, mappings)
    data = harmonize_measure_concept(data, file_manager)
    data = harmonize_measure_number(data)
    data = harmonize_measure_string(data)
    data = harmonize_measure_adhoc(data, adhoc_harmonization)

    patient_id_label = get_patient_id_label(file, args)
    load_new_measures(data, patient_id_label, args, adhoc_harmonization)
    data = clean_empty_measure(data)
    return data


def final_stage(data, file, dest_dir, file_sep, file_manager, args):
    source_code = file.split(CSV_MARK)[1]
    patient_id_label = get_patient_id_label(file, args)
    data = calculate_new_measures(data, patient_id_label, args, adhoc_harmonization)
    file_manager.toCsv(data, dest_dir, f"{CSV_MARK}{source_code}", file_sep)


def filter_data(data):
    return data[pd.notnull(data["Measure"])]


def harmonize_variable_concept(data, data_file, mappings):
    
    data_mapping = file_manager.getContentMappingBySourceCode(source_code) # usa o título do file para selecionar as respetivas linhas
    data_mapping = data_mapping.reindex(columns=["sourceName", "targetConceptId"])
    mapping_list = data_mapping.to_dict('records')
    
    data["VariableConcept"] = data["Variable"].map(lambda var: next((m["targetConceptId"] for m in mapping_list if m["sourceName"].strip() == var.strip()), None))
    return data


def harmonize_measure_concept(data, file_manager):
    data["MeasureConcept"] = data[["Variable", "Measure"]].apply(tuple, axis=1).map(file_manager.contentMapping)
    return data


def harmonize_measure_number(data):
    data["MeasureNumber"] = data["Measure"].astype(str).str.replace(",", ".")
    data["MeasureNumber"] = pd.to_numeric(data["MeasureNumber"], errors='coerce')
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


def load_new_measures(data, patient_id_label, args, adhoc_harmonization):
    if args.adhocmethods:
        sah = StandardAdHoc(adhoc_harmonization.cutOff if adhoc_harmonization else None)
        sah.definePatientIDLabel(patient_id_label)
        sah.processLoadingStage(data.to_dict('records'))


def clean_empty_measure(data):
    data = data[data["MeasureString"] != "n.a."]
    return data.dropna(how='all', subset=["MeasureConcept", "MeasureNumber", "MeasureString"])


def calculate_new_measures(data, patient_id_label, args, adhoc_harmonization):
    if args.adhocmethods:
        sah = StandardAdHoc(adhoc_harmonization.cutOff if adhoc_harmonization else None)
        sah.definePatientIDLabel(patient_id_label)
        return pd.DataFrame(sah.processCalculationAndAppendingStage(data.to_dict('records')))
    return data


def get_patient_id_label(file, args):
    file_name = file.split(CSV_MARK)[1].replace(" ", "_")
    return args.settings["patient_ids"].get(file_name, "").strip('"')
