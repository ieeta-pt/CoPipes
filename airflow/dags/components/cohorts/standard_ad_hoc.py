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

	#####################
	#	Loading stage 	#
	#####################

def process_loading_stage(data_dict, adhoc_harmonization : bool = False):
    for row in data_dict:
        variable_concept = str(row["variable_concept"])
        patient_id = str(row[sahc.PATIENT_ID_LABEL])

        if "2000000540" in variable_concept:
            __load_date_of_diagnosis(row, patient_id)
        if "2000000554" in variable_concept:
            __load_years_of_education(row, patient_id)
        if "2000000488" in variable_concept:
            __deal_with_age(row, patient_id)
        if "2000000609" in variable_concept:
            __load_gender(row, patient_id)
        if "2000000388" in variable_concept:
            __load_body_length(row, patient_id)
        if "2000000462" in variable_concept:
            __load_weight(row, patient_id)
        if "2000000013" in variable_concept:
            __load_extra_apo_e(row, patient_id)

        for domain in sahc.PRIORITY_DOMAINS_IDS:
            for variable in sahc.PRIORITY_DOMAINS_IDS[domain]["source"]:
                if variable in variable_concept:
                    __load_priority_domains(row, variable_concept)

        for comorbidity in sahc.AAL_COMORBIDITIES:
            for variable in sahc.AAL_COMORBIDITIES[comorbidity]["concepts"]:
                if variable in variable_concept:
                    return __add_comorbidities_sub_class(row, patient_id, sahc.AAL_COMORBIDITIES[comorbidity]["name"], comorbidity)

def __load_date_of_diagnosis(row, patient_id):
    global date_of_diagnosis, birthday_date
    if row['Measure'] != "":
        date_of_diagnosis[patient_id] = row['Measure']
    if len(birthday_date) > 0:
        if patient_id in birthday_date:
            __calculate_age(row)

def __load_years_of_education(row, patient_id):
    global years_of_education
    if row['Measure'] != "":
        years_of_education[patient_id] = int(float(row['Measure']))

def __load_gender(row, patient_id):
    global gender
    if row['MeasureConcept'] != "":
        gender[patient_id] = row['MeasureConcept']

def __load_body_length(row, patient_id):
    global body_length, weight
    if row['Measure'] != "":
        body_length[patient_id] = row['MeasureNumber']
    if len(weight) > 0:
        __calculate_body_mass_index(row, patient_id)

def __load_weight(row, patient_id):
    global weight, body_length
    if row['Measure'] != "":
        weight[patient_id] = row['MeasureNumber']
    if len(body_length) > 0:
        __calculate_body_mass_index(row, patient_id)

def __load_extra_apo_e(row, patient_id):
    global apo_e
    if row['MeasureString'] == row['MeasureString']:#Verify if is NaN
        measures = row['MeasureString'].split("/")
        if len(measures) == 2:
            apo_e += [
                __merge_dictionaries(row, {
                    sahc.PATIENT_ID_LABEL:patient_id,
                    'Variable': row['Variable'],
                    'Measure': row['Measure'],
                    'VariableConcept': '2000000320', #ApoE Allele 1
                    'MeasureConcept': None,
                    'MeasureNumber': None,
                    'MeasureString': measures[0]
                    }), 
                __merge_dictionaries(row, {
                    sahc.PATIENT_ID_LABEL:patient_id,
                    'Variable': row['Variable'],
                    'Measure': row['Measure'],
                    'VariableConcept': '2000000321', #ApoE Allele 2
                    'MeasureConcept': None,
                    'MeasureNumber': None,
                    'MeasureString': measures[1]
                    }),
                __merge_dictionaries(row, {
                    sahc.PATIENT_ID_LABEL:patient_id,
                    'Variable': row['Variable'],
                    'Measure': row['Measure'],
                    'VariableConcept': '2000000014', #ApoE4 Carrier
                    'MeasureConcept': sahc.YES if measures[0] == "4" or measures[1] == "4" else sahc.NO,
                    'MeasureNumber': None,
                    'MeasureString': None
                    })]
        else:
            msg = "This method was not able to split the measure by /"
            logger.warning(
                "WRONG_VALUE | Patient ID: %s | Variable: %s | Measure: %s | Message: %s",
                patient_id,
                row['Variable'],
                row['Measure'],
                msg
            )
    else:
        msg	= "This method was not able to split the measure by / because the measure is NaN"
        logger.warning(
                "MISSING_VALUE | Patient ID: %s | Variable: %s | Measure: %s | Message: %s",
                patient_id,
                row['Variable'],
                row['Measure'],
                msg
            )
        
