import pandas as pd
import numpy as np
import components.cohorts.ad_hoc as ad_hoc
from airflow.decorators import task

COLUMNS_DST = [
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

@task
def migrate(data: list[dict], mappings: dict, adhoc_migration: bool = False) -> dict:
    """
    Migrates data into structured Person and Observation objects.
    
    :param data: Harmonized data from the previous step.
    :return: Processed data as a dictionary.
    
    """
    
    mappings_df = pd.DataFrame.from_dict(mappings["data"])
    
    df_person = None
    f_person = None

    for d in data:
        if d["filename"].lower().find("patient") != -1:
            df_person = pd.DataFrame(d["data"])
            f_person = d["filename"]
            break   
    
    print(f"Person: {df_person}\n")
    person_data = migrate_person(df_person, f_person, mappings_df, True)
    # migrate_observation(df, data["filename"])
    # person_data = person_data.where(pd.notna(person_data), None)
    
    person_dict = person_data.to_dict(orient="records")
    person_dict_clean = replace_nan_with_none(person_dict)

    return {"person": {"data": person_dict_clean}}



def migrate_person(df: pd.DataFrame, filename: str, mappings: pd.DataFrame, adhoc_migration: bool = False):
    domain = "person"
    columns, columns_mapping = get_columns_mapping(filename, domain, mappings)
    df = df.reindex(columns=columns)
    
    if adhoc_migration:
        methodName = "filter_" + domain
        if(hasattr(ad_hoc, methodName)):
            df = getattr(ad_hoc, methodName)(df)

    result = populate(df, domain, columns_mapping)
    return result


def migrate_observation(df: pd.DataFrame, filename: str) -> dict:
    """Processes and structures observation-related data."""
    df["VisitConcept"] = "2100000000"
    df = calculate_visit_concepts(df)
    
    return {"data": df.to_dict(orient="records"), "filename": f"observation_{filename}"}


def calculate_visit_concepts(df: pd.DataFrame) -> pd.DataFrame:
    """Assigns visit concept IDs based on observation date differences."""
    df["VisitConcept"] = "2100000000"
    
    if "observation_date" in df.columns and "person_id" in df.columns:
        df = df.dropna(subset=["observation_date"])
        df["observation_date"] = pd.to_datetime(df["observation_date"], errors="coerce")
        
        first_visits = df.groupby("person_id")["observation_date"].min()
        df["months_since_first"] = df.apply(lambda row: (row["observation_date"] - first_visits[row["person_id"]]).days // 30, axis=1)
        df["VisitConcept"] = df["months_since_first"].apply(lambda x: f"21000000{str(min(max(x // 6, 0), 40)).zfill(2)}")
        df.drop(columns=["months_since_first"], inplace=True)
    
    return df


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

def populate(cohort, domain, columns_mapping):
    mapping = pd.DataFrame(columns=COLUMNS_DST, dtype=object)
    for element in COLUMNS_DST:
        sourceField = None
        
        if(element in columns_mapping):
            sourceField = columns_mapping[element]
        
        mapping[element] = None #Default value as None
        methodName = "set_" + domain + "_" + element
        
        if(hasattr(ad_hoc, methodName)): 
            #In case of exist an ad hoc method defined
            mapping[element] = getattr(ad_hoc, methodName)(cohort[sourceField] if sourceField in cohort else None)
        else:
            if(sourceField in cohort): #Normal behavior
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