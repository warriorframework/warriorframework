//
//
/*

Project File Data Handler 

Author: 
Date: 

The functions in this module are designed specifically for handling project XML files
for the warrior framework. 

It is expected to work with the editProject.html file and the calls to editProject in 
the views.py python for Django. 

*/
if (typeof jsonAllProjectPages === 'undefined') {
 //alert("Creating all jsonAllProjectPages");
 
 jsonAllProjectPages = { };
} else {
	//alert("Already there...");
}


//alert(jsonProjectID);
//jsonAllProjectPages[jsonProjectID] = [] 
var jsonProjectObject = []; // =  jsonAllProjectPages[jsonProjectID];
//alert(jsonAllProjectPages[jsonProjectID] );
var jsonTestSuites = [];

// Sets up the global project data holder for the UI. 
// This is called from the correspoding HTML file onLoad event 
// or when a new XML file is loaded into the interface.
// 
// Two variables are set when this function is called; 
// 1. jsonProjectObject 
// 2. jsonTestSuites is set to point to the Testsuites data structure in
//    the jsonProjectObject
//
//

function mapFullProjectJson(myobjectID){
	var sdata = katana.$activeTab.find("#listOfTestSuitesForProject").text();
	var jdata = sdata.replace(/'/g, '"');
	console.log('Mapping data ... ' + typeof(sdata) + ' is [' + sdata + "] " + sdata.length);  // This jdata is a string ....
	//console.log(jdata);                  // I show it as such. 
	jsonAllProjectPages[myobjectID] = JSON.parse(sdata); 
	//jsonAllProjectPages[myobjectID] = JSON.parse(jdata); 
	//alert(JSON.parse(sdata));
	console.log(typeof(jsonAllProjectPages[myobjectID]));
	jsonProjectObject =  jsonAllProjectPages[myobjectID]; 
	jsonTestSuites = jsonProjectObject['Testsuites']; 
	mapProjectJsonToUi(jsonTestSuites);
	
} 



// 
// Dynamically create a new TestSuite object and append to the jsonTestSuites 
// array. Default values are used to fill in a complete structure. If there is 
// no default value, a null value is inserted for the keyword
//
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
	// Now walk the DOM ..
	// Create dynamic ID values based on the Suite's location in the UI. 

	// Note that if we implement drag and drop we'll have to re-index the entire 
	// visual display to reflect the movements of the order of objects on display 
	// That would require a refresh after a drop anyway. 
	var xdata = jsonProjectObject['Testsuites']['Testsuite'];

	for (var s=0; s<Object.keys(xdata).length; s++ ) {
		var oneSuite = xdata[s];

		oneSuite['Execute']['$'] = ""
		id = '#'+s+"-Execute-at-ExecType";
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
	alert("HELLO");
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

function createSuitesTable(data) {
	var items = []; 
	var xdata = data['Testsuite'];
	if (!jQuery.isArray(xdata)) xdata = [xdata];
	//items.push('<ul id="suite_table_display"  >'); 

	items.push('<table id="suite_table_display" class="table" >');
	items.push('<thead>');
	items.push('<tr id="suiteRow"><th>Num</th><th>Suite</th><th>Execute</th><th>OnError</th><th>Impact</th></tr>');
	items.push('</thead>');
	items.push('<tbody>');
	katana.$activeTab.find("#tableOfTestSuitesForProject").html("");
	for (var s=0; s<Object.keys(xdata).length; s++ ) {
		var oneSuite = xdata[s];
		fillSuiteDefaults(oneSuite);
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
		items.push('</tr>');



	}
	items.push('</tbody>');
	
	items.push('</table>');
	//items.push('</ul>');
	
	//$('<div/>', {  collapsible: "true" , html: items.join("")}).appendTo(katana.$activeTab.find("#tableOfTestSuitesForProject"));
	katana.$activeTab.find("#tableOfTestSuitesForProject").html( items.join(""));
	katana.$activeTab.find('#suite_table_display tbody').sortable();
	katana.$activeTab.find('#suite_table_display').on('click',"td",   function() { 
		alert($(this).text());
	});

}

function fillSuiteDefaults(oneSuite){

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

	createSuitesTable(data);

	items.push('<div id="accordion_display" class="col-md-12">');
	console.log("xdata =" + xdata);
	katana.$activeTab.find("#listOfTestSuitesForProject").html("");

	for (var s=0; s<Object.keys(xdata).length; s++ ) {
		var oneSuite = xdata[s];
		console.log(oneSuite['path']);
		items.push('<h3>TestSuite '+s+"</h3>");
		items.push('<div class="collapse">');

		items.push('<label class="col-md-2 text-right" for="defaultOnError>'+oneSuite['path']+'</label><br>');
		// -------------------------------------------------------------------------
		// Validation and default assignments 
		// Create empty elements with defaults if none found. ;-)
		// -------------------------------------------------------------------------
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


		items.push('<label class=" text-right" >ExecType:</label>');
		items.push('<select type="text" class="text-right"id="'+s+'-Execute-at-ExecType"  value="'+oneSuite['Execute']['@ExecType']+'" >');
		items.push('<option value="If">If</option>'); 
		items.push('<option value="If Not">If Not</option>'); 
		items.push('<option value="Yes">Yes</option>'); 
		items.push('<option value="No">No</option>'); 
		items.push('</select>'); 
		items.push('<br><span class="label label-primary">Rules</span><br>');

		// Show Ruls for the ExecType
		items.push('<label class="col-md-2 text-right" >Rule-Condition:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-Execute-Rule-at-Condition" value="'+oneSuite['Execute']['Rule']['@Condition']+'" />');
		items.push('<label class="col-md-2 text-right" f>Rule-Condvalue:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-Execute-Rule-at-Condvalue" value="'+oneSuite['Execute']['Rule']['@Condvalue']+'" />');
		items.push('<label class="col-md-2 text-right" >Rule-Else:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-Execute-Rule-at-Else"  value="'+oneSuite['Execute']['Rule']['@Else']+'" />');
		items.push('<label class="col-md-2 text-right" >Rule-at-Elsevalue:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-Execute-Rule-at-Elsevalue"  value="'+oneSuite['Execute']['Rule']['@Elsevalue']+'" />');
		items.push('<br><span class="label label-primary">OnError</span><br>');


		items.push('<label class="col-md-2 text-right" >OnError-at-action:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-onError-at-action" value="'+oneSuite['onError']['@action']+'" />');
		items.push('<label class="col-md-2 text-right" >OnError-at-value:</label>');
		items.push('<select type="text" class="col-md-4 text-right" id="'+s+'-onError-at-value" value="'+oneSuite['onError']['@value']+'" >');
		items.push('<option value="next">next</option>'); 
		items.push('<option value="abort">abort</option>'); 
		items.push('<option value="abort_as_error">abort_as_error</option>'); 
		items.push('<option value="goto">goto</option>'); 
		items.push('</select>');


		items.push('<br><span class="label label-primary">Run mode</span><br>');
		items.push('<label class="col-md-2 text-right" >runmode-at-type:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-runmode-at-type" value="'+oneSuite['runmode']['@type']+'" />');
		items.push('<label class="col-md-2 text-right" >runmode-at-value:</label>');
		items.push('<select type="text" class="col-md-4 text-right" id="'+s+'-runmode-at-value" value="'+oneSuite['runmode']['@value']+'" >');
		items.push('<option value="RMT">RMT</option>'); 
		items.push('<option value="RUF">RUF</option>'); 
		items.push('<option value="RUP">RUP</option>'); 
		items.push('</select>');

		items.push('<br><span class="label label-primary">Retry</span><br>');
		items.push('<label class="col-md-2 text-right" >retry-at-type:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-retry-at-type" value="'+oneSuite['retry']['@type']+'" />');
		items.push('<label class="col-md-2 text-right" >retry-at-Condition:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-retry-at-Condition" value="'+oneSuite['retry']['@Condition']+'" />');
		items.push('<label class="col-md-2 text-right" >retry-at-Condvalue:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-retry-at-Condvalue" value="'+oneSuite['retry']['@Condvalue']+'" />');
		items.push('<label class="col-md-2 text-right" >retry-at-count:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-retry-at-count" value="'+oneSuite['retry']['@count']+'" />');
		items.push('<label class="col-md-2 text-right" >retry-at-interval:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-retry-at-interval" value="'+oneSuite['retry']['@interval']+'" />');
		items.push('<br>');

		items.push('<label class="col-md-2 text-right" >impact</label>');
		items.push('<select type="text" id="'+s+':"impact" value="'+oneSuite['impact']['$']+'" >');
		items.push('<option value="impact">impact</option>'); 
		items.push('<option value="noimpact">noimpact</option>'); 
		items.push('</select>');
		items.push("<br>");

		// Allow user to delete the UI object;
		// Create handler to destroy the object and then refresh the display. 
		bid = "deleteTestSuite-"+s;
		items.push('<input type="button" class="btn-danger" value="Delete" id="'+bid+'"/>');
		$('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
		$(document).on('click','#'+bid,function(  ) {
			//alert(this.id);
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			removeTestSuite(sid,xdata);
		});
		items.push("</div>");
	}
	//$('<div/>', {  collapsible: "true" , html: items.join("")}).appendTo(katana.$activeTab.find("#listOfTestSuitesForProject"));
	katana.$activeTab.find("#listOfTestSuitesForProject").html( items.join(""));
	katana.$activeTab.find("#accordion_display").accordion();
}  // end of function 

// Removes a test suite by its ID and refresh the page. 
function removeTestSuite( sid,xdata ){
			jsonTestSuites['Testsuite'].splice(sid,1);
			console.log("Removing test suites "+sid+" now " + Object.keys(jsonTestSuites).length);
			mapProjectJsonToUi(jsonTestSuites);	// Send in the modified array
}

	// This function does not work at the moment. I have to debug it later. 
	// Kamran
function openAllSuites() {

	$('.collapse').collapse('show');
	$("#accordion_display").collapse('show');
}



