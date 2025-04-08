from datetime import datetime
import pandas as pd
import components.utils.cohorts.zscore_calculator as zc
import components.utils.cohorts.cutoff_calculator as cc
import components.utils.cohorts.sah_constants as sahc
import components.utils.cohorts.ad_hoc as ad_hoc

from airflow.decorators import task
from airflow.utils.log.logging_mixin import LoggingMixin

date_of_diagnosis = {}
years_of_education = {}
def get_years_of_education(patient_id):
    global years_of_education
    eduy = None
    if patient_id in years_of_education:
        eduy = years_of_education.get(patient_id)
    return eduy

birthday_date = {}
gender = {}
def get_gender(patient_id):
    global gender
    gender_local = None
    if patient_id in gender:
        gender_local = gender.get(patient_id)
    return gender_local

age = {}
def get_age(patient_id):
    global age
    age_local = None
    if patient_id in age:
        age_local = age.get(patient_id)
    return age_local

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
def create_new_measures(data: list[dict], adhoc_harmonization : bool = False) -> list[dict]:
    temp_result = {}
    for file in data:
        df = file["data"]
        fname = file["filename"]
        _, temp_result[fname] = process_loading_stage(df)
        temp_result[fname] = clean_empty_measure(temp_result[fname])

    result = []
    for file in temp_result:
        df = temp_result[file]
        fname = file
        processed_df = pd.DataFrame(df)
        new_data = pd.DataFrame(process_calculation_and_appending_stage(df, adhoc_harmonization))

        processed_df = pd.concat([processed_df, new_data], ignore_index=True)
        processed_df = processed_df.to_dict(orient='records')
        processed_df = replace_nan_with_none(processed_df)

        result.append({"data":processed_df, "filename":fname})
    return result

def clean_empty_measure(data):
    data_df = pd.DataFrame(data)    
    data_df = data_df[data_df["MeasureString"] != "n.a."]
    data_df = data_df.dropna(how='all', subset=["MeasureConcept", "MeasureNumber", "MeasureString"])
    return data_df.to_dict(orient="records")

