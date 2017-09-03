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
if (typeof jsonAllProjectPages === 'undefined') {
 jsonAllProjectPages = { };
} else {
	//alert("Already there...");
}
var jsonProjectObject = []; 
var jsonTestSuites = [];			// for all Suites
var activePageID = getRandomID();   // for the page ID 


/// -------------------------------------------------------------------------------
// 
/// -------------------------------------------------------------------------------
function getRandomID() {
  min = Math.ceil(1);
  max = Math.floor(2000);
  return Math.floor(Math.random() * (max - min)) + min;
  
}
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
function mapFullProjectJson(myobjectID){
	//console.log('Mapping data ... ' + typeof(sdata) + ' is [' + sdata + "] " + sdata.length);  // This jdata is a string ....
	activePageID = getRandomID();                 
	var sdata = katana.$activeTab.find("#listOfTestSuitesForProject").text();
	katana.$activeTab.find("#listOfTestSuitesForProject").hide();
	var jdata = sdata.replace(/'/g, '"');
	console.log('Mapping data ... ' + typeof(sdata) + ' is [' + sdata + "] " + sdata.length);  // This jdata is a string ....
	//console.log(jdata);                  // I show it as such. 
	jsonAllProjectPages[myobjectID] = JSON.parse(sdata); 
	//jsonAllProjectPages[myobjectID] = JSON.parse(jdata); 
	//alert(JSON.parse(sdata));
	console.log(typeof(jsonAllProjectPages[myobjectID]));
	jsonProjectObject =  jsonAllProjectPages[myobjectID]; 
	jsonTestSuites = jsonProjectObject['Testsuites']; 
	mapProjectJsonToUi(jsonTestSuites);  // This is where the table and edit form is created. 
} 



/// -------------------------------------------------------------------------------
// Dynamically create a new TestSuite object and append to the jsonTestSuites 
// array. Default values are used to fill in a complete structure. If there is 
// no default value, a null value is inserted for the keyword
/// -------------------------------------------------------------------------------
function addSuiteToProject(){
	var newTestSuite = {	"path": "../suites/framework_tests/seq_par_execution/seq_ts_seq_tc.xml", 
	"Execute": { "@ExecType": "Yes",
			"Rule": {"@Condition": "","@Condvalue": "","@Else": "next", "@Elsevalue": "" }
		}, "runmode": {"@type": "ruf", "@value": "2"},
		"retry": {"@type": "if not", "@Condition": "testsuite_1_result", "@Condvalue": "PASS", "@count": "6", "@interval": "0"}, 
	"onError": { "@action": "next", "@value": "" }, "impact": "impact" };

	if (!jQuery.isArray(jsonTestSuites['Testsuite'])) {
		jsonTestSuites['Testsuite'] = [jsonTestSuites['Testsuite']];
		}

	jsonTestSuites['Testsuite'].push(newTestSuite);
	mapProjectJsonToUi(jsonTestSuites);
}



function mapProjectSuiteToUI(s,xdata) {

	// This is called from an event handler ... 
	console.log(xdata);
	console.log(s);
	var oneSuite = xdata[s];
	console.log(oneSuite);
	console.log(activePageID);
	console.log(oneSuite['path']['$']);
	katana.$activeTab.find("#suiteRowToEdit"+activePageID).val(s); 
	console.log(katana.$activeTab.find("#suiteRowToEdit"+activePageID).val());
	//katana.$activeTab.find("suitePath"+activePageID).val(oneSuite['path']['$']);
	katana.$activeTab.find("#suitePath"+activePageID).val(oneSuite['path']['$']);
	katana.$activeTab.find("#Execute-at-ExecType"+activePageID).val(oneSuite['Execute']['@ExecType']); 
	katana.$activeTab.find("#executeRuleAtCondition"+activePageID).val(oneSuite['Execute']['Rule']['@Condition']); 
	katana.$activeTab.find("#executeRuleAtCondvalue"+activePageID).val(oneSuite['Execute']['Rule']['@Condvalue']); 
	katana.$activeTab.find("#executeRuleAtElse"+activePageID).val(oneSuite['Execute']['Rule']['@Else']['$']); 
	katana.$activeTab.find("#executeRuleAtElsevalue"+activePageID).val(oneSuite['Execute']['Rule']['@Elsevalue']); 
	
	katana.$activeTab.find("#onError-at-action"+activePageID).val(oneSuite['onError']['@action']); 
	katana.$activeTab.find("#onError-at-value"+activePageID).val(oneSuite['onError']['@value']); 
	katana.$activeTab.find("#onError-at-type"+activePageID).val(oneSuite['runmode']['@type']); 
	katana.$activeTab.find("#onError-at-value"+activePageID).val(oneSuite['runmode']['@value']); 
	katana.$activeTab.find("#impact"+activePageID).val(oneSuite['impact']['$']); 
	

}


/// -------------------------------------------------------------------------------
// This function is called to map the currently edited project suite to 
// the field being edited. 
// Note that this function is calld from an event handler which catches the 
// row number from the table.
/// -------------------------------------------------------------------------------
function mapUItoProjectSuite(xdata){

		
	var s = parseInt(katana.$activeTab.find(s+':"suiteRowToEdit"'+activePageID).val());
	var oneSuite = xdata[s];
	var id = katana.$activeTab.find("suiteRowToEdit"+activePageID).val();

	if (s != id) {
		alert('Setting for '+s+" instead of " + id); 
	}
	oneSuite['path']['$'] = katana.$activeTab.find("#suitePath"+activePageID).val(); 
	oneSuite['Execute']['@ExecType'] = katana.$activeTab.find("#Execute-at-ExecType"+activePageID).val(); 
	oneSuite['Execute']['Rule']['@Condition']= katana.$activeTab.find("#executeRuleAtCondition"+activePageID).val(); 
	oneSuite['Execute']['Rule']['@Condvalue'] = katana.$activeTab.find("#executeRuleAtCondvalue"+activePageID).val(); 
	oneSuite['Execute']['Rule']['@Else']['$'] = katana.$activeTab.find("#executeRuleAtElse"+activePageID).val(); 
	oneSuite['Execute']['Rule']['@Elsevalue'] = katana.$activeTab.find("#executeRuleAtElsevalue"+activePageID).val(); 
	oneSuite['impact']['$'] = katana.$activeTab.find("#impact"+activePageID).val(); 
	oneSuite['onError']['@action'] = katana.$activeTab.find("#onError-at-action"+activePageID).val(); 
	oneSuite['onError']['@value'] = katana.$activeTab.find("#onError-at-value"+activePageID).val(); 
	oneSuite['runmode']['@type'] = katana.$activeTab.find("#onError-at-type"+activePageID).val(); 
	oneSuite['runmode']['@value'] = katana.$activeTab.find("#onError-at-value"+activePageID).val(); 
}

/*
Collects data into the global project data holder from the UI 

NOTE: At the time of writing I am using jQuery and Bootstrap to show the data.

Two global variables are heavily used when this function is called; 
1. jsonProjectObject 
2. jsonTestSuites which is set to point to the Testsuites data structure in
   the jsonProjectObject

*/
function mapUiToProjectJson() {
	
	jsonProjectObject['Details']['Name']['$'] = katana.$activeTab.find('#projectName').val();
	jsonProjectObject['Details']['Title']['$'] = katana.$activeTab.find('#projectTitle').val();
	jsonProjectObject['Details']['Engineer']['$'] = katana.$activeTab.find('#projectEngineer').val();
	jsonProjectObject['Details']['Title']['$'] = katana.$activeTab.find('#projectTitle').val();
	jsonProjectObject['Details']['Date']['$'] = katana.$activeTab.find('#projectDate').val();
	//jsonProjectObject['Details']['Time'] = $('#projectTime').val();
	jsonProjectObject['Details']['default_onError']['$'] = katana.$activeTab.find('#defaultOnError').val();
	jsonProjectObject['Details']['Datatype']['$'] = katana.$activeTab.find('#projectDatatype').val();
	jsonProjectObject['SaveToFile'] = { "$" : katana.$activeTab.find('#my_file_to_save').val()};
	//
	// Now walk the DOM ..
	// Create dynamic ID values based on the Suite's location in the UI. 

	// Note that if we implement drag and drop we'll have to re-index the entire 
	// visual display to reflect the movements of the order of objects on display 
	// That would require a refresh after a drop anyway. 
	var xdata = jsonProjectObject['Testsuites']['Testsuite'];



	for (var s=0; s<Object.keys(xdata).length; s++ ) {
		var oneSuite = xdata[s];

		oneSuite['Execute']['$'] = ""
		id = '#'+s+"-Suite-ID";
		oneSuite['Execute']['@ExecType']['$'] = ""; 

		id = '#'+s+"-Execute-Rule-at-Condition";
		oneSuite['Execute']['Rule']['@Condition'] = katana.$activeTab.find(id).val();
		id = '#'+s+"-Execute-Rule-at-Condvalue";
		oneSuite['Execute']['Rule']['@Condvalue'] = katana.$activeTab.find(id).val();
		id = '#'+s+"-Execute-Rule-at-Else";
		oneSuite['Execute']['Rule']['@Else'] = katana.$activeTab.find(id).val();
		id = '#'+s+"-Execute-Rule-at-Elsevalue";
		oneSuite['Execute']['Rule']['@Elsevalue'] = katana.$activeTab.find(id).val();

		oneSuite['onError']['$'] = "";

		id = '#'+s+"-onError-at-action";
		oneSuite['onError']['@action'] = katana.$activeTab.find(id).val();
		id = '#'+s+"-onError-at-value option:selected";
		oneSuite['onError']['@value'] = katana.$activeTab.find(id).val();

		oneSuite['runmode'] = {}
		id = '#'+s+"-runmode-at-value";
		oneSuite['runmode']['@value'] = katana.$activeTab.find(id).val();
		id = '#'+s+"-runmode-at-value option:selected";
		oneSuite['runmode']['@value'] = katana.$activeTab.find(id).val();
		oneSuite['runmode']['$'] = "";
		oneSuite['retry']['$'] = "";

		oneSuite['retry'] = {}
		id = '#'+s+"-retry-at-type";
		oneSuite['retry']['@type'] =  katana.$activeTab.find(id).val();
		id = '#'+s+"-retryat-Condition";
		oneSuite['retry']['@Condition'] =  katana.$activeTab.find(id).val();
		id = '#'+s+"-retry-at-Condvalue";
		oneSuite['retry']['@Condvalue'] =  katana.$activeTab.find(id).val();
		id = '#'+s+"-retry-at-count";
		oneSuite['retry']['@count'] =  katana.$activeTab.find(id).val();
		id = '#'+s+"-retry-at-interval";
		oneSuite['retry']['@interval'] =  katana.$activeTab.find(id).val();
		

	}
	// Now you have collected the user components...
	//alert("Here..");
	var url = "./projects/getProjectDataBack";
	//alert(url); 
	var csrftoken = $("[name='csrfmiddlewaretoken']").val();

	$.ajaxSetup({
			function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
    	}
	});
	
	var topNode  = { 'Project' : jsonProjectObject};
	var jj = new json() ; 
	// var mystring =  JSON.stringify(jsonProjectObject);
	var ns = jj.translate.toXML(topNode);
	
	alert(ns);

	$.ajax({
	    url : url,
	    type: "POST",
	    data : { 
	    	'json': JSON.stringify(topNode),
	    	'Project': ns,
	    	'filetosave': $('#my_file_to_save').val()
	    	},
	    headers: {'X-CSRFToken':csrftoken},
    
    success: function( data ){
        alert("Sent");
    	}
	});

}

