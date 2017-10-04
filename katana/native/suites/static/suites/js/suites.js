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
var suites= {

	jsonSuiteObject : [],
	jsonTestcases : [],			// for all Cases
	mySuiteKeywordsArray : ["path","context","runtype","impact"],
	mySuite_UI_Array : [ 'CasePath', 'CaseContext', 'CaseRuntype', 'CaseImpact'],


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
			suites.jsonSuiteObject = sdata['TestSuite'];
			if (!suites.jsonSuiteObject['Requirements']) suites.jsonSuiteObject['Requirements'] = [];
			suites.jsonTestcases = suites.jsonSuiteObject['Testcases']; 
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


	createNewCaseForSuite: function() {
		var newTestcase = {	
		'path' : "",
		"Step" : { "@Driver": "", "@keyword": "", "@TS": "1" },
		"Arguments": { "Argument" :  "" },
		"onError" :  "",
		"onError": { "@action": "next", "@value": "" }, 
		"runmode": { "@type": "standard", "@value": "" }, 
		"ExecType": { "@ExecType": "Yes", "Rule" : {} },
		"context": "",
		"impact": ""
		};
	return newTestcase;
	},

/// -------------------------------------------------------------------------------
// Dynamically create a new Testcase object and append to the suites.jsonTestcases 
// array. Default values are used to fill in a complete structure. If there is 
// no default value, a null value is inserted for the keyword
/// -------------------------------------------------------------------------------
	addCaseToSuite: function(){
	var newTestcase =suites.createNewCaseForSuite();	
	suites.jsonTestcases = suites.jsonSuiteObject['Testcases']; 
	console.log(suites.jsonSuiteObject);
	console.log(suites.jsonTestcases);
	if (!jQuery.isArray(suites.jsonTestcases['Testcase'])) {
		suites.jsonTestcases['Testcase'] = [suites.jsonTestcases['Testcase']];
		}
	console.log(suites.jsonTestcases);
	suites.jsonTestcases['Testcase'].push(newTestcase);
	suites.createCasesTable(suites.jsonTestcases['Testcase']);
},
 
	insertCaseToSuite: function(sid, copy){
	var newTestcase =suites.createNewCaseForSuite();	
	if (!jQuery.isArray(suites.jsonTestcases['Testcase'])) {
		suites.jsonTestcases['Testcase'] = [suites.jsonTestcases['Testcase']];
		}
	if (copy == 1) {
		newTestcase = jQuery.extend(true, {}, suites.jsonTestcases['Testcase'][sid]); 
	}
	suites.jsonTestcases['Testcase'].splice(sid,0,newTestcase);
	suites.createCasesTable(suites.jsonTestcases['Testcase']);
},

	mapSuiteCaseToUI: function(s,popup) {

	// This is called from an event handler ... 
	var xdata = suites.jsonTestcases['Testcase'];
	console.log(s, xdata);
	var oneCase = xdata[s];
	console.log(oneCase);
	console.log(oneCase['path']);
	popup.find("#CaseRowToEdit").val(s); 
	console.log(popup.find("#CaseRowToEdit").val());
	//katana.$activeTab.find("CasePath").val(oneCase['path']);
	popup.attr('oneCase', s);
	var myStringArray = suites.mySuiteKeywordsArray; 
	var arrayLength = suites.mySuiteKeywordsArray.length;
	for (var xi = 0; xi < arrayLength; xi++) {
		console.log("Fill "+ suites.mySuite_UI_Array[xi]);
			var xxx = "#"+ suites.mySuite_UI_Array[xi];
			popup.find(xxx).val(oneCase[myStringArray[xi]]); 
		}

	if (! oneCase['onError']) {
			oneCase['onError'] = { "@action": "next", "@value": "" };
		}

	if (! oneCase['Execute']) {
			alert("Missing Execute!!");
			oneCase['Execute'] = { "@ExecType": "yes", "Rule" : {} };
		}
	if (! oneCase['Execute']['@ExecType']) {
			alert("Missing ExecType!!");
			
			oneCase['Execute'] = { "@ExecType": "yes", "Rule" : {} };
		}

	if (! oneCase['Execute']['Rule']) {
			oneCase['Execute']['Rule'] = { '@Condition' : '', '@Condvalue' : '', '@Else': 'abort', '@Elsevalue':'' };
		}	

	oneCase['Execute']['@ExecType'] = oneCase['Execute']['@ExecType'].toLowerCase();	
	popup.find("#suiteExecuteAtExecType").val(oneCase['Execute']['@ExecType']); 
	popup.find("#executeRuleAtCondition").val(oneCase['Execute']['Rule']['@Condition']); 
	popup.find("#executeRuleAtCondvalue").val(oneCase['Execute']['Rule']['@Condvalue']); 
	popup.find("#executeRuleAtElse").val(oneCase['Execute']['Rule']['@Else']); 
	popup.find("#executeRuleAtElsevalue").val(oneCase['Execute']['Rule']['@Elsevalue']); 

	suites.fillSuiteCaseDefaultGoto(popup);
	popup.find('#caseonError-at-action').on('change', function(){ 
			
			suites.fillSuiteCaseDefaultGoto(suites.lastPopup);
	});
	console.log("FOUND Run mode  TYPE ",oneCase["runmode"]['@type'] )
	popup.find('.runmode_condition').show();
	oneCase["runmode"]['@type'] = oneCase["runmode"]['@type'].toLowerCase();
	if (oneCase["runmode"]['@type'] === 'standard') {
		console.log("Hiding... ",oneCase["runmode"]['@type']  )
		popup.find('.runmode_condition').hide();
	}

	popup.find('.rule-condition').hide();
	if (oneCase["Execute"]['@ExecType']) {
		console.log("FOUND EXECT TYPE ",oneCase["Execute"]['@ExecType'] )
		if (oneCase["Execute"]['@ExecType'] == 'if' || oneCase["Execute"]['@ExecType'] == 'if not') {
			popup.find('.rule-condition').show();
		} else {
		console.log("FOUND EXECT TYPE as  ",oneCase["Execute"]['@ExecType'] )
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
		var oneCase = suites.jsonTestcases['Testcase'][s];
		console.log("Item ",s, oneCase);
	
		oneCase['impact'] = popup.find('#CaseImpact').val();
		oneCase['path'] = popup.find('#CasePath').val();
		oneCase['context'] = popup.find('#CaseContext').val();
		oneCase['runtype'] = popup.find('#CaseRuntype').val();	
		oneCase['runmode'] = { '@type' : "" , '@value' : ""};
		oneCase['runmode']['@type'] = popup.find('#CaseRunmode').val();
		oneCase['runmode']['@value'] = popup.find('#CaseRunmodeAtValue').val();
		oneCase['onError']['@action'] = popup.find("#caseonError-at-action").val();
		oneCase['onError']['@value'] = popup.find("#caseonError-at-value").val();
		oneCase['Execute'] = {'@ExecType': '', 'Rule' : {} }
		oneCase['Execute']['Rule'] = { '@Condition' : '', '@Condvalue' : '', '@Else': 'abort', '@Elsevalue':'' };
		oneCase['Execute']['Rule'] = {}
		oneCase['Execute']['Rule']['@Condition']= popup.find("#executeRuleAtCondition").val(); 
		oneCase['Execute']['Rule']['@Condvalue'] = popup.find("#executeRuleAtCondvalue").val(); 
		oneCase['Execute']['Rule']['@Else'] = popup.find("#executeRuleAtElse").val(); 
		oneCase['Execute']['Rule']['@Elsevalue'] = popup.find("#executeRuleAtElsevalue").val(); 
		
		var exectype = popup.find("#suiteExecuteAtExecType").val();
		oneCase['Execute']['@ExecType'] = exectype ; 
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
	suites.jsonSuiteObject['Details']['Name'] = katana.$activeTab.find('#suiteName').val();
	suites.jsonSuiteObject['Details']['Title'] = katana.$activeTab.find('#suiteTitle').val();
	suites.jsonSuiteObject['Details']['Engineer'] = katana.$activeTab.find('#suiteEngineer').val();
	suites.jsonSuiteObject['Details']['Resultsdir'] = katana.$activeTab.find('#suiteResults').val();
	suites.jsonSuiteObject['Details']['State'] = katana.$activeTab.find('#suiteState').val();
	suites.jsonSuiteObject['Details']['default_onError'] = { '@value': '', '@action' : ''};
	suites.jsonSuiteObject['Details']['default_onError']['@action'] = katana.$activeTab.find('#default_OnError').val();
	suites.jsonSuiteObject['Details']['default_onError']['@value'] = katana.$activeTab.find('#default_OnError_goto').val();
	suites.jsonSuiteObject['Details']['InputDataFile'] = katana.$activeTab.find('#suiteInputDataFile').val();
	suites.jsonSuiteObject['SaveToFile'] = katana.$activeTab.find('#my_file_to_save').val();

	suites.jsonSuiteObject['Details']["type"]["@exectype"]= katana.$activeTab.find("#suiteDatatype").val();
	suites.jsonSuiteObject['Details']["type"]['@Number_Attempts']= katana.$activeTab.find("#data_type_num_attempts").val();
	suites.jsonSuiteObject['Details']["type"]['@Max_Attempts']= katana.$activeTab.find("#data_type_max_attempts").val();

	console.log("Saving ... ", suites.jsonSuiteObject['Details']);
	   var date = new Date();
	   var year = date.getFullYear();
       var month = date.getMonth() + 1;// months are zero indexed
       var day = date.getDate();
       var hour = date.getHours();
       var minute = date.getMinutes();
       if (minute < 10) {
       	minute = "0" + minute; 
       }
       
	suites.jsonSuiteObject['Details']['Date'] = month + "/" + day + "/" + year; 
	suites.jsonSuiteObject['Details']['Time'] = hour + ":" + minute;

	// Override the name 


	var xfname = suites.jsonSuiteObject['Details']['Name'];
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
	
	var topNode = { 'TestSuite' : suites.jsonSuiteObject};
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
        katana.$activeTab.find('#suiteName').val(suites.jsonSuiteObject['Details']['Name']);
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
      		suites.jsonSuiteObject['Details']['InputDataFile']= nf;
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
      		suites.jsonSuiteObject['Details']['Resultsdir']= nf;
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
      		console.log(selectedValue);
      		// Convert to relative path.
      		var sid = katana.$activeTab.attr('suite-case-row');
      		var pathToBase = katana.$activeTab.find('#savefilepath').text();
      		console.log("File path ==", pathToBase);
      		var nf = prefixFromAbs(pathToBase, selectedValue);
      		suites.jsonTestcases['Testcase'][sid]['path'] = nf;
      		console.log("Path set to ",nf," for ", sid);
      		createCasesTable(suites.jsonTestcases['Testcase']);
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
	var xdata = suites.jsonSuiteObject["Testcases"]; // ['Testcase'];
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
	for (var s=0; s<Object.keys(xdata).length; s++ ) {
		var oneCase = xdata[s];

		console.log(oneCase);
		suites.fillCaseDefaults(s,xdata);
		var showID = parseInt(s)+ 1; 
		items.push('<tr data-sid="'+s+'"><td>'+showID+'</td>');
		var bid = "fileTestcase-"+s+"-id";
		items.push('<td><i title="ChangeFile" class="fa fa-folder-open" id="'+bid+'" katana-click="suites.fileNewSuiteFromLine" key="'+bid+'"/></td>');
		items.push('<td katana-click="suites.showCaseFromSuite" skey="'+oneCase['path']+'"> '+oneCase['path']+'</td>');
		items.push('<td>'+oneCase['context']+'</td>');
		items.push('<td>'+oneCase['runtype']+'</td>');
		items.push('<td>'+oneCase['runmode']['@type']);
		if (oneCase['runmode']['@type'] != 'standard') {
			items.push('<br>'+oneCase['runmode']['@value'].toLowerCase());
		}
		items.push('</td>');
		items.push('<td>'+oneCase['onError']['@action']+'</td>');
		items.push('<td>'+oneCase['impact']+'</td>');
		bid = "deleteTestcase-"+s+"-id";
		items.push('<td><i title="Delete" class="fa fa-trash" id="'+bid+'" katana-click="suites.deleteSuiteFromLine" key="'+bid+'"/>');
		bid = "editTestcaseRow-"+s+"-id";
		items.push('<i title="Edit" class="fa fa-pencil" title="Edit" id="'+bid+'" katana-click="suites.editNewSuiteIntoLine" key="'+bid+'"/> ');
		bid = "insertTestcase-"+s+"-id";
		items.push('<i title="Insert" class="fa fa-plus" title="Insert New Case" id="'+bid+'" katana-click="suites.insertNewSuiteIntoLine" key="'+bid+'"/>');
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
	katana.$activeTab.attr('suite-case-row',sid);
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

	var oldCaseSteps = suites.jsonSuiteObject["Testcases"]['Testcase'];
	var newCaseSteps = new Array(listCases.length);

	for (xi=0; xi < listCases.length; xi++) {
		var xtr = listCases[xi];
		var ni  = xtr.getAttribute("data-sid");
		console.log(xi + " => " + ni);
		newCaseSteps[ni] = oldCaseSteps[xi];
	}

	suites.jsonSuiteObject["Testcases"]['Testcase'] = newCaseSteps;
	suites.jsonTestcases = suites.jsonSuiteObject['Testcases']; 
	suites.mapSuiteJsonToUi();  // This is where the table and edit form is created. 
},




	fillCaseDefaults : function(s, data){
		oneCase = data[s]
		console.log(data);
		if (oneCase == null) {
			data[s] = {} ;
			oneCase = data[s];
		}
		var myStringArray = suites.mySuiteKeywordsArray; // ["path","context","runtype","impact", ];
		var arrayLength =myStringArray.length;
		for (var xi = 0; xi < arrayLength; xi++) {
   				if (! oneCase[myStringArray[xi]]){
						oneCase[myStringArray[xi]] = myStringArray[xi];
					}	
		}

		if (! oneCase['onError']) {
			oneCase['onError'] = { "@action": "next", "@value": "" };
		}
		if (!oneCase['Execute']) {
			oneCase['Execute'] = { "@ExecType": "yes", "Rule": { "@Condition": "", "@Condvalue": "", "@Else": "next", "@Elsevalue": "" } };
		}
		if (!oneCase['Execute']['@ExecType']) {
			oneCase['Execute'] = { "@ExecType": "yes", "Rule": { "@Condition": "", "@Condvalue": "", "@Else": "next", "@Elsevalue": "" } };
		}
		if (!oneCase['Execute']['Rule']) {
			oneCase['Execute'][ "Rule"] = { "@Condition": "", "@Condvalue": "", "@Else": "next", "@Elsevalue": "" } ;
		}	
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
	for (var s=0; s<Object.keys(rdata).length; s++ ) {
		var oneReq = rdata[s];
		var idnumber = s + 1
		items.push('<tr data-sid=""><td>'+idnumber+'</td>');
		//items.push('<td>'+oneReq+'</td>');
		var bid = "textRequirement-name-"+s+"-id";	
		items.push('<td><input type="text" value="'+oneReq['@name']+'" id="'+bid+'" /></td>');
		bid = "deleteRequirement-"+s+"-id";
		
		items.push('<td><i  class="fa fa-trash"  title="Delete" skey="'+bid+'" katana-click="suites.deleteRequirementCB"/>');
		bid = "editRequirement-"+s+"-id";
		items.push('<i class="fa fa-floppy-o" title="Save Edit" skey="'+bid+'" katana-click="suites.saveRequirementCB"/>');
		bid = "insertRequirement-"+s+"-id";
		items.push('<i class="fa fa-plus"  title="Insert" skey="'+bid+'" katana-click="suites.insertRequirementCB"/></td>');
		
	}
	items.push('</tbody>');
	items.push('</table>');
	katana.$activeTab.find("#tableOfTestRequirements").html( items.join(""));
	

},

	saveAllRequirementsCB: function() { 
		var slen = suites.jsonSuiteObject['Requirements'].length;
		//console.log("slen=", slen);
		for (var sid = 0; sid < slen; sid++ ) {
			var txtNm = katana.$activeTab.find("#textRequirement-name-"+sid+"-id").val();
			//console.log("text ", txtNm);
			suites.jsonSuiteObject['Requirements'][sid]  = { "@name": txtNm, "@value": ''}
		}
		suites.createSuiteRequirementsTable(suites.jsonSuiteObject['Requirements']);	

	},


	saveRequirementCB:function() {
			var names = this.attr('skey').split('-');
			var sid = parseInt(names[1]);
			//console.log("xdata --> "+ rdata);  // Get this value and update your json. 
			var txtNm = katana.$activeTab.find("#textRequirement-name-"+sid+"-id").val();
			//var txtVl = katana.$activeTab.find("#textRequirement-value-"+sid+"-id").val();
			var txtVl = '';
			//console.log("Editing ..." + sid);
			// console.log(suites.jsonSuiteObject['Requirements'][sid])
			suites.jsonSuiteObject['Requirements'][sid]  = { "@name": txtNm, "@value": txtVl};
			suites.createSuiteRequirementsTable(suites.jsonSuiteObject['Requirements']);	

			//This is where you load in the edit form and display this row in detail. 
		},

	deleteRequirementCB:	function() {
			var names = this.attr('skey').split('-');
			var sid = parseInt(names[1]);
			// console.log("Remove " + sid + " " + this.id ); 
			suites.jsonSuiteObject['Requirements'].splice(sid,1);
			suites.createSuiteRequirementsTable(suites.jsonSuiteObject['Requirements']);	
			
		},
	
	insertRequirementCB:function( ) {
			var names = this.attr('skey').split('-');
			var sid = parseInt(names[1]);
			// console.log("Insert" + sid + " " + this.id ); 
			suites.insertRequirementToSuite(sid);
			suites.createSuiteRequirementsTable(suites.jsonSuiteObject['Requirements']);	
		},

	removeRequirement : function(s,rdata){
	// console.log(rdata);
	rdata.splice(s,1);
		
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
	if (!suites.jsonSuiteObject['Requirements']) suites.jsonSuiteObject['Requirements'] = [];
	if (!jQuery.isArray(suites.jsonSuiteObject['Requirements'])) suites.jsonSuiteObject['Requirements'] = [suites.jsonSuiteObject['Requirements']]; 
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


		datatype = suites.jsonSuiteObject["Details"]["type"]["@exectype"];
		datatype = datatype.toLowerCase(); 
		katana.$activeTab.find('#data_type_max_attempts').hide();
		katana.$activeTab.find('#data_type_num_attempts').hide();
		if (datatype == 'ruf' || datatype=='rup') {
			katana.$activeTab.find('#data_type_max_attempts').show();
		}
		if (datatype =='rmt'){
			katana.$activeTab.find('#data_type_num_attempts').show();
		}

	suites.createSuiteRequirementsTable(suites.jsonSuiteObject['Requirements']);
},  

// Saves your suite to disk. 
	saveSuitesCaseUI : function() {	
		suites.mapUItoSuiteCase();
		suites.createCasesTable(suites.jsonTestcases['Testcase']);
		suites.mapSuiteJsonToUi();
},

	insertRequirementToSuite : function(sid) {
			// console.log("Add Requirement... ");
			if (!suites.jsonSuiteObject['Requirements']) suites.jsonSuiteObject['Requirements'] = [];
			rdata = suites.jsonSuiteObject['Requirements'];
			var newReq = {"Requirement" : { "@name": "", "@value": ""},};
			rdata.splice(sid - 1, 0, newReq); 
			// console.log(suites.jsonSuiteObject);
			suites.createSuiteRequirementsTable(suites.jsonSuiteObject['Requirements']);	
},

	addRequirementToSuite : function() {
			if (!suites.jsonSuiteObject['Requirements']) suites.jsonSuiteObject['Requirements'] = [];
			suites.jsonSuiteObject['Requirements'].push({"Requirement" : { "@name": "", "@value": ""},});
			//console.log(suites.jsonSuiteObject);
			suites.createSuiteRequirementsTable(suites.jsonSuiteObject['Requirements']);	
},


// Removes a test Case by its ID and refresh the page. 
	removeTestcase : function(sid ){
	suites.jsonTestcases['Testcase'].splice(sid,1);
	console.log("Removing test Cases "+sid+" now " + Object.keys(suites.jsonTestcases).length);
	suites.mapSuiteJsonToUi();	// Send in the modified array
},


};