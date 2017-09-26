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
if (typeof jsonAllSuitePages === 'undefined') {
 jsonAllSuitePages = { };
} else {
	//alert("Already there...");
}
var jsonSuiteObject = []; 
var jsonTestcases = [];			// for all Cases
var mySuiteKeywordsArray = ["path","context","runtype","impact"];
var mySuite_UI_Array = [ 'CasePath', 'CaseContext', 'CaseRuntype', 'CaseImpact'];

function jsUcfirst(string) 
{
    return string.charAt(0).toUpperCase() + string.slice(1);
}	

/// -------------------------------------------------------------------------------
// Sets up the global Suite data holder for the UI. 
// This is called from the correspoding HTML file onLoad event 
// or when a new XML file is loaded into the interface.
// 
// Two variables are set when this function is called; 
// 1. jsonSuiteObject 
// 2. jsonTestcases is set to point to the Testcases data structure in
//    the jsonSuiteObject
//
/// -------------------------------------------------------------------------------
function mapFullSuiteJson(myobjectID){
	//console.log('Mapping data ... ' + typeof(sdata) + ' is [' + sdata + "] " + sdata.length);  // This jdata is a string ....
	
	var sdata = katana.$activeTab.find("#listOfTestcasesForSuite").text();
	katana.$activeTab.find("#listOfTestcasesForSuite").hide();
	katana.$activeTab.find("#savefilepath").hide();

	var jdata = sdata.replace(/'/g, '"');
	console.log('Mapping data ... ' + typeof(sdata) + ' is [' + sdata + "] " + sdata.length);  // This jdata is a string ....
	jsonAllSuitePages[myobjectID] = JSON.parse(sdata); 
	//jsonAllSuitePages[myobjectID] = JSON.parse(jdata); 
	//alert(JSON.parse(sdata));
	console.log(typeof(jsonAllSuitePages[myobjectID]));
	jsonSuiteObject =  jsonAllSuitePages[myobjectID]; 
	if (!jsonSuiteObject['Requirements']) jsonSuiteObject['Requirements'] = [];
	jsonTestcases = jsonSuiteObject['Testcases']; 
	mapSuiteJsonToUi(jsonTestcases);  // This is where the table and edit form is created. 
	katana.$activeTab.find('#default_onError').on('change',fillSuiteDefaultGoto );
	katana.$activeTab.find('#suiteState').on('change',fillSuiteState );
	
} 

function fillSuiteState(){
	var state = this.value; 
	if (state == 'Add Another') {
		var name = prompt("Please Enter New State");
		if (name) {
		katana.$activeTab.find('#suiteState').append($("<option></option>").attr("value", name).text(name));
		}
	}

}


function createNewCaseForSuite() {
		var newTestcase = {	
		'path' : "",
		"Step" : { "@Driver": "", "@keyword": "", "@TS": "1" },
		"Arguments": { "Argument" :  "" },
		"onError" :  "",
		"onError": { "@action": "next", "@value": "" }, 
		"runmode": { "@type": "Standard", "@value": "" }, 
		"ExecType": { "@ExecType": "Yes", "Rule" : {} },
		"context": "",
		"impact": ""
		};
	return newTestcase;
}

/// -------------------------------------------------------------------------------
// Dynamically create a new Testcase object and append to the jsonTestcases 
// array. Default values are used to fill in a complete structure. If there is 
// no default value, a null value is inserted for the keyword
/// -------------------------------------------------------------------------------
function addCaseToSuite(){
	var newTestcase =createNewCaseForSuite();	
	jsonTestcases = jsonSuiteObject['Testcases']; 
	console.log(jsonSuiteObject);
	console.log(jsonTestcases);
	if (!jQuery.isArray(jsonTestcases['Testcase'])) {
		jsonTestcases['Testcase'] = [jsonTestcases['Testcase']];
		}
	console.log(jsonTestcases);
	jsonTestcases['Testcase'].push(newTestcase);
	createCasesTable(jsonTestcases['Testcase']);
}

function insertCaseToSuite(sid, copy){
	var newTestcase =createNewCaseForSuite();	
	if (!jQuery.isArray(jsonTestcases['Testcase'])) {
		jsonTestcases['Testcase'] = [jsonTestcases['Testcase']];
		}
	if (copy == 1) {
		newTestcase = jQuery.extend(true, {}, jsonTestcases['Testcase'][sid]); 
	}
	jsonTestcases['Testcase'].splice(sid,0,newTestcase);
	createCasesTable(jsonTestcases['Testcase']);
}

function mapSuiteCaseToUI(s,xdata,popup) {

	// This is called from an event handler ... 
	console.log(xdata);
	console.log(s);
	var oneCase = xdata[s];
	console.log(oneCase);
	console.log(oneCase['path']);
	popup.find("#CaseRowToEdit").val(s); 
	console.log(popup.find("#CaseRowToEdit").val());
	//katana.$activeTab.find("CasePath").val(oneCase['path']);
	popup.attr('oneCase', s);
	var myStringArray = mySuiteKeywordsArray; 
	var arrayLength = mySuiteKeywordsArray.length;
	for (var xi = 0; xi < arrayLength; xi++) {
		console.log("Fill "+ mySuite_UI_Array[xi]);
			var xxx = "#"+mySuite_UI_Array[xi];
			popup.find(xxx).val(oneCase[myStringArray[xi]]); 
		}

	if (! oneCase['onError']) {
			oneCase['onError'] = { "@action": "next", "@value": "" };
		}

	if (! oneCase['Execute']) {
			oneCase['Execute'] = { "@ExecType": "Yes", "Rule" : {} };
		}
	if (! oneCase['Execute']['@ExecType']) {
			oneCase['Execute'] = { "@ExecType": "Yes", "Rule" : {} };
		}

	if (! oneCase['Execute']['Rule']) {
			oneCase['Execute']['Rule'] = { '@Condition' : '', '@Condvalue' : '', '@Else': 'abort', '@Elsevalue':'' };
		}	
	popup.find("#Execute-at-ExecType").val(oneCase['Execute']['@ExecType']); 
	popup.find("#executeRuleAtCondition").val(oneCase['Execute']['Rule']['@Condition']); 
	popup.find("#executeRuleAtCondvalue").val(oneCase['Execute']['Rule']['@Condvalue']); 
	popup.find("#executeRuleAtElse").val(oneCase['Execute']['Rule']['@Else']); 
	popup.find("#executeRuleAtElsevalue").val(oneCase['Execute']['Rule']['@Elsevalue']); 

	fillSuiteCaseDefaultGoto(popup);
	popup.find('#caseonError-at-action').on('change', function(){ 
			var popup = $(this).closest('.popup');
			fillSuiteCaseDefaultGoto(popup);
	});
	console.log("FOUND Run mode  TYPE ",oneCase["runmode"]['@type'] )
	popup.find('.runmode_condition').show();
	if (oneCase["runmode"]['@type'] === 'Standard') {
		console.log("Hiding... ",oneCase["runmode"]['@type']  )
		popup.find('.runmode_condition').hide();
	}

	popup.find('.rule-condition').hide();
	if (oneCase["Execute"]['@ExecType']) {
		console.log("FOUND EXECT TYPE ",oneCase["Execute"]['@ExecType'] )
		if (oneCase["Execute"]['@ExecType'] == 'If' || oneCase["Execute"]['@ExecType'] == 'If Not') {
			popup.find('.rule-condition').show();
		} else {
		console.log("FOUND EXECT TYPE as  ",oneCase["Execute"]['@ExecType'] )
		}	
	}
	popup.find("#Execute-at-ExecType").on('change',function() {
			if (this.value == 'If' || this.value == 'If Not') {
				popup.find('.rule-condition').show();			
			} else {
				popup.find('.rule-condition').hide();
				
			}
		});
	
	popup.find("#CaseRunmode").on('change',function() {

			console.log("this value = ", this.value);
			if ( this.value === 'Standard') {
				popup.find('.runmode_condition').hide();	
				console.log("HIDING");		
			} else {
				popup.find('.runmode_condition').show();
				console.log("SHOWING");	
			}
		});


}


/// -------------------------------------------------------------------------------
// This function is called to map the currently edited Suite Case to 
// the field being edited. 
// Note that this function is calld from an event handler which catches the 
// row number from the table.
/// -------------------------------------------------------------------------------
function mapUItoSuiteCase(popup,xdata){	
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
	oneCase['Execute']['@ExecType'] = popup.find("#Execute-at-ExecType").val(); 
	oneCase['Execute']['Rule'] = {}
	oneCase['Execute']['Rule']['@Condition']= popup.find("#executeRuleAtCondition").val(); 
	oneCase['Execute']['Rule']['@Condvalue'] = popup.find("#executeRuleAtCondvalue").val(); 
	oneCase['Execute']['Rule']['@Else'] = popup.find("#executeRuleAtElse").val(); 
	oneCase['Execute']['Rule']['@Elsevalue'] = popup.find("#executeRuleAtElsevalue").val(); 

}

/*
Collects data into the global Suite data holder from the UI and returns the XML back 
NOTE: At the time of writing I am using jQuery and Bootstrap to show the data.

Two global variables are heavily used when this function is called; 
1. jsonSuiteObject 
2. jsonTestcases which is set to point to the Testcases data structure in
   the jsonSuiteObject

*/
function mapUiToSuiteJson() {

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

	
	
	jsonSuiteObject['Details']['Name'] = katana.$activeTab.find('#suiteName').val();
	jsonSuiteObject['Details']['Title'] = katana.$activeTab.find('#suiteTitle').val();
	jsonSuiteObject['Details']['Engineer'] = katana.$activeTab.find('#suiteEngineer').val();
	jsonSuiteObject['Details']['Resultsdir'] = katana.$activeTab.find('#suiteResults').val();
	jsonSuiteObject['Details']['Date'] = katana.$activeTab.find('#suiteDate').val();
	jsonSuiteObject['Details']['default_onError'] = { '@value': '', '@action' : ''};
	jsonSuiteObject['Details']['default_onError']['@action'] = katana.$activeTab.find('#defaultOnError').val();
	jsonSuiteObject['Details']['default_onError']['@value'] = katana.$activeTab.find('#defaultOnError_goto').val();
	jsonSuiteObject['Details']['Datatype']['@exectype'] = katana.$activeTab.find('#suiteDatatype').val();
	jsonSuiteObject['SaveToFile'] = katana.$activeTab.find('#my_file_to_save').val();


	console.log(jsonSuiteObject);
	console.log(jsonSuiteObject['Testcases']);
	var url = "./suites/getSuiteDataBack";
	var csrftoken = $("[name='csrfmiddlewaretoken']").val();

	$.ajaxSetup({
			function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
    	}
	});
	
	var topNode = { 'TestSuite' : jsonSuiteObject};
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
    	}
	});

}



