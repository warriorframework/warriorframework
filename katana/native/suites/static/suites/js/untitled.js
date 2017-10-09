class projectDetailsObject{

	mapJSONdataToSelf(jsonDetailsData) {
			console.log(jsonDetailsData);
				
			this.fillDefaults();           // Fills internal values only
			console.log(jsonDetailsData);
				
			if (jsonDetailsData) {         // Overridden by incoming data.
				this.Name = jsonDetailsData['Name'];  
				this.Title = jsonDetailsData['Title']; 
				this.State = jsonDetailsData['State']; 
				this.Engineer = jsonDetailsData['Engineer']; 
				this.cDate = jsonDetailsData['Date']; 
				this.cTime = jsonDetailsData['Time']; 
				
				if (jsonDetailsData['default_onError']) {
					if ( jsonDetailsData['default_onError']['@action']) this.default_onError_action = jsonDetailsData['default_onError']['@action']; 
					if ( jsonDetailsData['default_onError']['@value'] ) this.default_onError_value = jsonDetailsData['default_onError']['@value']; 			
				}
			}
	}

	getJSON(){
		return { 
			'Name': this.Name, 
			'Title': this.Title,
			'Category' : this.Category, 
			'Engineer' : this.Engineer, 
			'Resultsdir' : this.Resultsdir, 
			'State' : this.State,
			'Time': this.cDate; 
			'Date' : this.cTime;
			'default_onError': { '@action': this.default_onError_action, '@value': this.default_onError_value},
		};
	}

	constructor(jsonDetailsData) {
			this.mapJSONdataToSelf(jsonDetailsData);
	}

	setTimeStamp() { 
		var date = new Date();
	   	var year = date.getFullYear();
	   	var month = date.getMonth() + 1;// months are zero indexed
	   	var day = date.getDate();
	   	var hour = date.getHours();
	   	var minute = date.getMinutes();
	   	if (minute < 10) {
	       	minute = "0" + minute; 
	       }
		this.cDate = month + "/" + day + "/" + year; 
		this.cTime = hour + ":" + minute; 
	}


	fillDefaults() {
		this.Name = '';  
		this.Title = ''; 
		this.Category = ''; 
		this.Engineer = ''; 
		this.Resultsdir = ''; 
		this.State = ''; 
		this.default_onError_action = ''; 
		this.default_onError_value = ''; 
		this.setTimeStamp();
	}

	duplicateSelf() { 
		return jQuery.extend(true, {}, this); 
	}
}



class projectSuiteObject {
	constructor(inputJsonData) {
		var jsonData = inputJsonData;
		this.setupFromJSON(jsonData);
	}

	setupFromJSON(jsonData) { 
		if (!jsonData) {
			jsonData = 	this.createEmptyCase(); 
		}
		// Fill defaults here. 
		this.fillDefaults(jsonData);
		this.path = jsonData['path'];
		this.context = jsonData['context'].toLowerCase();
		this.runtype = jsonData['runtype'].toLowerCase();
		this.impact = jsonData['impact'].toLowerCase();
		this.InputDataFile = jsonData['InputDataFile'];
		this.runmode_value = jsonData['runmode']['@value'].toLowerCase();
		this.runmode_type = jsonData['runmode']['@type'].toLowerCase();
		this.Execute_ExecType = jsonData['Execute']['@ExecType'].toLowerCase();
		this.Execute_Rule_Condition = jsonData['Execute']['Rule']['@Condition'].toLowerCase();
		this.Execute_Rule_Condvalue = jsonData['Execute']['Rule']['@Condvalue'];
		this.Execute_Rule_Else = jsonData['Execute']['Rule']['@Else'].toLowerCase();
		this.Execute_Rule_Elsevalue = jsonData['Execute']['Rule']['@Elsevalue'];
		this.onError_action = jsonData['onError']['@action'];
		this.onError_value = jsonData['onError']['@value'];	

	}

