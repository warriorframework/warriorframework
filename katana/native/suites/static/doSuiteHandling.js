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
var activePageID = getRandomSuiteID();   // for the page ID 


/// -------------------------------------------------------------------------------
// 
/// -------------------------------------------------------------------------------
function getRandomSuiteID() {
  min = Math.ceil(1);
  max = Math.floor(2000);
  return Math.floor(Math.random() * (max - min)) + min;
  
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
	activePageID = getRandomSuiteID();                 
	var sdata = katana.$activeTab.find("#listOfTestcasesForSuite").text();
	katana.$activeTab.find("#listOfTestcasesForSuite").hide();
	var jdata = sdata.replace(/'/g, '"');
	console.log('Mapping data ... ' + typeof(sdata) + ' is [' + sdata + "] " + sdata.length);  // This jdata is a string ....
	jsonAllSuitePages[myobjectID] = JSON.parse(sdata); 
	//jsonAllSuitePages[myobjectID] = JSON.parse(jdata); 
	//alert(JSON.parse(sdata));
	console.log(typeof(jsonAllSuitePages[myobjectID]));
	jsonSuiteObject =  jsonAllSuitePages[myobjectID]; 
	jsonTestcases = jsonSuiteObject['Testcases']; 
	mapSuiteJsonToUi(jsonTestcases);  // This is where the table and edit form is created. 
} 



/// -------------------------------------------------------------------------------
// Dynamically create a new Testcase object and append to the jsonTestcases 
// array. Default values are used to fill in a complete structure. If there is 
// no default value, a null value is inserted for the keyword
/// -------------------------------------------------------------------------------
function addCaseToSuite(){
	var newTestcase = {	
		"Step" : { "@Driver": "", "@keyword": "", "@TS": "1" },
		"Arguments": { "Argument" : { "$": "" }, },
		"onError" : { "$": ""},
		"onError": { "@action": "next", "@value": "" }, 
		
		"context": { "$": ""},
		"impact": { "$": "impact"}
		};
	
		//"path": "../Cases/framework_tests/seq_par_execution/seq_ts_seq_tc.xml", 
	 	//"runmode": {"@type": "ruf", "@value": "2"},
		//"retry": {"@type": "if not", "@Condition": "testCase_1_result", "@Condvalue": "PASS", "@count": "6", "@interval": "0"}, 
	
	if (!jQuery.isArray(jsonTestcases['Testcase'])) {
		jsonTestcases['Testcase'] = [jsonTestcases['Testcase']];
		}

	jsonTestcases['Testcase'].push(newTestcase);
	mapSuiteJsonToUi(jsonTestcases);
}



function mapSuiteCaseToUI(s,xdata) {

	// This is called from an event handler ... 
	console.log(xdata);
	console.log(s);
	var oneCase = xdata[s];
	console.log(oneCase);
	console.log(activePageID);
	console.log(oneCase['path']['$']);
	katana.$activeTab.find("#CaseRowToEdit"+activePageID).val(s); 
	console.log(katana.$activeTab.find("#CaseRowToEdit"+activePageID).val());
	//katana.$activeTab.find("CasePath"+activePageID).val(oneCase['path']['$']);
	
	var myStringArray = ["path","context","runtype","impact"];
	var arrayLength = myStringArray.length;
	for (var xi = 0; xi < arrayLength; xi++) {
			katana.$activeTab.find("#impact"+activePageID).val(oneCase[myStringArray[xi]]['$']); 
		}

	if (! oneCase['onError']) {
			oneCase['onError'] = { "@action": "next", "@value": "" };
		}
		

}


/// -------------------------------------------------------------------------------
// This function is called to map the currently edited Suite Case to 
// the field being edited. 
// Note that this function is calld from an event handler which catches the 
// row number from the table.
/// -------------------------------------------------------------------------------
function mapUItoSuiteCase(xdata){

		
	var s = parseInt(katana.$activeTab.find(s+':"CaseRowToEdit"'+activePageID).val());
	var oneCase = xdata[s];
	var id = katana.$activeTab.find("CaseRowToEdit"+activePageID).val();

	if (s != id) {
		alert('Setting for '+s+" instead of " + id); 
	}

		id = 'CaseImpact'+activePageID
		oneCase['impact']['$'] = katana.$activeTab.find(id).val();

		id = 'CasePath'+activePageID		
		oneCase['path']['$'] = katana.$activeTab.find(id).val();

		id = 'CaseContext'+activePageID
		oneCase['context']['$'] = katana.$activeTab.find(id).val();

		id = 'CaseRuntype'+activePageID
		oneCase['runtype']['$'] = katana.$activeTab.find(id).val();


		id = "onError-at-action"+activePageID
		oneCase['onError']['@action'] = katana.$activeTab.find(id).val();


	
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
	
	jsonSuiteObject['Details']['Name']['$'] = katana.$activeTab.find('#suiteName').val();
	jsonSuiteObject['Details']['Title']['$'] = katana.$activeTab.find('#suiteTitle').val();
	jsonSuiteObject['Details']['Engineer']['$'] = katana.$activeTab.find('#suiteEngineer').val();
	jsonSuiteObject['Details']['Resultsdir']['$'] = katana.$activeTab.find('#suiteResults').val();
	jsonSuiteObject['Details']['Date']['$'] = katana.$activeTab.find('#suiteDate').val();
	jsonSuiteObject['Details']['default_onError']['$'] = katana.$activeTab.find('#defaultOnError').val();
	jsonSuiteObject['Details']['Datatype']['@exectype'] = katana.$activeTab.find('#suiteDatatype').val();
	jsonSuiteObject['SaveToFile'] = { "$" : katana.$activeTab.find('#my_file_to_save').val()};

	var url = "./Suites/getSuiteDataBack";
	var csrftoken = $("[name='csrfmiddlewaretoken']").val();

	$.ajaxSetup({
			function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
    	}
	});
	
	var topNode  = { 'Suite' : jsonSuiteObject};
	var jj = new json() ; 
	var ns = jj.translate.toXML(topNode);
	
	alert(ns);

	$.ajax({
	    url : url,
	    type: "POST",
	    data : { 
	    	'json': JSON.stringify(topNode),
	    	'Suite': ns,
	    	'filetosave': $('#my_file_to_save').val()
	    	},
	    headers: {'X-CSRFToken':csrftoken},
    
    success: function( data ){
        alert("Sent");
    	}
	});

}