function getResultsDirForSuiteRow() {
      var callback_on_accept = function(selectedValue) { 
      		console.log(selectedValue);
      		// Convert to relative path.
      		var sid = katana.$activeTab.attr('suite-case-row');
      		var pathToBase = katana.$activeTab.find('#savefilepath').text();
      		console.log("File path ==", pathToBase);
      		var nf = prefixFromAbs(pathToBase, selectedValue);
      		jsonTestcases['Testcase'][sid]['path'] = nf;
      		console.log("Path set to ",nf," for ", sid);
      		createCasesTable(jsonTestcases['Testcase']);
            };
      var callback_on_dismiss =  function(){ 
      		console.log("Dismissed");
	 };
     katana.fileExplorerAPI.openFileExplorer("Select a file", false , $("[name='csrfmiddlewaretoken']").val(), false, callback_on_accept, callback_on_dismiss);
};

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


var fillSuiteDefaultGoto = function() {

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
	var xdata = jsonSuiteObject["Testcases"]; // ['Testcase'];
	if (!jQuery.isArray(xdata)) xdata = [xdata]; 
	for (var s=0; s<Object.keys(xdata).length; s++ ) {
		defgoto.append($('<option>',{ value: s,  text: s+1}));
	}
}

var fillSuiteCaseDefaultGoto = function(popup) {

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
	var xdata = jsonSuiteObject["Testcases"]; // ['Testcase'];
	if (!jQuery.isArray(xdata)) xdata = [xdata]; 
	for (var s=0; s<Object.keys(xdata).length; s++ ) {
		defgoto.append($('<option>',{ value: s,  text: s+1}));
	}
}


