from datetime import datetime
import pandas as pd

cerad_wl_rounds      = []
cerad_wl_recognition = []
apo_e                = []
diagnosis            = {}
etiology             = {}

#### CUT OFF AD_HOC ####

def calculate_cut_off_values(row):
    '''
		CSF date before 03.12.2014:
			Cutoffs not available
		CSF date between 03.12.2014 and 31.12.2016:
			Cutoff: amyloid <600, cutoff t-tau >300, cutoff p-tau >60
		CSF date between 31.12.2016 and 28.11.2018:
			Cutoff amyloid <1000, cutoff t-tau >400, cutoff p-tau >62
		CSF date after 28.11.2018:
			Cutoff amyloid <680, cutoff t-tau >400, cutoff p-tau >62.
	'''
    try:
        date = datetime.datetime.strptime(row['Date of puncture (Liquor)'], '%d-%M-%Y')
    except:
        print("No date defined for the cutOffs, which is necessary in this cohort:\t", row)
        return None, None
    if date < datetime.datetime(2014, 12, 3):
        return None, None
    elif date < datetime.datetime(2016, 12, 31):
        if "2000000070" in row["VariableConcept"]: 
            return "<", 600
        if "2000000073" in row["VariableConcept"]:
            return ">", 60
        if "2000000075" in row["VariableConcept"]:
            return ">", 300
    elif date < datetime.datetime(2018, 11, 28):
        if "2000000070" in row["VariableConcept"]:
            return "<", 1000
        if "2000000073" in row["VariableConcept"]:
            return ">", 62
        if "2000000075" in row["VariableConcept"]:
            return ">", 400
    else:
        if "2000000070" in row["VariableConcept"]:
            return "<", 680
        if "2000000073" in row["VariableConcept"]:
            return ">", 62
        if "2000000075" in row["VariableConcept"]:
            return ">", 400
    return None, None

CUT_OFFS = {
		"2000000297":{"conditionalMethod": calculate_cut_off_values}, #Amyloid Beta 1-42 Cut-off
		"2000000298":{"conditionalMethod": calculate_cut_off_values}, #Total Tau Cut-off
		"2000000463":{"conditionalMethod": calculate_cut_off_values}  #Phosphorylated Tau Cut-off
		}

#### HARMONIZER AD_HOC ####

def harmonizer(row):
    variable_concept = str(row["VariableConcept"])
    if "2000000049" in variable_concept:
        return read_cerad_wl_rounds(row)
    if "2000000051" in variable_concept:
        return read_cerad_wl_recognition(row)
    if "2000000551" in variable_concept:
        return read_diagnosis_and_etiology(row)
    if "2000000013" in variable_concept:
        read_apo_e(row)

    if "2000000468" in variable_concept:
        return deal_with_family_history_dementia(row)
    if "2000000434" in variable_concept:
        return deal_with_sleep_disorders_clinical_information(row)
    if "2000000609" in variable_concept:
        return deal_with_gender(row)
    if "2000000293" in variable_concept:
        return deal_with_csf_assay(row)

    # Deal with the errors in the cohort
    if "2000000462" in variable_concept:
        return deal_with_weight(row)
    if "2000000388" in variable_concept:
        return deal_with_height(row)
    if "2000000421" in variable_concept:
        return deal_with_pulse_rate(row)
    if "2000000358" in variable_concept:
        return deal_with_cholesterol(row)
    if "2000000532" in variable_concept:
        return deal_with_csf_measure(row)
    if "2000000068" in variable_concept:
        return deal_with_amyloid_beta_138(row)

    return row

def add_missing_rows():
    missing_rows = []
    missing_rows += process_cerad_wl_rounds()
    missing_rows += process_cerad_wl_recognition()
    missing_rows += process_diagnosis_and_etiology()
    # missing_rows += process_apo_e()
    # missing_rows += process...
    # ....
    return missing_rows

def read_cerad_wl_rounds(row):
    global cerad_wl_rounds
    cerad_wl_rounds += [row]
    return []

def read_cerad_wl_recognition(row):
    global cerad_wl_recognition
    cerad_wl_recognition += [row]
    return []

def read_apo_e(row):
    global apo_e
    apo_e += [row]

def read_diagnosis_and_etiology(row):
    global diagnosis, etiology
    if row["Variable"] == "Diagnosis":
        diagnosis[row["Patient ID"]] = row
    if row["Variable"] == "Etiology":
        etiology[row["Patient ID"]] = row
    return []

def deal_with_family_history_dementia(row):
    # convert 0 = no or 1 = yes
    row["MeasureNumber"] = None
    if row["Measure"] == '0':
        row["MeasureConcept"] = 2000000239
    if row["Measure"] == '1':
        row["MeasureConcept"] = 2000000238
    return row

def deal_with_sleep_disorders_clinical_information(row):
    if row["Measure"] == "n.b.":
        row["MeasureString"] = None
    return row

