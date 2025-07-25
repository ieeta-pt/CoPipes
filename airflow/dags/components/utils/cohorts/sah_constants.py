PATIENT_ID_LABEL = "Patient ID"

DATE_FORMAT = "%d-%m-%Y"

NO 		= 2000000239
YES 	= 2000000238

PRIORITY_DOMAINS_IDS = { #IDs sorted by priority
	"Attention":{ #Priority Attention Type
		"source":[
            "2000000210", 
            "2000000276", 
            "2000000278", 
            "2000000424"
            ],
		"targetValue":"2000000180", "targetType":"2000000282", "zscore":"2000000181"
		}, 	
	"Executive":{ #Priority Executive Type
		"source":[
            "2000000212", 
            "2000000280"
            ],		
		"targetValue":"2000000182", "targetType":"2000000283", "zscore":"2000000183"
		},					 	
	"Language":	{ #Priority Language Type
		"source":[
            "2000000009", 
            "2000000144", 
            "2000000146", 
            "2000000011"
            ], 
		"targetValue":"2000000184", "targetType":"2000000284", "zscore":"2000000185"
		},					 	
	"MemoryDelayed": { #Priority Memory Type
		"source":[
			"2000000015",#1=RAVLT
			"2000000047",#2=CERAD
			"2000000611",#4=Story recall test
			"2000000152",#5=Logical memory
			"2000000134" #6=Hopkins
            ],  
		"targetValue":"2000000186", "targetType":"2000000285", "zscore":"2000000187"
		},						 	
	"MemoryImmediate":{ #Priority Memory Type
		"source":[
			"2000000017",#1=RAVLT
			"2000000049",#2=CERAD
			"2000000613",#4=Story recall test
			"2000000578",#5=Logical memory
			"2000000136" #6=Hopkins
		], 
		"targetValue":"2000000188", "zscore":"2000000189"
		},					 	
	"Visuoconstruction":{ #Priority Visuoconstruction Type
		"source":[
            "2000000054", 
            "2000000045", 
            "2000000062"
            ], 
		"targetValue":"2000000419", "targetType":"2000000657", "zscore":"2000000420"
		},	
	}

CONCEPT_NAMES = {#This dictionary was created to simplify the method for Pirority domain, consider refactor this
	"2000000210":"Trail Making Test A",
	"2000000276":"Stroop 1",
	"2000000278":"Stroop 2",
	"2000000424":"Symbol Digit Substitution Task",
	"2000000212":"Trail Making Test B", 
	"2000000280":"Stroop 3",
	"2000000009":"Animal Fluency 1 min", 
	"2000000144":"Letter Fluency 1 min", 
	"2000000146":"Letter Fluency 2 min", 
	"2000000011":"Animal Fluency 2 min", 
	"2000000015":"RAVLT Delayed",
	"2000000047":"CERAD Delayed",
	"2000000611":"Story recall test Delayed",
	"2000000152":"Logical memory  Delayed",
	"2000000134":"Hopkins Delayed",
	"2000000017":"RAVLT Immediate",
	"2000000049":"CERAD Immediate",
	"2000000613":"Story recall test Immediate",
	"2000000578":"Logical memory Immediate",
	"2000000136":"Hopkins Immediate",
	"2000000054":"Rey complex Figure copy",
	"2000000045":"Copy of CERAD Figures",
	"2000000062":"Clock Drawing",
	}

#Comorbidities to calculate yes
AAL_COMORBIDITIES = {
	"2000000637":{
		"name":"Cardiovascular Disorders",
		"concepts":["2000000326", "2000000341", "2000000357", "2000000360", "2000000367", "2000000390", "2000000400"]
	},
	"2000000638":{
		"name":"Cardiovascular Risk Factors",
		"concepts":["2000000381", "2000000382", "2000000383", "2000000396", "2000000402"]
	},
	"2000000639":{
		"name":"Cerebrovascular Disorders",
		"concepts":["2000000337", "2000000403", "2000000438", "2000000441"]
	},
	"2000000640":{
		"name":"Endocrine Disorders",
		"concepts":["2000000363", "2000000384", "2000000385", "2000000405"]
	},
	"2000000641":{
		"name":"Neurological Disorders",
		"concepts":["2000000378", "2000000408", "2000000416", "2000000434"]
	},
	"2000000473":{
		"name":"Other Cardiac Diseases",
		"concepts":["2000000334", "2000000379", "2000000415"]
	},
	"2000000642":{
		"name":"Psychiatric Disorders",
		"concepts":["2000000331", "2000000469", "2000000470", "2000000410"]
	},
	"2000000643":{
		"name":"Somatic Disorders",
		"concepts":["2000000343", "2000000432", "2000000433", "2000000412"]
	}
}