//
// This creates the table for viewing data in a sortable view. 
// 
function createCasesTable(xdata) {
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
		fillCaseDefaults(s,xdata);
		var showID = parseInt(s)+ 1; 
		items.push('<tr data-sid="'+s+'"><td>'+showID+'</td>');
		var bid = "fileTestcase-"+s+"-id";
		items.push('<td><i title="ChangeFile" class="fa fa-folder-open" id="'+bid+'" katana-click="fileNewSuiteFromLine()" key="'+bid+'"/></td>');
		items.push('<td onclick="showCaseFromSuite('+"'"+oneCase['path']+"'"+')">'+oneCase['path']+'</td>');
		items.push('<td>'+oneCase['context']+'</td>');
		items.push('<td>'+oneCase['runtype']+'</td>');
		items.push('<td>'+oneCase['runmode']['@type']);
		if (oneCase['runmode']['@type'] != 'Standard') {
			items.push('<br>'+oneCase['runmode']['@value']);
		}
		items.push('</td>');
		items.push('<td>'+oneCase['onError']['@action']+'</td>');
		items.push('<td>'+oneCase['impact']+'</td>');
		bid = "deleteTestcase-"+s+"-id";
		items.push('<td><i title="Delete" class="fa fa-trash" id="'+bid+'" katana-click="deleteSuiteFromLine()" key="'+bid+'"/>');
		bid = "editTestcaseRow-"+s+"-id";
		items.push('<i title="Edit" class="fa fa-pencil" title="Edit" id="'+bid+'" katana-click="editNewSuiteIntoLine()" key="'+bid+'"/> ');
		bid = "insertTestcase-"+s+"-id";
		items.push('<i title="Insert" class="fa fa-plus" title="Insert New Case" id="'+bid+'" katana-click="insertNewSuiteIntoLine()" key="'+bid+'"'+bid+'"/>');
		bid = "dupTestcase-"+s+"-id";
		items.push('<i title="Duplicate" class="fa fa-copy" title="Duplicate New Case" id="'+bid+'" katana-click="duplicateNewSuiteIntoLine()" key="'+bid+'"/></td>');
		items.push('</tr>');
	}
	items.push('</tbody>');
	items.push('</table>');
	katana.$activeTab.find("#tableOfTestcasesForSuite").html( items.join(""));
	katana.$activeTab.find('#Case_table_display tbody').sortable( { stop: testSuiteSortEventHandler});

	fillSuiteDefaultGoto();
}

