import components.utils.cohorts.standard_ad_hoc as sah

MALE = 8507
FEMALE = 8532

def calculate(row_data, patient_id_label, variable_concept):
    row = dict(row_data)
    patient_id = str(row[patient_id_label])
    measure_number = row.get('MeasureNumber')
    
    zscore_mapping = {
        "2000000210": (calculate_zcore_tmta, "TMT-A Z-score", "2000000211"),
        "2000000212": (calculate_zcore_tmtb, "TMT-B Z-score", "2000000213"),
        "2000000009": (calculate_zcore_animals_fluency, "Animals Fluency 1 min Z-score", "2000000010"),
        "2000000045": (calculate_zcore_cerad_figures, "CERAD Figures Z-score", "2000000046"),
        "2000000015": (calculate_zcore_avlt_delayed, "AVLT Delayed Z-score", "2000000016"),
        "2000000017": (calculate_zcore_avlt_immediate, "AVLT Immediate Z-score", "2000000018"),
        "2000000276": (calculate_zcore_stroop_part1, "Stroop Part 1 Z-score", "2000000277"),
        "2000000278": (calculate_zcore_stroop_part2, "Stroop Part 2 Z-score", "2000000279"),
        "2000000280": (calculate_zcore_stroop_part3, "Stroop Part 3 Z-score", "2000000281"),
        "2000000424": (calculate_zcore_sdst, "SDST Z-score", "2000000425")
    }
    
    for key, (func, variable, concept) in zscore_mapping.items():
        if key in variable_concept:
            res = func(patient_id, measure_number)
            if res is not None:
                row.update({
                    'Variable': variable,
                    'VariableConcept': concept,
                    'Measure': "Calculated automatically",
                    'MeasureNumber': res
                })
                return row
    
    return []

def get_initial_variables(patientID):
    try:
        gender_local = sah.get_gender(patientID)
        eduy = sah.get_years_of_education(patientID)
        age_local = sah.get_age(patientID)
        return gender_local, eduy, age_local
    except:
        print(f"FODEU: {patientID}")
        return None, None, None

def calculate_zcore_tmta(patientID, measure):
    gender_local, eduy, age_local = get_initial_variables(patientID)
    if gender_local and eduy and age_local:
        if gender_local == FEMALE:
            if eduy < 13:
                if age_local > 79.99:
                    return (53.6 - measure) / 20.4
                elif age_local > 69.99:
                    return (48.1 - measure) / 15.3
                elif age_local > 50.99:
                    return (44.4 - measure) / 13.7
            else:
                if age_local > 79.99:
                    return (61 - measure) / 20.4
                elif age_local > 69.99:
                    return (51 - measure) / 22.3
                elif age_local > 50:
                    return (39.7 - measure) / 11
        elif gender_local == MALE:
            if eduy < 13:
                if age_local > 79.99:
                    return (62 - measure) / 22.1
                elif age_local > 69.99:
                    return (50.1 - measure) / 16.2
                elif age_local > 50:
                    return (44.6 - measure) / 13.7
            else:
                if age_local > 79.99:
                    return (59.6 - measure) / 12.2
                elif age_local > 69.99:
                    return (45.8 - measure) / 15.1
                elif age_local > 50:
                    return (43.8 - measure) / 17.2
    return None

def calculate_zcore_tmtb(patientID, measure):
    gender_local, eduy, age_local = get_initial_variables(patientID)
    if gender_local and eduy and age_local:
        if gender_local == FEMALE:
            if eduy < 13:
                if age_local > 79.99:
                    return (141.6 - measure) / 42.5
                elif age_local > 69.99:
                    return (138.3 - measure) / 58.9
                elif age_local > 50.99:
                    return (106.6 - measure) / 37.9
            else:
                if age_local > 79.99:
                    return (145 - measure) / 42.5
                elif age_local > 69.99:
                    return (107.6 - measure) / 40
                elif age_local > 50:
                    return (95.1 - measure) / 35.9
        elif gender_local == MALE:
            if eduy < 13:
                if age_local > 79.99:
                    return (190.7 - measure) / 69.9
                elif age_local > 69.99:
                    return (141 - measure) / 65.6
                elif age_local > 50:
                    return (117.8 - measure) / 50.9
            else:
                if age_local > 79.99:
                    return (124.6 - measure) / 34.2
                elif age_local > 69.99:
                    return (104.7 - measure) / 31.7
                elif age_local > 50:
                    return (96.9 - measure) / 34.2
    return None

def calculate_zcore_animals_fluency(patient_id, measure):
    gender_local, eduy, age_local = get_initial_variables(patient_id)
    if eduy and age_local:
        edulow = 1 if eduy < 7 else 0
        eduhigh = 1 if eduy > 12 else 0
        
        return (measure - (30.24 + (-0.124 * age_local) + (-11.42 * edulow) + (5.861 * eduhigh) + (0.135 * age_local * edulow) - (0.0404 * age_local * eduhigh))) / 5.604
    return None


