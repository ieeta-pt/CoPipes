import pandas as pd
from dateutil import parser, relativedelta
from datetime import datetime
import math
import components.cohorts.ad_hoc as ad_hoc
import components.cohorts.sah_constants as sahc
from airflow.decorators import task
from airflow.utils.log.logging_mixin import LoggingMixin

COLUMNS_PERSON = [
            'person_id',
            'gender_concept_id',
            'year_of_birth',
            'month_of_birth',
            'day_of_birth',
    		'birth_datetime',
            'death_datetime',
            'race_concept_id',
            'ethnicity_concept_id',
            'location_id',
    		'provider_id',
            'care_site_id',
            'person_source_value',
            'gender_source_value',
            'gender_source_concept_id',
    		'race_source_value',
            'race_source_concept_id',
            'ethnicity_source_value',
            'ethnicity_source_concept_id'
        ]

COLUMNS_OBSERVATION = [
            'observation_id',
            'person_id',
            'observation_concept_id',
            'observation_date',
            'observation_datetime',
            'observation_type_concept_id',
            'value_as_number',
            'value_as_string',
            'value_as_concept_id',
            'unit_concept_id',
            'provider_id',
            'visit_occurrence_id',
            'visit_detail_id',
            'observation_source_value',
            'observation_source_concept_id',
            'unit_source_value',
            'qualifier_source_value'
        ]

PATIENT_IDS = {}
OBSERVATION_ID = 0
OBSERVATION_ID_SET = []

logger = LoggingMixin().log

@task
def migrate(person_data: list[dict], observation_data: list[dict], mappings: dict, adhoc_migration: bool = False) -> dict:
    mappings_df = pd.DataFrame.from_dict(mappings["data"])

    df_person = None
    f_person = None

    for d in person_data:
        if d["filename"].lower().find("patient") != -1:
            df_person = pd.DataFrame(d["data"])
            f_person = d["filename"]
            break

    person_data = migrate_person(df_person, f_person, mappings_df, adhoc_migration)

    person_dict = person_data.to_dict(orient="records")
    person_clean = replace_nan_with_none(person_dict)

    observations = []
    for d in observation_data:
        df = pd.DataFrame(d["data"])
        fname = d["filename"]
        observations += [migrate_observation(df, fname, mappings_df, adhoc_migration)]

    observation_result = pd.concat(observations)
    observation_dict = observation_result.to_dict(orient="records")
    observation_clean = replace_nan_with_none(observation_dict)
    
    return {"person": person_clean, "observation": observation_clean}


def migrate_person(df: pd.DataFrame, filename: str, mappings: pd.DataFrame, adhoc_migration: bool = False):
    domain = "person"
    columns, columns_mapping = get_columns_mapping(filename, domain, mappings)
    df = df.reindex(columns=columns)
    
    if adhoc_migration: df = cohort_filter(df, domain)

    result = populate(df, domain, columns_mapping)
    return result


def migrate_observation(df: pd.DataFrame, filename: str, mappings: pd.DataFrame, adhoc_migration: bool = False) -> dict:
    global OBSERVATION_ID, OBSERVATION_ID_SET
    domain = "observation"
    
    columns, columns_mapping = get_columns_mapping(filename, domain, mappings)
    columns += ["Variable", "Measure", "VariableConcept", "MeasureConcept", "MeasureString", "MeasureNumber", "VisitConcept"]

    columns_mapping["observation_source_value"] = "Variable"
    columns_mapping["qualifier_source_value"] = "Measure"
    columns_mapping["observation_concept_id"] = "VariableConcept" 
    columns_mapping["value_as_concept_id"] = "MeasureConcept"
    columns_mapping["value_as_string"] = "MeasureString" 
    columns_mapping["value_as_number"] = "MeasureNumber" 
    columns_mapping["observation_type_concept_id"] = "VisitConcept"

    df = calculate_visit_concepts(df, columns_mapping)
    df = df.reindex(columns=columns)

    if adhoc_migration: df = cohort_filter(df, domain)

    OBSERVATION_ID_SET = range(OBSERVATION_ID, OBSERVATION_ID + len(df))
    OBSERVATION_ID += len(df)

    result = populate(df, domain, columns_mapping)
    
    return result