def replace_nan_with_none(obj):
    if isinstance(obj, dict):
        return {k: replace_nan_with_none(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_nan_with_none(item) for item in obj]
    elif isinstance(obj, float) and pd.isna(obj):
        return None
    else:
        return obj

def process_calculation_and_appending_stage(data_dict, adhoc_harmonization):
	output_data_dict = []
	for row in data_dict:
		variable_concept = str(row["VariableConcept"])
		if (__validate_measure_content(row, str(row[sahc.PATIENT_ID_LABEL]), variable_concept)):
			data = __process_row(row, str(row[sahc.PATIENT_ID_LABEL]), variable_concept)
			if isinstance(data, list):
				output_data_dict += data
			else:
				output_data_dict += [data]
			zscore = zc.calculate(row, sahc.PATIENT_ID_LABEL, variable_concept)
			if isinstance(zscore, list):
				output_data_dict += zscore
			else:
				output_data_dict += [zscore]
			if adhoc_harmonization != None:
				cutOff = cc.calculate(row, variable_concept, ad_hoc.CUT_OFFS)
				output_data_dict += cutOff
	output_data_dict += __add_new_measurements()
	return output_data_dict

	#####################
	#	Loading stage 	#
	#####################

def process_loading_stage(data_dict):
    for row in data_dict:
        variable_concept = str(row["VariableConcept"])
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
                    return __add_comorbidities_sub_class(row, patient_id, sahc.AAL_COMORBIDITIES[comorbidity]["name"], comorbidity), data_dict
    return None, data_dict

def __load_date_of_diagnosis(row, patient_id):
    global date_of_diagnosis, birthday_date
    if row['Measure'] != "":
        date_of_diagnosis[patient_id] = row['Measure']
    if len(birthday_date) > 0 and patient_id in birthday_date:
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
    if len(weight) > 0 and patient_id in weight:
        __calculate_body_mass_index(row, patient_id)

def __load_weight(row, patient_id):
    global weight, body_length
    if row['Measure'] != "":
        weight[patient_id] = row['MeasureNumber']
    if len(body_length) > 0 and patient_id in body_length:
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
    if len(date_of_diagnosis) > 0 and patient_id in date_of_diagnosis:
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
            patient_age = int(delta.days/365)
            age[patient_id] = patient_age
            age_measurement += [__merge_dictionaries(row, {
				sahc.PATIENT_ID_LABEL:patient_id,
				'Age':patient_age,
				'Variable': 'Calculated age', 
				'Measure': "",
				'MeasureNumber': patient_age, 
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

def __parse_to_standard_format(date_str):
    known_formats = ["%d-%b-%y", "%m/%d/%Y", "%Y-%m-%d"]  # Extend if needed
    for fmt in known_formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime(sahc.DATE_FORMAT)  # Normalize to your desired format
        except ValueError:
            continue
    return None

def __compare_dates(initial_date, final_date):
    norm_initial = __parse_to_standard_format(initial_date)
    norm_final = __parse_to_standard_format(final_date)

    if not norm_initial or not norm_final:
        return None

    d0 = datetime.strptime(norm_initial, sahc.DATE_FORMAT)
    d1 = datetime.strptime(norm_final, sahc.DATE_FORMAT)

    return d0 - d1
    
def __merge_dictionaries(row, newData):
	for key in row:
		if key not in newData:
			newData[key] = row[key]
	return newData

def __add_comorbidities_sub_class(row, patient_id, variable, concept_id):
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

	#########################
	#	Validation stage 	#
	#########################
     
def __validate_measure_content(row, patient_id, variable_concept):
	''' Validate measures. This is a work in process. 
	Default is True because we considered everything valid until something wrong happen.'''
	
	list_of_ranges = {
		"2000000173":{"min":0, "max":144},
		"2000000170":{"min":0, "max":4},
		"2000000171":{"min":0, "max":4},
		"2000000168":{"min":0, "max":8},
		"2000000121":{"min":0, "max":52},
		}
	for variable in list_of_ranges:
		if variable in variable_concept:
			return __is_variable_in_numeric_range(variable_concept=variable_concept, 
												   patient_id=patient_id,
												   measure=row["Measure"], 
												   minimum=list_of_ranges[variable]["min"], 
												   maximum=list_of_ranges[variable]["max"])
	return True

def __is_variable_in_numeric_range(variable_concept, patient_id, measure, minimum, maximum):
    if measure.isdigit():
        if minimum <= float(measure) <= maximum:
            return True
        msg = f"The range of values defined for this variable are {minimum}-{maximum}"
        logger.warning(
            "OUT_OF_RANGE | Patient ID: %s | Variable: %s | Measure: %s | Message: %s",
            patient_id,
            variable_concept,
            measure,
            msg
        )
    else:
        logger.warning(
            "WRONG_TYPE | Patient ID: %s | Variable: %s | Measure: %s",
            patient_id,
            variable_concept,
            measure
        )
    return False

	#########################
	#	Processing stage 	#
	#########################
def __process_row(row, patient_id, variable_concept):
	if "2000000480" in variable_concept:
		return __deal_with_dates_differences_in_days(row, patient_id)
	if "2000000479" in variable_concept:
		return __deal_with_dates_differences_in_days(row, patient_id)
	if "2000000482" in variable_concept:
		return __deal_with_dates_differences_in_days(row, patient_id)
	if "2000000477" in variable_concept:
		return __deal_with_dates_differences_in_days(row, patient_id)
	return __cleaner(row, variable_concept)

def __deal_with_dates_differences_in_days(row, patient_id):
    global date_of_diagnosis
    try:
        delta = __compare_dates(date_of_diagnosis[patient_id], row["Measure"])
        if delta:
            if round(delta.days/365, 5) > -15 and round(delta.days/365, 5) < 15:
                row["MeasureNumber"] = round(delta.days/365, 5)
                row["MeasureString"] = None
                return row
            else:
                msg = "The difference of dates is too big (more than 15 years)"
                logger.warning(
                    "INVALID_DATE | Patient ID: %s | Variable: %s | Measure: %s | Message: %s",
                    patient_id,
                    row["Variable"], 
                    round(delta.days/365, 5),
                    msg
                )
    except Exception as e:
        var = row["Variable"]
        if patient_id not in date_of_diagnosis:
            var = "Date Of Diagnosis"
        msg = "Missing date to calculate the difference of dates"
        logger.warning(
            "INVALID_DATE | Patient ID: %s | Variable: %s | Message: %s",
            patient_id,
            var,
            msg
        )
    return []
    
def __cleaner(row, variable_concept):
	if "2000000488" in variable_concept:
		return []
	if "2000000540" in variable_concept:
		return []
	return row

	#############################################
	#	Final stage 							#
	#											#
	# This stage runs one time for each file 	#
	#############################################
def __add_new_measurements():
    global age_measurement, body_mass, comorbidities, comorbidity_yes, apo_e
    newMeasurements = []
    newMeasurements += __add_measurement(age_measurement)
    newMeasurements += __add_measurement(body_mass)
    for comorbidity in comorbidities:
        newMeasurements += __add_measurement(comorbidities[comorbidity])
    newMeasurements += __add_measurement(comorbidity_yes)
    newMeasurements += __add_measurement(apo_e)
    #Priority Domains
    newMeasurements += __add_priority_domains()
    #newMeasurements += self.__addMeasurement...
    #....
    return newMeasurements

def __add_measurement(list_of_measurements):
	results = []
	if len(list_of_measurements) > 0:
		results = list_of_measurements.copy()
		list_of_measurements.clear()
	return results

def __add_priority_domains():
    global priority_domains
    results = []
    for domain in sahc.PRIORITY_DOMAINS_IDS:
        tmpResults = []
        for conceptID in sahc.PRIORITY_DOMAINS_IDS[domain]["source"]:
            if conceptID in priority_domains:
                for row in priority_domains[conceptID]:
                    if conceptID in row['VariableConcept']:
                        #Entry with value
                        newRow = row.copy()
                        newRow['VariableConcept'] = sahc.PRIORITY_DOMAINS_IDS[domain]["targetValue"]
                        tmpResults.append(newRow)
                        #Entry with type
                        if "targetType" in sahc.PRIORITY_DOMAINS_IDS[domain]:
                            newRow = row.copy()
                            newRow['VariableConcept'] = sahc.PRIORITY_DOMAINS_IDS[domain]["targetType"]
                            newRow['Measure'] = sahc.CONCEPT_NAMES[conceptID]
                            newRow['MeasureConcept'] = None
                            newRow['MeasureNumber'] = None
                            newRow['MeasureString'] = sahc.CONCEPT_NAMES[conceptID]
                            tmpResults.append(newRow)
                        #Entry with Z-Score
                        zcore = zc.calculate(row, sahc.PATIENT_ID_LABEL, conceptID)
                        if isinstance(zcore, list):
                            for entry in zcore:
                                entry['VariableConcept'] = sahc.PRIORITY_DOMAINS_IDS[domain]["zscore"]
                                tmpResults.append(entry)
                        else:
                            zcore['VariableConcept'] = sahc.PRIORITY_DOMAINS_IDS[domain]["zscore"]
                            tmpResults.append(zcore)
            if len(tmpResults) > 0:
                results += tmpResults
                break
    return results