//
// Creates the display table for the test suite. 
function createCaseEditTable(xdata) {
	//var xdata = data['Testcase'];   // Just in case 
	//if (!jQuery.isArray(xdata)) xdata = [xdata];
	
	katana.$activeTab.find("#editTestcaseEntry").html( "");
	var items = []; 
	
	items.push('<div class="field">'); 
	items.push('<label >Row Id</label>');
	items.push('<input type="text" id="CaseRowToEdit'+activePageID+'" value=""/>');
	items.push('</div>');			

	items.push('<div class="field">');
	items.push('<label >Path*:</label>');
	items.push('<input type="text" id="CasePath'+activePageID+'" value=""/>');
	items.push('</div>');
	items.push('<div class="field">');
	items.push('<label >Context:</label>');
	items.push('<input type="text" id="CaseContext'+activePageID+'" value=""/>');
	items.push('</div>');
	items.push('<div class="field">');
	items.push('<label >Run Type:</label>');
	items.push('<input type="text" id="CaseRuntype'+activePageID+'" value=""/>');
	items.push('</div>');
	items.push('<div class="field">');
	items.push('<label >Impact:</label>');
	items.push('<input type="text" id="CaseImpact'+activePageID+'" value=""/>');
	items.push('</div>');

	items.push('<div class="field">');
	items.push('<label class="col-md-2 text-right" >On Error action:</label>');
	items.push('<select type="text" class="col-md-4 text-right" id="onError-at-action'+activePageID+'" value="" >');
	items.push('<option value="next">next</option>');
	items.push('<option value="abort">abort</option>');
	items.push('<option value="abort_as_error">abort_as_error</option>');
	items.push('<option value="goto">goto</option>');
	items.push('</select>');
	items.push('</div>');
		
	
	// Now create the buttons to save the data. 

	var bid = "editTestcase-"+activePageID+"-id"+getRandomSuiteID();;
	items.push('<td><input type="button" class="btn" value="Save Changes" id="'+bid+'"/></td>');
	katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
	$(document).on('click','#'+bid,function(  ) {
			//var names = this.id.split('-');
			//var sid = parseInt(names[1]);
			mapUItoSuiteCase(xdata);
			
		});

	katana.$activeTab.find("#editTestcaseEntry").html( items.join(""));
	
}
//
// This creates the table for viewing data in a sortable view. 
// 
function createCasesTable(xdata) {
	var items = []; 

	items.push('<table id="Case_table_display" class="table" >');
	items.push('<thead>');
	items.push('<tr id="CaseRow"><th>Num</th><th>Path</th><th>context</th><th>OnError</th><th>Impact</th><th/><th/></tr>');
	items.push('</thead>');
	items.push('<tbody>');

	console.log(xdata);
	katana.$activeTab.find("#tableOfTestcasesForSuite").html("");
	for (var s=0; s<Object.keys(xdata).length; s++ ) {
		var oneCase = xdata[s];

		console.log(oneCase);
		fillCaseDefaults(s,xdata);
		console.log(oneCase['path']);
		
		items.push('<tr><td>'+s+'</td>');
		items.push('<td>'+oneCase['path']['$']+'</td>');
		items.push('<td>Context='+oneCase['context']['$']+",<br>"+oneCase['runtype']['$']+'</td>');
		//items.push('<td>'+oneCase['runtype']['$']+'</td>');
		items.push('<td>'+oneCase['onError']['@action']+'</td>');
		items.push('<td>'+oneCase['impact']['$']+'</td>');

		var bid = "deleteTestcase-"+s+"-id"+getRandomSuiteID();
		//alert(bid);
		items.push('<td><input type="button" class="btn-danger" value="Delete" id="'+bid+'"/></td>');
		katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
		$(document).on('click','#'+bid,function( ) {
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			removeTestcase(sid,xdata);
		});
		bid = "editTestcase-"+s+"-id"+getRandomSuiteID();;
		items.push('<td><input type="button" class="btn" value="Edit" id="'+bid+'"/></td>');
		katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
		$(document).on('click','#'+bid,function(  ) {
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			console.log("xdata --> "+ xdata);
			mapSuiteCaseToUI(sid,xdata);
			//This is where you load in the edit form and display this row in detail. 
		});

		items.push('</tr>');
	}
	items.push('</tbody>');
	items.push('</table>');

	katana.$activeTab.find("#tableOfTestcasesForSuite").html( items.join(""));
	katana.$activeTab.find('#Case_table_display tbody').sortable();
	katana.$activeTab.find('#Case_table_display').on('click',"td",   function() { 
	});

}