def deal_with_gender(row):
    # convert {1:8507, 0:8532}
    row["MeasureNumber"] = None
    if row["Measure"] == '0':
        row["MeasureConcept"] = 8532
    if row["Measure"] == '1':
        row["MeasureConcept"] = 8507
    return row

def deal_with_csf_assay(row):
    '''
    CSF date before 03.12.2014:
        Assay: Innotest
    CSF date between 03.12.2014 and 31.12.2016:
        Assay: MSD
    CSF date after 31.12.2016:
        Assay: Luminex
    '''
    try:
        date = datetime.strptime(row['Date of puncture (Liquor)'], '%d-%M-%Y')
    except:
        print("No date defined in CSF Assay:\t", row)
        return []
    if date < datetime(2014, 12, 3):
        row["MeasureString"] = "Innotest"
    elif date < datetime(2016, 12, 31):
        row["MeasureString"] = "MSD"
    else:
        row["MeasureString"] = "Luminex"
    row["MeasureNumber"] = None
    return row

def deal_with_weight(row):
    if row["Measure"].isdigit():
        if float(row["Measure"]) < 0 or float(row["Measure"]) > 150:  # remove invalid weights
            return []
        return row
    return []

def deal_with_height(row):
    if row["Measure"].isdigit():
        if float(row["Measure"]) < 100 or float(row["Measure"]) > 230:  # remove invalid heights
            return []
        return row
    return []

def deal_with_pulse_rate(row):
    if row["Measure"].isdigit():
        return row
    return []

def deal_with_cholesterol(row):
    if row["Measure"].isdigit():
        return row
    return []

def deal_with_csf_measure(row):
    if row["Measure"].isdigit():
        return row
    return []

def deal_with_amyloid_beta_138(row):
    if row["Measure"].isdigit():
        return row
    return []

def process_cerad_wl_rounds():
    global cerad_wl_rounds
    results = []
    if len(cerad_wl_rounds) > 0:
        # key will be (patient, date)
        measure_dict = {}
        sum_of_measures_dict = {}
        for entry in cerad_wl_rounds:
            if (entry["Patient ID"], entry["Date of neuropsychological testing"]) in sum_of_measures_dict:
                sum_of_measures_dict[(entry["Patient ID"], entry["Date of neuropsychological testing"])] += int(entry["Measure"])
                measure_dict[(entry["Patient ID"], entry["Date of neuropsychological testing"])] += "," + str(entry["Measure"])
            else:
                sum_of_measures_dict[(entry["Patient ID"], entry["Date of neuropsychological testing"])] = int(entry["Measure"])
                measure_dict[(entry["Patient ID"], entry["Date of neuropsychological testing"])] = str(entry["Measure"])
        for entry in sum_of_measures_dict:
            results += [{
                'Patient ID': entry[0],
                'Date of neuropsychological testing': entry[1],
                'Variable': '[Cerad WL round 1, Cerad WL round 2, Cerad WL round 3]',
                'Measure': measure_dict[entry],
                'MeasureNumber': sum_of_measures_dict[entry],
                'VariableConcept': '2000000049',
                'MeasureConcept': None
            }]
    cerad_wl_rounds = []
    return results

def process_cerad_wl_recognition():
    global cerad_wl_recognition
    results = []
    if len(cerad_wl_recognition) > 0:
        # key will be (patient, date)
        measure_dict = {}
        sum_of_measures_dict = {}
        for entry in cerad_wl_recognition:
            if (entry["Patient ID"], entry["Date of neuropsychological testing"]) in sum_of_measures_dict:
                sum_of_measures_dict[(entry["Patient ID"], entry["Date of neuropsychological testing"])] += int(entry["Measure"])
                measure_dict[(entry["Patient ID"], entry["Date of neuropsychological testing"])] += "," + str(entry["Measure"])
            else:
                sum_of_measures_dict[(entry["Patient ID"], entry["Date of neuropsychological testing"])] = int(entry["Measure"])
                measure_dict[(entry["Patient ID"], entry["Date of neuropsychological testing"])] = str(entry["Measure"])
        for entry in sum_of_measures_dict:
            results += [{
                'Patient ID': entry[0],
                'Date of neuropsychological testing': entry[1],
                'Variable': '[Cerad WL recognition no, Cerad WL recognition yes]',
                'Measure': measure_dict[entry],
                'MeasureNumber': (sum_of_measures_dict[entry] - 10),
                'VariableConcept': '2000000051',
                'MeasureConcept': None
            }]
    cerad_wl_recognition = []
    return results

