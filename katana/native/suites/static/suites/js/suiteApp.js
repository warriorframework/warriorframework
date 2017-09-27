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
	var tlen = rf.length - stack.length; 
    var blen = stack.length;
	for (var k=0;k < tlen-1; k++) {
		upem.push("..");
	}
	return upem.join("/") + "/" + bf.splice(blen).join('/') + "/" +  rf[rf.length - 1];
}


var suiteApp = {

	jsonSuiteObject : [],
	jsonTestcases : [],			// for all Cases
	mySuiteKeywordsArray : ["path","context","runtype","impact"],
	mySuite_UI_Array : [ 'CasePath', 'CaseContext', 'CaseRuntype', 'CaseImpact'],


	startNewSuite: function() {
	  var xref="./suites/editSuite/?fname=NEW"; 
	  katana.templateAPI.load(xref, null, null, 'SuiteNew') ;
	   katana.$view.one('tabAdded', function(){
	      suiteApp.mapFullSuiteJson("NEW");
	  });
	},


	displayTreeOfSuites: function(){
		jQuery.getJSON("./suites/getSuiteListTree/").done(function(data) {
			var sdata = data['treejs'];
			console.log("tree ", sdata);
			var jdata = { 'core' : { 'data' : sdata }}; 
			katana.$activeTab.find('#mySuiteTree').jstree(jdata); 
		});
		katana.$activeTab.find('#mySuiteTree').on("select_node.jstree", function (e, data) { 
			      var thePage = data.node.li_attr['data-path'];
			      console.log(thePage);
			      var extn = thePage.indexOf(".xml");
			      if (extn < 4){
			        return;
			      }
			      katana.$view.one('tabAdded', function(){
			      suiteApp.mapFullSuiteJson(thePage);
		  	});
		  var xref="./suites/editSuite/?fname=" + thePage; 
		  katana.templateAPI.load(xref, null, null, 'Suite') ;
		});

	},
/// -------------------------------------------------------------------------------
// Sets up the global Suite data holder for the UI. 
// This is called from the correspoding HTML file onLoad event 
// or when a new XML file is loaded into the interface.
// 
// Two variables are set when this function is called; 
// 1. suiteApp.jsonSuiteObject 
// 2. suiteApp.jsonTestcases is set to point to the Testcases data structure in
//    the suiteApp.jsonSuiteObject
//
/// -------------------------------------------------------------------------------
	mapFullSuiteJson: function(myobjectID){
	//console.log('Mapping data ... ' + typeof(sdata) + ' is [' + sdata + "] " + sdata.length);  // This jdata is a string ....
	var myfile = katana.$activeTab.find('#fullpathname').text();
	jQuery.getJSON("./suites/getJSONSuiteData/?fname="+myfile).done(function(data) {
			var sdata = data['fulljson'];
			console.log("from views.py call=", sdata);
			suiteApp.jsonSuiteObject = sdata['TestSuite'];
			if (!suiteApp.jsonSuiteObject['Requirements']) suiteApp.jsonSuiteObject['Requirements'] = [];
			suiteApp.jsonTestcases = suiteApp.jsonSuiteObject['Testcases']; 
			suiteApp.mapSuiteJsonToUi();  // This is where the table and edit form is created. 
			katana.$activeTab.find('#default_onError').on('change',suiteApp.fillSuiteDefaultGoto );
			katana.$activeTab.find('#suiteState').on('change',suiteApp.fillSuiteState );
		});
	} ,

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
// Dynamically create a new Testcase object and append to the suiteApp.jsonTestcases 
// array. Default values are used to fill in a complete structure. If there is 
// no default value, a null value is inserted for the keyword
/// -------------------------------------------------------------------------------
	addCaseToSuite: function(){
	var newTestcase =suiteApp.createNewCaseForSuite();	
	suiteApp.jsonTestcases = suiteApp.jsonSuiteObject['Testcases']; 
	console.log(suiteApp.jsonSuiteObject);
	console.log(suiteApp.jsonTestcases);
	if (!jQuery.isArray(suiteApp.jsonTestcases['Testcase'])) {
		suiteApp.jsonTestcases['Testcase'] = [suiteApp.jsonTestcases['Testcase']];
		}
	console.log(suiteApp.jsonTestcases);
	suiteApp.jsonTestcases['Testcase'].push(newTestcase);
	suiteApp.createCasesTable(suiteApp.jsonTestcases['Testcase']);
},
 
	insertCaseToSuite: function(sid, copy){
	var newTestcase =suiteApp.createNewCaseForSuite();	
	if (!jQuery.isArray(suiteApp.jsonTestcases['Testcase'])) {
		suiteApp.jsonTestcases['Testcase'] = [suiteApp.jsonTestcases['Testcase']];
		}
	if (copy == 1) {
		newTestcase = jQuery.extend(true, {}, suiteApp.jsonTestcases['Testcase'][sid]); 
	}
	suiteApp.jsonTestcases['Testcase'].splice(sid,0,newTestcase);
	suiteApp.createCasesTable(suiteApp.jsonTestcases['Testcase']);
},

	mapSuiteCaseToUI: function(s,popup) {

	// This is called from an event handler ... 
	var xdata = suiteApp.jsonTestcases['Testcase'];
	console.log(s, xdata);
	var oneCase = xdata[s];
	console.log(oneCase);
	console.log(oneCase['path']);
	popup.find("#CaseRowToEdit").val(s); 
	console.log(popup.find("#CaseRowToEdit").val());
	//katana.$activeTab.find("CasePath").val(oneCase['path']);
	popup.attr('oneCase', s);
	var myStringArray = suiteApp.mySuiteKeywordsArray; 
	var arrayLength = suiteApp.mySuiteKeywordsArray.length;
	for (var xi = 0; xi < arrayLength; xi++) {
		console.log("Fill "+ suiteApp.mySuite_UI_Array[xi]);
			var xxx = "#"+ suiteApp.mySuite_UI_Array[xi];
			popup.find(xxx).val(oneCase[myStringArray[xi]]); 
		}

	if (! oneCase['onError']) {
			oneCase['onError'] = { "@action": "next", "@value": "" };
		}

	if (! oneCase['Execute']) {
			oneCase['Execute'] = { "@ExecType": "yes", "Rule" : {} };
		}
	if (! oneCase['Execute']['@ExecType']) {
			oneCase['Execute'] = { "@ExecType": "yes", "Rule" : {} };
		}

	if (! oneCase['Execute']['Rule']) {
			oneCase['Execute']['Rule'] = { '@Condition' : '', '@Condvalue' : '', '@Else': 'abort', '@Elsevalue':'' };
		}	
	popup.find("#Execute-at-ExecType").val(oneCase['Execute']['@ExecType']); 
	popup.find("#executeRuleAtCondition").val(oneCase['Execute']['Rule']['@Condition']); 
	popup.find("#executeRuleAtCondvalue").val(oneCase['Execute']['Rule']['@Condvalue']); 
	popup.find("#executeRuleAtElse").val(oneCase['Execute']['Rule']['@Else']); 
	popup.find("#executeRuleAtElsevalue").val(oneCase['Execute']['Rule']['@Elsevalue']); 

	suiteApp.fillSuiteCaseDefaultGoto(popup);
	popup.find('#caseonError-at-action').on('change', function(){ 
			
			suiteApp.fillSuiteCaseDefaultGoto(suiteApp.lastPopup);
	});
	console.log("FOUND Run mode  TYPE ",oneCase["runmode"]['@type'] )
	popup.find('.runmode_condition').show();
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
	popup.find("#Execute-at-ExecType").on('change',function() {
			if (this.value == 'if' || this.value == 'if not') {
				popup.find('.rule-condition').show();			
			} else {
				popup.find('.rule-condition').hide();
				
			}
		});
	
	popup.find("#CaseRunmode").on('change',function() {

			if ( this.value === 'standard') {
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
	var popup = suiteApp.lastPopup; 
	var xdata = suiteApp.jsonTestcases['Testcase'];
	var s = parseInt(popup.find("#CaseRowToEdit").val());
	console.log(xdata);
	console.log(s);
	var oneCase = xdata[s];
	var id = s; // katana.$activeTab.find("#CaseRowToEdit").val();
	console.log(oneCase);
	
	oneCase['impact'] = popup.find('#CaseImpact').val();
	oneCase['path'] = popup.find('#CasePath').val();
	oneCase['context'] = popup.find('#CaseContext').val();
	oneCase['runtype'] = popup.find('#CaseRuntype').val();
	
	oneCase['runmode'] = { '@type' : "" , '@value' : ""};
	oneCase['runmode']['@type'] = popup.find('#CaseRunmode').val();
	oneCase['runmode']['@value'] = popup.find('#caseRunmodeAtValue').val();

	oneCase['onError']['@action'] = popup.find("#caseonError-at-action").val();
	oneCase['onError']['@value'] = popup.find("#caseonError-at-value").val();

	oneCase['Execute'] = {}
	oneCase['Execute']['@ExecType'] = popup.find("#Execute-at-ExecType").val().toLowerCase(); 
	oneCase['Execute']['Rule'] = {}
	oneCase['Execute']['Rule']['@Condition']= popup.find("#executeRuleAtCondition").val(); 
	oneCase['Execute']['Rule']['@Condvalue'] = popup.find("#executeRuleAtCondvalue").val(); 
	oneCase['Execute']['Rule']['@Else'] = popup.find("#executeRuleAtElse").val(); 
	oneCase['Execute']['Rule']['@Elsevalue'] = popup.find("#executeRuleAtElsevalue").val(); 

},
/*
Collects data into the global Suite data holder from the UI and returns the XML back 
NOTE: At the time of writing I am using jQuery and Bootstrap to show the data.

Two global variables are heavily used when this function is called; 
1. suiteApp.jsonSuiteObject 
2. suiteApp.jsonTestcases which is set to point to the Testcases data structure in
   the suiteApp.jsonSuiteObject

*/
	mapUiToSuiteJson: function() {

	if (katana.$activeTab.find("#suiteName").val().length < 1) {
		alert("Please specify a Suite name");
		return
	}
	if (katana.$activeTab.find("#suiteTitle").val().length < 1) {
		alert("Please specify a Suite title");
		return
	}

	if (katana.$activeTab.find("#suiteEngineer").val().length < 1) {
		alert("Please specify a Suite Engineer");
		return
	}
	
	suiteApp.jsonSuiteObject['Details']['Name'] = katana.$activeTab.find('#suiteName').val();
	suiteApp.jsonSuiteObject['Details']['Title'] = katana.$activeTab.find('#suiteTitle').val();
	suiteApp.jsonSuiteObject['Details']['Engineer'] = katana.$activeTab.find('#suiteEngineer').val();
	suiteApp.jsonSuiteObject['Details']['Resultsdir'] = katana.$activeTab.find('#suiteResults').val();
	suiteApp.jsonSuiteObject['Details']['Date'] = katana.$activeTab.find('#suiteDate').val().split(' ')[0];
	suiteApp.jsonSuiteObject['Details']['Time'] = katana.$activeTab.find('#suiteDate').val().split(' ')[1];
	suiteApp.jsonSuiteObject['Details']['default_onError'] = { '@value': '', '@action' : ''};
	suiteApp.jsonSuiteObject['Details']['default_onError']['@action'] = katana.$activeTab.find('#defaultOnError').val();
	suiteApp.jsonSuiteObject['Details']['default_onError']['@value'] = katana.$activeTab.find('#defaultOnError_goto').val();
	suiteApp.jsonSuiteObject['Details']['InputDataFile'] = katana.$activeTab.find('#suiteInputDataFile').val();
	suiteApp.jsonSuiteObject['SaveToFile'] = katana.$activeTab.find('#my_file_to_save').val();

	console.log("Saving ... ", suiteApp.jsonSuiteObject['Details']);


	// Override the name 
	var newname = katana.$activeTab.find('#my_file_to_save').val();
	var nlen = newname.length - 4; 
	suiteApp.jsonSuiteObject['Details']['Name'] = newname.slice(0,nlen); 
	
	console.log(suiteApp.jsonSuiteObject);
	console.log(suiteApp.jsonSuiteObject['Testcases']);
	var url = "./suites/getSuiteDataBack";
	var csrftoken = $("[name='csrfmiddlewaretoken']").val();

	$.ajaxSetup({
			function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
    	}
	});
	
	var topNode = { 'TestSuite' : suiteApp.jsonSuiteObject};
	//var topNode = 
	$.ajax({
	    url : url,
	    type: "POST",
	    data : { 
	    	'json': JSON.stringify(topNode),
	    	
	    	'filetosave': $('#my_file_to_save').val(),
	    	'savefilepath': katana.$activeTab.find('#savefilepath').text()
	    	},
	    headers: {'X-CSRFToken':csrftoken},
    
    success: function( data ){
        alert("Saved " + katana.$activeTab.find('#savefilepath').text());
        katana.$activeTab.find('#suiteName').val(suiteApp.jsonSuiteObject['Details']['Name']);
    	}
	});

},


	 getInputDataForSuite: function () {
      var callback_on_accept = function(selectedValue) { 
      		console.log(selectedValue);
      		var pathToBase = katana.$activeTab.find('#savefilepath').text();
      		console.log("File path ==", pathToBase);
      		var nf = prefixFromAbs(pathToBase, selectedValue);
      		suiteApp.jsonSuiteObject['Details']['InputDataFile']= nf;
      		console.log("Path set to ",nf);
      		katana.$activeTab.find('#suiteInputDataFile').val(nf);
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
      		suiteApp.jsonSuiteObject['Details']['Resultsdir']= nf;
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
      		suiteApp.jsonTestcases['Testcase'][sid]['path'] = nf;
      		console.log("Path set to ",nf," for ", sid);
      		createCasesTable(suiteApp.jsonTestcases['Testcase']);
            };
      var callback_on_dismiss = function(){ 
      		console.log("Dismissed");
	 };
     katana.fileExplorerAPI.openFileExplorer("Select a file", false , $("[name='csrfmiddlewaretoken']").val(), false, callback_on_accept, callback_on_dismiss);
},

	fillSuiteDefaultGoto :function() {

	var gotoStep = katana.$activeTab.find('#default_onError').val();
	//console.log("Step ", gotoStep);
	var defgoto = katana.$activeTab.find('#suite_default_onError_goto'); 
		defgoto.hide();

	if (gotoStep.trim() == 'goto'.trim()) { 
		defgoto.show();
	} else {
		defgoto.hide();
		
	}

	defgoto.empty(); 
	var xdata = suiteApp.jsonSuiteObject["Testcases"]; // ['Testcase'];
	if (!jQuery.isArray(xdata)) xdata = [xdata]; 
	for (var s=0; s<Object.keys(xdata).length; s++ ) {
		defgoto.append($('<option>',{ value: s,  text: s+1}));
	}
},

	fillSuiteCaseDefaultGoto : function(popup) {

	var gotoStep =popup.find('#caseonError-at-action').val();
	var defgoto = popup.find('#caseonError-at-value'); 
	defgoto.hide();

	if (gotoStep.trim() == 'goto'.trim()) { 
		defgoto.show();
	} else {
		defgoto.hide();
		
	}
	//var sid = popup.find('#CaseRowToEdit').val();
	defgoto.empty(); 
	var xdata = suiteApp.jsonSuiteObject["Testcases"]; // ['Testcase'];
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

	items.push('<table id="Case_table_display" class="suite_configuration_table" width="100%">');
	items.push('<thead>');
	items.push('<tr id="CaseRow"><th>Num</th><th></th><th>Path</th><th></th><th>context</th><th>Run Type</th><th>Mode</th><th>OnError</th><th>Impact</th><th/><th/></tr>');
	items.push('</thead>');
	items.push('<tbody>');

	//console.log(xdata);
	katana.$activeTab.find("#tableOfTestcasesForSuite").html("");
	for (var s=0; s<Object.keys(xdata).length; s++ ) {
		var oneCase = xdata[s];

		console.log(oneCase);
		suiteApp.fillCaseDefaults(s,xdata);
		var showID = parseInt(s)+ 1; 
		items.push('<tr data-sid="'+s+'"><td>'+showID+'</td>');
		var bid = "fileTestcase-"+s+"-id";
		items.push('<td><i title="ChangeFile" class="fa fa-folder-open" id="'+bid+'" katana-click="fileNewSuiteFromLine" key="'+bid+'"/></td>');
		items.push('<td onclick="showCaseFromSuite('+"'"+oneCase['path']+"'"+')">'+oneCase['path']+'</td>');
		items.push('<td>'+oneCase['context']+'</td>');
		items.push('<td>'+oneCase['runtype']+'</td>');
		items.push('<td>'+oneCase['runmode']['@type']);
		if (oneCase['runmode']['@type'] != 'standard') {
			items.push('<br>'+oneCase['runmode']['@value']);
		}
		items.push('</td>');
		items.push('<td>'+oneCase['onError']['@action']+'</td>');
		items.push('<td>'+oneCase['impact']+'</td>');
		bid = "deleteTestcase-"+s+"-id";
		items.push('<td><i title="Delete" class="fa fa-trash" id="'+bid+'" katana-click="suiteApp.deleteSuiteFromLine" key="'+bid+'"/>');
		bid = "editTestcaseRow-"+s+"-id";
		items.push('<i title="Edit" class="fa fa-pencil" title="Edit" id="'+bid+'" katana-click="suiteApp.editNewSuiteIntoLine" key="'+bid+'"/> ');
		bid = "insertTestcase-"+s+"-id";
		items.push('<i title="Insert" class="fa fa-plus" title="Insert New Case" id="'+bid+'" katana-click="suiteApp.insertNewSuiteIntoLine" key="'+bid+'"/>');
		bid = "dupTestcase-"+s+"-id";
		items.push('<i title="Duplicate" class="fa fa-copy" title="Duplicate New Case" id="'+bid+'" katana-click="suiteApp.duplicateNewSuiteIntoLine" key="'+bid+'"/></td>');
		items.push('</tr>');
	}
	items.push('</tbody>');
	items.push('</table>');
	katana.$activeTab.find("#tableOfTestcasesForSuite").html( items.join(""));
	katana.$activeTab.find('#Case_table_display tbody').sortable( { stop: suiteApp.testSuiteSortEventHandler});

	suiteApp.fillSuiteDefaultGoto();
},

	insertNewSuiteIntoLine : function() {
	console.log(this.attr('key'));
	var names = this.attr('key').split('-');
	console.log(this.attr('key'));
	var sid = parseInt(names[1]);
	suiteApp.insertCaseToSuite(sid,0);
},

 deleteSuiteFromLine :function() {
	var names = this.attr('key').split('-');
	var sid = parseInt(names[1]);
	suiteApp.removeTestcase(sid,xdata);
},

	 duplicateNewSuiteIntoLine : function( ){
	var names = this.attr('key').split('-');
	var sid = parseInt(names[1]);
	suiteApp.insertCaseToSuite(sid,1);
},


	editNewSuiteIntoLine : function() {
	var names = this.attr('key').split('-');
	var sid = parseInt(names[1]);
		katana.popupController.open(katana.$activeTab.find("#editTestCaseEntry").html(),"Edit..." + sid, function(popup) {
			suiteApp.lastPopup = popup;
			suiteApp.mapSuiteCaseToUI(sid,popup);
		});

},

	fileNewSuiteFromLine :function(){ 
	var names = this.attr('key').split('-');
	var sid = parseInt(names[1]);
	katana.$activeTab.attr('suite-case-row',sid);
	suiteApp.getResultsDirForSuiteRow();
},

	showCaseFromSuite : function (fname) {
  var xref="./cases/editCase/?fname="+fname; 
  //console.log("Calling case ", fname, xref);
    katana.$view.one('tabAdded', function(){
         suiteApp.mapFullCaseJson(fname,'#listOfTestStepsForCase');
    });
  katana.templateAPI.load(xref, null, null, 'suite') ;;
},
//
	testSuiteSortEventHandler : function(event, ui ) {
	var listItems = [] ; 
	var listCases = katana.$activeTab.find('#Case_table_display tbody').children(); 
	console.log(listCases);
		if (listCases.length < 2) {
	 return; 
	}

	var oldCaseSteps = suiteApp.jsonSuiteObject["Testcases"]['Testcase'];
	var newCaseSteps = new Array(listCases.length);

	for (xi=0; xi < listCases.length; xi++) {
		var xtr = listCases[xi];
		var ni  = xtr.getAttribute("data-sid");
		console.log(xi + " => " + ni);
		newCaseSteps[ni] = oldCaseSteps[xi];
	}

	suiteApp.jsonSuiteObject["Testcases"]['Testcase'] = newCaseSteps;
	suiteApp.jsonTestcases = suiteApp.jsonSuiteObject['Testcases']; 
	suiteApp.mapSuiteJsonToUi();  // This is where the table and edit form is created. 
},




	fillCaseDefaults : function(s, data){
		oneCase = data[s]
		console.log(data);
		if (oneCase == null) {
			data[s] = {} ;
			oneCase = data[s];
		}
		var myStringArray = suiteApp.mySuiteKeywordsArray; // ["path","context","runtype","impact", ];
		var arrayLength =myStringArray.length;
		for (var xi = 0; xi < arrayLength; xi++) {
   				if (! oneCase[myStringArray[xi]]){
						oneCase[myStringArray[xi]] = myStringArray[xi];
					}
   				
		}

		if (! oneCase['onError']) {
			oneCase['onError'] = { "@action": "next", "@value": "" };
		}
		oneCase['Execute'] = { "@ExecType": "Yes", "Rule": { "@Condition": "", "@Condvalue": "", "@Else": "next", "@Elsevalue": "" } };
		
},

	createSuiteRequirementsTable : function(rdata){
	var items =[]; 
	katana.$activeTab.find("#tableOfTestRequirements").html("");
	
	items.push('<table id="Case_Req_table_display" class="suite_req_configuration_table  striped" width="100%" >');
	items.push('<thead>');
	items.push('<tr id="ReqRow"><th>#</th><th>Requirement</th><th/><th/></tr>');
	items.push('</thead>');
	items.push('<tbody>');
	console.log(rdata);
	for (var s=0; s<Object.keys(rdata).length; s++ ) {
		var oneReq = rdata[s];
		var idnumber = s + 1
		items.push('<tr data-sid=""><td>'+idnumber+'</td>');
		//items.push('<td>'+oneReq+'</td>');
		var bid = "textRequirement-name-"+s+"-id";	
		items.push('<td><input type="text" value="'+oneReq['@name']+'" id="'+bid+'" /></td>');
		bid = "deleteRequirement-"+s+"-id";
		console.log("Line 328 or so "+bid); 
		items.push('<td><i  class="fa fa-trash"  title="Delete" key="'+bid+'" katana-click="deleteRequirementCB"/>');
		bid = "editRequirement-"+s+"-id";
		items.push('<i class="fa fa-pencil" title="Save Edit" key="'+bid+'" katana-click="saveRequirementCB"/>');
		bid = "insertRequirement-"+s+"-id";
		items.push('<i class="fa fa-plus"  title="Insert" key="'+bid+'" katana-click="insertRequirementCB"/></td>');
		
	}
	items.push('</tbody>');
	items.push('</table>');
	katana.$activeTab.find("#tableOfTestRequirements").html( items.join(""));
	

},


	saveRequirementCB:function() {
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			//console.log("xdata --> "+ rdata);  // Get this value and update your json. 
			var txtNm = katana.$activeTab.find("#textRequirement-name-"+sid+"-id").val();
			//var txtVl = katana.$activeTab.find("#textRequirement-value-"+sid+"-id").val();
			var txtVl = '';
			console.log("Editing ..." + sid);
			console.log(suiteApp.jsonSuiteObject['Requirements'][sid])
			suiteApp.jsonSuiteObject['Requirements'][sid]  = { "@name": txtNm, "@value": txtVl};
			suiteApp.createSuiteRequirementsTable(suiteApp.jsonSuiteObject['Requirements']);	

			//This is where you load in the edit form and display this row in detail. 
		},

	deleteRequirementCB:	function() {
			var names = this.attr('key').split('-');
			var sid = parseInt(names[1]);
			console.log("Remove " + sid + " " + this.id +" from " + rdata); 
			suiteApp.jsonSuiteObject['Requirements'].splice(sid,1);
			suiteApp.createSuiteRequirementsTable(suiteApp.jsonSuiteObject['Requirements']);	
			
		},
	
	insertRequirementCB:function( ) {
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			console.log("Insert" + sid + " " + this.id +" from " + rdata); 
			suiteApp.insertRequirementToSuite(sid);
			suiteApp.createSuiteRequirementsTable(suiteApp.jsonSuiteObject['Requirements']);	
		},

	removeRequirement : function(s,rdata){
	console.log(rdata);
	rdata.splice(s,1);
		
	},
/*
// Shows the global Suite data holder in the UI.

NOTE: At the time of writing I am using jQuery and Bootstrap to show the data.

Two global variables are heavily used when this function is called; 
1. suiteApp.jsonSuiteObject 
2. suiteApp.jsonTestcases which is set to point to the Testcases data structure in
   the suiteApp.jsonSuiteObject

*/
 mapSuiteJsonToUi: function(data){
	if (!jQuery.isArray(suiteApp.jsonTestcasesj)) suiteApp.jsonTestcasesj = [suiteApp.jsonTestcasesj]; 
	if (!suiteApp.jsonSuiteObject['Requirements']) suiteApp.jsonSuiteObject['Requirements'] = [];
	if (!jQuery.isArray(suiteApp.jsonSuiteObject['Requirements'])) suiteApp.jsonSuiteObject['Requirements'] = [suiteApp.jsonSuiteObject['Requirements']]; 
	suiteApp.createCasesTable(suiteApp.jsonTestcases['Testcase']);

	suiteApp.createSuiteRequirementsTable(suiteApp.jsonSuiteObject['Requirements']);
},  

// Saves your suite to disk. 
	saveSuitesCaseUI : function() {	
		suiteApp.mapUItoSuiteCase();
		suiteApp.createCasesTable(suiteApp.jsonTestcases['Testcase']);
		console.log('Closing');
		katana.popupController.close(suiteApp.lastPopup);
},

	insertRequirementToSuite : function(sid) {
			console.log("Add Requirement... ");
			if (!suiteApp.jsonSuiteObject['Requirements']) suiteApp.jsonSuiteObject['Requirements'] = [];
			rdata = suiteApp.jsonSuiteObject['Requirements'];
			var newReq = {"Requirement" : { "@name": "", "@value": ""},};
			rdata.splice(sid - 1, 0, newReq); 
			console.log(suiteApp.jsonSuiteObject);
			suiteApp.createSuiteRequirementsTable(suiteApp.jsonSuiteObject['Requirements']);	
},

	addRequirementToSuite : function() {
			if (!suiteApp.jsonSuiteObject['Requirements']) suiteApp.jsonSuiteObject['Requirements'] = [];
			suiteApp.jsonSuiteObject['Requirements'].push({"Requirement" : { "@name": "", "@value": ""},});
			//console.log(suiteApp.jsonSuiteObject);
			suiteApp.createSuiteRequirementsTable(suiteApp.jsonSuiteObject['Requirements']);	
},


// Removes a test Case by its ID and refresh the page. 
	removeTestcase : function(sid,xdata ){
	suiteApp.jsonTestcases['Testcase'].splice(sid,1);
	console.log("Removing test Cases "+sid+" now " + Object.keys(suiteApp.jsonTestcases).length);
	sutieApp.mapSuiteJsonToUi();	// Send in the modified array
},


};