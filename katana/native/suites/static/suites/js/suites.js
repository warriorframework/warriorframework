//
//
/*
/// -------------------------------------------------------------------------------

Suite File Data Handler 

Author: 
Date: 

The functions in this module are designed specifically for handling Suite XML files
for the warrior framework. 

It is expected to work with the editSuite.html file and the calls to editSuite in 
the views.py python for Django. 
/// -------------------------------------------------------------------------------

*/ 
function jsUcfirst(string) 
{
    return string.toLowerCase();
}	



function absFromPrefix(pathToBase, pathToFile) {
	// Converts an absolute path to one that is relative to pathToBase 
	// Input: 
	// 
	if (!pathToFile) return "";
	if (pathToFile.length < 1) return "";
	var bf = pathToBase.split('/');
	var rf = pathToFile.split('/');
	var nrf = pathToFile.split('/');
	//console.log("Removing", nrf, bf);
	
	for (var i=0;i< rf.length; i++) {
		if (rf[i] == "..")  { 
			bf.pop();
			nrf.splice(0,1);
			//console.log("Removing", nrf, bf);
	
		} else {
			break;
		}
	}
	return bf.join('/') + '/' + nrf.join('/');
}


function prefixFromAbs(pathToBase, pathToFile) {
	var stack = []; 
    var upem  = [];
	var bf = pathToBase.split('/');
	var rf = pathToFile.split('/');
	for (var i=0;i< rf.length; i++) {
		if (rf[i] == bf[i]) { 
			stack.push(bf[i]);
		} else {
			break;
		}
	}
	var tlen = bf.length - stack.length; 
	var blen = stack.length;
	// console.log("bf=",bf);
	// console.log("rf=",rf);
	// console.log("prefixFromAbs", rf, tlen, blen, stack);
    for (var k=0;k < tlen; k++) {
		upem.push("..");
	}
	var tail = rf.splice(blen,rf.length);
	// console.log('tail=', tail);
	return upem.join("/") + "/" +   tail.join('/');
}

class suiteDetailsObject{

	mapJSONdataToSelf(jsonDetailsData) {
			console.log(jsonDetailsData);
				
			this.fillDefaults();           // Fills internal values only
			console.log(jsonDetailsData);
				
			if (jsonDetailsData) {         // Overridden by incoming data.
				this.Name = jsonDetailsData['Name'];  
				this.Title = jsonDetailsData['Title']; 
				this.Category = jsonDetailsData['Category']; 
				this.Engineer = jsonDetailsData['Engineer']; 
				this.Resultsdir = jsonDetailsData['Resultsdir']; 
				this.State = jsonDetailsData['State']; 
				this.InputDataFile = jsonDetailsData['InputDataFile'];
				// Fill only if they exist...
				if (jsonDetailsData['default_onError']) {
					if ( jsonDetailsData['default_onError']['@action']) this.default_onError_action = jsonDetailsData['default_onError']['@action']; 
					if ( jsonDetailsData['default_onError']['@value'] ) this.default_onError_value = jsonDetailsData['default_onError']['@value']; 			
				}
				if ( jsonDetailsData['type']['@exectype'] )this.ExecType = jsonDetailsData['type']['@exectype']; 
				if ( jsonDetailsData['type']['@Num_attempts']) this.ExecType_num_attempts = jsonDetailsData['type']['@Num_attempts']; 
				if ( jsonDetailsData['type']['@Max_attempts']) this.ExecType_max_attempts = jsonDetailsData['type']['@Max_attempts']; 
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
			'Time': this.cDate,
			'Date' : this.cTime,

			'default_onError': { '@action': this.default_onError_action, '@value': this.default_onError_value},
			'InputDataFile' : this.InputDataFile,
			'type' : { "@exectype":this.ExecType,'@Number_Attempts': this.ExecType_num_attempts, '@Max_Attempts':  this.ExecType_max_attempts}
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
		this.InputDataFile = '';
		
		this.ExecType = ''; 
		this.ExecType_num_attempts = ''; 
		this.ExecType_max_attempts = ''; 
		this.setTimeStamp();
	}

	duplicateSelf() { 
		return jQuery.extend(true, {}, this); 
	}
}



class suiteRequirementsObject{

	constructor (jsonRequirements) { 
		this.aRequirements = [];
		if (!jsonRequirements) return this; 
		for (var k =0; k < jsonRequirements.length; k++ ) {
			this.aRequirements.push(jsonRequirements[k]);
		}
	}

	getJSONdata() {
		return this.aRequirements; 
		// var r = [];
		// for (var k=0; k < this.aRequirements.length; k++) {
		// 	r.push( this.aRequirements[k] );
		// }
		// return r ;  // this matches the XML ... 
	}

	insertRequirement(where,what){
		this.aRequirements.splice(where,0,what);
	}

	getRequirements() {
		return this.aRequirements;
	}