var insertNewSuiteIntoLine = function() {
	console.log(this.attr('key'));
	var names = this.attr('key').split('-');
	console.log(this.attr('key'));
	var sid = parseInt(names[1]);
	insertCaseToSuite(sid,0);
};

var deleteSuiteFromLine = function() {
	var names = this.attr('key').split('-');
	var sid = parseInt(names[1]);
	removeTestcase(sid,xdata);
};

var duplicateNewSuiteIntoLine = function( ){
	var names = this.attr('key').split('-');
	var sid = parseInt(names[1]);
	insertCaseToSuite(sid,1);
};


var editNewSuiteIntoLine = function() {
	var names = this.attr('key').split('-');
	var sid = parseInt(names[1]);
		katana.popupController.open(katana.$activeTab.find("#editTestCaseEntry").html(),"Edit..." + sid, function(popup) {
			var popup = $(this).closest('.popup');
		
			mapSuiteCaseToUI(sid,xdata,popup);
		});

};

var fileNewSuiteFromLine = function(){ 
	var names = this.attr('key').split('-');
	var sid = parseInt(names[1]);
	katana.$activeTab.attr('suite-case-row',sid);
	getResultsDirForSuiteRow();
};


var showCaseFromSuite = (fname) {
  var xref="./cases/editCase/?fname="+fname; 
  //console.log("Calling case ", fname, xref);
    katana.$view.one('tabAdded', function(){
         mapFullCaseJson(fname,'#listOfTestStepsForCase');
    });
  katana.templateAPI.load(xref, null, null, 'suite') ;;
}
//
var testSuiteSortEventHandler = function(event, ui ) {
	var listItems = [] ; 
	var listCases = katana.$activeTab.find('#Case_table_display tbody').children(); 
	console.log(listCases);
		if (listCases.length < 2) {
	 return; 
	}

	var oldCaseSteps = jsonSuiteObject["Testcases"]['Testcase'];
	var newCaseSteps = new Array(listCases.length);

	for (xi=0; xi < listCases.length; xi++) {
		var xtr = listCases[xi];
		var ni  = xtr.getAttribute("data-sid");
		console.log(xi + " => " + ni);
		newCaseSteps[ni] = oldCaseSteps[xi];
	}

	jsonSuiteObject["Testcases"]['Testcase'] = newCaseSteps;
	jsonTestcases = jsonSuiteObject['Testcases']; 
	mapSuiteJsonToUi(jsonTestcases);  // This is where the table and edit form is created. 
};