def calculate_visit_concepts(cohort_df, columns_mapping, base_visit_code="2100000000", visit_prefix="21000000", max_months=40):
    df = cohort_df.copy()
    df["VisitConcept"] = pd.Series(base_visit_code)

    patient_col = columns_mapping["person_id"].strip()
    date_col = columns_mapping["observation_date"].strip()

    # Step 1: Get the earliest observation date per patient
    earliest_dates = {}

    for _, row in df.iterrows():
        patient_id = row[patient_col]
        date = row[date_col]

        if isinstance(date, float) and math.isnan(date) or not date:
            continue

        if patient_id in earliest_dates:
            norm_0 = __parse_to_standard_format(earliest_dates[patient_id])
            norm_1 = __parse_to_standard_format(date)

            d0 = datetime.strptime(norm_0, sahc.DATE_FORMAT)
            d1 = datetime.strptime(norm_1, sahc.DATE_FORMAT)

            r = relativedelta.relativedelta(d1, d0)

            if (r.years * 12) + r.months < 0:
                earliest_dates[patient_id] = date
        else:
            earliest_dates[patient_id] = date

    # Step 2: Calculate months and assign VisitConcept
    result_rows = []

    for _, row in df.iterrows():
        patient_id = row[patient_col]
        date = row[date_col]

        if isinstance(date, float) and math.isnan(date) or not date:
            row["VisitConcept"] = base_visit_code
            result_rows.append(row)
            continue

        norm_0 = __parse_to_standard_format(earliest_dates[patient_id])
        norm_1 = __parse_to_standard_format(date)
        
        d0 = datetime.strptime(norm_0, sahc.DATE_FORMAT)
        d1 = datetime.strptime(norm_1, sahc.DATE_FORMAT)
        
        r = relativedelta.relativedelta(d1, d0)
        months_diff = round((r.years * 12 + r.months) / 6)

        if 0 <= months_diff <= max_months:
            row["VisitConcept"] = f"{visit_prefix}{str(months_diff).zfill(2)}"
        else:
            logger.warning(
                "OUT_OF_RANGE | Patient ID: %s | Variable: Visit Concept | Measure: %d | Message: Difference of follow up months superior to 90 (rounded)",
                patient_id,
                months_diff * 6
            )
            continue
    return pd.DataFrame(result_rows, columns=cohort_df.columns)

def __parse_to_standard_format(date_str):
    known_formats = ["%d-%b-%y", "%m/%d/%Y", "%Y-%m-%d"]  # Extend if needed
    for fmt in known_formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime(sahc.DATE_FORMAT)  # Normalize to your desired format
        except ValueError:
            continue
    return None

def get_columns_mapping(filename:str, domain: str, mappings: pd.DataFrame, source_name_as_key = False):
    rows_source_code = mappings[mappings['sourceCode'].str.contains(filename)]
    rows_domain = rows_source_code[rows_source_code['targetDomainId'].str.contains(domain)]
    data_rows = rows_domain[['sourceName','targetConceptName']]
    
    if(source_name_as_key):
        columns_mapping = pd.Series(data_rows['targetConceptName'].values, index=data_rows['sourceName']).to_dict()
    else:
        columns_mapping = pd.Series(data_rows['sourceName'].values, index=data_rows['targetConceptName']).to_dict()
	
    columns = data_rows['sourceName'].drop_duplicates().reset_index(drop=True).tolist()
    return columns, columns_mapping


def cohort_filter(df, domain, patient_id_label = "Patient ID"):
    methodName = "filter_" + domain
    df_filtered = df.copy()
    
    if(hasattr(ad_hoc, methodName)):
        df_filtered = getattr(ad_hoc, methodName)(df)
    if domain == 'observation':
        df_filtered[pd.notnull(df_filtered["VariableConcept"])]
        df_filtered[pd.notnull(df_filtered[patient_id_label].map(PATIENT_IDS))].reset_index(drop=True)

    return df_filtered


def populate(cohort, domain, columns_mapping):
    global PATIENT_IDS
    columns = None
    if domain == 'person':
        columns = COLUMNS_PERSON
    elif domain == 'observation':
        columns = COLUMNS_OBSERVATION
    mapping = pd.DataFrame(columns=columns, dtype=object)
    for element in columns:
        sourceField = None
        
        if(element in columns_mapping):
            sourceField = columns_mapping[element]
        
        mapping[element] = None #Default value as None
        methodName = "set_" + domain + "_" + element
        
        if(methodName == "set_person_person_id"):
            mapping[element], PATIENT_IDS = getattr(ad_hoc, methodName)(cohort[sourceField] if sourceField in cohort else None)
        elif(methodName == "set_observation_observation_id"):
            mapping[element] = OBSERVATION_ID_SET if sourceField in cohort else None
        elif(methodName == "set_observation_person_id"):
            mapping[element] = cohort[sourceField].map(PATIENT_IDS) if sourceField in cohort else None
        elif(hasattr(ad_hoc, methodName)): 
            #In case of exist an ad hoc method defined
            mapping[element] = getattr(ad_hoc, methodName)(cohort[sourceField] if sourceField in cohort else None)
        elif(sourceField in cohort): #Normal behavior
            mapping[element] = cohort[sourceField]
    
    return mapping

def replace_nan_with_none(obj):
    if isinstance(obj, dict):
        return {k: replace_nan_with_none(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_nan_with_none(item) for item in obj]
    elif isinstance(obj, float) and pd.isna(obj):
        return None
    else:
        return obj