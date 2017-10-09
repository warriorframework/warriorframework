/*
/// -------------------------------------------------------------------------------

Case File Data Handler 

Author: 
Date: 

The functions in this module are designed specifically for handling Suite XML files
for the warrior framework. 

It is expected to work with the editCase.html file and the calls in 
the views.py python for Django. 
/// -------------------------------------------------------------------------------

*/ 
// Belongs in main.js when ok. 
// Converts a path that is relative to pathToBase into an absolute path with .. constructs. 
//

function absFromPrefix(pathToBase, pathToFile) {
	// Converts an absolute path to one that is relative to pathToBase 
	// Input: 
	// 		
	var bf = pathToBase.split('/');
	var rf = pathToFile.split('/');
	var nrf = pathToFile.split('/');
	console.log("Removing", nrf, bf);
	
	for (var i=0;i< rf.length; i++) {
		if (rf[i] == "..")  { 
			bf.pop();
			nrf.splice(0,1);
			console.log("Removing", nrf, bf);
	
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
	console.log("bf=",bf);
	console.log("rf=",rf);
	console.log("prefixFromAbs", rf, tlen, blen, stack);
    for (var k=0;k < tlen; k++) {
		upem.push("..");
	}
	var tail = rf.splice(blen,rf.length);
	console.log('tail=', tail);
	return upem.join("/") + "/" +   tail.join('/');
}

function jsUcfirst(string) 
{
	//return string.charAt(0).toUpperCase() + string.slice(1);
	return string.toLowerCase();
}



class caseRequirementsObject{

	constructor (jsonRequirements) { 
		this.Requirements = [];
		if (!jsonRequirements) return this; 
		for (var k =0; k < jsonRequirements.length; k++ ) {
			this.Requirements.push(jsonRequirements[k]);
		}
	}

	getJSONdata() {
		return this.Requirements;
		// var r = [];
		// for (var k=0; k < this.Requirements.length; k++) {
		// 	r.push({ 'Requirement': this.Requirements[k]} );
		// }
		// return r ;  // this matches the XML ... 
	}

	insertRequirement(sid,where,what){
		this.Requirements.splice(sid,where,what);
	}

	getRequirements() {
		return this.Requirements;
	}

	setRequirement(s,v){
		this.Requirements[s]=v;
	}
}

class caseDetailsObject{ 
	// Define the members in the same manner as their XML counter parts
	mapJSONdataToSelf(jsonDetailsData) {
			this.fillDefaults();           // Fills internal values only
			if (jsonDetailsData) {         // Overridden by incoming data.
				var keys = Object.keys(jsonDetailsData);
				for (var k=0; k < keys.length; k++) {
					var key = keys[k];
					this[key] = jsonDetailsData[key];
				}
			}
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
		this.State = ''; 
		// this.cDate = ''; 
		// this.cTime = ''; 
		this.default_onError = ''; 
		this.Datatype = ''; 
		this.InputDataFile = '';
		this.Resultsdir = ''; 
		this.Logsdir = ''; 
		this.ExpectedResults = ''; 
		this.setTimeStamp();
		}

	getJSON() {
		var details = {} ;
		details.Name = this.Name  ;    
		details.Title = this.Title   ;  
		details.Category = this.Category   ;  		
		details.Engineer = this.Engineer ;    		
		details.State = this.State ;    
		details.Date = this.cDate ;    
		details.Time = this.cTime ;    
		details.default_onError = this.default_onError;
		details.Datatype = this.Datatype ;
		details.InputDataFile = this.InputDataFile ;
		details.Resultsdir = this.Resultsdir;
		details.Logsdir = this.Logsdir;
		details.ExpectedResults = this.ExpectedResults;
		return details;
	}

	// returns a copy of itself. 
	duplicateSelf() { 
		return jQuery.extend(true, {}, this); 
	}


}
//
//  Input: 
//		jsonData = ['Teststeps']['Teststep'] 
//		which should be an array; if it is one element, make sure
//		that it is an array of one element. 
//
class caseTestStepObject {

	constructor(inputJsonData) {
		var jsonData = inputJsonData;
		this.setupFromJSON(jsonData);
	}

	setupFromJSON(jsonData) { 
		console.log("Asetup from ",jsonData);
		if (!jsonData) {
			jsonData = 	this.createEmptyTestStep(); 
		}
		this.Arguments = [] ; 
		for (var a=0;a<jsonData['Arguments'].length; a++) {
			var ao = jsonData['Arguments'][a];
			this.Arguments.push({ 'value': ao['@value'], 'name' : ao['@name']})
		}
		console.log("Adding-->",jsonData);
		this.step_driver = jsonData['@Driver']; 
		this.step_keyword = jsonData['@Keyword']; 
		this.step_TS = jsonData['@TS']; 
		this.onError_action=jsonData['onError']['@action'];
		this.onError_value=jsonData['onError']['@value'];
		this.Description = jsonData['Description'];
		this.iteration_type= jsonData['iteration_type'];
		// Make sure the Execute and types exist
		if (! jsonData['Execute']){
				jsonData['Execute'] = { "@ExecType": "yes", 
						"Rule": { "@Condition": "", "@Condvalue": "", "@Else": "next", "@Elsevalue": "" }
					}; 
			}
		if (! jsonData['Execute']['@ExecType']){
			jsonData['Execute']['@ExecType'] = 'yes'; 
		}
		// Make sure the rules and types exist
		if (! jsonData['Execute']['Rule']){
				jsonData['Execute']['Rule'] ={ "@Condition": "", "@Condvalue": "", "@Else": "next", "@Elsevalue": "" }; 
			}
		
		this.Execute_ExecType = jsonData['Execute']['@ExecType'].toLowerCase();
		this.Execute_Rule_Condition = jsonData['Execute']['Rule']['@Condition'];
		this.Execute_Rule_Condvalue = jsonData['Execute']['Rule']['@Condvalue'];
		this.Execute_Rule_Else = jsonData['Execute']['Rule']['@Else'];
		this.Execute_Rule_Elsevalue = jsonData['Execute']['Rule']['@Elsevalue'];
		this.impact = jsonData['impact'];
		this.context = jsonData['context'];

		if (! jsonData['runmode']) {
			jsonData['runmode'] = { '@value': '', '@type' : ''}; 
		}
		this.runmode_value = jsonData['runmode']['@value'];
		this.runmode_type  = jsonData['runmode']['@type'];

		if (! jsonData['iteration_type']) {
			jsonData['iteration_type']['@type'] = 'sequential_testcases';
			jsonData['iteration_type']['@value'] = '';
		}
		// 
		this.iteration_type = jsonData['iteration_type']['@type'];
		this.iteration_value = jsonData['iteration_type']['@value'];

		if (! jsonData['InputDataFile']) {
			jsonData['InputDataFile'] = '';
		}
		this.InputDataFile = jsonData['InputDataFile'];
	// End of constructor 
	}


	copyToDocument(tag) {
		localStorage.setItem(tag, JSON.stringify(this.getJSON()));
	}

	copyFromDocument(tag) {
		return JSON.parse(localStorage.getItem(tag));
	}

	createEmptyTestStep() {
		var newCaseStep = {
				"@Driver": "demo_driver", 
				"@Keyword": "" , 
				"@TS": "0" ,
				"Arguments" : 
					{ 'Argument': [] },
				"onError": {  "@action" : "next", "@value" : "" } ,
				"iteration_type": {   "@type" : "" } ,
				"Description":"",
				"Execute": {   "@ExecType": "yes",
					"Rule": {   "@Condition": "","@Condvalue": "","@Else": "next", "@Elsevalue": "" }
				}, 
				"context": "positive", 
				"impact" :  "impact",
				"runmode" : { '@type': 'standard', '@value': ""},
				"InputDataFile" : "", 
			 	};
		 return newCaseStep;
	}


	getJSON() { 
		var myArgs = [];
		for (var x in this.Arguments){
			myArgs.push({ 'argument' : { '@name': this.Arguments[x].name , '@value': this.Arguments[x].value }});
		}

		return  {
				"@Driver": this.step_driver, "@Keyword": this.step_keyword , "@TS": this.step_TS ,
				"Arguments" : 	myArgs  ,
				"onError": {  "@action" : this.onError_action , "@value" : this.onError_value } ,
				"iteration_type": {   "@type" : "" } ,
				"Description":this.Description,
				"Execute": {   "@ExecType": this.Execute_ExecType,
					"Rule": {   "@Condition": this.Execute_Rule_Condition ,
								"@Condvalue": this.Execute_Rule_Condvalue,
								"@Else": this.Execute_Rule_Else, 
								"@Elsevalue": this.Execute_Rule_Elsevalue }
				}, 
				"context": this.context, 
				"impact" : this.impact,
				"runmode" : { '@type': this.runmode_type, '@value': this.runmode_value},
				"InputDataFile" : this.InputDataFile, 
			};
	}
}


	class caseObject {
		constructor(jsonData) { 
			//
			// First confirm that the object is complete. 
			// Return empty object if incomplete. 
			//
			console.log("In constructor", jsonData);
			if (!jsonData['Details']) {
				this.Details = new caseDetailsObject(null);
			} else {
				this.Details = new caseDetailsObject(jsonData['Details'])
			}
			// Use an empty as a starting point for 
			if (!jsonData['Requirements']) {
				jsonData['Requirements'] = [] 
			} 
			if (!jsonData['Requirements']['Requirement']) {
				jsonData['Requirements']['Requirement']= [] 
			}
			if (!jQuery.isArray(jsonData['Requirements']['Requirement'] )) {
				jsonData['Requirements']['Requirement'] = [jsonData['Requirements']['Requirement']];
			}
			this.Requirements = new caseRequirementsObject(jsonData['Requirements']['Requirement']);
			
			// Adjust up front. 

			console.log("After", jsonData['Steps']);
			
			if (!jsonData['Steps']) {
				jsonData['Steps']['step'] = [] 
			} 
			if (!jsonData['Steps']['step']) {
				jsonData['Steps']['step'] = [] 
			} 
			//
			if (!jQuery.isArray(jsonData['Steps']['step'])) {
			 jsonData['Steps']['step'] = [ jsonData['Steps']['step'] ];
			}
			this.Teststeps = [];
			for (var k=0; k<jsonData['Steps']['step'].length; k++) {	
				var ts = new caseTestStepObject(jsonData['Steps']['step'][k]);
				this.Teststeps.push(ts);
				}
			// 
			}

		getJSON(){
			var testStepsJSON = [];
			for (var ts =0; ts< this.Teststeps.length; ts++ ) {
				testStepsJSON.push(this.Teststeps[ts].getJSON());
			}

			return { 'Details': this.Details.getJSON(), 
				'Requirements' : { 'Requirement' : this.Requirements.getJSONdata() },
				'Steps' : { 'step': testStepsJSON}, };

		}
	}


 

///////////////////////////////////////////////////////////////////////////////////
// The application code begins here.
///////////////////////////////////////////////////////////////////////////////////
var cases = {

 	init: function() { 
 		cases.displayTreeOfCases();
			katana.$activeTab.find(".linkToCase").click(function() { 
				var $elem = $(this);
				var thePage = $elem.attr('href');
				var theID   = $elem.attr('fname');
				katana.templateAPI.load( thePage, null, null, 'case') ;
			});
 	},

	startNewCase: function() {
	  var xref="./cases/editCase/?fname=NEW"; 
	     katana.$view.one('tabAdded', function(){
	        cases.mapFullCaseJson(); // ("NEW",'#emptyTestCaseData');
	    });
	  katana.templateAPI.load(xref, null, null, 'Case') ;
	},




	start_wdfEditor: function() { 
		// Start the WDF editor. 
		var tag = '#caseInputDataFile';
		var filename = katana.$activeTab.find('#caseInputDataFile').attr("fullpath");
		var csrftoken = $("[name='csrfmiddlewaretoken']").val();
		//http://localhost:5000/katana/#

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



	displayTreeOfCases: function() {
			jQuery.getJSON("./cases/getCaseListTree").done(function(data) {
				var sdata = data['treejs'];
				console.log(sdata);
				//var jdata = { 'core' : { 'data' : [ JSON.parse(sdata)]}};
				var jdata = { 'core' : { 'data' : sdata }}; 
				katana.$activeTab.find('#myCaseTree').on("select_node.jstree", function (e, data) { 
			      var thePage = data.node.li_attr['data-path'];
			      console.log(thePage);
			      // If there is no XML extension return immediately
			      var extn = thePage.indexOf(".xml");
			      if (extn < 4){
			      	return;
			      }
				  var xref="./cases/editCase/?fname=" + thePage; 
				  cases.thefile = thePage;				  // Load the response here. ...	
				  katana.$activeTab.find(".case-single-toolbar").hide()
				  katana.templateAPI.subAppLoad(xref, null, function(thisPage) { 
			   			cases.mapFullCaseJson(); // (cases.thefile, null);
				  });
				  //katana.templateAPI.load(xref, null, null, 'Case') ;
				});
				katana.$activeTab.find('#myCaseTree').jstree(jdata);
			});
		
	},

	closeCase: function(){
		katana.closeSubApp();
	},


	 lastPopup: null,
	 jsonCaseObject : [],
	 jsonCaseDetails : [],				// A pointer to the Details   
	 jsonCaseSteps : [],		  		// A pointer to the Steps object
	
//
// This function is called when the page loads in cases.js . 
//
	mapFullCaseJson: function(){
		var myfile = katana.$activeTab.find('#fullpathname').text();
		jQuery.getJSON("./cases/getJSONcaseDataBack/?fname="+myfile).done(function(data) {
			a_items = data['fulljson']['Testcase'];

			cases.jsonCaseObject  = new caseObject(a_items);
			//console.log("Objects--->",a_items, myObj, myObj.getJSON());
			cases.jsonCaseSteps  = cases.jsonCaseObject.Teststeps;      //
			cases.jsonCaseDetails = cases.jsonCaseObject.Details;
			katana.$activeTab.find("#editCaseStepDiv").hide();
			katana.$activeTab.find("#tableOfTestStepsForCase").removeClass();
			katana.$activeTab.find("#tableOfTestStepsForCase").addClass('col-md-12');
			katana.$activeTab.find("#tableOfTestStepsForCase").show();
			console.log("Here", cases.jsonCaseObject, cases.jsonCaseSteps);
			cases.mapCaseJsonToUi(cases.jsonCaseSteps);
			cases.createRequirementsTable();

	//$('#myform :checkbox').change(function()
		katana.$activeTab.find('#ck_dataPath').change(function() {
				if (this.checked) {
					katana.$activeTab.find('.case-results-dir').hide();
				} else {
					katana.$activeTab.find('.case-results-dir').show();
				}
		  	});

		cases.fillCaseDefaultGoto();

		});
	},





	mapUiToCaseJson: function() {

		if ( katana.$activeTab.find('#caseName').attr('value').length < 1) {
			data = { 'heading': "Error", 'text' : "Please specific a case name "}
			katana.openAlert(data);
			return -1;
		}

		if ( katana.$activeTab.find('#caseTitle').attr('value').length < 1) {
			data = { 'heading': "Error", 'text' : "Please specific a title "}
			katana.openAlert(data);
			return -1;
		}
		if ( katana.$activeTab.find('#caseEngineer').attr('value').length < 1) {
			data = { 'heading': "Error", 'text' : "Please specific a name for the engineer"}
			katana.openAlert(data);
			return -1;
		}


			var xfname = katana.$activeTab.find('#caseName').val();
			if (xfname.indexOf(".xml") < 0) { 
				xfname  = xfname + ".xml";
			}

	cases.jsonCaseObject['Details']['Name'] = katana.$activeTab.find('#caseName').val();
	cases.jsonCaseObject['Details']['Title'] = katana.$activeTab.find('#caseTitle').val();
	cases.jsonCaseObject['Details']['Category'] = katana.$activeTab.find('#caseCategory').val();
	cases.jsonCaseObject['Details']['State'] = katana.$activeTab.find('#caseState').val();
	cases.jsonCaseObject['Details']['Engineer'] = katana.$activeTab.find('#caseEngineer').val();
	
	//cases.jsonCaseObject['Details']['Date'] = katana.$activeTab.find('#caseDate').val();

	console.log("Attributes ", cases.jsonCaseObject);
	var date = new Date();
   	var year = date.getFullYear();
   	var month = date.getMonth() + 1;// months are zero indexed
   	var day = date.getDate();
   	var hour = date.getHours();
   	var minute = date.getMinutes();
   	if (minute < 10) {
       	minute = "0" + minute; 
       }
   	
	cases.jsonCaseObject['Details']['Date'] = month + "/" + day + "/" + year; 
	cases.jsonCaseObject['Details']['Time'] = hour + ":" + minute; 



	// cases.jsonCaseObject['expectedDir'] =  katana.$activeTab.find('#caseExpectedResults').attr('value');
	cases.jsonCaseObject['Details']['default_onError'] = katana.$activeTab.find('#default_onError').val();
	cases.jsonCaseObject['Details']['Datatype'] = katana.$activeTab.find('#caseDatatype').val();
	cases.jsonCaseObject['Details']['InputDataFile'] =  katana.$activeTab.find('#caseInputDataFile').val();
	cases.jsonCaseObject['Details']['Resultsdir'] =  katana.$activeTab.find('#caseResultsDir').val();
	cases.jsonCaseObject['Details']['Logsdir'] =  katana.$activeTab.find('#caseLogsDir').val();
	cases.jsonCaseObject['Details']['ExpectedResults'] =  katana.$activeTab.find('#caseExpectedResults').val();

	if (!cases.jsonCaseObject['Requirements']) {
		cases.jsonCaseObject['Requirements'] = []; 
	}
 
	// Now you have collected the user components...

	return 0;
	} ,



	getFileSavePath: function () {
			var tag = '#caseName';
			var callback_on_accept = function(selectedValue) { 
	  		console.log(selectedValue);
	  		var savefilepath = katana.$activeTab.find('#savesubdir').text();
	  		console.log("File path ==", savefilepath);
	  		var nf = prefixFromAbs(savefilepath, selectedValue);
	  		katana.$activeTab.find(tag).attr("value", nf);
	  		katana.$activeTab.find(tag).attr("fullpath", selectedValue);
			//katana.$activeTab.find(tag).text('');
			};
	  var callback_on_dismiss =  function(){ 
	  		console.log("Dismissed");
	 };
	 katana.fileExplorerAPI.openFileExplorer("Select a file", false , $("[name='csrfmiddlewaretoken']").val(), false, callback_on_accept, callback_on_dismiss);
},

// Get Results directory from the case on the main page.
	getCaseInputDataFile: function () {

			var callback_on_accept = function(selectedValue) { 
	  		console.log(selectedValue);
	  		var tag = '#caseInputDataFile'
	  		var savefilepath = katana.$activeTab.find('#savesubdir').text();
	  		
	  		console.log("File path ==", savefilepath);
	  		var nf = prefixFromAbs(savefilepath, selectedValue);
	  		katana.$activeTab.find(tag).attr("value", nf);
	  		katana.$activeTab.find(tag).attr("fullpath", selectedValue);
			katana.$activeTab.find(tag).text(nf); // 
			};
	  var callback_on_dismiss =  function(){ 
	  		console.log("Dismissed");
	 };
	 katana.fileExplorerAPI.openFileExplorer("Select a file", false , $("[name='csrfmiddlewaretoken']").val(), false, callback_on_accept, callback_on_dismiss);
},


	getResultsDirForCases: function() {
		var callback_on_accept = function(selectedValue) { 
			  		console.log(selectedValue);
			  		var tag = '#caseResultsdir'
			  		var savefilepath = katana.$activeTab.find('#savesubdir').text();
			  		console.log("File path ==", savefilepath);
			  		var nf = prefixFromAbs(savefilepath, selectedValue);
			  		katana.$activeTab.find(tag).attr("value", nf);
			  		katana.$activeTab.find(tag).attr("fullpath", selectedValue);
					katana.$activeTab.find(tag).text(nf); // 
					};
		  var callback_on_dismiss =  function(){ 
		  		console.log("Dismissed");
		 };
	katana.fileExplorerAPI.openFileExplorer("Select a file", false , $("[name='csrfmiddlewaretoken']").val(), false, callback_on_accept, callback_on_dismiss);

	},

	getStepInputDataFile: function() {
		
			var callback_on_accept = function(selectedValue) { 
			  		var sid = katana.$activeTab.find("#editCaseStepDiv").attr('row-id');
			  		console.log("Got this file" , selectedValue, names, sid);
			  		var popup = cases.lastPopup; // katana.$activeTab.find("#editCaseStepDiv").attr('data-popup-id');
			  		var savefilepath = katana.$activeTab.find('#savesubdir').text();  
			  		console.log("File path ==", savefilepath);
					var nf = prefixFromAbs(savefilepath, selectedValue);
					var oneCaseStep = cases.jsonCaseSteps[sid];
					oneCaseStep["InputDataFile"] = nf;
					};
			 var callback_on_dismiss = function(){ 
			  		var popup = katana.$activeTab.find("#editCaseStepDiv").attr('data-popup-id');
			  		console.log("Dismissed", popup);

			 	};
			var popup = katana.$activeTab.find("#editCaseStepDiv").attr('data-popup-id');
			katana.fileExplorerAPI.openFileExplorer("Select a file", false , $("[name='csrfmiddlewaretoken']").val(), popup, callback_on_accept, callback_on_dismiss)

	},

// Get Results directory from the case on a popup dialog
// The dialog is shown BELOW the popup. BUG. 

				
// Fills in the drop down based on the number of steps you have 
// in the case. 

	fillCaseDefaultGoto: function() {
		var gotoStep = katana.$activeTab.find('#default_onError').val();
		console.log("Step ", gotoStep);
		var defgoto = katana.$activeTab.find('#default_onError_goto'); 
			defgoto.hide();

		if (gotoStep.trim() == 'goto') { 
			defgoto.show();
		} else {
			defgoto.hide();
			
		}

	defgoto.empty(); 
	var xdata = cases.jsonCaseObject.Teststeps;
	//console.log("Step....",Object.keys(xdata).length, xdata);
	for (var s=0; s<Object.keys(xdata).length; s++ ) {
		defgoto.append($('<option>',{ value: s,  text: s+1}));
	}
},

// Saves the UI to memory and sends to server as a POST request
	sendCaseToServer: function () {
		if ( cases.mapUiToCaseJson() < 0) { 
			return; 
		}
		var url = "./cases/getCaseDataBack";
		var csrftoken = katana.$activeTab.find("[name='csrfmiddlewaretoken']").val();
		//console.log("sending case 2");
		$.ajaxSetup({
				function(xhr, settings) {
				xhr.setRequestHeader("X-CSRFToken", csrftoken)
			}
		});


		var xfname = katana.$activeTab.find('#caseName').val();
		if (xfname.indexOf(".xml") < 0) { 
			xfname  = xfname + ".xml";
		}
		
		console.log(cases.jsonCaseObject.getJSON());
		var topNode  = { 'Testcase' : cases.jsonCaseObject.getJSON()};
		//console.log("sending case 3", xfname, cases.jsonCaseObject);
		
		$.ajax({
		url : url,
		type: "POST",
		data : { 
			'json': JSON.stringify(topNode),	
			'filetosave': xfname,
			'savesubdir': katana.$activeTab.find('#savesubdir').text(),
			},
		headers: {'X-CSRFToken':csrftoken},
		success: function( data ){
			// The following causes an exception
			//xdata = { 'heading': "Sent", 'text' : "sent the file... "+data}
			//katana.openAlert(xdata);
			alert("Saved...");
	
		},
	});
},



/*
Maps the data from a Testcase object to the UI. 
The UI currently uses jQuery and Bootstrap to display the data.
*/
 mapCaseJsonToUi: function(xdata){
	//
	// This gives me ONE object - The root for test cases
	// The step tag is the basis for each step in the Steps data array object.
	// 
	var items = []; 
	
	if (!jQuery.isArray(xdata)) xdata = [xdata]; // convert singleton to array

	console.log("mapCaseJsonToUi", cases.jsonCaseSteps, xdata); 
	//console.log("xdata =" + xdata);
	katana.$activeTab.find("#tableOfTestStepsForCase").html("");	  // Start with clean slate
	items.push('<table class="case-configuration-table table-striped" id="Step_table_display"  width="100%" >');
	items.push('<thead>');
	items.push('<tr id="StepRow"><th>#</th><th>Driver</th><th>Keyword</th><th>Description</th><th>Arguments</th>\
		<th>OnError</th><th>Execute</th><th>Run Mode</th><th>Context</th><th>Impact</th><th>Other</th></tr>');
	items.push('</thead>');
	items.push('<tbody>');
	for (var s=0; s<Object.keys(xdata).length; s++ ) {  // for s in xdata
		var oneCaseStep = xdata[s];			 // for each step in case
		console.log("The Step : ", oneCaseStep);
		var showID = parseInt(s)+1;
		items.push('<tr data-sid="'+s+'"><td>'+showID+'</td>');		// ID 
		// -------------------------------------------------------------------------
		// Validation and default assignments 
		// Create empty elements with defaults if none found. ;-)
		// -------------------------------------------------------------------------
		items.push('<td>'+oneCaseStep.step_driver +'</td>'); 
		var outstr; 
		items.push('<td>'+oneCaseStep.step_keyword + "<br>TS=" +oneCaseStep.step_TS+'</td>'); 
		outstr =  oneCaseStep['Description'];
		bid = "SelectStepInputData-"+s+"-id-";
		var fileExp = '<i title="Select Warrior Input Data" class="fa fa-plus" theSid="'+s+'" id="'+bid+'" katana-click="cases.getStepInputDataFile()" key="'+bid+'"/>';

		items.push('<td>'+outstr+'</td>'); 

		var arguments = oneCaseStep['Arguments'];
		var out_array = [] 
		var ta = 0; 
		for (xarg in arguments) {

			if (!arguments[xarg]) {
				continue;
			}
			var argvalue = arguments[xarg]['@value'];
			console.log("argvalue", argvalue);
				if (argvalue) {
				if (argvalue.length > 1) {
					var xstr =  arguments[xarg]['@name']+" = "+arguments[xarg]['@value'] + "<br>";
					//console.log(xstr);
					out_array.push(xstr); 
					}
				ta  = ta + 1; 
				}
			}
		outstr = out_array.join("");
		//console.log("Arguments --> "+outstr);
		items.push('<td>'+outstr+'</td>'); 
		items.push('<td>'+oneCaseStep.onError_action+'</td>'); 
		
		outstr = "ExecType=" + oneCaseStep.Execute_ExecType + "<br>";
		if (oneCaseStep.Execute_ExecType == 'if' || oneCaseStep.Execute_ExecType == 'if not') {
			outstr = outstr + "Condition="+oneCaseStep.Execute_Rule_Condition+ "<br>" + 
			"Condvalue="+oneCaseStep.Execute_Rule_Condvalue+ "<br>" + 
			"Else="+oneCaseStep.Execute_Rule_Elsevalue+ "<br>" +
			"Elsevalue="+oneCaseStep.Execute_Rule_Elsevalue;
		}
		 
			
		items.push('<td>'+outstr+'</td>'); 
		items.push('<td>'+oneCaseStep.runmode_type+'</td>');
		items.push('<td>'+oneCaseStep.context+'</td>');
		items.push('<td>'+oneCaseStep.impact+'</td>'); 
		var bid = "deleteTestStep-"+s+"-id-"
		items.push('<td><i title="Delete" class="fa fa-trash" theSid="'+s+'" id="'+bid+'" katana-click="cases.deleteCaseFromLine()" key="'+bid+'"/>');

		bid = "editTestStep-"+s+"-id-";
		items.push('<i title="Edit" class="fa fa-pencil" theSid="'+s+'"  id="'+bid+'" katana-click="cases.editCaseFromLine()" key="'+bid+'"/>');

		bid = "addTestStepAbove-"+s+"-id-";
		items.push('<i title="Insert" class="fa fa-plus" theSid="'+s+'"   id="'+bid+'" katana-click="cases.addCaseFromLine()" key="'+bid+'"/>');

		bid = "copyToStorage-"+s+"-id-";
		items.push('<i title="Copy to clipboard" class="fa fa-clipboard" theSid="'+s+'"   id="'+bid+'" katana-click="cases.saveTestStep()" key="'+bid+'"/>');
		bid = "copyFromStorage-"+s+"-id-";
		items.push('<i title="Copy from clipboard" class="fa fa-outdent" theSid="'+s+'"   id="'+bid+'" katana-click="cases.restoreTestStep()" key="'+bid+'"/>');

		bid = "dupTestStepAbove-"+s+"-id-";
		items.push('<i title="Duplicate" class="fa fa-copy" theSid="'+s+'"  id="'+bid+'" katana-click="cases.duplicateCaseFromLine()" key="'+bid+'"/></td>');

	}

	items.push('</tbody>');
	items.push('</table>'); // 
	katana.$activeTab.find("#tableOfTestStepsForCase").html( items.join(""));
	katana.$activeTab.find('#Step_table_display tbody').sortable( { stop: cases.testCaseSortEventHandler});
	
	cases.fillCaseDefaultGoto();
	katana.$activeTab.find('#default_onError').on('change',cases.fillCaseDefaultGoto )


	var tag = '#caseInputDataFile'
	var xf = katana.$activeTab.find(tag).val() ;
	var savefilepath = katana.$activeTab.find('#savesubdir').text();
	var nf = absFromPrefix(savefilepath,xf);
	katana.$activeTab.find(tag).attr("value", xf);			
	katana.$activeTab.find(tag).attr("fullpath", nf);
	console.log("File path ==", savefilepath, xf, nf);
			

	/*
	if (cases.jsonCaseDetails['Datatype'] == 'Custom') {
		$(".arguments-div").hide();
	} else {

		$(".arguments-div").show();
	}
	*/
	
	}, // end of function 

	deleteCaseFromLine : function() {
	var names = this.attr('key').split('-');
	var sid = parseInt(names[1]);
	cases.removeTestStep(sid);
	},

	editCaseFromLine: function() { 
	var names = this.attr('key').split('-');
	var sid = parseInt(names[1]);
	katana.popupController.open(katana.$activeTab.find("#editCaseStepDiv").html(),"Edit..." + sid, function(popup) {
		cases.setupPopupDialog(sid,cases.jsonCaseSteps,popup);
	});
	},	

	addCaseFromLine: function() {
	var names = this.attr('key').split('-');
	var sid = parseInt(names[1]);
	cases.addTestStepAboveToUI(sid,cases.jsonCaseSteps,0);
	},


	saveTestStep: function() {
	var names = this.attr('key').split('-');
	var sid = parseInt(names[1]);
	cases.jsonCaseSteps[sid].copyToDocument('lastStepCopied');
	},


	restoreTestStep: function() {
	var names = this.attr('key').split('-');
	var sid = parseInt(names[1]);
	jsonData = cases.jsonCaseSteps[sid].copyFromDocument('lastStepCopied');
	console.log("Retrieving ... ", jsonData);
	cases.addTestStepAboveToUI(sid,cases.jsonCaseSteps,2,jsonData);
	},



	duplicateCaseFromLine :function() { 
		var names = this.attr('key').split('-');
		var sid = parseInt(names[1]);
		cases.addTestStepAboveToUI(sid,cases.jsonCaseSteps,1);
	},

	makePopupArguments: function(popup,  oneCaseStep) {
		cases.lastPopup = popup; 
		var a_items = [] ;
		var xstr;
		var bid;
		var arguments = oneCaseStep['Arguments'];
		var ta = 0; 
		var sid = parseInt(popup.find("#StepRowToEdit").attr('value'));	
		console.log("Making arguments at ",sid, oneCaseStep);
		for (xarg in arguments) {
			console.log(arguments[xarg]);
			a_items.push('<div class="row">');
			a_items.push('<label class="col-md-2">Name</label><input  type="text" argid="caseArgName-'+ta+'" value="'+arguments[xarg]["@name"]+'"/>');
			a_items.push('<label class="col-md-2">Value</label><input  type="text" argid="caseArgValue-'+ta+'" value="'+arguments[xarg]["@value"]+'"/>');
			// Now a button to edit or delete ... 
			bid = "deleteCaseArg-"+sid+"-"+ta+"-id"
			a_items.push('<td><i title="Delete" class="fa fa-eraser" value="X" id="'+bid+'" key="'+bid+'"  katana-click="cases.deletePopupArgument"/>');
			
			bid = "saveCaseArg-"+sid+"-"+ta+"-id"
			a_items.push('<td><i  title="Save Argument Change" class="fa fa-floppy-o" value="Save" id="'+bid+'" key="'+bid+'"  katana-click="cases.savePopupArgument"/>');

			bid = "insertCaseArg-"+sid+"-"+ta+"-id";
			a_items.push('<td><i  title="Insert one" class="fa fa-plus" value="Save" id="'+bid+'" key="'+bid+'" katana-click="cases.insertPopupArgument"/>');
			
			ta += 1
			a_items.push('</div>');
			
		}
		popup.find("#arguments-textarea").html( a_items.join("\n"));	
		console.log("Making arguments at ",sid, oneCaseStep, popup, popup.find("#arguments-textarea"), a_items);

	},


// Fill in default GoTo steps for a popup window for a case step. 
	fillCaseStepDefaultGoto : function(popupx) {
		var popup = cases.lastPopup ;
		var gotoStep =popup.find('#SteponError-at-action').val();
		console.log("Step ", gotoStep, popup.find('#SteponError-at-action'));
		var defgoto = popup.find('#SteponError-at-value'); 
		defgoto.hide();
		defgoto.empty(); 
		var xdata = cases.jsonCaseObject.Teststeps; // ['Testcase']; 
		console.log("Step....",xdata.length, xdata);
		for (var s=0; s<xdata.length; s++ ) {
			defgoto.append($('<option>',{ value: s,  text: s+1}));
		}
		if (gotoStep == 'goto') {
			defgoto.show();
		}
	},


// Show a popup dialog with items from a case.
	setupPopupDialog: function (sid,xdata,popup) {
		katana.$activeTab.find("#editCaseStepDiv").attr('data-popup-id',popup);
		katana.$activeTab.find("#editCaseStepDiv").attr('row-id',sid);
		cases.lastPopup = popup;
		console.log(popup);  					// Merely returns the div tag
		var dd_driver = popup.find('#StepDriver');
		oneCaseStep = xdata[sid]
		var driver = oneCaseStep.step_driver  // 
		var keyword  = oneCaseStep.step_keyword   // 
		var a_items = []; 
		console.log("---- oneCase ---- ", oneCaseStep.step_driver, oneCaseStep.step_keyword , oneCaseStep);
		popup.attr("caseStep", oneCaseStep);
		popup.attr("sid", sid);
		//
		// Check if you already have this keyword defined....
		//
		if (katana.$activeTab.data("data-comments"+driver+"-"+keyword)) {
			a_items = katana.$activeTab.data("data-drivers");   // Get the list of cations 
			console.log("a_items for drivers ", a_items);       
			popup.find("#StepDriver").empty();  				// Empty all the options....
			katana.$activeTab.attr("data-drivers", a_items);                     
			for (var x =0; x < a_items.length; x++) {
					popup.find("#StepDriver").append($('<option>',{ value: a_items[x],  text: a_items[x]}));
				}
			a_items = katana.$activeTab.data("data-keywords-"+driver);                      // keep list of keywords... 
			popup.find('#StepDriver').val(oneCaseStep.step_driver);
			popup.find("#StepKeyword").empty();
	 		console.log(a_items);
	 		for (let x of a_items) {
	 			popup.find("#StepKeyword").append($('<option>',{ value: x,  text: x }));
	 			}
	 		popup.find("#StepKeyword").val(oneCaseStep.step_keyword);
			a_items = katana.$activeTab.data("data-comments"+driver+"-"+keyword);
		 	console.log("received", a_items);
			out_array = a_items[0]['comment'];
			var outstr = out_array.join("\n");
			//console.log(outstr);
			cases.lastPopup.find("#sourceCaseFileText").html(""); 
			cases.lastPopup.find("#sourceCaseFileText").html(outstr);
			cases.lastPopup.find("#sourceCaseFileDef").html(""); 
			if (a_items[0]['def']) {
 				outstr = a_items[0]['def'];
 				console.log(outstr);
				cases.lastPopup.find("#sourceCaseFileDef").html(outstr);	
 				}
 			console.log("Setting attributes",driver,keyword,a_items)
			popup.find('#StepDriver').val(oneCaseStep.step_driver);
			popup.find("#StepKeyword").val(oneCaseStep.step_keyword);
		} else {
			jQuery.getJSON("./cases/getListOfActions").done(function(data) {
					//a_items = data['actions'];
					var a_items = jQuery.extend( true, [], data['actions']);
					console.log(a_items, data['actions']);
	 				popup.find("#StepDriver").empty();  // Empty all the options....
					katana.$activeTab.data("data-drivers", a_items);                      // keep list of actions... 
					for (var x =0; x < a_items.length; x++) {
							popup.find("#StepDriver").append($('<option>',{ value: a_items[x],  text: a_items[x]}));
						}

					var sid = katana.$activeTab.find("#editCaseStepDiv").attr('row-id');
					var oneCaseStep = cases.jsonCaseSteps[sid]
		
					//console.log(dd_driver.html());
					popup.find('#StepDriver').val(oneCaseStep.step_driver);
					popup.find("#StepKeyword").val(oneCaseStep.step_keyword);
					// Now set up the keywords

					var driver = oneCaseStep.step_driver  ;
					var keyword  = oneCaseStep.step_keyword;
					console.log("Collecting ...", driver, keyword);

					jQuery.getJSON("./cases/getListOfKeywords/?driver="+driver).done(function(data) {
	 						popup.find("#StepKeyword").empty();
	 						var driver = oneCaseStep.step_driver  ;
	 						var a_items = jQuery.extend( true, [], data['keywords']);
	 						katana.$activeTab.data("data-keywords-"+driver, a_items);                      // keep list of actions... 
							console.log(a_items, driver, data['keywords']);
	 						for (let x of a_items) {
	 							popup.find("#StepKeyword").append($('<option>',{ value: x,  text: x }));
	 						}
	 					popup.find('#StepKeyword').val(oneCaseStep.step_keyword);
					
						jQuery.getJSON("./cases/getListOfComments/?driver="+driver+"&keyword="+keyword).done(function(data) {
		 					var a_items = jQuery.extend( true, {}, data['fields']);
	 						//a_items = data['fields'];
			 				console.log("received", data, a_items);
			 				out_array = a_items[0]['comment'];
			 				var outstr = out_array.join("\n");
			 				
			 				cases.lastPopup.find("#sourceCaseFileText").html(""); 
			 				cases.lastPopup.find("#sourceCaseFileText").html(outstr);
			 				cases.lastPopup.find("#sourceCaseFileDef").html(""); 
							if (a_items[0]['def']) {
				 				outstr = a_items[0]['def'];
				 				console.log(outstr);
								cases.lastPopup.find("#sourceCaseFileDef").html(outstr);	
				 				}
				 			console.log("Setting attributes",driver,keyword,a_items)
							katana.$activeTab.data("data-comments"+driver+"-"+keyword, a_items);
						});
				});
			});
		}



		//console.log(xdata);
		console.log('oneCaseStep', oneCaseStep);
		popup.find("#StepRowToEdit").attr("value",sid);

		//popup.find("#StepDriver").attr("value",oneCaseStep.step_driver);
		popup.find("#StepDriver").val(oneCaseStep.step_driver);
		console.log(popup.find("#StepDriver").val());
		popup.find("#StepKeyword").val(oneCaseStep.step_keyword);
		popup.find("#StepTS").attr("value",oneCaseStep.step_TS);
		popup.find("#StepDescription").attr("value",oneCaseStep["Description"]);
		popup.find("#StepContext").attr("value",oneCaseStep["context"]);
		popup.find("#SteponError-at-action").attr("value",oneCaseStep.onError_action);
		popup.find("#SteponError-at-value").attr("value",oneCaseStep.onError_value);
		popup.find("#runmode-at-type").attr("type",oneCaseStep.runmode_type);
		popup.find("#runmode-at-value").attr("value",oneCaseStep.runmode_value);
		popup.find("#StepImpact").attr("value",oneCaseStep["impact"]);
		popup.find("#StepInputDataFile").attr("value",oneCaseStep["InputDataFile"]);
		popup.find('.rule-condition').hide();
		if (oneCaseStep.Execute_ExecType) {
			if (oneCaseStep.Execute_ExecType == 'if' || oneCaseStep.Execute_ExecType == 'if not') {
				popup.find('.rule-condition').show();
			}
			
		}
		if (oneCaseStep.Execute_Rule) {
			popup.find('#executeRuleAtCondition').attr('value',oneCaseStep.Execute_Rule_Condition);
			popup.find('#executeRuleAtCondvalue').attr('value',oneCaseStep.Execute_Rule_Condvalue);
			popup.find('#executeRuleAtElse').attr('value',oneCaseStep.Execute_Rule_Else);
			popup.find('#executeRuleAtElsevalue').attr('value',oneCaseStep.Execute_Rule_Elsevalue);
		}
	//katana.popupController.updateActiveWindow(popup);

	cases.makePopupArguments(popup, oneCaseStep);

	// Now  set the callbacks once the DOM has new HTML elements in it
	
	// Fill in the value based on keyword and action 
	var opts = jQuery.getJSON("./cases/getListOfComments/?driver="+driver+"&keyword="+keyword).done(function(data) {
 			a_items = data['fields'];
 			console.log(data, a_items);
 			out_array = a_items[0]['comment'];
 			var outstr = out_array.join("<br>");
 			console.log(outstr);
 			popup.find("#sourceCaseFileText").html(""); 
 			popup.find("#sourceCaseFileText").html(outstr);
 			if (a_items[0]['def']) {
 				outstr = a_items[0]['def'];
 				console.log(outstr);
				cases.lastPopup.find("#sourceCaseFileDef").html(outstr);	
 				}
 		});
	
	popup.find("#StepDriver").on('change',function() {
		sid  = popup.find("#StepDriver").attr('theSid');   // 
		var oneCaseStep = cases.jsonCaseSteps[sid];
		console.log(oneCaseStep);
		//console.log("------");
		console.log(popup.find("#StepDriver").val());

		var driver =popup.find("#StepDriver").val();
		var xopts = jQuery.getJSON("./cases/getListOfKeywords/?driver="+driver).done(function(data) {
 			popup.find("#StepKeyword").empty();
 			a_items = data['keywords'];
 			console.log(xopts);
 			console.log(a_items);
 			for (let x of a_items) {
 				popup.find("#StepKeyword").append($('<option>',{ value: x,  text: x }));
 			}
 		});
	});


	popup.find("#casesExecuteAtExecType").on('change',function() {
		if (this.value == 'if' || this.value == 'if not') {
			popup.find('.rule-condition').show();			
		} else {
			popup.find('.rule-condition').hide();	
		}
	});


	popup.find("#runmode-at-value").on('change',function() {
		if (this.value == 'standard' ) {
			popup.find('.runmode-value').hide();			
		} else {
			popup.find('.runmode-value').show();	
		}
	});


	popup.find("#StepKeyword").on('change',function() {
		sid  = popup.find("#StepKeyword").attr('theSid');   // 
		var oneCaseStep = cases.jsonCaseSteps[sid];
		var keyword = popup.find("#StepKeyword").val();  // 
		var driver  = popup.find("#StepDriver").val();   // 
		var xopts = jQuery.getJSON("./cases/getListOfComments/?driver="+driver+"&keyword="+keyword).done(function(data) {
 			//console.log(data);
 			a_items = data['fields'];
 			//console.log(a_items);
 			out_array = a_items[0]['comment'];
 			var outstr = out_array.join("<br>");
 			var hhh = popup.find("#sourceCaseFileText");
 			hhh.empty(); 
 			hhh.append(outstr);
 			});
		});
	},


	closeEditedCaseStep: function() {
		// Close the popup contrller 
			katana.popupController.close();
			cases.mapCaseJsonToUi(cases.jsonCaseSteps);
	},

	saveTestCaseChanges: function() { 
			// Save popup ui to json object.
			var popup = cases.lastPopup;
			var sid = parseInt(popup.find("#StepRowToEdit").attr('value'));	
			console.log("Saving...", sid);
			cases.mapUItoTestStep(sid,popup);	
			cases.mapCaseJsonToUi(cases.jsonCaseSteps);
	},

	deletePopupArgument: function( ) {
			// Delete selected argument and save popup ui to json object.
				var names = this.attr("key").split('-');
				var sid = parseInt(names[1]);
				var aid = parseInt(names[2]);
				cases.removeOneArgument(sid,aid,cases.lastPopup);
			}, 

	savePopupArgument: function() {  
				var names = this.attr("key").split('-');
				var sid = parseInt(names[1]);
				var aid = parseInt(names[2]);
				cases.saveOneArgument(sid,aid,cases.lastPopup);
			},

	insertPopupArgument: function() {  
				var names = this.attr("key").split('-');
				var sid = parseInt(names[1]);
				var aid = parseInt(names[2]);
				cases.insertOneArgument(sid,aid,cases.lastPopup);
			},

	appendPopupArgument: function( ) {
				var sid = cases.lastPopup.find('#StepRowToEdit').attr('value');
				cases.addOneArgument(sid);
			},

	insertRequirementIntoLine: function() {
		var names = this.attr('key').split('-');
		var sid = parseInt(names[1]);
		cases.adjustRequirementsTable();
		console.log("Insert log in, ", cases.jsonCaseObject, sid);
		cases.jsonCaseObject.Requirements.insertRequirement(sid, 0, "");
		cases.createRequirementsTable();	
	},

	saveAllRequirementsCB: function() { 
		var slen = cases.jsonCaseObject.Requirements.getRequirements().length;
		for (var sid = 0; sid < slen; sid++ ) {
			var txtVl = katana.$activeTab.find("#textRequirement-name-"+sid+"-id").val();
			cases.jsonCaseObject.Requirements.setRequirement(sid, txtVl);
			console.log("Saving", sid, txtVl);
		}
		cases.createRequirementsTable();		

	},
			
	saveRequirementToLine : function(){
		var names = this.attr('key').split('-');
		var sid = parseInt(names[1]);
		var txtVl = katana.$activeTab.find("#textRequirement-name-"+sid+"-id").val();
		cases.jsonCaseObject.Requirements.setRequirement(sid, txtVl);
		cases.createRequirementsTable();	
	},

	deleteOneRequirementToLine : function() {
		var names = this.attr('key').split('-');
		var sid = parseInt(names[1]);
		cases.adjustRequirementsTable();
		rdata = cases.jsonCaseObject['Requirements']['Requirement'];
		rdata.splice(sid,1); 
		cases.createRequirementsTable();
	},



// For sorting the test case steps table. 
// Renumbers the IDs on the table and redraws it. 
	testCaseSortEventHandler : function(event, ui ) {

		var listItems = [] ; 
		var listCases = katana.$activeTab.find('#Step_table_display tbody').children(); 
		console.log(listCases);
		if (listCases.length < 2) {
		 return; 
		}
		var oldCaseSteps = cases.jsonCaseSteps;
		var newCaseSteps = new Array(listCases.length);
			
		for (xi=0; xi < listCases.length; xi++) {
			var xtr = listCases[xi];
			var ni  = xtr.getAttribute("data-sid");
			console.log(xi + " => " + ni);
			newCaseSteps[ni] = oldCaseSteps[xi];
		}

		cases.jsonCaseObject["Steps"] = newCaseSteps;
		cases.jsonCaseSteps  = cases.jsonCaseObject["Steps"]
		cases.mapCaseJsonToUi(cases.jsonCaseSteps);
		
	},

// Removes a test suite by its ID and refresh the page. 
	removeTestStep: function ( sid ){
		cases.jsonCaseSteps.splice(sid,1);
		console.log("Removing testcases "+sid+" now " + Object.keys(cases.jsonCaseSteps).length);
		cases.mapCaseJsonToUi(cases.jsonCaseSteps);
	},

// Create a fresh step at the end of the table.
	addNewTestStepToUI: function() {
		var newObj = new caseTestStepObject();

		if (!cases.jsonCaseSteps) {
			cases.jsonCaseSteps = [];
			}
		if (!jQuery.isArray(cases.jsonCaseSteps)) {
			cases.jsonCaseSteps = [cases.jsonCaseSteps];
			}

		console.log("Adding new step", cases.jsonCaseSteps,cases.jsonCaseSteps);
		cases.jsonCaseSteps.push(newObj);  // Don't delete anything
		cases.mapCaseJsonToUi(cases.jsonCaseSteps);		
	},

// Inserts a new test step 
	addTestStepAboveToUI: function (sid,xdata,copy,jsonData) {

		if (!cases.jsonCaseSteps) {
			cases.jsonCaseSteps = [];
			}
		if (!jQuery.isArray(cases.jsonCaseSteps)) {
			cases.jsonCaseSteps = [cases.jsonCaseSteps];
			}
		var aid = 0;   // Insert here. 
		if (sid < 1) { 
			aid = 0 ;
		} else {
			aid = sid;				// One below the current one. 
		}
		var newObj; 
		if (copy == 0){
			newObj = new caseTestStepObject();
			}
		if (copy == 1){
			console.log("Copying...object ", sid, " from ", cases.jsonCaseSteps[sid]);
			newObj = jQuery.extend(true, {}, cases.jsonCaseSteps[sid]); 
			}
		if (copy == 2){
			console.log("Copying...JSON data ", sid, " from ", jsonData);
			newObj = new caseTestStepObject(jsonData);
			}
		cases.jsonCaseSteps.splice(aid,0,newObj);  // Don't delete anything
		cases.mapCaseJsonToUi(cases.jsonCaseSteps);		
		},

	

	saveOneArgument: function( sid, aid, xdata) {
		var obj = cases.jsonCaseSteps[sid]['Arguments'][aid]; 	
		obj['@name'] = cases.lastPopup.find('[argid=caseArgName-'+aid+']').val();
		obj['@value'] = cases.lastPopup.find('[argid=caseArgValue-'+aid+']').val();
		console.log("Saving..arguments-div "+ sid + " aid = "+ aid);
		console.log(cases.lastPopup.find('[argid=caseArgName-'+aid+']'));
		console.log(cases.lastPopup.find('[argid=caseArgValue-'+aid+']'));
		console.log(obj);
		cases.mapCaseJsonToUi(cases.jsonCaseSteps);		
	},

 	addOneArgument: function( sid ) {
		var xx = { "@name": "New" , "@value": "New" };
		console.log("sid = ", sid, cases.jsonCaseSteps, cases.jsonCaseSteps[sid]['Arguments'] );
		cases.jsonCaseSteps[sid]['Arguments'].push(xx);
		oneCaseStep = cases.jsonCaseSteps[sid];
		cases.makePopupArguments(cases.lastPopup, oneCaseStep);
	},

	// Empty argument into location aid, for step sid in popup
 	insertOneArgument: function( sid , aid,  popup ) {
		var xx = { "@name": "" , "@value": " " };
		// if (! jQuery.isArray(cases.jsonCaseSteps[sid]['Arguments']['argument']))  {
		// 	cases.jsonCaseSteps[sid]['Arguments']['argument'] = [ cases.jsonCaseSteps[sid]['Arguments']['argument'] ];
		// }
		cases.jsonCaseSteps[sid]['Arguments'].splice(aid,0,xx);
		oneCaseStep = cases.jsonCaseSteps[sid];
		cases.makePopupArguments(cases.lastPopup, oneCaseStep);
	},

	// remove argument into location aid, for step sid in popup
 	
	removeOneArgument: function( sid, aid, popup ) {
		if (cases.jsonCaseSteps[sid]['Arguments']) { 
			cases.jsonCaseSteps[sid]['Arguments'].splice(aid,1);	
			console.log("sid =" + sid);
			console.log("aid =" + aid);
			console.log(popup);
			}
		oneCaseStep = cases.jsonCaseSteps[sid];
		cases.makePopupArguments(cases.lastPopup, oneCaseStep);
	},

// When the edit button is clicked, map step to the UI. 
	mapUItoTestStep: function(sid,popup) {
		//var sid = parseInt(katana.$activeTab.find("#StepRowToEdit").attr('value'));	
		console.log("mapUItoTestStep: ", cases.jsonCaseSteps);
			
		// Validate whether sid 
		var xdata = cases.jsonCaseSteps;

		console.log(xdata);
		console.log(sid);
		oneCaseStep = xdata[sid];
		oneCaseStep.step_driver = popup.find("#StepDriver").val();
		oneCaseStep.step_keyword = popup.find("#StepKeyword").val();
		oneCaseStep.step_TS =popup.find("#StepTS").val();
		oneCaseStep["Description"] = popup.find("#StepDescription").val();
		oneCaseStep["context"] =  popup.find("#StepContext").val();
		oneCaseStep.Execute_ExecType  = popup.find("#casesExecuteAtExecType").val();	
		//oneCaseStep["Execute"]["@ExecType"]['Rule'] = {} 
		oneCaseStep.Execute_Rule_Condition = popup.find("#executeRuleAtCondition").val();	
		oneCaseStep.Execute_Rule_Condvalue = popup.find("#executeRuleAtCondvalue").val();	
		oneCaseStep.Execute_Rule_Else      = popup.find("#executeRuleAtElse").val();	
		oneCaseStep.Execute_Rule_Elsevalue = popup.find("#executeRuleAtElsevalue").val();	
		oneCaseStep.onError_action = popup.find("#SteponError-at-action").val();
		oneCaseStep.onError_value = popup.find("#SteponError-at-value").val();
		oneCaseStep.runmode_type = popup.find("#runmode-at-type").val();
		oneCaseStep.runmode_value = popup.find("#runmode-at-value").val();
		oneCaseStep["impact"] =  popup.find("#StepImpact").val();
		oneCaseStep["InputDataFile"] =  popup.find("#StepInputDataFile").val();

		// Save all arguments already in dialog...
		console.log(cases.jsonCaseSteps[sid]['Arguments']);
		var slen =  cases.jsonCaseSteps[sid]['Arguments'].length; 
		for (var aid=0; aid<slen; aid++){
			var obj = cases.jsonCaseSteps[sid]['Arguments'][aid]; 	
			obj['@name'] = cases.lastPopup.find('[argid=caseArgName-'+aid+']').val();
			obj['@value'] = cases.lastPopup.find('[argid=caseArgValue-'+aid+']').val();
			
		}
		console.log("after saving ",oneCaseStep);
},


	addStepToCase: function(){
	// Add an entry to the jsonTestSuites....
	var newCaseStep = new caseTestStepObject();
	if (!cases.jsonCaseSteps) {
		cases.jsonCaseSteps = [];
		}
	if (!jQuery.isArray(cases.jsonCaseSteps)) {
		cases.jsonCaseSteps = [cases.jsonCaseSteps];
		}
	cases.jsonCaseSteps.push(newCaseStep);
	cases.mapCaseJsonToUi(cases.jsonCaseSteps);
},

// Save UI Requirements to JSON table. 
	saveUItoRequirements: function(){
	rdata= cases.jsonCaseObject['Requirements']['Requirement'];
	rlen = Object.keys(rdata).length;
	console.log("Number of Requirements = " + rlen );
	console.log(rdata);
	for (var s=0; s<Object.keys(rdata).length; s++ ) {
				console.log("Requirements before save "+rdata[s]);
				rdata[s] = katana.$activeTab.find("#textRequirement-"+s+"-id").attr('value');
				console.log("Requirements after save "+rdata[s]);
		}

},

	 createRequirementsTable: function(){
	var items =[]; 
	katana.$activeTab.find("#tableOfCaseRequirements").html("");  // This is a blank div. 
	items.push('<table id="Requirements_table_display" class="case-req-configuration-table  striped" width="100%" >');
	items.push('<thead>');
	items.push('<tr id="ReqRow"><th>#</th><th>Requirement</th><th>');
	items.push('<i title="Save Edit" katana-click="cases.saveAllRequirementsCB">Save All</i>')
	items.push('</th></tr>');
	items.push('</thead>');
	items.push('<tbody>');
	console.log("createRequirementsTable");
	cases.adjustRequirementsTable();
	rdata = cases.jsonCaseObject.Requirements.getRequirements() ; //cases.jsonCaseObject['Requirements']['Requirement'];
	console.log(rdata, rdata.length, cases.jsonCaseObject);
					
	for (var s=0; s<rdata.length; s++ ) {
			var oneReq = rdata[s];
			//console.log("oneReq", oneReq);
			var idnumber = parseInt(s) + 1;

			if (oneReq == null) {
				oneReq = '';
			}

			items.push('<tr data-sid=""><td>'+idnumber+'</td>');
			var bid = "textRequirement-name-"+s+"-id";	
				
			items.push('<td><input type="text" value="'+oneReq+'" id="'+bid+'"/></td>');
		
			bid = "deleteRequirement-"+s+"-id";
			items.push('<td><i  class="fa fa-trash"  title="Delete" id="'+bid+'" katana-click="cases.deleteOneRequirementToLine()" key="'+bid+'"/>');
			bid = "saveOneRequirement-"+s+"-id";
			var tbid = "textRequirement-name-"+s+"-id";	
			items.push('<i class="fa fa-floppy-o" title="Save Edit" id="'+bid+'" txtId="'+tbid+'" katana-click="cases.saveRequirementToLine()" key="'+bid+'"/>');
			bid = "insertRequirement-"+s+"-id";
			items.push('<i class="fa fa-plus"  title="Insert" id="'+bid+'" katana-click="cases.insertRequirementIntoLine()" key="'+bid+'"/></td>');

		}
	
	items.push('</tbody>');
	items.push('</table>');
		
	katana.$activeTab.find("#tableOfCaseRequirements").html(items.join(""));  //
},

	adjustRequirementsTable: function(){
		return; 
	// if (!cases.jsonCaseObject['Requirements']) cases.jsonCaseObject['Requirements'] =  { 'Requirement': [] } ;
	// if (!jQuery.isArray(cases.jsonCaseObject['Requirements']['Requirement'])) {
	// 		cases.jsonCaseObject['Requirements']['Requirement'] = [cases.jsonCaseObject['Requirements']['Requirement']];
	// }
},


	addRequirementToCase: function() {
			cases.jsonCaseObject.Requirements.insertRequirement(0,0,"");
			console.log(cases.jsonCaseObject.Requirements);
			cases.createRequirementsTable();	
		},

};

