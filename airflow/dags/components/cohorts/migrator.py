import pandas as pd
import numpy as np
from airflow.decorators import task
from components.extract.csv import extract_csv
from components.cohorts.transform_to_kv import transform_to_kv
from components.cohorts.harmonizer import harmonize

@task
def migrate(data: list[dict], mappings: dict) -> dict:
    """
    Migrates data into structured Person and Observation objects.
    
    :param data: Harmonized data from the previous step.
    :return: Processed data as a dictionary.
    """
    df_person = None

    for d in data:
        if d["filename"].lower().find("patient") != -1:
            df_person = pd.DataFrame(d["data"])
            print(f"\n Found patient data: {df_person.head()}")
            break

    df_person = df_person.where(pd.notnull(df_person), None)
    return {"data" : df_person.to_dict(orient="records")}

    migrate_person(df_person)
    # migrate_observation(df, data["filename"])


def migrate_person(df: pd.DataFrame, filename: str) -> dict:
    pass


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
