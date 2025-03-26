from datetime import datetime
import pandas as pd
from airflow.decorators import task
import zscore_calculator as zc
import cutoff_calculator as cc
import sah_constants as sahc
import ad_hoc
from airflow.utils.log.logging_mixin import LoggingMixin

date_of_diagnosis = {}
years_of_education = {}
birthday_date = {}
gender = {}
age = {}

body_length = {}
weight = {}
age_measurement = []
body_mass = []
comorbidities = {}
comorbidity_yes = []
apo_e = []
priority_domains = {}

logger = LoggingMixin().log

@task
def create_new_measures(data: list[dict], adhoc_harmonization : bool = False) -> dict:
    for file in data:
        df = file["data"]
        process_loading_stage(df, adhoc_harmonization)

def process_loading_stage(data_dict, adhoc_harmonization : bool = False):
    for row in data_dict:
        variable_concept = str(row["variable_concept"])
        patient_id = str(row[sahc.PATIENT_ID_LABEL])

        if "2000000540" in variable_concept:
            __loadDateOfDiagnosis(row, patient_id)
        if "2000000554" in variable_concept:
            __loadYearsOfEducation(row, patient_id)
        if "2000000488" in variable_concept:
            __dealWithAge(row, patient_id)
        if "2000000609" in variable_concept:
            __loadGender(row, patient_id)
        if "2000000388" in variable_concept:
            __loadBodyLength(row, patient_id)
        if "2000000462" in variable_concept:
            __loadWeight(row, patient_id)
        if "2000000013" in variable_concept:
            __loadExtraApoE(row, patient_id)

def __loadDateOfDiagnosis(row, patient_id):
    global date_of_diagnosis, birthday_date
    if row['Measure'] != "":
        date_of_diagnosis[patient_id] = row['Measure']
    if len(birthday_date) > 0:
        if patient_id in birthday_date:
            __calculateAge(row)



def __calculateAge(row, patient_id):
    global date_of_diagnosis, birthday_date, age, age_measurement
    try:
        delta = __compareDates(date_of_diagnosis[patient_id], birthday_date[patient_id])
        if delta:
            age = int(delta.days/365)
            age[patient_id] = age
            age_measurement += [__mergeDictionaries(row, {
				sahc.PATIENT_ID_LABEL:patient_id,
				'Age':age,
				'Variable': 'Calculated age', 
				'Measure': "",
				'MeasureNumber': age, 
				'VariableConcept': '2000000488', 
				'MeasureConcept': None
			})]
    except:
        var = "Calculated age"
        msg = "Age not calculated due to missing variable."
        if patient_id not in date_of_diagnosis:
            var = "Date of Diagnosis"
        elif patient_id not in birthday_date:
            var = "Birthday Date"
        else:
            msg = "Age calculation fail maybe due to the date format."
            logger.warning(
                "MISSING_VALUE | Patient ID: %s | Variable: %s | Message: %s",
                patient_id,
                var,
                msg
            )
          


def __compareDates(inital_date, final_date):
	try:
		d0 = datetime.strptime(inital_date, sahc.DATE_FORMAT)
		d1 = datetime.strptime(final_date, sahc.DATE_FORMAT)
		return (d0 - d1)
	except:
		return None
    


def __mergeDictionaries(row, newData):
	for key in row:
		if key not in newData:
			newData[key] = row[key]
	return newData