from datetime import datetime

def harmonizer(row):
    variableConcept = str(row["VariableConcept"])
    if "2000000049" in variableConcept:
        return readCeradWLRounds(row)
    if "2000000051" in variableConcept:
        return readCeradWLRecognition(row)
    if "2000000551" in variableConcept:
        return readDiagnosisAndEtiology(row)
    if "2000000013" in variableConcept:
        readApoE(row)

    if "2000000468" in variableConcept:
        return dealWithFamilyHistoryDementia(row)
    if "2000000434" in variableConcept:
        return dealWithSleepDisordersClinicalInformation(row)
    if "2000000609" in variableConcept:
        return dealWithGender(row)
    if "2000000293" in variableConcept:
        return dealWithCSFAssay(row)

    #Deal with the errors in the cohort
    if "2000000462" in variableConcept:
        return dealWithWeight(row)
    if "2000000388" in variableConcept:
        return dealWithHeight(row)
    if "2000000421" in variableConcept:
        return dealWithPulseRate(row)
    if "2000000358" in variableConcept:
        return dealWithCholesterol(row)
    if "2000000532" in variableConcept:
        return dealWithCSFMeasure(row)
    if "2000000068" in variableConcept:
        return dealWithAmyloidBeta138(row)

    return row

def readCeradWLRounds(row):
    global ceradWLRounds
    ceradWLRounds += [row]
    return []

def readCeradWLRecognition(row):
    global ceradWLRecognition
    ceradWLRecognition += [row]
    return []

def readApoE(row):
    global apoE
    apoE += [row]

def readDiagnosisAndEtiology(row):
    global diagnosis, etiology
    if row["Variable"] == "Diagnosis":
        diagnosis[row["Patient ID"]] = row
    if row["Variable"] == "Etiology":
        etiology[row["Patient ID"]] = row
    return []

def dealWithFamilyHistoryDementia(row):
    #convert 0 = no or 1 = yes
    row["MeasureNumber"] = None
    if row["Measure"] == '0':
        row["MeasureConcept"] = 2000000239
    if row["Measure"] == '1':
        row["MeasureConcept"] = 2000000238
    return row

def dealWithSleepDisordersClinicalInformation(row):
    if row["Measure"] == "n.b.":
        row["MeasureString"] = None
    return row

def dealWithGender(row):
    #convert {1:8507, 0:8532}
    row["MeasureNumber"] = None
    if row["Measure"] == '0':
        row["MeasureConcept"] = 8532
    if row["Measure"] == '1':
        row["MeasureConcept"] = 8507
    return row

def dealWithCSFAssay(row):
    '''
    CSF date before 03.12.2014:
        Assay: Innotest
    CSF date between 03.12.2014 and 31.12.2016:
        Assay: MSD
    CSF date after 31.12.2016:
        Assay: Luminex
    '''
    try:
        date = datetime.datetime.strptime(row['Date of puncture (Liquor)'], '%d-%M-%Y')
    except:
        print("No date defined in CSF Assay:\t", row)
        return []
    if date < datetime.datetime(2014, 12, 3):
        row["MeasureString"] = "Innotest"
    elif date < datetime.datetime(2016, 12, 31):
        row["MeasureString"] = "MSD"
    else:
        row["MeasureString"] = "Luminex"
    row["MeasureNumber"] = None
    return row

def dealWithWeight(row):
    if row["Measure"].isdigit():
        if float(row["Measure"]) < 0 or float(row["Measure"]) > 150:# remove invalid weights
            return []
        return row
    return []

def dealWithHeight(row):
    if row["Measure"].isdigit():
        if float(row["Measure"]) < 100 or float(row["Measure"]) > 230:# remove invalid heights
            return []
        return row
    return []

def dealWithPulseRate(row):
    if row["Measure"].isdigit():
        return row
    return []

def dealWithCholesterol(row):
    if row["Measure"].isdigit():
        return row
    return []

def dealWithCSFMeasure(row):
    if row["Measure"].isdigit():
        return row
    return []

def dealWithAmyloidBeta138(row):
    if row["Measure"].isdigit():
        return row
    return []