//
function createSuiteEditTable(xdata) {
	//var xdata = data['Testsuite'];   // Just in case 
	//if (!jQuery.isArray(xdata)) xdata = [xdata];
	
	katana.$activeTab.find("#editTestSuiteEntry").html( "");
	var items = []; 
	
	items.push('<div class="field">'); 
	items.push('<label >Row Id</label>');
	items.push('<input type="text" id="suiteRowToEdit'+activePageID+'" value=""/>');
	items.push('</div>');			

	items.push('<div class="field">');
	items.push('<label >Path*:</label>');
	items.push('<input type="text" id="suitePath'+activePageID+'" value=""/>');
	items.push('</div>');
	items.push('<div class="field">');
	items.push('<label class=" text-right" >ExecType:</label>');
	items.push('<select type="text" class="text-right" id="Execute-at-ExecType'+activePageID+'"" value="" >');
	items.push('<option value="If">If</option> ');
	items.push('<option value="If Not">If Not</option> ');
	items.push('<option value="Yes">Yes</option> ');
	items.push('<option value="No">No</option> ');
	items.push('</select>');
	items.push('</div>');
			
	items.push('<div class="field">');
	items.push('<label for="executeRuleAtCondition">Rule Condition:</label>');
	items.push('<input type="text" id="executeRuleAtCondition'+activePageID+'" value=""/>');
	items.push('</div>');			
	items.push('<div class="field">');
	items.push('<label for="executeRuleAtCondvalue">Rule Condition Value:</label>');
	items.push('<input type="text" id="executeRuleAtCondvalue'+activePageID+'" value=""/>');
	items.push('</div>');			
	items.push('<div class="field">');
	items.push('<label for="executeRuleAtElse">Rule Else:</label>');
	items.push('<input type="text" id="executeRuleAtElse'+activePageID+'" value=""  />');
	items.push('</div>	');		
	items.push('<div class="field">');
	items.push('<label for="executeRuleAtElsevalue">Rule Else Value:</label>');
	items.push('<input type="text" id="executeRuleAtElsevalue'+activePageID+'" value="" />');
	items.push('</div>');
	items.push('<div class="field">');
	items.push('<label for="onError-at-action">On Error*:</label>');
	items.push('<input type="text" id="onError-at-action'+activePageID+'" value=""/>');
	items.push('</div>');

	items.push('<div class="field">');
	items.push('<label class="col-md-2 text-right" >On Error value:</label>');
	items.push('<select type="text" class="col-md-4 text-right" id="onError-at-value'+activePageID+'" value="" >');
	items.push('<option value="next">next</option>');
	items.push('<option value="abort">abort</option>');
	items.push('<option value="abort_as_error">abort_as_error</option>');
	items.push('<option value="goto">goto</option>');
	items.push('</select>');
	items.push('</div>');
		
	items.push('	<div class="field">');
	items.push('	<br><span class="label label-primary">Run mode</span><br>');
	items.push('	<label class="col-md-2 text-right" >runmode type:</label>');
	items.push('	<input type="text" class="col-md-4 text-right" id="runmode-at-type"'+activePageID + ' value="" />');
	items.push('	<label class="col-md-2 text-right" >runmode value:</label>');
	items.push('	<select type="text" class="col-md-4 text-right" id="runmode-at-value'+activePageID+'" value="" >');
	items.push('	<option value="RMT">RMT</option> ');
	items.push('	<option value="RUF">RUF</option> ');
	items.push('	<option value="RUP">RUP</option> ');
	items.push('	</select>');
	items.push('		</div>');

	items.push('	<div class="field">');
	items.push('		<label class="col-md-2 text-right" >impact</label>');
	items.push('			<select type="text" id="impact"'+activePageID + ' value="" >');
	items.push('			<option value="impact">impact</option> ');
	items.push('			<option value="noimpact">noimpact</option> ');
	items.push('			</select>');
	items.push('			<br>');
	items.push('		</div>');

	// Now create the buttons to save the data. 

	var bid = "editTestSuite-"+activePageID+"-id"+getRandomID();;
	items.push('<td><input type="button" class="btn" value="Edit" id="'+bid+'"/></td>');
	katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
	$(document).on('click','#'+bid,function(  ) {
			//var names = this.id.split('-');
			//var sid = parseInt(names[1]);
			mapUItoProjectSuite(xdata);
			
		});

	katana.$activeTab.find("#editTestSuiteEntry").html( items.join(""));
	
}


