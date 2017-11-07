 //
//
/*
/// -------------------------------------------------------------------------------

Project File Data Handler 

Author: 
Date: 

The functions in this module are designed specifically for handling project XML files
for the warrior framework. 

It is expected to work with the editProject.html file and the calls to editProject in 
the views.py python for Django. 
/// -------------------------------------------------------------------------------

*/


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
					if ( jsonDetailsData['default_onError']['@action']) this.onError_action = jsonDetailsData['default_onError']['@action'].toLowerCase(); 
					if ( jsonDetailsData['default_onError']['@value'] ) this.onError_value = jsonDetailsData['default_onError']['@value']; 			
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
			'Time': this.cDate,
			'Date' : this.cTime,
			'default_onError': { '@action': this.onError_action, '@value': this.onError_value},
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
		this.onError_action = ''; 
		this.onError_value = ''; 
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
			jsonData = 	this.createEmptySuite(); 
		}
		// Fill defaults here. 
		this.fillDefaults(jsonData);
		this.path = jsonData['path'];
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


		if (!jsonData['path']) {
			jsonData['path'] =  "New";
		}

		if (!jsonData['impact']) {
			jsonData['impact'] =  "impact";
		}

		if (! jsonData['runmode']) {
			jsonData['runmode'] = { "@type": "standard", "@value": "" };
		}

		if (! jsonData['runmode']['@value']) {
			jsonData['runmode'] = { "@type": "standard", "@value": "" };
		}
		if (! jsonData['runmode']['@type']) {
			jsonData['runmode'] = { "@type": "standard", "@value": "" };
		}

		if (!jsonData['onError']) {
			jsonData['onError'] = { "@action": "next", "@value": "" };
		}
		if (!jsonData['onError']['@value']) {
			jsonData['onError']['@value'] = "";
		}
		if (!jsonData['onError']['@action']) {
			jsonData['onError']['@action'] = "";
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

	createEmptySuite() {
		return {
			'path': '',
			'impact': '',
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



 var projects = {

	closeProject: function(){
		katana.closeSubApp();
	},

	emailCases: {
		generalBody: '',

		init: function () {
			console.log('test auto init of app');
			Cases.emailCases.generalBody = $(this);
		},
	},


	save: function(){
		katana.templateAPI.post.call( katana.$activeTab.find('.to-save'), null, null, katana.toJSON(), function( data ) {
			console.log('saved', data);
		});
	},

	lastPopup : null, 
	jsonProjectObject : [],
	jsonTestSuites : [],			// for all Suites


	initProjectTree: function() {
		jQuery.getJSON("./projects/getProjectListTree/").done(function(data) {
			var sdata = data['treejs'];
			//console.log("tree ", sdata);
			var jdata = { 'core' : { 'data' : sdata },
    					"plugins" : [ "sort" ],
    					}; 

			//console.log("Tree", sdata);
			katana.$activeTab.find('#myProjectTree').on("select_node.jstree", function (e, data) { 
		      var thePage = data.node.li_attr['data-path'];
	
		      var extn = thePage.indexOf(".xml");
		      if (extn < 4){
		        return;
		      }
		  //     katana.$view.one('tabAdded', function(){
		  //     projects.mapFullProjectJson(thePage);
		  // });
		  //
			  var xref="./projects/editProject/?fname=" + thePage; 
			  projects.thefile = thePage;

		  
			 	katana.templateAPI.subAppLoad(xref, null, function(thisPage) { 
			   			console.log("starting ...", this);
				  		projects.mapFullProjectJson(projects.thefile);
				  });
			   // katana.templateAPI.load(xref, null, null, 'Project') ;
			  });

		create_jstree_search('#myProjectTree', '#jstreeFilterText' , sdata);
			
		//katana.$activeTab.find('#myProjectTree').jstree(jdata);
		});

},

/// -------------------------------------------------------------------------------
// 
/// -------------------------------------------------------------------------------
startNewProject : function() {
  var xref="./projects/editProject/?fname=NEW" ;
  katana.templateAPI.load(xref, null, null, 'NEW') ;
},

/// -------------------------------------------------------------------------------
// Sets up the global project data holder for the UI. 
// This is called from the correspoding HTML file onLoad event 
// or when a new XML file is loaded into the interface.
// 
// Two variables are set when this function is called; 
// 1. jsonProjectObject 
// 2. jsonTestSuites is set to point to the Testsuites data structure in
//    the jsonProjectObject
//
/// -------------------------------------------------------------------------------
	mapFullProjectJson: function (myfile){
	//var sdata = katana.$activeTab.find("#listOfTestSuitesForProject").text();
	//katana.$activeTab.find('#savefilepath').hide();  // To remove later...
	//var myfile = katana.$activeTab.find('#fullpathname').text();
	jQuery.getJSON("./projects/getJSONProjectData/?fname="+myfile).done(function(data) {
			var sdata = data['fulljson'];
			console.log("from views.py call=", sdata);
			//projects.jsonProjectObject = JSON.parse(sdata); 
			projects.jsonProjectObject = new projectsObject(sdata['Project']);
			katana.$activeTab.data('projectsJSON', projects.jsonProjectObject );
			projects.jsonTestSuites = projects.jsonProjectObject['Testsuites']; 
			projects.mapProjectJsonToUi();  // This is where the table and edit form is created. 
			projects.fillProjectDefaultGoto();
			console.log("Adding defaults ");
			katana.$activeTab.find('#project_onError_action').on('change',projects.fillProjectDefaultGoto );
			katana.$activeTab.find('#Execute-at-ExecType').on('change',function() { 
				if (this.value == 'if' || this.value == 'if not')
				{
					katana.$activeTab.find('.rule-condition').hide();
				} else {
					katana.$activeTab.find('.rule-condition').show();
				}
			});
		});

	}, 

	resetUIfromFile : function() {
	  	var thePage = katana.$activeTab.find('#fullpathname').text();
	  	var xref="./projects/editProject/?fname=" + thePage; 
	  	katana.templateAPI.load(xref, null, null, 'Project') ;
	},

	addSuiteToProject: function(){
		var newTestSuite = new projectSuiteObject();
		projects.jsonProjectObject = katana.$activeTab.data('projectsJSON');
		projects.jsonTestSuites = projects.jsonProjectObject['Testsuites']; 
		projects.jsonTestSuites.push(newTestSuite);
		projects.mapProjectJsonToUi();
	},


	fillProjectSuitePopupDefaultGoto: function(popup) {

		var gotoStep =popup.find('#default_onError').val();
		console.log("Step ", gotoStep);
		var defgoto = popup.find('#default_onError_goto'); 
			defgoto.hide();

		if (gotoStep.trim() == 'goto') { 
			defgoto.show();
		} else {
			defgoto.hide();
			
		}
		defgoto.empty(); 
		projects.jsonProjectObject = katana.$activeTab.data('projectsJSON');
		projects.jsonTestSuites = projects.jsonProjectObject['Testsuites']; 
		
		var xdata = projects.jsonProjectObject['Testsuites']; 
		if (!jQuery.isArray(xdata)) xdata = [xdata]; 
		for (var s=0; s<Object.keys(xdata).length; s++ ) {
			defgoto.append($('<option>',{ value: s,  text: s}));
		}
	},


	setupProjectPopupDialog: function(s,popup) {
	console.log(s);
	projects.jsonProjectObject = katana.$activeTab.data('projectsJSON');
	projects.jsonTestSuites = projects.jsonProjectObject['Testsuites']; 
		
	var oneSuite = projects.jsonProjectObject.Testsuites[s];
	console.log(oneSuite);
	popup.find("#suiteRowToEdit").val(s); 
	popup.find("#suitePath").val(oneSuite['path']);
	popup.find("#Execute-at-ExecType").val(jsUcfirst(oneSuite.Execute_ExecType)); 
	popup.find("#executeRuleAtCondition").val(oneSuite.Execute_Rule_Condition); 
	popup.find("#executeRuleAtCondvalue").val(oneSuite.Execute_Rule_Condvalue); 
	popup.find("#executeRuleAtElse").val(oneSuite.Execute_Rule_Else); 
	popup.find("#executeRuleAtElsevalue").val(oneSuite.Execute_Rule_Elsevalue); 
	popup.find("#onError-at-action").val(oneSuite.onError_action); 
	popup.find("#onError-at-value").val(oneSuite.onError_value); 
	popup.find("#runmode-at-type").val(oneSuite.runmode_type.toLowerCase()); 
	popup.find("#runmode-at-value").val(oneSuite.runmode_value); 
	popup.find("#impact").val(oneSuite.impact); 
	projects.fillProjectSuitePopupDefaultGoto(popup);
	popup.find('#onError-at-action').on('change', function(){ 
			var popup = $(this).closest('.popup');
			projects.fillProjectSuitePopupDefaultGoto(popup);
	});
	popup.find('.rule-condition').hide();
	if (oneSuite.Execute_ExecType) {
		if (oneSuite.Execute_ExecType == 'if' || oneSuite.Execute_ExecType == 'if not') {
			popup.find('.rule-condition').show();
		}	
	}
	popup.find("#runmode-at-type").on('change', function() {
		var popup = projects.lastPopup;
		var sid = popup.find("#suiteRowToEdit").val();
		console.log(projects.jsonProjectObject.Testsuites, sid); 
		var oneSuite = projects.jsonProjectObject.Testsuites[sid];
		console.log(oneSuite);
		oneSuite.runmode_type = this.value; 
		popup.find("#runmode-at-value").show();
		if (oneSuite.runmode_type == 'standard') {
		popup.find("#runmode-at-value").hide();
		}
		
	});
	popup.find("#runmode-at-value").show();
	if (oneSuite.runmode_type == 'standard') {
		popup.find("#runmode-at-value").hide();

	}


	popup.find("#Execute-at-ExecType").on('change',function() {
			if (this.value == 'if' || this.value == 'if not') {
				popup.find('.rule-condition').show();			
			} else {
				popup.find('.rule-condition').hide();
			}
		});

	},



	mapProjectSuiteToUI: function(s,xdata) {

		projects.jsonProjectObject = katana.$activeTab.data('projectsJSON');
		projects.jsonTestSuites = projects.jsonProjectObject['Testsuites']; 
		
		var oneSuite = projects.jsonProjectObject.Testsuites[s];
		console.log(oneSuite);
		katana.$activeTab.find("#suiteRowToEdit").val(s); 
		katana.$activeTab.find("#suitePath").val(oneSuite['path']);
		katana.$activeTab.find("#Execute-at-ExecType").val(oneSuite.Execute_ExecType); 
		katana.$activeTab.find("#executeRuleAtCondition").val(oneSuite.Execute_Rule_Condition); 
		katana.$activeTab.find("#executeRuleAtCondvalue").val(oneSuite.Execute_Rule_Condvalue); 
		katana.$activeTab.find("#executeRuleAtElse").val(oneSuite.Execute_Rule_Else); 
		katana.$activeTab.find("#executeRuleAtElsevalue").val(oneSuite.Execute_ule_Elsevalue); 
		
		katana.$activeTab.find("#onError-at-action").val(oneSuite['onError_action']); 
		katana.$activeTab.find("#onError-at-value").val(oneSuite['onError_value']); 
		katana.$activeTab.find("#runmode-at-type").val(oneSuite['runmodetype'].toLowerCase()); 
		katana.$activeTab.find("#runmode-at-value").val(oneSuite['runmode_value']); 
		katana.$activeTab.find("#impact").val(oneSuite['impact']); 
		projects.fillProjectDefaultGoto();

	},

	fillProjectDefaultGoto : function() {
		projects.jsonProjectObject = katana.$activeTab.data('projectsJSON');
		projects.jsonTestSuites = projects.jsonProjectObject['Testsuites']; 
		
		var action = katana.$activeTab.find('#project_onError_action').val();
		var defgoto = katana.$activeTab.find('#project_onError_value'); 
		
		if (action.trim() == 'goto') { 
			defgoto.show();
		} else {
			defgoto.hide();
		}
		var listSuites = katana.$activeTab.find('#tableOfTestSuitesForProject tbody').children(); 
		defgoto.empty(); 
		for (xi=0; xi < listSuites.length; xi++) {
			defgoto.append($('<option>',{ value: xi,  text: xi+1}));
		}
	},

	fillProjectSuitePopupDefaultGoto : function(popup) {
		projects.jsonProjectObject = katana.$activeTab.data('projectsJSON');
		projects.jsonTestSuites = projects.jsonProjectObject['Testsuites']; 
		
		var gotoStep =popup.find('#onError-at-action').val();
		//console.log("Step ", gotoStep);
		var defgoto = popup.find('#onError-at-value'); 
		defgoto.hide();

		if (gotoStep.trim() == 'goto'.trim()) { 
			defgoto.show();
		} 
		//var sid = popup.find('#CaseRowToEdit').val();
		defgoto.empty(); 
		var xdata = projects.jsonProjectObject['Testsuites'] // ['Testcase'];
		if (!jQuery.isArray(xdata)) xdata = [xdata]; 
		for (var s=0; s<Object.keys(xdata).length; s++ ) {
			defgoto.append($('<option>',{ value: s,  text: s+1}));
		}
	},

/// -------------------------------------------------------------------------------
// This function is called to map the currently edited project suite to 
// the field being edited. 
// Note that this function is calld from an event handler which catches the 
// row number from the table.
/// -------------------------------------------------------------------------------
	mapUItoProjectSuite: function(popup, xdata){
	if (popup.find("#suitePath").val().length < 1) {
		
		data = { 'heading': "Error", 'text' : "Please specify a suite path name"}
		katana.openAlert(data);
	
		return
	}
	projects.jsonProjectObject = katana.$activeTab.data('projectsJSON');
	projects.jsonTestSuites = projects.jsonProjectObject['Testsuites']; 
		
	var s = parseInt(popup.find("#suiteRowToEdit").val());
	var oneSuite = projects.jsonProjectObject.Testsuites[s];
	oneSuite['path'] = popup.find("#suitePath").val(); 
	oneSuite['Execute'] = {}
	oneSuite.Execute_ExecType = popup.find("#Execute-at-ExecType").val(); 
	oneSuite.Execute_Rule_Condition= popup.find("#executeRuleAtCondition").val(); 
	oneSuite.Execute_Rule_Condvalue = popup.find("#executeRuleAtCondvalue").val(); 
	oneSuite.Execute_Rule_Else = popup.find("#executeRuleAtElse").val(); 
	oneSuite.Execute_Rule_Elsevalue = popup.find("#executeRuleAtElsevalue").val(); 
	oneSuite['impact'] = popup.find("#impact").val(); 
	oneSuite.onError_action = popup.find("#onError-at-action").val(); 
	oneSuite.onError_value = popup.find("#onError-at-value").val(); 
	oneSuite.runmode_type = popup.find("#runmode-at-type").val().toLowerCase(); 
	oneSuite.runmode_value = popup.find("#runmode-at-value").val(); 
	console.log("Saving", oneSuite);
},




	getSuiteDataFileForProject: function (tag) {
      var callback_on_accept = function(selectedValue) { 
      		console.log(selectedValue);
      		// Convert to relative path.
      		var pathToBase = katana.$activeTab.find('#savefilepath').text();
      		console.log("File path ==", pathToBase);
      		//var nf = katana.fileExplorerAPI.prefixFromAbs(pathToBase, selectedValue);
      		var nf = prefixFromAbs(pathToBase, selectedValue);
      		katana.$activeTab.find(tag).attr("value", nf);
      		katana.$activeTab.find(tag).attr("fullpath", selectedValue);
            };
      var callback_on_dismiss =  function(){ 
      		console.log("Dismissed");
	 };
     katana.fileExplorerAPI.openFileExplorer("Select a file", false , $("[name='csrfmiddlewaretoken']").val(), false, callback_on_accept, callback_on_dismiss);
},

	getSuiteDataForProject: function () {
		projects.jsonProjectObject = katana.$activeTab.data('projectsJSON');
		projects.jsonTestSuites = projects.jsonProjectObject['Testsuites']; 
		
		  var popup = projects.lastPopup;
		  var tag = popup.find('#suitePath');
	      var callback_on_accept = function(selectedValue) { 
	      		console.log(selectedValue);
	      		var popup = projects.lastPopup;
		 		var tag = popup.find('#suitePath');
		 		console.log(tag);
	      		// Convert to relative path.
	      		var pathToBase = katana.$activeTab.find('#savefilepath').text();
	      		var nf = prefixFromAbs(pathToBase, selectedValue);
	      		console.log("File path ==", pathToBase, nf);
	      		popup.find("#suitePath").val(nf);
	      		//katana.$activeTab.find("#suitePath").val(nf);
	      		tag.attr("value", nf);
	      		tag.attr("fullpath", selectedValue);
	            };
	      var callback_on_dismiss =  function(){ 
	      		console.log("Dismissed");
		 };
	     katana.fileExplorerAPI.openFileExplorer("Select a file", false , $("[name='csrfmiddlewaretoken']").val(), false, callback_on_accept, callback_on_dismiss);
	},


	getResultsDirForProject: function() {
      var callback_on_accept = function(selectedValue) { 
      		console.log(selectedValue);
      		// Convert to relative path.
      		var pathToBase = katana.$activeTab.find('#savefilepath').text();
      		console.log("File path ==", pathToBase);
      		var nf = prefixFromAbs(pathToBase, selectedValue);
      		katana.$activeTab.find("#projectResultsDir").attr("value", nf);
      		katana.$activeTab.find("#projectResultsDir").attr("fullpath", selectedValue);
      		katana.$activeTab.find("#projectResultsDir").val(nf);
            };
      var callback_on_dismiss =  function(){ 
      		console.log("Dismissed");
	 };
     katana.fileExplorerAPI.openFileExplorer("Select a file", false , $("[name='csrfmiddlewaretoken']").val(), false, callback_on_accept, callback_on_dismiss);

	},
 


/*
Collects data into the global project data holder from the UI 

NOTE: At the time of writing I am using jQuery and Bootstrap to show the data.

Two global variables are heavily used when this function is called; 
1. jsonProjectObject 
2. jsonTestSuites which is set to point to the Testsuites data structure in
   the jsonProjectObject

*/
	 mapUiToProjectJson: function() {

	if (katana.$activeTab.find('#projectName').val().length < 1) {
		data = { 'heading': "Error", 'text' : "Please specific a project name "}
		katana.openAlert(data);
		return; 
	}

	if (katana.$activeTab.find('#projectTitle').val().length < 1) {
		data = { 'heading': "Error", 'text' : "Please specific a title "}
		katana.openAlert(data);
		return; 
	}

	if (katana.$activeTab.find('#projectEngineer ').val().length < 1) {
		data = { 'heading': "Error", 'text' : "Please specific a name for the engineer"}
		katana.openAlert(data);
		return;
	}
	projects.jsonProjectObject = katana.$activeTab.data('projectsJSON');
		projects.jsonTestSuites = projects.jsonProjectObject['Testsuites']; 
		
	projects.jsonProjectObject['Details']['Name'] = katana.$activeTab.find('#projectName').val();

	// 
	var xfname = katana.$activeTab.find('#projectName').val();
	if (xfname.indexOf(".xml") < 2) {
		xfname = xfname + ".xml";
	}

	console.log("Save to",xfname );
	
	projects.jsonProjectObject['Details']['Title'] = katana.$activeTab.find('#projectTitle').val();
	projects.jsonProjectObject['Details']['Engineer'] = katana.$activeTab.find('#projectEngineer').val();
	projects.jsonProjectObject['Details']['State'] = katana.$activeTab.find('#projectState').val();
	projects.jsonProjectObject['Details']['Date'] = katana.$activeTab.find('#projectDate').val();
	projects.jsonProjectObject['Details']['default_onError'] = {}
	projects.jsonProjectObject['Details']['default_onError']['@action'] = katana.$activeTab.find('#default_onError').val();
	projects.jsonProjectObject['Details']['default_onError']['@value'] = katana.$activeTab.find('#default_onError_goto').val();
	projects.jsonProjectObject['Details']['ResultsDir'] = katana.$activeTab.find('#projectResultsDir').val();
	
		var date = new Date();
	  
	   var year = date.getFullYear();
       var month = date.getMonth() + 1;// months are zero indexed
       var day = date.getDate();
       var hour = date.getHours();
       var minute = date.getMinutes();
       if (minute < 10) {
       	minute = "0" + minute; 
       }
     

	projects.jsonProjectObject['Details']['Date'] = month + "/" + day + "/" + year; 
	projects.jsonProjectObject['Details']['Time'] = hour + ":" + minute; 
	
	//
	// Now walk the DOM ..
	// Create dynamic ID values based on the Suite's location in the UI. 

	// Note that if we implement drag and drop we'll have to re-index the entire 
	// visual display to reflect the movements of the order of objects on display 
	// That would require a refresh after a drop anyway. 
	//;
	var url = "./projects/getProjectDataBack";
	var csrftoken = $("[name='csrfmiddlewaretoken']").val();

	$.ajaxSetup({
			function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
    	}
	});
	
	var topNode  = { 'Project' : projects.jsonProjectObject};
	console.log("Save to",xfname , projects.jsonProjectObject);

	$.ajax({
		url:url,
	    type: "POST",
	    data : { 
	    	'json': JSON.stringify(topNode),
	    	'filetosave': xfname
	    	},
	    headers: {'X-CSRFToken':csrftoken},
    	
    success: function( data ){
    	//var outstr = "Saved "+katana.$activeTab.find('#filesavepath').text() + "/" + katana.$activeTab.find('#projectName').val();
    	//xdata = { 'heading': "Saved", 'text' : outstr }
		//katana.openAlert(xdata);
		alert("Saved...");
    	}
	});

},

//
// This creates the table for viewing data in a sortable view. 
// 
	createSuitesTable: function() {
		projects.jsonProjectObject = katana.$activeTab.data('projectsJSON');
		projects.jsonTestSuites = projects.jsonProjectObject['Testsuites']; 
		
		var items = []; 
		items.push('<table id="suite_table_display" class="project-configuration-table striped" width="100%">');
		items.push('<thead>');
		items.push('<tr id="suiteRow"><th>Num</th><th/><th>Suite</th><th>Execute</th><th>OnError</th><th>Impact</th><th/></tr>');
		items.push('</thead>');
		items.push('<tbody>');
		console.log("Create suites for ", projects.jsonProjectObject); 
		projects.jsonTestSuites = projects.jsonProjectObject['Testsuites']; 
		console.log("Create suites for ", projects.jsonProjectObject['Testsuites']); 
		
		console.log("Create suites for ", projects.jsonTestSuites); 
		var slen = projects.jsonTestSuites.length;
		katana.$activeTab.find("#tableOfTestSuitesForProject").html("");
		for (var s=0; s<slen; s++ ) {
			var oneSuite = projects.jsonProjectObject.Testsuites[s];
		
			items.push('<tr data-sid="'+s+'">');
			items.push('<td>'+(parseInt(s)+1)+'</td>');
			var tbid = "textTestSuiteFile-"+s+"-id";

			var bid = "fileSuitecase-"+s+"-id";
			items.push('<td><i title="ChangeFile" class="fa fa-folder-open" skey="'+bid+'" katana-click="projects.getFileForSuite" /></td>');
			
			//oneSuite.Execute_ExecType = jsUcfirst(oneSuite.Execute_ExecType); 
			items.push('<td id="'+tbid+'" katana-click="projects.showSuiteFromProject" skey="'+oneSuite.path+'">'+oneSuite.path+'</td>');
			items.push('<td>Type='+oneSuite.Execute_ExecType+'<br>');

			if (oneSuite.Execute_ExecType == 'if' || oneSuite.Execute_ExecType == 'if not') {
				items.push('Condition='+oneSuite.Execute_Rule_Condition+'<br>');
				items.push('Condvalue='+oneSuite.Execute_Rule_Condvalue+'<br>');
				items.push('Else='+oneSuite.Execute_Rule_Else+'<br>');
				items.push('Elsevalue='+oneSuite.Execute_Rule_Elsevalue+'<br>');
			}

			items.push('</td>');
			items.push('<td>'+oneSuite.onError_action+'</td>');
			if (oneSuite.onError_action == 'goto') {
				items.push('<td>'+oneSuite.onError_action+' '+oneSuite.onError_value+'</td>');
			} else {
				items.push('<td>'+oneSuite.onError_action+'</td>');
			}


			items.push('<td>'+oneSuite.impact+'</td>');

			var bid = "deleteTestSuite-"+s+"-id";
			items.push('<td><i  title="Delete" class="fa fa-trash" value="X" skey="'+bid+'" katana-click="projects.deleteTestSuiteCB"/>');

			bid = "editTestSuite-"+s+"-id";
			items.push('<i  title="Edit" class="fa fa-pencil" title="Edit" skey="'+bid+'" katana-click="projects.editTestSuiteCB"/>');

			bid = "InsertTestSuitebtn-"+s+"-id"
			items.push('<i  title="Insert" class="fa fa-plus" value="Insert" skey="'+bid+'" katana-click="projects.insertTestSuiteCB"/>');


			bid = "copyToStorage-"+s+"-id-";
			items.push('<i title="Copy to clipboard" class="fa fa-clipboard" theSid="'+s+'"   id="'+bid+'" katana-click="projects.copyToClipboardCB" skey="'+bid+'"/>');
			bid = "copyFromStorage-"+s+"-id-";
			items.push('<i title="Copy from clipboard" class="fa fa-outdent" theSid="'+s+'"   id="'+bid+'" katana-click="projects.insertFromClipboardCB" skey="'+bid+'"/>');

			bid = "DuplicateTestSuite-"+s+"-id"
			items.push('<i  title="Duplicate" class="fa fa-copy" value="Duplicate" skey="'+bid+'" katana-click="projects.duplicateTestSuiteCB"/></td>');

			items.push('</tr>');
			}
		items.push('</tbody>');
		items.push('</table>');

		katana.$activeTab.find("#tableOfTestSuitesForProject").html( items.join(""));
		katana.$activeTab.find('#suite_table_display tbody').sortable( { stop: projects.testProjectSortEventHandler});
		projects.fillProjectDefaultGoto();
		katana.$activeTab.find('#project_onError_action').on('change',projects.fillProjectDefaultGoto );
	},


	getFileForSuite: function() {
			var fname = this.attr('skey');
			var names = fname.split('-');
			var sid = parseInt(names[1]);
			projects.jsonProjectObject = katana.$activeTab.data('projectsJSON');
		projects.jsonTestSuites = projects.jsonProjectObject['Testsuites']; 
		
			katana.$activeTab.attr('project-suite-row',sid);
			projects.getResultsDirForProjectRow('Suites');
	},

	deleteTestSuiteCB : function(){
			var names = this.attr('skey').split('-');
			var sid = parseInt(names[1]);
			projects.jsonProjectObject = katana.$activeTab.data('projectsJSON');
		projects.jsonTestSuites = projects.jsonProjectObject['Testsuites']; 
		projects.jsonTestSuites.splice(sid,1);
			projects.mapProjectJsonToUi();	// Send in the modified array
		},

	editTestSuiteCB : function(){
			var names = this.attr('skey').split('-');
			var sid = parseInt(names[1]);
			katana.popupController.open(katana.$activeTab.find("#editTestSuiteEntry").html(),"Edit..." + sid, function(popup) {
				projects.lastPopup = popup; 
				console.log(katana.$activeTab.find("#editTestSuiteEntry"));
				projects.setupProjectPopupDialog(sid,popup);
			});
		},

	insertTestSuiteCB : function(){
			var names = this.attr('skey').split('-');
			var sid = parseInt(names[1]);
			var nb = new projectSuiteObject();
			projects.jsonProjectObject = katana.$activeTab.data('projectsJSON');
			projects.jsonTestSuites = projects.jsonProjectObject['Testsuites']; 
			projects.jsonTestSuites.splice(sid,0,nb);
			projects.mapProjectJsonToUi();	// Send in the modified array
		},


	copyToDocument: function (tag, obj) {
		localStorage.setItem(tag, JSON.stringify(obj.getJSON()));
	},

	copyFromDocument: function(tag) {
		return JSON.parse(localStorage.getItem(tag));
	},

	copyToClipboardCB : function() { 
		var names = this.attr('skey').split('-');
		var sid = parseInt(names[1]);
		//projects.jsonTestSuites[sid].copytoDocument('lastSuiteCopied', projects.jsonTestSuites[sid]);
		projects.jsonProjectObject = katana.$activeTab.data('projectsJSON');
		projects.jsonTestSuites = projects.jsonProjectObject['Testsuites']; 
		
		projects.copyToDocument('lastSuiteCopied', projects.jsonTestSuites[sid]);

	},

	insertFromClipboardCB : function() { 
		var names = this.attr('skey').split('-');
		var sid = parseInt(names[1]);
		projects.jsonProjectObject = katana.$activeTab.data('projectsJSON');
		projects.jsonTestSuites = projects.jsonProjectObject['Testsuites']; 
		
		//jsonData = projects.jjsonTestSuites[sid].copyFromDocument('lastSuiteCopied');
		jsonData = projects.copyFromDocument('lastSuiteCopied');
		console.log("Retrieving ... ", jsonData);
		var nb  = new projectSuiteObject(jsonData);
		projects.jsonTestSuites.splice(sid,0,nb);
		projects.mapProjectJsonToUi();	// Send in the modified array
	},

	duplicateTestSuiteCB : function(){
			var names = this.attr('skey').split('-');
			var sid = parseInt(names[1]);
			projects.jsonProjectObject = katana.$activeTab.data('projectsJSON');
			projects.jsonTestSuites = projects.jsonProjectObject['Testsuites']; 
		
			var jsonData = projects.jsonTestSuites[sid].getJSON();
			var nb  = new projectSuiteObject(jsonData);
			projects.jsonTestSuites.splice(sid,0,nb);
			projects.mapProjectJsonToUi();	// Send in the modified array
		},

	getResultsDirForProjectRow: function() {
	      var callback_on_accept = function(selectedValue) { 
	      		console.log(selectedValue);
	      		var sid = katana.$activeTab.attr('project-suite-row');
	      		var pathToBase = katana.$activeTab.find('#savefilepath').text();
	      		console.log("File path ==", pathToBase);
	      		var nf = prefixFromAbs(pathToBase, selectedValue);
	      		projects.jsonProjectObject = katana.$activeTab.data('projectsJSON');
				projects.jsonTestSuites = projects.jsonProjectObject['Testsuites']; 
		
	      		projects.jsonTestSuites[sid]['path'] = nf;
	      		console.log("Path set to ",nf," for ", sid);
	      		console.log(projects.jsonTestSuites);
	      		projects.createSuitesTable();
	            };
	      var callback_on_dismiss =  function(){ 
	      		console.log("Dismissed");
		 };
	     katana.fileExplorerAPI.openFileExplorer("Select a file", false , $("[name='csrfmiddlewaretoken']").val(), false, callback_on_accept, callback_on_dismiss);
	},


	showSuiteFromProject:function () {
		var fname = this.attr('skey');
		var href='/katana/suites';
		katana.templateAPI.load.call(this, href, '/static/suites/js/suites.js,', null, 'suite', function() { 
				var xref="./suites/editSuite/?fname="+fname; 
	    		katana.templateAPI.subAppLoad(xref,null,function(thisPage) {
						suites.mapFullSuiteJson(fname);
	    		});

		}); 
	},

	testProjectSortEventHandler : function(event, ui ) {
		var listSuites = katana.$activeTab.find('#tableOfTestSuitesForProject tbody').children(); 
		console.log(listSuites);
				if (listSuites.length < 2) {
		 return; 
		}
		projects.jsonProjectObject = katana.$activeTab.data('projectsJSON');
		projects.jsonTestSuites = projects.jsonProjectObject['Testsuites']; 
		
		console.log(projects.jsonProjectObject.Testsuites );
		var oldSuitesteps = projects.jsonProjectObject.Testsuites;
		var newSuitesteps = new Array(listSuites.length);
		console.log("List of ... "+listSuites.length);
		for (xi=0; xi < listSuites.length; xi++) {
			var xtr = listSuites[xi];
			var ni  = xtr.getAttribute("data-sid");
			console.log(xi + " => " + ni);
			newSuitesteps[ni] = oldSuitesteps[xi];
			}

		console.log(projects.jsonProjectObject);
		projects.jsonProjectObject.Testsuites = newSuitesteps;
		console.log(projects.jsonProjectObject.Testsuites);
		
		projects.jsonTestSuites = projects.jsonProjectObject.Testsuites;
		projects.mapProjectJsonToUi();

	},

	copyTestSuite: function (src,dst) { 
		var dst = jQuery.extend(true, {}, src); 
		return dst; 
	},

/*
// Shows the global project data holder in the UI.

NOTE: At the time of writing I am using jQuery and Bootstrap to show the data.

Two global variables are heavily used when this function is called; 
1. jsonProjectObject 
2. jsonTestSuites which is set to point to the Testsuites data structure in
   the jsonProjectObject

*/
	mapProjectJsonToUi: function(){
		projects.jsonProjectObject = katana.$activeTab.data('projectsJSON');
		projects.jsonTestSuites = projects.jsonProjectObject['Testsuites']; 
		
		katana.$activeTab.find('#projectState').val(projects.jsonProjectObject.Details.State);
		katana.$activeTab.find('#projectDate').val(projects.jsonProjectObject.Details.cDate + " " + projects.jsonProjectObject.Details.cTime);
		katana.$activeTab.find('#project_onError_action').val(projects.jsonProjectObject.Details.onError_action);
		katana.$activeTab.find('#project_onError_value').val(projects.jsonProjectObject.Details.onError_value);
		katana.$activeTab.find('#projectResultsDir').val(katana.$activeTab.find("#projectResultsDir").val());
		projects.createSuitesTable();
		projects.fillProjectDefaultGoto();
	},  // end of function 

	saveChangesToRowCB: function() {
		projects.jsonProjectObject = katana.$activeTab.data('projectsJSON');
		projects.jsonTestSuites = projects.jsonProjectObject['Testsuites']; 
		
			projects.mapUItoProjectSuite( projects.lastPopup);
			katana.popupController.close(projects.lastPopup);
			projects.mapProjectJsonToUi();
	},


};