def processCeradWLRounds():
    global ceradWLRounds
    results = []
    if len(ceradWLRounds) > 0:
        #key will be (patient, date)
        measureDict = {}
        sumOfMeasuresDict = {} 
        for entry in ceradWLRounds:
            if (entry["Patient ID"], entry["Date of neuropsychological testing"]) in sumOfMeasuresDict:
                sumOfMeasuresDict[(entry["Patient ID"], entry["Date of neuropsychological testing"])] += int(entry["Measure"])
                measureDict[(entry["Patient ID"], entry["Date of neuropsychological testing"])] += "," + str(entry["Measure"])
            else:
                sumOfMeasuresDict[(entry["Patient ID"], entry["Date of neuropsychological testing"])] = int(entry["Measure"])
                measureDict[(entry["Patient ID"], entry["Date of neuropsychological testing"])] = str(entry["Measure"])
        for entry in sumOfMeasuresDict:
            results += [{
                'Patient ID':entry[0],
                'Date of neuropsychological testing':entry[1],
                'Variable': '[Cerad WL round 1, Cerad WL round 2, Cerad WL round 3]', 
                'Measure': measureDict[entry],
                'MeasureNumber': sumOfMeasuresDict[entry], 
                'VariableConcept': '2000000049', 
                'MeasureConcept': None
            }]
    ceradWLRounds = []
    return results
    
def processCeralWLRecognition():
    global ceradWLRecognition
    results = []
    if len(ceradWLRecognition) > 0:
        #key will be (patient, date)
        measureDict = {}
        sumOfMeasuresDict = {} 
        for entry in ceradWLRecognition:
            if (entry["Patient ID"], entry["Date of neuropsychological testing"]) in sumOfMeasuresDict:
                sumOfMeasuresDict[(entry["Patient ID"], entry["Date of neuropsychological testing"])] += int(entry["Measure"])
                measureDict[(entry["Patient ID"], entry["Date of neuropsychological testing"])] += "," + str(entry["Measure"])
            else:
                sumOfMeasuresDict[(entry["Patient ID"], entry["Date of neuropsychological testing"])] = int(entry["Measure"])
                measureDict[(entry["Patient ID"], entry["Date of neuropsychological testing"])] = str(entry["Measure"])
        for entry in sumOfMeasuresDict:
            results += [{
                'Patient ID':entry[0],
                'Date of neuropsychological testing':entry[1],
                'Variable': '[Cerad WL recognition no, Cerad WL recognition yes]', 
                'Measure': measureDict[entry],
                'MeasureNumber': (sumOfMeasuresDict[entry] - 10), 
                'VariableConcept': '2000000051', 
                'MeasureConcept': None
            }]
    ceradWLRecognition = []
    return results

def processDiagnosisAndEtiology():
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
            concept = "2000000254" #MCI
        elif str(row['Measure']) == "1":
            concept = "2000000256" #SCI
        elif str(row['Measure']) == "81" or str(row['Measure']) == "8":
            concept = "2000000470" #Depression
        elif str(row['Measure']) == "2" or str(row['Measure']) == "3":
            concept = "2000000700" #Other
        elif str(row['Measure']) == "5" or str(row['Measure']) == "6" or str(row['Measure']) == "7":
            if patient in etiology:
                if str(etiology[patient]['Measure']) == "1":
                    concept = "2000000255" #AD
                elif str(etiology[patient]['Measure']) == "2":
                    concept = "2000000701" #Mixed dementia
                elif str(etiology[patient]['Measure']) == "3":
                    concept = "2000000685" #VAD
                elif str(etiology[patient]['Measure']) == "5":
                    concept = "2000000665" #FTD
                elif str(etiology[patient]['Measure']) == "8":
                    concept = "2000000699" #Other Dementia

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

def processApoE():
    global apoE
    print("Check and remove this shit, because now we have a standard ad hoc method for this")
    results = []
    if len(apoE) > 0:
        for row in apoE:
            measures = row['Measure'].split("/")
            if len(measures) == 2:
                results += [{
                    'Patient ID': row['Patient ID'],
                    'Date of puncture (Liquor)': row['Date of puncture (Liquor)'],
                    'Variable': row['Variable'],
                    'Measure': row['Measure'],
                    'VariableConcept': '2000000320', #ApoE Allele 1
                    'MeasureConcept': None,
                    'MeasureNumber': None,
                    'MeasureString': measures[0]
                    },{
                    'Patient ID': row['Patient ID'],
                    'Date of puncture (Liquor)': row['Date of puncture (Liquor)'],
                    'Variable': row['Variable'],
                    'Measure': row['Measure'],
                    'VariableConcept': '2000000321', #ApoE Allele 2
                    'MeasureConcept': None,
                    'MeasureNumber': None,
                    'MeasureString': measures[1]
                    },{
                    'Patient ID': row['Patient ID'],
                    'Date of puncture (Liquor)': row['Date of puncture (Liquor)'],
                    'Variable': row['Variable'],
                    'Measure': row['Measure'],
                    'VariableConcept': '2000000014', #ApoE4 Carrier
                    'MeasureConcept': None,
                    'MeasureNumber': None,
                    'MeasureString': "Yes" if measures[0] == "4" or measures[1] == "4" else "No"
                    }]
    apoE = []
    return results