function fillCaseDefaults(s, data){
		oneCase = data[s]

		var myStringArray = ["path","context","runtype","impact"];
		var arrayLength = myStringArray.length;
		for (var xi = 0; xi < arrayLength; xi++) {
   				if (! oneCase[myStringArray[xi]]){
						oneCase[myStringArray[xi]] = { "$": ""};
					}
		}

		if (! oneCase['onError']) {
			oneCase['onError'] = { "@action": "next", "@value": "" };
		}
		
}


function createRequirementsTable(rdata){
	var items =[]; 
	katana.$activeTab.find("#tableOfTestRequirements").html("");
	
	items.push('<table id="Case_table_display" class="table" >');
	items.push('<thead>');
	items.push('<tr id="ReqRow"><th>Num</th><th>Requirement</th><th/><th/></tr>');
	items.push('</thead>');
	items.push('<tbody>');
	for (var s=0; s<Object.keys(rdata).length; s++ ) {
		var oneReq = rdata[s];
		items.push('<tr><td>'+s+'</td>');
		//items.push('<td>'+oneReq['$']+'</td>');
		var bid = "textRequirement-"+s+"-id"+activePageID;	
		items.push('<td><input type="text" value="'+oneReq['$']+'" id="'+bid+'"/></td>');
		
		bid = "deleteRequirement-"+s+"-id"+getRandomSuiteID();
		//alert(bid);
		items.push('<td><input type="button" class="btn-danger" value="Delete" id="'+bid+'"/></td>');
		katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
		$(document).on('click','#'+bid,function( ) {
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			//removeTestcase(sid,xdata);
		});
		bid = "editRequirement-"+s+"-id"+getRandomSuiteID();;
		items.push('<td><input type="button" class="btn" value="Save" id="'+bid+'"/></td>');
		katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
		$(document).on('click','#'+bid,function(  ) {
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			console.log("xdata --> "+ rdata);  // Get this value and update your json. 
			var txtIn = katana.$activeTab.find("#textRequirement-"+sid+"-id"+activePageID).val();
			console.log(katana.$activeTab.find("#textRequirement-"+sid+"-id"+activePageID));
			console.log(sid);
			console.log(jsonSuiteObject['Requirements'][sid])
			jsonSuiteObject['Requirements'][sid]['$'] = txtIn;

			createRequirementsTable(jsonSuiteObject['Requirements']);	
			event.stopPropagation();
			//This is where you load in the edit form and display this row in detail. 
		});
	}
	items.push('</tbody>');
	items.push('</table>');

	bid = "addRequirement-"+getRandomSuiteID();
	items.push('<td><input type="button" class="btn" value="Add Requirement" id="'+bid+'"/></td>');
	katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
	$(document).on('click','#'+bid,function( event  ) {
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			console.log("Add Requirement... ");
			if (!jsonSuiteObject['Requirements']) jsonSuiteObject['Requirements'] = [];
			rdata = jsonSuiteObject['Requirements'];
			rdata.push({"Requirement" : { "$": ""},});
			console.log(jsonSuiteObject);
			createRequirementsTable(jsonSuiteObject['Requirements']);	
			event.stopPropagation();
		});

	katana.$activeTab.find("#tableOfTestRequirements").html( items.join(""));
	katana.$activeTab.find('#Case_table_display tbody').sortable();
	katana.$activeTab.find('#Case_table_display').on('click',"td",   function() { 
	});

}

/*
// Shows the global Suite data holder in the UI.

NOTE: At the time of writing I am using jQuery and Bootstrap to show the data.

Two global variables are heavily used when this function is called; 
1. jsonSuiteObject 
2. jsonTestcases which is set to point to the Testcases data structure in
   the jsonSuiteObject

*/
function mapSuiteJsonToUi(data){
	var items = []; 
	var xdata = data['Testcase'];
	if (!jQuery.isArray(xdata)) xdata = [xdata]; 

	if (!data['Requirements']) data['Requirements'] = [];
	var rdata = data['Requirements'];
	if (!jQuery.isArray(rdata)) rdata = [rdata]; 

	createCasesTable(xdata);
	createRequirementsTable(rdata);
	createCaseEditTable(xdata);
}  // end of function 

// Removes a test Case by its ID and refresh the page. 
function removeTestcase( sid,xdata ){
	jsonTestcases['Testcase'].splice(sid,1);
	console.log("Removing test Cases "+sid+" now " + Object.keys(jsonTestcases).length);
	mapSuiteJsonToUi(jsonTestcases);	// Send in the modified array
}