def process_diagnosis_and_etiology():
    global diagnosis, etiology
    ''' Isabelle email (3/9/2019)       
        If the column "Diagnosis" in the Berlin dataset =10, Diagnosis on transmart should be "MCI", 
            independent of the collum "Etiology" in the Berlin dataset. This applies to n=60 patients
        If "Diagnosis" is 1, Diagnosis on transmart should be "SCI". This applies to n=25 patients. 
        If Diagnosis is 81 or 8, Diagnosis on transmart should be "Depression". This applies to n=81 patients
        If Diagnosis is 2 or 3, Diagnosis should be "Other" 
        If Diagnosis is 5,6 or 7 we need the category "Etiology" to define the type of dementia. 
            If (Diagnosis =>5 and <8) and Etiology=1 Diagnosis =AD
            If (Diagnosis =>5 and <8) and Etiology=2 Diagnosis =Mixed dementia
            If (Diagnosis =>5 and <8) and Etiology=3 Diagnosis =VAD
            If (Diagnosis =>5 and <8) and Etiology=5 Diagnosis =FTD
            If (Diagnosis =>5 and <8) and Etiology=8 Diagnosis =Other Dementia
    '''
    results = []
    for patient in diagnosis:
        row = diagnosis[patient]
        concept = None
        if str(row['Measure']) == "10":
            concept = "2000000254"  # MCI
        elif str(row['Measure']) == "1":
            concept = "2000000256"  # SCI
        elif str(row['Measure']) == "81" or str(row['Measure']) == "8":
            concept = "2000000470"  # Depression
        elif str(row['Measure']) == "2" or str(row['Measure']) == "3":
            concept = "2000000700"  # Other
        elif str(row['Measure']) == "5" or str(row['Measure']) == "6" or str(row['Measure']) == "7":
            if patient in etiology:
                if str(etiology[patient]['Measure']) == "1":
                    concept = "2000000255"  # AD
                elif str(etiology[patient]['Measure']) == "2":
                    concept = "2000000701"  # Mixed dementia
                elif str(etiology[patient]['Measure']) == "3":
                    concept = "2000000685"  # VAD
                elif str(etiology[patient]['Measure']) == "5":
                    concept = "2000000665"  # FTD
                elif str(etiology[patient]['Measure']) == "8":
                    concept = "2000000699"  # Other Dementia

        results += [{
            'Patient ID': patient,
            'Number of Visit': row['Number of Visit'],
            'Date of Diagnosis': row['Date of Diagnosis'],
            'Variable': row['Variable'],
            'Measure': row['Measure'],
            'VariableConcept': '2000000551',
            'MeasureConcept': concept,
            'MeasureNumber': None,
            'MeasureString': None
        }]
    diagnosis = {}
    etiology = {}
    return results

def process_apo_e():
    global apo_e
    print("Check and remove this shit, because now we have a standard ad hoc method for this")
    results = []
    if len(apo_e) > 0:
        for row in apo_e:
            measures = row['Measure'].split("/")
            if len(measures) == 2:
                results += [{
                    'Patient ID': row['Patient ID'],
                    'Date of puncture (Liquor)': row['Date of puncture (Liquor)'],
                    'Variable': row['Variable'],
                    'Measure': row['Measure'],
                    'VariableConcept': '2000000320',  # ApoE Allele 1
                    'MeasureConcept': None,
                    'MeasureNumber': None,
                    'MeasureString': measures[0]
                }, {
                    'Patient ID': row['Patient ID'],
                    'Date of puncture (Liquor)': row['Date of puncture (Liquor)'],
                    'Variable': row['Variable'],
                    'Measure': row['Measure'],
                    'VariableConcept': '2000000321',  # ApoE Allele 2
                    'MeasureConcept': None,
                    'MeasureNumber': None,
                    'MeasureString': measures[1]
                }, {
                    'Patient ID': row['Patient ID'],
                    'Date of puncture (Liquor)': row['Date of puncture (Liquor)'],
                    'Variable': row['Variable'],
                    'Measure': row['Measure'],
                    'VariableConcept': '2000000014',  # ApoE4 Carrier
                    'MeasureConcept': None,
                    'MeasureNumber': None,
                    'MeasureString': "Yes" if measures[0] == "4" or measures[1] == "4" else "No"
                }]
    apo_e = []
    return results

#### PERSON AD_HOC ####
def filter_person(cohort: pd.DataFrame) -> pd.DataFrame:
    cohort.drop_duplicates().reset_index(drop=True)
    cohort = cohort[pd.notnull(cohort['Sex'])]
    return cohort.reset_index(drop=True)

def set_person_gender_concept_id(value):
	gender_map = {"1":8507, "0":8532}
	return value.map(gender_map)

def set_person_year_of_birth(value):
	return pd.DatetimeIndex(value).year

def set_person_month_of_birth(value):
	return pd.DatetimeIndex(value).month

def set_person_day_of_birth(value):
	return pd.DatetimeIndex(value).day

def set_person_person_id(value):
    person_dict = value.to_dict()
    person_dict = {i[1]:i[0] for i in person_dict.items()}
    return value.map(person_dict), person_dict