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
	var sdata = katana.$activeTab.find("#listOfTestSuitesForProject").text();
	katana.$activeTab.find("#listOfTestSuitesForProject").hide();
	katana.$activeTab.find('#savefilepath').hide();  // To remove later...

	var jdata = sdata.replace(/'/g, '"');
	console.log('Mapping data ... ' + typeof(sdata) + ' is [' + sdata + "] " + sdata.length);  // This jdata is a string ....
	//console.log(jdata);                  // I show it as such. 
	jsonAllProjectPages[myobjectID] = JSON.parse(sdata); 
	//console.log(typeof(jsonAllProjectPages[myobjectID]));
	jsonProjectObject =  jsonAllProjectPages[myobjectID]; 
	jsonTestSuites = jsonProjectObject['Testsuites']; 
	mapProjectJsonToUi(jsonTestSuites);  // This is where the table and edit form is created. 
} 



/// -------------------------------------------------------------------------------
// Dynamically create a new TestSuite object and append to the jsonTestSuites 
// array. Default values are used to fill in a complete structure. If there is 
// no default value, a null value is inserted for the keyword
/// -------------------------------------------------------------------------------
function makeNewSuite() { 
		var newTestSuite = {	
		"path": "path/to/suite", 
		"Execute": { "@ExecType": "Yes",
			"Rule": {"@Condition": "","@Condvalue": "","@Else": "next", "@Elsevalue": "" }
		}, 
		"runmode": {
			"@type": "ruf", "@value": "2"
		},
		"retry": {
			"@type": "if not", 
			"@Condition": 
			"testsuite_1_result", 
			"@Condvalue": "PASS", 
			"@count": "6", 
			"@interval": "0"
		}, 
		"onError": { 
			"@action": "next",
			 "@value": "" }, 
		"impact": "impact" 
		};
		return newTestSuite;
}

function addSuiteToProject(){
	var newTestSuite = makeNewSuite();
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
	katana.$activeTab.find("#suiteRowToEdit").val(s); 
	katana.$activeTab.find("#suitePath").val(oneSuite['path']);
	katana.$activeTab.find("#Execute-at-ExecType").val(oneSuite['Execute']['@ExecType']); 
	katana.$activeTab.find("#executeRuleAtCondition").val(oneSuite['Execute']['Rule']['@Condition']); 
	katana.$activeTab.find("#executeRuleAtCondvalue").val(oneSuite['Execute']['Rule']['@Condvalue']); 
	katana.$activeTab.find("#executeRuleAtElse").val(oneSuite['Execute']['Rule']['@Else']); 
	katana.$activeTab.find("#executeRuleAtElsevalue").val(oneSuite['Execute']['Rule']['@Elsevalue']); 
	
	katana.$activeTab.find("#onError-at-action").val(oneSuite['onError']['@action']); 
	katana.$activeTab.find("#onError-at-value").val(oneSuite['onError']['@value']); 
	katana.$activeTab.find("#onError-at-type").val(oneSuite['runmode']['@type']); 
	katana.$activeTab.find("#onError-at-value").val(oneSuite['runmode']['@value']); 
	katana.$activeTab.find("#impact").val(oneSuite['impact']); 
	

}