	getLength() {
		return this.aRequirements.length; 
	}

	setRequirement(s,v){
		this.aRequirements[s]=v;
	}

	deleteRequirement(sid) {
		this.aRequirements.splice(s,1);
	}
}

class suiteCaseObject {
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
			'context': this.context,
			'runtype': this.runtype,
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
		if (!jsonData['onError']['@action']) {
			jsonData['onError']['@action'] = "";
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


class testSuiteObject{
	constructor(jsonData){
		this.mapJsonData(jsonData);
	}
	mapJsonData(jsonData){ 
			console.log("In constructor", jsonData);
			if (!jsonData['Details']) {
				this.Details = new suiteDetailsObject(null);
			} else {
				this.Details = new suiteDetailsObject(jsonData['Details'])
			}

			if (!jsonData['Requirements']) {
				jsonData['Requirements'] = [] 
			} 
			if (!jsonData['Requirements']['Requirement']) {
				jsonData['Requirements']['Requirement']= [] 
			}
			if (!jQuery.isArray(jsonData['Requirements']['Requirement'] )) {
				jsonData['Requirements']['Requirement'] = [jsonData['Requirements']['Requirement']];
			}

			this.Requirements = new suiteRequirementsObject(jsonData['Requirements']['Requirement']);
			console.log("After", jsonData['Testcases']);
			
			if (!jsonData['Testcases']) {
				jsonData['Testcases']['Testcase'] = [] 
			} 
			if (!jsonData['Testcases']['Testcase']) {
				jsonData['Testcases']['Testcase'] = [] 
			} 
			//
			if (!jQuery.isArray(jsonData['Testcases']['Testcase'])) {
			 jsonData['Testcases']['Testcase'] = [ jsonData['Testcases']['Testcase'] ];
			}

			this.Testcases = [];
			for (var k=0; k<jsonData['Testcases']['Testcase'].length; k++) {	
				var ts = new suiteCaseObject(jsonData['Testcases']['Testcase'][k]);
				this.Testcases.push(ts);
				}
			// 
			}

		getJSON(){
			var testcasesJSON = [];
			for (var ts =0; ts< this.Testcases.length; ts++ ) {
				testcasesJSON.push(this.Testcases[ts].getJSON());
			}
			console.log(this);

			return { 'Details': this.Details.getJSON(), 
				'Requirements' : { 'Requirement': this.Requirements.getJSONdata() },
				'Testcases' :  testcasesJSON };
		}

	}



var suites= {

	jsonSuiteObject : null,
	jsonTestcases : null,			// for all Cases
	
	startNewSuite: function() {
	  var xref="./suites/editSuite/?fname=NEW"; 
	  katana.templateAPI.load(xref, null, null, 'SuiteNew') ;
	   katana.$view.one('tabAdded', function(){
	      suites.mapFullSuiteJson("NEW");
	  });
	},


	initSuiteTree: function(){
		//console.log("Starting suite ");
		jQuery.getJSON("./suites/getSuiteListTree/").done(function(data) {
			var sdata = data['treejs'];
			console.log("tree ", sdata);
			var jdata = { 'core' : { 'data' : sdata }}; 
			
			katana.$activeTab.find('#mySuiteTree').on("select_node.jstree", function (e, data) { 
			      var thePage = data.node.li_attr['data-path'];
			      console.log(thePage);
			      var extn = thePage.indexOf(".xml");
			      if (extn < 4){
			        return;
			      }
			 	//     katana.$view.one('tabAdded', function(){
			 	//     suites.mapFullSuiteJson(thePage);
		  		// });
		  	  	suites.thefile = thePage; 
		  		var xref="./suites/editSuite/?fname=" + thePage; 
			  	//katana.$activeTab.find("#OverwriteSuiteHere").load(xref, function() {
			  		katana.templateAPI.subAppLoad(xref, null, function(thisPage) { 
		
			   			console.log("starting ...", this);
				  		suites.mapFullSuiteJson(suites.thefile);
				  });


		  		//katana.templateAPI.load(xref, null, null, 'Suite') ;
				});
			katana.$activeTab.find('#mySuiteTree').jstree(jdata); 
		});

	},
/// -------------------------------------------------------------------------------
// Sets up the global Suite data holder for the UI. 
// This is called from the correspoding HTML file onLoad event 
// or when a new XML file is loaded into the interface.
// 
// Two variables are set when this function is called; 
// 1. suites.jsonSuiteObject 
// 2. suites.jsonTestcases is set to point to the Testcases data structure in
//    the suites.jsonSuiteObject
//
/// -------------------------------------------------------------------------------
	mapFullSuiteJson: function(incomingFile){
	var myfile = katana.$activeTab.find('#fullpathname').text();
	if (incomingFile) {
		myFile = incomingFile; 
	}
	
	jQuery.getJSON("./suites/getJSONSuiteData/?fname="+myfile).done(function(data) {
			var sdata = data['fulljson'];
			console.log("from views.py call=", sdata);
			suites.jsonSuiteObject = new testSuiteObject(sdata['TestSuite']);
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
			suites.mapSuiteJsonToUi();  // This is where the table and edit form is created. 
			katana.$activeTab.find('#default_onError').on('change',suites.fillSuiteDefaultGoto );
			katana.$activeTab.find('#suiteState').on('change',suites.fillSuiteState );
			katana.$activeTab.find('#suiteDatatype').on('change',suites.fillSuiteDataOptions);
		});
	} ,

	fillSuiteDataOptions: function() { 
		var datatype = this.value; 
		datatype = datatype.toLowerCase(); 
		katana.$activeTab.find('#data_type_max_attempts').hide();
		katana.$activeTab.find('#data_type_num_attempts').hide();
		if (datatype == 'ruf' || datatype=='rup') {
			katana.$activeTab.find('#data_type_max_attempts').show();
		}
		if (datatype =='rmt'){
			katana.$activeTab.find('#data_type_num_attempts').show();
		}
	},


	fillSuiteState: function (){
		var state = this.value; 
		if (state == 'Add Another') {
			var name = prompt("Please Enter New State");
			if (name) {
			katana.$activeTab.find('#suiteState').append($("<option></option>").attr("value", name).text(name));
			}
		}
	},


/// -------------------------------------------------------------------------------
// Dynamically create a new Testcase object and append to the suites.jsonTestcases 
// array. Default values are used to fill in a complete structure. If there is 
// no default value, a null value is inserted for the keyword
/// -------------------------------------------------------------------------------
	addCaseToSuite: function(){
		var newTestcase =	new suiteCaseObject(); 	
		console.log(suites.jsonTestcases);
		suites.jsonTestcases.push(newTestcase);
		suites.createCasesTable(suites.jsonTestcases);
	},
	 
	insertCaseToSuite: function(sid, copy){
		var newTestcase =new suiteCaseObject(); 		
		suites.jsonTestcases.splice(sid,0,newTestcase);
		suites.createCasesTable(suites.jsonTestcases);
	},

	mapSuiteCaseToUI: function(s,popup) {

	// This is called from an event handler ... 
	var xdata = suites.jsonTestcases;
	console.log(s, xdata);
	var oneCase = xdata[s];
	console.log(oneCase);
	console.log(oneCase['path']);
	popup.find("#CaseRowToEdit").val(s); 
	katana.$activeTab.attr('suite_case_row',s);  // for the file dialog.
	console.log(popup.find("#CaseRowToEdit").val());
	//katana.$activeTab.find("CasePath").val(oneCase['path']);
	popup.attr('oneCase', s);
	popup.find('#CasePath').val(oneCase.path);
	popup.find('#CaseContext').val(oneCase.context);
	popup.find('#CaseRuntype').val(oneCase.runtype);
	popup.find('#CaseImpact').val(oneCase.impact);
	popup.find("#suiteExecuteAtExecType").val(oneCase.Execute_ExecType); 
	popup.find("#executeRuleAtCondition").val(oneCase.Execute_Rule_Condition); 
	popup.find("#executeRuleAtCondvalue").val(oneCase.Execute_Rule_Condvalue); 
	popup.find("#executeRuleAtElse").val(oneCase.Execute_Rule_Else); 
	popup.find("#executeRuleAtElsevalue").val(oneCase.Execute_Rule_Elsevalue); 
	popup.find("#StepInputDataFile").val(oneCase.InputDataFile); 

	suites.fillSuiteCaseDefaultGoto(popup);
	popup.find('#caseonError-at-action').on('change', function(){ 
			
			suites.fillSuiteCaseDefaultGoto(suites.lastPopup);
	});
	console.log("FOUND Run mode  TYPE ",oneCase.runmode_type )
	popup.find('.runmode_condition').show();
	oneCase.runmode_type = oneCase.runmode_type.toLowerCase();
	if (oneCase.runmode_type === 'standard') {
		console.log("Hiding... ",oneCase.runmode_type  )
		popup.find('.runmode_condition').hide();
	}

	popup.find('.rule-condition').hide();
	if (oneCase.Execute_ExecType) {
		console.log("FOUND EXECT TYPE ",oneCase.Execute_ExecType )
		if (oneCase.Execute_ExecType == 'if' || oneCase.Execute_ExecType == 'if not') {
			popup.find('.rule-condition').show();
		} else {
		console.log("FOUND EXECT TYPE as  ",oneCase.Execute_ExecType )
		}	
	}
	popup.find("#suiteExecuteAtExecType").on('change',function() {
			if (this.value == 'if' || this.value == 'if not') {
				popup.find('.rule-condition').show();			
			} else {
				popup.find('.rule-condition').hide();
				
			}
		});
	
	popup.find("#CaseRunmode").on('change',function() {
			var mode = this.value.toLowerCase();
			if ( mode === 'standard') {
				popup.find('.runmode_condition').hide();	
					
			} else {
				popup.find('.runmode_condition').show();
					
			}
		});


},


/// -------------------------------------------------------------------------------
// This function is called to map the currently edited Suite Case to 
// the field being edited. 
// Note that this function is calld from an event handler which catches the 
// row number from the table.
/// -------------------------------------------------------------------------------
	mapUItoSuiteCase: function(){
		var popup = suites.lastPopup; 
		var s = parseInt(popup.find("#CaseRowToEdit").val());
		var oneCase = suites.jsonTestcases[s];
		console.log("Item ",s, oneCase);
		oneCase.impact = popup.find('#CaseImpact').val();
		oneCase.path = popup.find('#CasePath').val();
		oneCase.context= popup.find('#CaseContext').val();
		oneCase.runtype= popup.find('#CaseRuntype').val();	
		oneCase.runmode_type= popup.find('#CaseRunmode').val();
		oneCase.runmode_value= popup.find('#CaseRunmodeAtValue').val();
		oneCase.onError_action= popup.find("#caseonError-at-action").val();
		oneCase.onError_value= popup.find("#caseonError-at-value").val();
		oneCase.Execute_Rule_Condition = popup.find("#executeRuleAtCondition").val(); 
		oneCase.Execute_Rule_Condvalue= popup.find("#executeRuleAtCondvalue").val(); 
		oneCase.Execute_Rule_Else= popup.find("#executeRuleAtElse").val(); 
		oneCase.Execute_Rule_Elsevalue= popup.find("#executeRuleAtElsevalue").val(); 
		
		var exectype = popup.find("#suiteExecuteAtExecType").val();
		oneCase.Execute_ExecType = exectype ; 
		console.log(popup.find('#suiteExecuteAtExecType').val(),popup.find('#CaseImpact').val());
		console.log("After saving", s, oneCase);
},
/*
Collects data into the global Suite data holder from the UI and returns the XML back 
NOTE: At the time of writing I am using jQuery and Bootstrap to show the data.

Two global variables are heavily used when this function is called; 
1. suites.jsonSuiteObject 
2. suites.jsonTestcases which is set to point to the Testcases data structure in
   the suites.jsonSuiteObject

*/
	mapUiToSuiteJson: function() {

		if (katana.$activeTab.find("#suiteName").val().length < 1) {
			data = { 'heading': "Error", 'text' : "Please specific a suite name "}
			katana.openAlert(data);
			return
		}
		if (katana.$activeTab.find("#suiteTitle").val().length < 1) {
			data = { 'heading': "Error", 'text' : "Please specific a title "}
			katana.openAlert(data);
			return
		}

		if (katana.$activeTab.find("#suiteEngineer").val().length < 1) {
					data = { 'heading': "Error", 'text' : "Please specific a name for the engineer"}
			katana.openAlert(data);
			return
		}

	// Add an XML to saved file name 
		var xfname = katana.$activeTab.find('#suiteName').val();
		if (xfname.indexOf(".xml") < 0) {
			xfname = xfname + '.xml';
			}
		katana.$activeTab.find('#savefilepath').text(xfname);
		katana.$activeTab.find('#my_file_to_save').val(xfname);

		suites.jsonSuiteObject.Details.Name = katana.$activeTab.find('#suiteName').val();
		suites.jsonSuiteObject.Details.Title = katana.$activeTab.find('#suiteTitle').val();
		suites.jsonSuiteObject.Details.Engineer = katana.$activeTab.find('#suiteEngineer').val();
		suites.jsonSuiteObject.Details.Resultsdir = katana.$activeTab.find('#suiteResults').val();
		suites.jsonSuiteObject.Details.State = katana.$activeTab.find('#suiteState').val();
		suites.jsonSuiteObject.Details.default_onError_action = katana.$activeTab.find('#default_OnError').val();
		suites.jsonSuiteObject.Details.default_onError_value = katana.$activeTab.find('#default_OnError_goto').val();
		suites.jsonSuiteObject.Details.InputDataFile = katana.$activeTab.find('#suiteInputDataFile').val();
		suites.jsonSuiteObject.Details.ExecType = katana.$activeTab.find("#suiteDatatype").val();
		suites.jsonSuiteObject.Details.ExecType_num_Attempts = katana.$activeTab.find("#data_type_num_attempts").val();
		suites.jsonSuiteObject.Details.ExecType_max_Attempts = katana.$activeTab.find("#data_type_max_attempts").val();
		suites.jsonSuiteObject.Details.setTimeStamp();


		var xfname = suites.jsonSuiteObject.Details.Name;
		if (xfname.indexOf(".xml") < 2) {
			xfname = xfname + ".xml";
		}
		
		console.log(suites.jsonSuiteObject);
		console.log(suites.jsonSuiteObject['Testcases']);
		var url = "./suites/getSuiteDataBack";
		var csrftoken = $("[name='csrfmiddlewaretoken']").val();

		$.ajaxSetup({
				function(xhr, settings) {
	            xhr.setRequestHeader("X-CSRFToken", csrftoken)
	    	}
		});
	
		var topNode = { 'TestSuite' : suites.jsonSuiteObject.getJSON()};
		//var topNode = 
		$.ajax({
		    url : url,
		    type: "POST",
		    data : { 
		    	'json': JSON.stringify(topNode),
		    	'filetosave': xfname,
		    	'savefilepath': katana.$activeTab.find('#savefilepath').text()
		    	},
		    headers: {'X-CSRFToken':csrftoken},
	    
			success: function( data ){
			        var outstr = "Saved " + katana.$activeTab.find('#savefilepath').text() +katana.$activeTab.find('#my_file_to_save').val(); 
					xdata = { 'heading': "Saved", 'text' : outstr}
					katana.openAlert(xdata);
			        katana.$activeTab.find('#suiteName').val(suites.jsonSuiteObject.Details.Name);
			    	}
				});

	},

		start_wdfEditor: function() { 
			var tag = '#suiteInputDataFile';
			var filename = katana.$activeTab.find(tag).attr("fullpath");
			console.log("WDF editor opening...", filename); 
			var csrftoken = $("[name='csrfmiddlewaretoken']").val();
		
			var href='/katana/wdf/index';
			dd = { 'path' : filename}; 
			pd = { type: 'POST',
				   headers: {'X-CSRFToken':csrftoken},
				   data:  dd};
				  console.log("Pd = ", pd);
		  		   katana.templateAPI.load.call(this, href, '/static/wdf_edit/js/main.js,', null, 'wdf', function() { 
					//var xref="/katana/wdf/index"; 
		    		//katana.templateAPI.subAppLoad(xref,null,function(thisPage) {
					console.log("loaded wdf");
		    		//});
			}, pd);
		},

	getInputDataForSuite: function () {
      var callback_on_accept = function(selectedValue) { 
      		console.log(selectedValue);
      		var pathToBase = katana.$activeTab.find('#savefilepath').text();
      		console.log("File path ==", pathToBase);
      		var nf = prefixFromAbs(pathToBase, selectedValue);
      		suites.jsonSuiteObject.Details['InputDataFile']= nf;
      		console.log("Path set to ",nf);
      		var tag = '#suiteInputDataFile';
      		katana.$activeTab.find(tag).val(nf);
      		katana.$activeTab.find(tag).attr("value", nf);
	  		katana.$activeTab.find(tag).attr("fullpath", selectedValue);
            };
      var callback_on_dismiss = function(){ 
      		console.log("Dismissed");
	 };
     katana.fileExplorerAPI.openFileExplorer("Select a file", false , $("[name='csrfmiddlewaretoken']").val(), false, callback_on_accept, callback_on_dismiss);
	},


	getResultsDirForSuite: function () {
      var callback_on_accept = function(selectedValue) { 
      		console.log(selectedValue);
      		var pathToBase = katana.$activeTab.find('#savefilepath').text();
      		console.log("File path ==", pathToBase);
      		var nf = prefixFromAbs(pathToBase, selectedValue);
      		suites.jsonSuiteObject.Details.Resultsdir = nf;
      		console.log("Path set to ",nf);
            katana.$activeTab.find('#suiteResults').val(nf);
           };
      var callback_on_dismiss = function(){ 
      		console.log("Dismissed");
	 };
     katana.fileExplorerAPI.openFileExplorer("Select a file", false , $("[name='csrfmiddlewaretoken']").val(), false, callback_on_accept, callback_on_dismiss);
	},

	getResultsDirForSuiteRow: function () {
      var callback_on_accept = function(selectedValue) { 
      		// Convert to relative path.
      		var sid = katana.$activeTab.attr('suite_case_row');
			var popup = suites.lastPopup;
      		var pathToBase = katana.$activeTab.find('#savefilepath').text();
      		console.log("File path ==", pathToBase, sid);
      		var nf = prefixFromAbs(pathToBase, selectedValue);
      		suites.jsonTestcases[sid]['InputDataFile'] = nf;
      		console.log("Path set to ",nf," for ", sid);
      		//createCasesTable(suites.jsonTestcases);
      		popup.find("#StepInputDataFile").val(nf); 
            };
      var callback_on_dismiss = function(){ 
      		console.log("Dismissed");
	 };
     katana.fileExplorerAPI.openFileExplorer("Select a file", false , $("[name='csrfmiddlewaretoken']").val(), false, callback_on_accept, callback_on_dismiss);
},

	fillSuiteDefaultGoto :function() {

	var gotoStep = katana.$activeTab.find('#default_onError').val();
	//console.log("Step ", gotoStep);
	var defgoto = katana.$activeTab.find('#default_onError_goto'); 
		defgoto.hide();

	if (gotoStep.trim() == 'goto') { 
		defgoto.show();
	} else {
		defgoto.hide();
		
	}

	defgoto.empty(); 
	var xdata = suites.jsonSuiteObject["Testcases"]; 
	if (!jQuery.isArray(xdata)) xdata = [xdata]; 
	for (var s=0; s<Object.keys(xdata).length; s++ ) {
		defgoto.append($('<option>',{ value: s,  text: s+1}));
	}
},

	fillSuiteCaseDefaultGoto : function(popup) {

		var gotoStep =popup.find('#caseonError-at-action').val();
		var defgoto = popup.find('#caseonError-at-value'); 
		defgoto.hide();

		if (gotoStep.trim() == 'goto') { 
			defgoto.show();
		} else {
			defgoto.hide();
			
		}
		//var sid = popup.find('#CaseRowToEdit').val();
		defgoto.empty(); 
		var xdata = suites.jsonSuiteObject["Testcases"]; // ['Testcase'];
		if (!jQuery.isArray(xdata)) xdata = [xdata]; 
		for (var s=0; s<Object.keys(xdata).length; s++ ) {
			defgoto.append($('<option>',{ value: s,  text: s+1}));
		}
	},

//
// This creates the table for viewing data in a sortable view. 
// 
	createCasesTable: function(xdata) {
		var items = []; 

		items.push('<table id="Case_table_display" class="suite-configuration-table" width="100%">');
		items.push('<thead>');
		items.push('<tr id="CaseRow"><th>Num</th><th></th><th>Path</th><th>context</th><th>Run Type</th><th>Mode</th><th>OnError</th><th>Impact</th><th/></tr>');
		items.push('</thead>');
		items.push('<tbody>');

		//console.log(xdata);
		katana.$activeTab.find("#tableOfTestcasesForSuite").html("");

		var slen = suites.jsonSuiteObject.Testcases.length; 
		for (var s=0; s< slen; s++ ) {
			var oneCase = suites.jsonSuiteObject.Testcases[s];
			console.log(oneCase);
			var showID = parseInt(s)+ 1; 
			items.push('<tr data-sid="'+s+'"><td>'+showID+'</td>');
			var bid = "fileTestcase-"+s+"-id";
			items.push('<td><i title="ChangeFile" class="fa fa-folder-open" id="'+bid+'" katana-click="suites.fileNewSuiteFromLine" key="'+bid+'"/></td>');
			items.push('<td katana-click="suites.showCaseFromSuite" skey="'+oneCase['path']+'"> '+oneCase['path']+'</td>');
			items.push('<td>'+oneCase.context+'</td>');
			items.push('<td>'+oneCase.runtype+'</td>');
			items.push('<td>'+oneCase.runmode_type);
			if (oneCase.runmode_type != 'standard') {
				items.push('<br>'+oneCase.runmode_value.toLowerCase());
			}
			items.push('</td>');
			items.push('<td>'+oneCase.onError_action+'</td>');
			items.push('<td>'+oneCase.impact+'</td>');
			bid = "deleteTestcase-"+s+"-id";
			items.push('<td><i title="Delete" class="fa fa-trash" id="'+bid+'" katana-click="suites.deleteSuiteFromLine" key="'+bid+'"/>');
			bid = "editTestcaseRow-"+s+"-id";
			items.push('<i title="Edit" class="fa fa-pencil" title="Edit" id="'+bid+'" katana-click="suites.editNewSuiteIntoLine" key="'+bid+'"/> ');
			bid = "insertTestcase-"+s+"-id";
			items.push('<i title="Insert" class="fa fa-plus" title="Insert New Case" id="'+bid+'" katana-click="suites.insertNewSuiteIntoLine" key="'+bid+'"/>');
			bid = "copyToStorage-"+s+"-id-";
			items.push('<i title="Copy to clipboard" class="fa fa-clipboard" theSid="'+s+'"   id="'+bid+'" katana-click="suites.saveTestStep" key="'+bid+'"/>');
			bid = "copyFromStorage-"+s+"-id-";
			items.push('<i title="Copy from clipboard" class="fa fa-outdent" theSid="'+s+'"   id="'+bid+'" katana-click="suites.restoreTestStep" key="'+bid+'"/>');
			bid = "dupTestcase-"+s+"-id";
			items.push('<i title="Duplicate" class="fa fa-copy" title="Duplicate New Case" id="'+bid+'" katana-click="suites.duplicateNewSuiteIntoLine" key="'+bid+'"/></td>');
			items.push('</tr>');
		}
	items.push('</tbody>');
	items.push('</table>');
	katana.$activeTab.find("#tableOfTestcasesForSuite").html( items.join(""));
	katana.$activeTab.find('#Case_table_display tbody').sortable( { stop: suites.testSuiteSortEventHandler});
	suites.fillSuiteDefaultGoto();
},

	insertNewSuiteIntoLine : function() {
	console.log(this.attr('key'));
	var names = this.attr('key').split('-');
	console.log(this.attr('key'));
	var sid = parseInt(names[1]);
	suites.insertCaseToSuite(sid,0);
},

 	deleteSuiteFromLine :function() {
	var names = this.attr('key').split('-');
	var sid = parseInt(names[1]);
	suites.removeTestcase(sid);
	},

	duplicateNewSuiteIntoLine : function( ){
	var names = this.attr('key').split('-');
	var sid = parseInt(names[1]);
	suites.insertCaseToSuite(sid,1);
	},


	saveTestStep: function() {
		var names = this.attr('key').split('-');
		var sid = parseInt(names[1]);
		console.log("Saving ...", suites.jsonTestcases[sid] );
		suites.jsonTestcases[sid].copyToDocument('lastCaseCopied', suites.jsonTestcases[sid]);
		},


	restoreTestStep: function() {
		var names = this.attr('key').split('-');
		var sid = parseInt(names[1]);
		jsonData = suites.jsonTestcases[sid].copyFromDocument('lastCaseCopied');
		console.log("Retrieving ... ", jsonData);
		newTestcase = new projectSuiteObject(jsonData);
		
		},


	editNewSuiteIntoLine : function() {
	var names = this.attr('key').split('-');
	var sid = parseInt(names[1]);
		katana.popupController.open(katana.$activeTab.find("#editTestCaseEntry").html(),"Edit..." + sid, function(popup) {
			suites.lastPopup = popup;
			suites.mapSuiteCaseToUI(sid,popup);
		});

},

	fileNewSuiteFromLine :function(){ 
	var names = this.attr('key').split('-');
	var sid = parseInt(names[1]);
	katana.$activeTab.attr('suite_case_row',sid);
	suites.getResultsDirForSuiteRow();
	},

	showCaseFromSuite : function () {
		var fname = this.attr('skey');
		var xref="./cases/editCase/?fname="+fname; 
	  	console.log("Calling case ", fname, xref);
		var href='/katana/cases';
	  	katana.templateAPI.load.call(this, href, '/static/cases/js/cases.js,', null, 'case', function() { 
				var xref="./cases/editCase/?fname="+fname; 
	    		katana.templateAPI.subAppLoad(xref,null,function(thisPage) {
						cases.mapFullCaseJson(fname,'#listOfTestStepsForCase');
	    		});

		});
	},
//
	testSuiteSortEventHandler : function(event, ui ) {
	var listItems = [] ; 
	var listCases = katana.$activeTab.find('#Case_table_display tbody').children(); 
	console.log(listCases);
		if (listCases.length < 2) {
	 return; 
	}

	var oldCaseSteps = suites.jsonSuiteObject.Testcases;
	var newCaseSteps = new Array(listCases.length);

	for (xi=0; xi < listCases.length; xi++) {
		var xtr = listCases[xi];
		var ni  = xtr.getAttribute("data-sid");
		console.log(xi + " => " + ni);
		newCaseSteps[ni] = oldCaseSteps[xi];
	}

	suites.jsonSuiteObject.Testcases = newCaseSteps;
	suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
	suites.mapSuiteJsonToUi();  // This is where the table and edit form is created. 
},






	createSuiteRequirementsTable : function(rdata){
	var items =[]; 
	katana.$activeTab.find("#tableOfTestRequirements").html("");
	
	items.push('<table id="Case_Req_table_display" class="suite-req-configuration-table  striped" width="100%" >');
	items.push('<thead>');
	items.push('<tr id="ReqRow"><th>#</th><th>Requirement</th><th>')
	items.push('<i title="Save Edit" katana-click="suites.saveAllRequirementsCB">Save All</i>')
	items.push('</th></tr>');
	items.push('</thead>');
	items.push('<tbody>');
	//console.log(rdata);
	var slen = rdata.getLength();
	var reqs = rdata.getRequirements();
	for (var s=0; s<slen; s++ ) {
		var idnumber = s + 1;
		items.push('<tr data-sid=""><td>'+idnumber+'</td>');
		var bid = "textRequirement-name-"+s+"-id";	
		items.push('<td><input type="text" value="'+reqs[s]+'" id="'+bid+'" /></td>');
		bid = "deleteRequirementbtn-"+s+"-id";
		
		items.push('<td><i  class="fa fa-trash"  title="Delete" skey="'+bid+'" katana-click="suites.deleteRequirementCB"/>');
		bid = "editRequirementbtn-"+s+"-id";
		items.push('<i class="fa fa-floppy-o" title="Save Edit" skey="'+bid+'" katana-click="suites.saveRequirementCB"/>');
		bid = "insertRequirementbtn-"+s+"-id";
		items.push('<i class="fa fa-plus"  title="Insert" skey="'+bid+'" katana-click="suites.insertRequirementCB"/></td>');
		
	}
	items.push('</tbody>');
	items.push('</table>');
	katana.$activeTab.find("#tableOfTestRequirements").html( items.join(""));
	

},

	saveAllRequirementsCB: function() { 
		var slen = suites.jsonSuiteObject.Requirements.getLength();
		//console.log("slen=", slen);
		for (var sid = 0; sid < slen; sid++ ) {
			var txtNm = katana.$activeTab.find("#textRequirement-name-"+sid+"-id").val();
			suites.jsonSuiteObject.Requirements.setRequirement( sid,  txtNm );
		}
		suites.createSuiteRequirementsTable(suites.jsonSuiteObject.Requirements);	

	},


	saveRequirementCB:function() {
			var names = this.attr('skey').split('-');
			var sid = parseInt(names[1]);
			var txtVl = katana.$activeTab.find("#textRequirement-name-"+sid+"-id").val();
			suites.jsonSuiteObject.Requirements.setRequirement( sid,  txtVl);
			suites.createSuiteRequirementsTable(suites.jsonSuiteObject.Requirements);	
		},

	deleteRequirementCB:	function() {
			var names = this.attr('skey').split('-');
			var sid = parseInt(names[1]);
			// console.log("Remove " + sid + " " + this.id ); 
			suites.jsonSuiteObject.Requirements.deleteRequirement(sid);
			suites.createSuiteRequirementsTable(suites.jsonSuiteObject.Requirements);	
			
		},
	
	insertRequirementCB:function( ) {
			var names = this.attr('skey').split('-');
			var sid = parseInt(names[1]);
			suites.jsonSuiteObject.Requirements.insertRequirement(sid,'');
			suites.createSuiteRequirementsTable(suites.jsonSuiteObject.Requirements);	
		},

	addRequirementToSuite() {
		suites.jsonSuiteObject.Requirements.insertRequirement(0,'');
		suites.createSuiteRequirementsTable(suites.jsonSuiteObject.Requirements);	
	},
/*
// Shows the global Suite data holder in the UI.

NOTE: At the time of writing I am using jQuery and Bootstrap to show the data.

Two global variables are heavily used when this function is called; 
1. suites.jsonSuiteObject 
2. suites.jsonTestcases which is set to point to the Testcases data structure in
   the suites.jsonSuiteObject

*/
 mapSuiteJsonToUi: function(data){
	if (!jQuery.isArray(suites.jsonTestcasesj)) suites.jsonTestcasesj = [suites.jsonTestcasesj]; 
	// if (!suites.jsonSuiteObject['Requirements']) suites.jsonSuiteObject['Requirements'] = [];
	// if (!jQuery.isArray(suites.jsonSuiteObject['Requirements'])) suites.jsonSuiteObject['Requirements'] = [suites.jsonSuiteObject['Requirements']]; 
	suites.createCasesTable(suites.jsonTestcases['Testcase']);

	// Resolve the relative path for the wdf editor to get full path. ..
	if (!suites.jsonSuiteObject['InputDataFile']) {
		var tag = '#suiteInputDataFile';
		var nf = suites.jsonSuiteObject["Details"]['InputDataFile'];
		var pathToBase = katana.$activeTab.find('#savefilepath').text();
		var fpath = absFromPrefix(pathToBase, nf);
		//console.log("mapSuiteJsonToUi:", fpath, nf, pathToBase);
		
		katana.$activeTab.find(tag).val(nf);
      	katana.$activeTab.find(tag).attr("value", nf);
	  	katana.$activeTab.find(tag).attr("fullpath", fpath);
	}


		datatype = suites.jsonSuiteObject.Details.ExecType;
		datatype = datatype.toLowerCase(); 
		katana.$activeTab.find('#data_type_max_attempts').hide();
		katana.$activeTab.find('#data_type_num_attempts').hide();
		if (datatype == 'ruf' || datatype=='rup') {
			katana.$activeTab.find('#data_type_max_attempts').show();
		}
		if (datatype =='rmt'){
			katana.$activeTab.find('#data_type_num_attempts').show();
		}
		suites.createSuiteRequirementsTable(suites.jsonSuiteObject.Requirements);		
},  

// Saves your suite to disk. 
	saveSuitesCaseUI : function() {	
		suites.mapUItoSuiteCase();
		suites.createCasesTable(suites.jsonTestcases['Testcase']);
		suites.mapSuiteJsonToUi();
},




// Removes a test Case by its ID and refresh the page. 
	removeTestcase : function(sid ){
	suites.jsonTestcases['Testcase'].splice(sid,1);
	console.log("Removing test Cases "+sid+" now " + Object.keys(suites.jsonTestcases).length);
	suites.mapSuiteJsonToUi();	// Send in the modified array
},


};