def __load_birthday_date(row, patient_id):
    global birthday_date, date_of_diagnosis
    if row['Measure'] != "":
        birthday_date[patient_id] = row['Measure']
    if len(date_of_diagnosis) > 0:
        if patient_id in date_of_diagnosis:
            __calculate_age(row, patient_id)

def __load_priority_domains(row, variable_concept):
    global priority_domains
    if variable_concept not in priority_domains:
        priority_domains[variable_concept] = []
    priority_domains[variable_concept].append(row)
	
def __calculate_age(row, patient_id):
    global date_of_diagnosis, birthday_date, age, age_measurement
    try:
        delta = __compare_dates(date_of_diagnosis[patient_id], birthday_date[patient_id])
        if delta:
            age = int(delta.days/365)
            age[patient_id] = age
            age_measurement += [__merge_dictionaries(row, {
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

def __calculate_body_mass_index(row, patient_id):
    global weight, body_length, body_mass
    try:
        bmi = weight[patient_id]/((body_length[patient_id]/100)*(body_length[patient_id]/100))
        if bmi > 30:
            value = sahc.YES
        else:
            value = sahc.NO
        body_mass += [__merge_dictionaries(row, {
            sahc.PATIENT_ID_LABEL:patient_id,
            'Body Mass Index':bmi,
            'Variable': 'Calculated bmi', 
            'Measure': "",
            'MeasureNumber': bmi, 
            'VariableConcept': '2000000339', 
            'MeasureConcept': None
        }), __merge_dictionaries(row, {
            sahc.PATIENT_ID_LABEL:patient_id,
            'Variable': 'Calculated obesity', 
            'Measure': "",
            'MeasureNumber': None, 
            'VariableConcept': '2000000396', 
            'MeasureConcept': value
        })]

    except Exception as ex:
        var = "Body Mass Index"
        if patient_id not in weight:
            var = "Weight"
        elif patient_id not in body_length:
            var = "Length"
        msg = "Body Mass Index not calculated due to missing variable"
        logger.warning(
            "MISSING_VALUE | Patient ID: %s | Variable: %s | Message: %s",
            patient_id,
            var,
            msg
        )
          
def __deal_with_age(row, patient_id):
    global age_measurement, age
    if(row['Measure'].isdigit()):
        age_measurement.append(row)
        age[patient_id] = int(row['Measure'])
    else:   
        __load_birthday_date(row, patient_id)

def __compare_dates(inital_date, final_date):
	try:
		d0 = datetime.strptime(inital_date, sahc.DATE_FORMAT)
		d1 = datetime.strptime(final_date, sahc.DATE_FORMAT)
		return (d0 - d1)
	except:
		return None

def __merge_dictionaries(row, newData):
	for key in row:
		if key not in newData:
			newData[key] = row[key]
	return newData

def __add_comorbidities_sub_class(self, row, patient_id, variable, concept_id):
    global comorbidities
    if row["MeasureConcept"] == sahc.YES:
        if variable not in comorbidities:
            comorbidities[variable] = []
        if len(list(filter(lambda line: line[sahc.PATIENT_ID_LABEL] == patient_id, comorbidities[variable]))) == 0:
            comorbidities[variable] += [__merge_dictionaries(row, {
                sahc.PATIENT_ID_LABEL:patient_id,
                'Variable': "Ontology rule " + variable, 
                'Measure': "",
                'MeasureNumber': None, 
                'VariableConcept': concept_id,
                'MeasureConcept': sahc.YES
            })]
            __add_comorbidity(row, patient_id)

def __add_comorbidity(row, patient_id):
    global comorbidity_yes
    if len(list(filter(lambda line: line[sahc.PATIENT_ID_LABEL] == patient_id, comorbidity_yes))) == 0:
        comorbidity_yes += [__merge_dictionaries(row, {
            sahc.PATIENT_ID_LABEL:patient_id,
            'Variable': 'Ontology rule (Comorbidity - Yes)', 
            'Measure': "",
            'MeasureNumber': None, 
            'VariableConcept': "2000000525",
            'MeasureConcept': sahc.YES
        })]