var fillCaseDefaults = function(s, data){
		oneCase = data[s]
		console.log(data);
		if (oneCase == null) {
			data[s] = {} ;
			oneCase = data[s];
		}
		var myStringArray = mySuiteKeywordsArray; // ["path","context","runtype","impact", ];
		var arrayLength = myStringArray.length;
		for (var xi = 0; xi < arrayLength; xi++) {
   				if (! oneCase[myStringArray[xi]]){
						oneCase[myStringArray[xi]] = myStringArray[xi];
					}
   				
		}

		if (! oneCase['onError']) {
			oneCase['onError'] = { "@action": "next", "@value": "" };
		}
		oneCase['Execute'] = { "@ExecType": "Yes", "Rule": { "@Condition": "", "@Condvalue": "", "@Else": "next", "@Elsevalue": "" } };
		
}


var createSuiteRequirementsTable = function(rdata){
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
		items.push('<td><input type="text" value="'+oneReq['@name']+'" id="'+bid+'"/></td>');
		bid = "deleteRequirement-"+s+"-id";
		console.log("Line 328 or so "+bid); 
		items.push('<td><i  class="fa fa-trash"  title="Delete" id="'+bid+'"/>');
		bid = "editRequirement-"+s+"-id";
		items.push('<i class="fa fa-pencil" title="Save Edit" id="'+bid+'"/>');
		bid = "insertRequirement-"+s+"-id";
		items.push('<i class="fa fa-plus"  title="Insert" id="'+bid+'"/></td>');
		
	}
	items.push('</tbody>');
	items.push('</table>');
	katana.$activeTab.find("#tableOfTestRequirements").html( items.join(""));
	//katana.$activeTab.find('#tableOfTestRequirements').sortable();
	
	for (var s=0; s<Object.keys(rdata).length; s++ ) {
		var oneReq = rdata[s];
		var idnumber = s + 1
		var bid = "textRequirement-name-"+s+"-id";	
		bid = "deleteRequirement-"+s+"-id";
		console.log("Line 328 or so "+bid); 
		katana.$activeTab.find('#'+bid).off('click'); 
		katana.$activeTab.find('#'+bid).on('click','#'+bid,function( event ) {
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			console.log("Remove " + sid + " " + this.id +" from " + rdata); 
			jsonSuiteObject['Requirements'].splice(sid,1);
			createSuiteRequirementsTable(jsonSuiteObject['Requirements']);	
			return false;
		});
		bid = "editRequirement-"+s+"-id";
		
		katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
		katana.$activeTab.find('#'+bid).on('click','#'+bid,function(  ) {
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			//console.log("xdata --> "+ rdata);  // Get this value and update your json. 
			var txtNm = katana.$activeTab.find("#textRequirement-name-"+sid+"-id").val();
			//var txtVl = katana.$activeTab.find("#textRequirement-value-"+sid+"-id").val();
			var txtVl = '';
			console.log("Editing ..." + sid);
			console.log(jsonSuiteObject['Requirements'][sid])
			jsonSuiteObject['Requirements'][sid]  = { "@name": txtNm, "@value": txtVl};
			createSuiteRequirementsTable(jsonSuiteObject['Requirements']);	
			event.stopPropagation();
			//This is where you load in the edit form and display this row in detail. 
		});

		bid = "insertRequirement-"+s+"-id";
		katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
		katana.$activeTab.find('#'+bid).on('click','#'+bid,function( event ) {
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			console.log("Insert" + sid + " " + this.id +" from " + rdata); 
			insertRequirementToSuite(sid);

			createSuiteRequirementsTable(jsonSuiteObject['Requirements']);	
			return false;
		});
	}





}