/// -------------------------------------------------------------------------------
// This function is called to map the currently edited project suite to 
// the field being edited. 
// Note that this function is calld from an event handler which catches the 
// row number from the table.
/// -------------------------------------------------------------------------------
function mapUItoProjectSuite(xdata){

		
	var s = parseInt(katana.$activeTab.find("#suiteRowToEdit").val());
	var oneSuite = xdata[s];

	oneSuite['path'] = katana.$activeTab.find("#suitePath").val(); 
	oneSuite['Execute'] = {}
	oneSuite['Execute']['@ExecType'] = katana.$activeTab.find("#Execute-at-ExecType").val(); 
	oneSuite['Execute']['Rule'] = {}
	oneSuite['Execute']['Rule']['@Condition']= katana.$activeTab.find("#executeRuleAtCondition").val(); 
	oneSuite['Execute']['Rule']['@Condvalue'] = katana.$activeTab.find("#executeRuleAtCondvalue").val(); 
	oneSuite['Execute']['Rule']['@Else'] = katana.$activeTab.find("#executeRuleAtElse").val(); 
	oneSuite['Execute']['Rule']['@Elsevalue'] = katana.$activeTab.find("#executeRuleAtElsevalue").val(); 
	oneSuite['impact'] = katana.$activeTab.find("#impact").val(); 
	oneSuite['onError']['@action'] = katana.$activeTab.find("#onError-at-action").val(); 
	oneSuite['onError']['@value'] = katana.$activeTab.find("#onError-at-value").val(); 
	oneSuite['runmode']['@type'] = katana.$activeTab.find("#onError-at-type").val(); 
	oneSuite['runmode']['@value'] = katana.$activeTab.find("#onError-at-value").val(); 
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
	
	jsonProjectObject['Details']['Name'] = katana.$activeTab.find('#projectName').val();
	jsonProjectObject['Details']['Title'] = katana.$activeTab.find('#projectTitle').val();
	jsonProjectObject['Details']['Engineer'] = katana.$activeTab.find('#projectEngineer').val();
	jsonProjectObject['Details']['State'] = katana.$activeTab.find('#projectState').val();
	jsonProjectObject['Details']['Date'] = katana.$activeTab.find('#projectDate').val();
	jsonProjectObject['Details']['default_onError'] = katana.$activeTab.find('#defaultOnError').val();
	jsonProjectObject['Details']['Datatype'] = katana.$activeTab.find('#projectDatatype').val();
	jsonProjectObject['SaveToFile'] = katana.$activeTab.find('#my_file_to_save').val();
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
	
	var topNode  = { 'Project' : jsonProjectObject};


	$.ajax({
	    url : url,
	    type: "POST",
	    data : { 
	    	'json': JSON.stringify(topNode),
	    	//'Project': ns,
	    	'filetosave': katana.$activeTab.find('#filesavepath').text() + "/" + $('#my_file_to_save').val()
	    	},
	    headers: {'X-CSRFToken':csrftoken},
    
    success: function( data ){
        alert("Saved "+katana.$activeTab.find('#filesavepath').text() );
    	}
	});

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
		console.log(xdata);
		if (oneSuite == null) {
			xdata[s] = {} ;
			oneSuite = xdata[s];
		}
		console.log(oneSuite);
		fillSuiteDefaults(s,xdata);
		console.log(oneSuite);
		console.log(oneSuite['path']);
		
		items.push('<tr data-sid="'+s+'">');
		items.push('<td class="col-md-1">'+(parseInt(s)+1)+'</td>');
		items.push('<td>'+oneSuite['path']+'</td>');
		items.push('<td>Type='+oneSuite['Execute']['@ExecType']+'<br>');
		items.push('Condition='+oneSuite['Execute']['Rule']['@Condition']+'<br>');
		items.push('Condvalue='+oneSuite['Execute']['Rule']['@Condvalue']+'<br>');
		items.push('Else='+oneSuite['Execute']['Rule']['@Else']+'<br>');
		items.push('Elsevalue='+oneSuite['Execute']['Rule']['@Elsevalue']+'<br>');
		items.push('</td>');
		items.push('<td>'+oneSuite['onError']['@action']+'</td>');
		items.push('<td>'+oneSuite['impact']+'</td>');

		var bid = "deleteTestSuite-"+s+"-id"+getRandomID();
		//alert(bid);
		items.push('<td><i  title="Delete" class="fa fa-eraser" value="X" id="'+bid+'"/>');
		katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
		$(document).on('click','#'+bid,function( ) {

			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			removeTestSuite(sid,xdata);
		});
		bid = "editTestSuite-"+s+"-id"+getRandomID();;
		items.push('<i  title="Edit" class="fa fa-pencil" title="Edit" id="'+bid+'"/>');
		katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
		$(document).on('click','#'+bid,function(  ) {
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			console.log("xdata --> "+ xdata);
			mapProjectSuiteToUI(sid,xdata);
			//This is where you load in the edit form and display this row in detail. 
		});

		bid = "InsertTestSuite-"+s+"-id"+getRandomID();;
		items.push('<i  title="Insert" class="fa fa-plus" value="Insert" id="'+bid+'"/></td>');
		katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
		$(document).on('click','#'+bid,function(  ) {
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			console.log("xdata --> "+ xdata);
			insertTestSuite(sid,xdata);
			mapProjectSuiteToUI(sid,xdata);
			//This is where you load in the edit form and display this row in detail. 
		});


		items.push('</tr>');
	}
	items.push('</tbody>');
	items.push('</table>');

	katana.$activeTab.find("#tableOfTestSuitesForProject").html( items.join(""));
	katana.$activeTab.find('#suite_table_display tbody').sortable( { stop: testProjectSortEventHandler});
	katana.$activeTab.find('#suite_table_display').on('click',"td",   function() { 
	});
	//katana.$activeTab.find("#tableOfTestSuitesForProject").setAttribute( "style","overflow-y:scroll");

 	 katana.$activeTab.find('table#suite_table_display thead tr th').each(function(index) {
    		var thisWidth = $(this).width();
    		if ( index == 0 ) { thisWidth = 40; }
    		console.log(thisWidth + "  "+ index);
    		var elem = this; 
    		$(this).css('width',40);
    		katana.$activeTab.find('table#suite_table_display tbody tr td').each(function(xindex) {	
    				$(this).css('width',40);
    		});
  	});



}