//
// This creates the table for viewing data in a sortable view. 
// 
function createSuitesTable(xdata) {
	var items = []; 
	//var xdata = data['Testsuite'];
	//if (!jQuery.isArray(xdata)) xdata = [xdata];
	//items.push('<ul id="suite_table_display"  >'); 

	items.push('<table id="suite_table_display" class="table" >');
	items.push('<thead>');
	items.push('<tr id="suiteRow"><th>Num</th><th>Suite</th><th>Execute</th><th>OnError</th><th>Impact</th><th/><th/></tr>');
	items.push('</thead>');
	items.push('<tbody>');

	katana.$activeTab.find("#tableOfTestSuitesForProject").html("");
	for (var s=0; s<Object.keys(xdata).length; s++ ) {
		var oneSuite = xdata[s];
		fillSuiteDefaults(s,xdata);
		console.log(oneSuite['path']);
		
		items.push('<tr><td>'+s+'</td>');
		items.push('<td>'+oneSuite['path']['$']+'</td>');
		items.push('<td>Type='+oneSuite['Execute']['@ExecType']+'<br>');
		items.push('Condition='+oneSuite['Execute']['Rule']['@Condition']+'<br>');
		items.push('Condvalue='+oneSuite['Execute']['Rule']['@Condvalue']+'<br>');
		items.push('Else='+oneSuite['Execute']['Rule']['@Else']+'<br>');
		items.push('Elsevalue='+oneSuite['Execute']['Rule']['@Elsevalue']+'<br>');
		items.push('</td>');
		items.push('<td>'+oneSuite['onError']['@action']+'</td>');
		items.push('<td>'+oneSuite['impact']['$']+'</td>');

		var bid = "deleteTestSuite-"+s+"-id"+getRandomID();
		//alert(bid);
		items.push('<td><input type="button" class="btn-danger" value="Delete" id="'+bid+'"/></td>');
		katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
		$(document).on('click','#'+bid,function( ) {
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			removeTestSuite(sid,xdata);
		});
		bid = "editTestSuite-"+s+"-id"+getRandomID();;
		items.push('<td><input type="button" class="btn" value="Edit" id="'+bid+'"/></td>');
		katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
		$(document).on('click','#'+bid,function(  ) {
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			console.log("xdata --> "+ xdata);
			mapProjectSuiteToUI(sid,xdata);
			//This is where you load in the edit form and display this row in detail. 
		});

		items.push('</tr>');
	}
	items.push('</tbody>');
	items.push('</table>');

	katana.$activeTab.find("#tableOfTestSuitesForProject").html( items.join(""));
	katana.$activeTab.find('#suite_table_display tbody').sortable();
	katana.$activeTab.find('#suite_table_display').on('click',"td",   function() { 
	});

}

