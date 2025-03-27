import sah_constants as sahc

Relation = {
	"2000000070":{"cutOff"	:"2000000297", "cutOffName"		:"Amyloid Beta 1-42 Cut-off",
				  "abnormal":"2000000071", "abnormalName"	:"Amyloid Beta 1-42 Abnormal"},
	"2000000073":{"cutOff"	:"2000000463", "cutOffName"		:"Phosphorylated Tau Cut-off", 
				  "abnormal":"2000000074", "abnormalName"	:"Phosphorylated Tau Abnormal"},
	"2000000075":{"cutOff"	:"2000000298", "cutOffName"		:"Total Tau Cut-off", 
				  "abnormal":"2000000076", "abnormalName"	:"Total Tau Abnormal"},
	"2000000168":{"cutOff"	:"2000000310", "cutOffName"		:"MTA Bilateral Abnormal Cut-off", 
				  "abnormal":"2000000169", "abnormalName"	:"MTA Bilateral Abnormal"},
	"2000000121":{"cutOff"	:"", 		   "cutOffName"		:"", 
				  "abnormal":"2000000122", "abnormalName"	:"HDS Abnormal"}
}

def calculate(rowData, variableConcept, cutOffs):
	if variableConcept in Relation:
		if Relation[variableConcept]["cutOff"] in cutOffs:
			if "conditionalMethod" in cutOffs[Relation[variableConcept]["cutOff"]]:
				#This is a method
				operator, value = cutOffs[Relation[variableConcept]["cutOff"]]["conditionalMethod"](dict(rowData))
				if value == None:
					return []
			else:
				operator = cutOffs[Relation[variableConcept]["cutOff"]]["operator"]
				value = cutOffs[Relation[variableConcept]["cutOff"]]["value"]
			cutOffResult = __cutOffBuilder(dict(rowData), variableConcept, operator, value)
			abdnormalResult = __abnormalBuilder(dict(rowData), variableConcept, operator, value)
			return [cutOffResult, abdnormalResult]
		elif Relation[variableConcept]["abnormal"] in cutOffs:#special cases like HDS with abnormal but without cut off
			operator = cutOffs[Relation[variableConcept]["abnormal"]]["operator"]
			value = cutOffs[Relation[variableConcept]["abnormal"]]["value"]
			abdnormalResult = __abnormalBuilder(dict(rowData), variableConcept, operator, value)
			return [abdnormalResult]
	return [] 

def __cutOffBuilder(row, variableConcept, operator, value):
	row['Variable'] 		= Relation[variableConcept]["cutOffName"]
	row['VariableConcept'] 	= Relation[variableConcept]["cutOff"]
	row['Measure'] 			= "Calculated automatically"
	row['MeasureNumber'] 	= None
	row['MeasureString'] 	= operator + str(value)
	return row

def __abnormalBuilder(self, row, variableConcept, operator, cutOffValue):
	value = row['Measure']
	row['Variable'] 		= Relation[variableConcept]["abnormalName"]
	row['VariableConcept'] 	= Relation[variableConcept]["abnormal"]
	row['Measure'] 			= "Calculated automatically"
	row['MeasureNumber'] 	= None
	if operator == ">":
		row['MeasureConcept'] = sahc.YES if float(value) > float(cutOffValue) else sahc.NO
	elif operator == "<":
		row['MeasureConcept'] = sahc.YES if float(value) < float(cutOffValue) else sahc.NO
	else:
		print("Abnormal calculator error:", operator, "operator not recognized! Variable:", Relation[variableConcept]["abnormalName"])
		return []
	return row