var testProjectSortEventHandler = function(event, ui ) {
	var listSuites = katana.$activeTab.find('#suite_table_display tbody').children(); 
	console.log(listSuites);
	console.log(jsonProjectObject["Testsuites"] );
	var oldSuitesteps = jsonProjectObject["Testsuites"]['Testsuite'];
	var newSuitesteps = new Array(listSuites.length);
	console.log("List of ... "+listSuites.length);
	for (xi=0; xi < listSuites.length; xi++) {
		var xtr = listSuites[xi];
		var ni  = xtr.getAttribute("data-sid");
		console.log(xi + " => " + ni);
		newSuitesteps[ni] = oldSuitesteps[xi];
	}

	
	console.log(jsonProjectObject);
	jsonProjectObject["Testsuites"]['Testsuite']= newSuitesteps;
	console.log(jsonProjectObject["Testsuites"] );
	

	jsonTestSuites = jsonProjectObject['Testsuites'] 
	mapProjectJsonToUi(jsonTestSuites);

}

function fillSuiteDefaults(s, data){
		if(data[s] == null) {
			data[s] = {} ;
		}    
		oneSuite = data[s]


		if (!oneSuite['path']) {
			oneSuite['path'] =  "New";
		}

		if (!oneSuite['impact']) {
			oneSuite['impact'] = "New";
		}
		if (!oneSuite['impact']) {
			oneSuite['impact'] =  "impact";
		}

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
	katana.$activeTab.find('#saveChangesToRow').off('click');  // unbind is deprecated - debounces the click event. 
	$(document).on('click','#saveChangesToRow',function(  ) {
			console.log(xdata);
			mapUItoProjectSuite(xdata);
		});

}  // end of function 



// Removes a test suite by its ID and refresh the page. 
function removeTestSuite( sid,xdata ){
	jsonTestSuites['Testsuite'].splice(sid,1);
	console.log("Removing test suites "+sid+" now " + Object.keys(jsonTestSuites).length);
	mapProjectJsonToUi(jsonTestSuites);	// Send in the modified array
}
// Removes a test suite by its ID and refresh the page. 
function insertTestSuite( sid,xdata ){
	var newTestSuite = makeNewSuite();	
	jsonTestSuites['Testsuite'].splice(sid,0,newTestSuite);
	console.log("Removing test suites "+sid+" now " + Object.keys(jsonTestSuites).length);
	mapProjectJsonToUi(jsonTestSuites);	// Send in the modified array
}