var removeRequirement = function(s,rdata){
	console.log(rdata);
	rdata.splice(s,1);
			
}
/*
// Shows the global Suite data holder in the UI.

NOTE: At the time of writing I am using jQuery and Bootstrap to show the data.

Two global variables are heavily used when this function is called; 
1. jsonSuiteObject 
2. jsonTestcases which is set to point to the Testcases data structure in
   the jsonSuiteObject

*/
var mapSuiteJsonToUi = function(data){
	var items = []; 
	var xdata = data['Testcase'];
	if (!jQuery.isArray(xdata)) xdata = [xdata]; 

	if (!data['Requirements']) data['Requirements'] = [];
	var rdata = data['Requirements'];
	if (!jQuery.isArray(rdata)) rdata = [rdata]; 

	createCasesTable(xdata);
	createSuiteRequirementsTable(rdata);
}  

// Saves your suite to disk. 
var saveSuitesCaseUI = function() {
		var xdata = jsonTestcases['Testcase'];
		var popup = $(this).closest('.popup');
		mapUItoSuiteCase(popup,xdata);
		createCasesTable(xdata);  //Refresh the screen.
		console.log('Closing');
		katana.popupController.close(popup);
}

var insertRequirementToSuite = function(sid) {
			console.log("Add Requirement... ");
			if (!jsonSuiteObject['Requirements']) jsonSuiteObject['Requirements'] = [];
			rdata = jsonSuiteObject['Requirements'];
			var newReq = {"Requirement" : { "@name": "", "@value": ""},};
			rdata.splice(sid - 1, 0, newReq); 
			console.log(jsonSuiteObject);
			createSuiteRequirementsTable(jsonSuiteObject['Requirements']);	
}

var addRequirementToSuite = function() {
			if (!jsonSuiteObject['Requirements']) jsonSuiteObject['Requirements'] = [];
			rdata = jsonSuiteObject['Requirements'];
			rdata.push({"Requirement" : { "@name": "", "@value": ""},});
			//console.log(jsonSuiteObject);
			createSuiteRequirementsTable(jsonSuiteObject['Requirements']);	
}


// Removes a test Case by its ID and refresh the page. 
var removeTestcase = function(sid,xdata ){
	jsonTestcases['Testcase'].splice(sid,1);
	console.log("Removing test Cases "+sid+" now " + Object.keys(jsonTestcases).length);
	mapSuiteJsonToUi(jsonTestcases);	// Send in the modified array
}