	getJSON(){
		return {
			'path': this.path,
			'impact': this.impact,
			'InputDataFile' : this.InputDataFile,
			'runmode' : { "@value": this.runmode_value, "@type": this.runmode_type },
			'onError': { "@action": this.onError_action, "@value": this.onError_value },
			'Execute': { "@ExecType": this.Execute_ExecType, 
				"Rule": { "@Condition": this.Execute_Rule_Condition, "@Condvalue": this.Execute_Rule_Condvalue , 
					"@Else": this.Execute_Rule_Else , "@Elsevalue": this.Execute_Rule_Elsevalue } 
			},
		};

	}

	copyToDocument(tag, obj) {
		localStorage.setItem(tag, JSON.stringify(obj.getJSON()));
	}

	copyFromDocument(tag) {
		return JSON.parse(localStorage.getItem(tag));
	}

	fillDefaults(jsonData){


		if (!oneSuite['path']) {
			jsonData['path'] =  "New";
		}

		if (!oneSuite['impact']) {
			jsonData['impact'] =  "impact";
		}

		if (! jsonData['runmode']) {
			jsonData['onError'] = { "@type": "standard", "@value": "" };
		}
		if (! jsonData['runmode']['@value']) {
			jsonData['onError'] = { "@type": "standard", "@value": "" };
		}
		if (! jsonData['runmode']['@type']) {
			jsonData['onError'] = { "@type": "standard", "@value": "" };
		}

		if (!jsonData['onError']) {
			jsonData['onError'] = { "@action": "next", "@value": "" };
		}
		if (!jsonData['onError']['@value']) {
			jsonData['onError']['@value'] = "";
		}

		if (!jsonData['Execute']) {
			jsonData['Execute'] = { "@ExecType": "yes", "Rule": { "@Condition": "", "@Condvalue": "", "@Else": "next", "@Elsevalue": "" } };
		}
		if (!jsonData['Execute']['@ExecType']) {
			jsonData['Execute'] = { "@ExecType": "yes", "Rule": { "@Condition": "", "@Condvalue": "", "@Else": "next", "@Elsevalue": "" } };
		}
		if (!jsonData['Execute']['Rule']) {
			jsonData['Execute'][ "Rule"] = { "@Condition": "", "@Condvalue": "", "@Else": "next", "@Elsevalue": "" } ;
		}
		return jsonData;

	}

	createEmptyCase() {
		return {
			'path': '',
			'context': 'positive',
			'runtype': 'sequential_keywords',
			'runmode' : { "@value": "standard", "@type": "" },
			'onError': { "@action": "next", "@value": "" },
			'Execute': { "@ExecType": "yes", 
				"Rule": { "@Condition": "", "@Condvalue": "", "@Else": "next", "@Elsevalue": "" } 
			},
		};

	}
}


class projectsObject{
	constructor(jsonData){
		this.mapJsonData(jsonData);
	}
	mapJsonData(jsonData){ 
			console.log("In constructor", jsonData);
			if (!jsonData['Details']) {
				this.Details = new projectDetailsObject(null);
			} else {
				this.Details = new projectDetailsObject(jsonData['Details'])
			}

			
			if (!jsonData['Testsuites']) {
				jsonData['Testsuites']['Testsuite'] = [] 
			} 
			if (!jsonData['Testsuites']['Testsuite']) {
				jsonData['Testsuites']['Testsuite'] = [] 
			} 
			//
			if (!jQuery.isArray(jsonData['Testsuites']['Testsuite'])) {
			 jsonData['Testsuites']['Testsuite'] = [ jsonData['Testsuites']['Testsuite'] ];
			}

			this.Testsuites = [];
			for (var k=0; k<jsonData['Testsuites']['Testsuite'].length; k++) {	
				var ts = new projectSuiteObject(jsonData['Testsuites']['Testsuite'][k]);
				this.Testsuites.push(ts);
				}
			// 
			}

		getJSON(){
			var testsuitesJSON = [];
			for (var ts =0; ts< this.Testsuites.length; ts++ ) {
				testsuitesJSON.push(this.Testsuites[ts].getJSON());
			}
			console.log(this);

			return { 'Details': this.Details.getJSON(), 
				'Testsuites' :  testsuitesJSON };
		}

	}