function fillSuiteDefaults(s, data){
		oneSuite = data[s]
		if (! oneSuite['Execute']){
			oneSuite['Execute'] = { "@ExecType": "Yes", 
					"Rule": { "@Condition": "", "@Condvalue": "", "@Else": "next", "@Elsevalue": "" }
				}; 
		}
		if (! oneSuite['Execute']['@ExecType']){
				oneSuite['Execute']['@ExecType'] = "Yes";
		}
		if (!oneSuite['Execute']['Rule']) {
				oneSuite['Execute']['Rule'] = { "Rule": { "@Condition": "", "@Condvalue": "", "@Else": "next", "@Elsevalue": "" } };
		}
		if (! oneSuite['onError']) {
			oneSuite['onError'] = { "@action": "next", "@value": "" };
		}
		if (! oneSuite['runmode']) {
			oneSuite['runmode'] = { "@type": "next", "@value": "" };
		}
		if (! oneSuite['retry']) {
			oneSuite['retry'] = { "@type": "next", "@Condition": "", "@Condvalue": "", "@count": "" , "@interval": ""};
		}

}
/*
// Shows the global project data holder in the UI.

NOTE: At the time of writing I am using jQuery and Bootstrap to show the data.

Two global variables are heavily used when this function is called; 
1. jsonProjectObject 
2. jsonTestSuites which is set to point to the Testsuites data structure in
   the jsonProjectObject

*/
function mapProjectJsonToUi(data){
	var items = []; 
	var xdata = data['Testsuite'];
	if (!jQuery.isArray(xdata)) xdata = [xdata]; 

	createSuitesTable(xdata);
	createSuiteEditTable(xdata);
}  // end of function 

// Removes a test suite by its ID and refresh the page. 
function removeTestSuite( sid,xdata ){
	jsonTestSuites['Testsuite'].splice(sid,1);
	console.log("Removing test suites "+sid+" now " + Object.keys(jsonTestSuites).length);
	mapProjectJsonToUi(jsonTestSuites);	// Send in the modified array
}