def calculate_zcore_cerad_figures(patientID, measure):
    gender_local, eduy, age_local = get_initial_variables(patientID)
    if gender_local and eduy and age_local:
        if gender_local == FEMALE:
            if eduy < 13:
                if age_local > 79.99:
                    return (measure - 9.5) / 1.2
                elif age_local > 69.99:
                    return (measure - 10) / 1
                elif age_local > 50.99:
                    return (measure - 10.1) / 0.9
            else:
                if age_local > 79.99:
                    return (measure - 10.4) / 0.5
                elif age_local > 69.99:
                    return (measure - 10.5) / 0.7
                elif age_local > 50:
                    return (measure - 10.5) / 0.7
        elif gender_local == MALE:
            if eduy < 13:
                if age_local > 79.99:
                    return (measure - 9.8) / 1.2
                elif age_local > 69.99:
                    return (measure - 10.4) / 0.8
                elif age_local > 50:
                    return (measure - 10.4) / 0.8
            else:
                if age_local > 79.99:
                    return (measure - 10.5) / 0.8
                elif age_local > 69.99:
                    return (measure - 10.6) / 0.6
                elif age_local > 50:
                    return (measure - 10.6) / 0.6
    return None

def calculate_zcore_avlt_delayed(patientID, measure):
    gender_local, eduy, age_local = get_initial_variables(patientID)
    if eduy and age_local and gender_local:
        edulow = 1 if eduy < 7 else 0
        eduhigh = 1 if eduy > 12 else 0
        sex = 1 if gender_local == MALE else 0
        return (measure - (10.924 + (-0.073 * (age_local - 50)) + (-0.0009 * (age_local - 50) ** 2) + (-1.197 * sex) + (-0.844 * edulow) + (0.424 * eduhigh))) / 2.496
    return None

def calculate_zcore_avlt_immediate(patientID, measure):
    gender_local, eduy, age_local = get_initial_variables(patientID)
    if eduy and age_local and gender_local:
        edulow = 1 if eduy < 7 else 0
        eduhigh = 1 if eduy > 12 else 0
        sex = 1 if gender_local == MALE else 0
        return (measure - (49.672 + (-0.247 * (age_local - 50)) + (-0.0033 * (age_local - 50) ** 2) + (-4.227 * sex) + (-3.055 * edulow) + (2.496 * eduhigh))) / 7.826
    return None

def calculate_zcore_stroop_part1(patient_id, measure):
    gender_local, eduy, age_local = get_initial_variables(patient_id)
    if eduy and age_local:
        
        edulow = 1 if eduy < 7 else 0
        eduhigh = 1 if eduy > 12 else 0

        return ((1 / measure) - (0.01566 + 0.000315 * age_local - 0.00112 * edulow + 0.001465 * eduhigh - 0.0000032 * age_local ** 2)) / 0.0034
    return None

def calculate_zcore_stroop_part2(patient_id, measure):
    return None  # Not implemented

def calculate_zcore_stroop_part3(patient_id, measure):
    gender_local, eduy, age_local = get_initial_variables(patient_id)
    if eduy and age_local and gender_local:
        
        edulow = 1 if eduy < 7 else 0
        eduhigh = 1 if eduy > 12 else 0
        sex = 1 if gender_local == MALE else 0

        return ((1 / measure) - (0.001926 + 0.000348 * age_local + 0.0002244 * sex - 0.0006982 * edulow + 0.001015 * eduhigh - 0.000003522 * age_local ** 2)) / 0.002
    return None

def calculate_zcore_sdst(patient_id, measure):
    gender_local, eduy, age_local = get_initial_variables(patient_id)
    if age_local:
        thresholds = [
            (75, [(-1, -3), (0, -2.7), (1, -2.3), (2, -2), (4, -1.3), (6, -1), (8, -0.7),
                   (11, -0.3), (15, 0), (18, 0.3), (20, 0.7), (24, 1), (28, 1.3), (32, 1.7),
                   (41, 2), (45, 2.3), (47, 2.7), (50, 3)]),
            (69, [(-1, -3), (2, -2.7), (3, -2.3), (6, 2), (7, -1.7), (8, -1.3), (9, -1),
                   (11, -0.7), (14, -0.3), (18, 0), (20, 0.3), (24, 0.7), (27, 1), (30, 1.3),
                   (35, 1.7), (41, 2), (46, 2.3), (48, 2.7), (51, 3)]),
            (51, [(-1, -3), (3, -2.7), (4, -2.3), (6, -2), (7, -1.7), (8, -1.3), (12, -1),
                   (16, -0.7), (21, -0.3), (25, 0), (28, 0.3), (32, 0.7), (35, 1), (38, 1.3),
                   (41, 1.7), (42, 2), (46, 2.3), (54, 2.7), (56, 3)])
        ]

        for age_threshold, scores in thresholds:
            if age_local > age_threshold:
                for threshold, score in scores:
                    if measure > threshold:
                        return score
    return None