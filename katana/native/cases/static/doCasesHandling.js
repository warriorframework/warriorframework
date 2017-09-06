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
function getRandomCaseID() {
  min = Math.ceil(1);
  max = Math.floor(4000);
  return Math.floor(Math.random() * (max - min)) + min;
  
}

if (typeof jsonAllCasePages === 'undefined') {
 jsonAllCasePages = { };
} else {
	//alert("Already there...");
}

var jsonCaseObject = [];
var jsonCaseDetails = [];         
var jsonCaseSteps = [];           
var jsonCaseRequirements = []; 	  // This is the JSON model for the UI requirements
var activePageID = getRandomCaseID();   // for the page ID 

function mapFullCaseJson(myobjectID){
	activePageID = getRandomCaseID();
	console.log("HELLO");
	var sdata = katana.$activeTab.find("#listOfTestStepsForCase").text();
	katana.$activeTab.find("#listOfTestcasesForSuite").hide();
	var jdata = sdata.replace(/'/g, '"');
	jsonAllCasePages[myobjectID] = JSON.parse(sdata);               
	jsonCaseObject = jsonAllCasePages[myobjectID]
	jsonCaseSteps  = jsonCaseObject["Steps"];
	jsonCaseRequirements = jsonCaseObject['Requirements'];
	if (!jQuery.isArray(jsonCaseRequirements)) jsonCaseObject['Requirements'] = [jsonCaseObject['Requirements']]; 
	jsonCaseDetails = jsonCaseObject['Details'];
	mapCaseJsonToUi(jsonCaseSteps);
	//mapRequirementsToUI(jsonCaseRequirements);
	createRequirementsTable(jsonCaseRequirements);


	// Must define handlers inside this function ... 

	$('#caseDatatype').change(function(e){	
		jsonCaseDetails['Datatype'] = this.value; 
		$(".iteration-div").hide();
		$(".arguments-div").show();

		if (this.value == 'Custom') {
			$(".arguments-div").hide();
		} 
		// Iterative tag is show only for Hybird. 
		if (this.value == 'Hybrid') {
			$(".iteration-div").show();
		}
		//mapCaseJsonToUi(jsonCaseSteps);
	});

}



function addOneArgument( sid ) {
	var xx = { 'Argument': { "@name": "" , "@value": " " } };
	jsonCaseSteps['step'][sid]['Arguments']['argument'].push(xx);
	mapCaseJsonToUi(jsonCaseSteps);
}

function removeOneArgument( sid, aid) {

	jsonCaseSteps['step'][sid]['Arguments']['argument'].splice(aid,1);	
	mapCaseJsonToUi(jsonCaseSteps);
}


function mapUiToCaseJson() {
	
	jsonCaseObject['Details']['Name']['$'] = katana.$activeTab.find('#caseName').val();
	jsonCaseObject['Details']['Title']['$'] = katana.$activeTab.find('#caseTitle').val();
	jsonCaseObject['Details']['Category']['$'] = katana.$activeTab.find('#caseCategory').val();
	jsonCaseObject['Details']['State']['$'] = katana.$activeTab.find('#caseState').val();
	jsonCaseObject['Details']['Engineer']['$'] = katana.$activeTab.find('#caseEngineer').val();
	jsonCaseObject['Details']['Title']['$'] = katana.$activeTab.find('#caseTitle').val();
	jsonCaseObject['Details']['Date']['$'] = katana.$activeTab.find('#caseDate').val();
	//jsonCaseObject['Details']['Time'] = $('#suiteTime').val();
	jsonCaseObject['Details']['default_onError']['$'] = katana.$activeTab.find('#default_onError').val();
	jsonCaseObject['Details']['Datatype']['$'] = katana.$activeTab.find('#caseDatatype').val();
	jsonCaseObject['dataPath'] = { "$" : katana.$activeTab.find('#caseInputDataFile').val()};
	jsonCaseObject['resultsDir'] = { "$" : katana.$activeTab.find('#caseResultsDir').val()};
	jsonCaseObject['logsDir'] = { "$" : katana.$activeTab.find('#caseLogsDir').val()};
	jsonCaseObject['expectedDir'] = { "$" : katana.$activeTab.find('#caseExpectedResults').val()};
	

	jsonCaseObject['SaveToFile'] = { "$" : katana.$activeTab.find('#my_file_to_save').val()};
	// Now walk the DOM ..


	jsonCaseObject['Requirements'] = { "$" : "" , "Requirement" : [] };
	var rdata = jsonCaseObject['Steps']['step'];
	for (var s=0; s<Object.keys(rdata).length; s++ ) {
		var oneReqStep = rdata[s];
		sx = { "Requirement" :  { '$' :  oneReqStep['Requirement'] } }
		jsonCaseObject['Requirements']['Requirement'].append(sx); 

	}

	
	// Now you have collected the user components...

	var url = "../getCaseDataBack";
	var csrftoken = $("[name='csrfmiddlewaretoken']").val();

	$.ajaxSetup({
			function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
    	}
	});

	var topNode  = { 'Testcase' : jsonCaseObject};
	var jj = new json() ; 
	// var mystring =  JSON.stringify(jsonCaseObject);
	var ns = jj.translate.toXML(topNode);

	//alert(ns);

	$.ajax({
    url : url,
    type: "POST",
    data : { 
    	'json': JSON.stringify(topNode),
    	'Testcase': ns,
    	'filetosave': $('#my_file_to_save').val()
    	},
    headers: {'X-CSRFToken':csrftoken},
    //contentType: 'application/json',
    success: function( data ){
        alert("Sent");
    	}
	});

}

function fillStepDefaults(oneCaseStep) {

		if (! oneCaseStep['step']){
			oneCaseStep['step'] = { "@ExecType": "Yes", 
					"Rule": { "@Condition": "", "@Condvalue": "", "@Else": "next", "@Elsevalue": "" }
				}; 
		}
		if (!oneCaseStep['step']['Rule']) {
				oneCaseStep['step']['Rule'] = { "Rule": { "@Condition": "", "@Condvalue": "", "@Else": "next", "@Elsevalue": "" } };
		}
		if (! oneCaseStep['onError']) {
			oneCaseStep['onError'] = { "@action": "next", "@value": "" };
		}
		if (! oneCaseStep['runmode']) {
			oneCaseStep['runmode'] = { "@type": "next", "@value": "" };
		}
		if (! oneCaseStep['retry']) {
			oneCaseStep['retry'] = { "@type": "next", "@Condition": "", "@Condvalue": "", "@count": "" , "@interval": ""};
		}


}

/*

Maps the data from a Testcase object to the UI. 
The UI currently uses jQuery and Bootstrap to display the data.

*/
function mapCaseJsonToUi(data){
	//
	// This gives me ONE object - The root for test cases
	// The step tag is the basis for each step in the Steps data array object.
	// 
	var items = []; 
	var xdata = data['step'];
	if (!jQuery.isArray(xdata)) xdata = [xdata]; // convert singleton to array


	//console.log("xdata =" + xdata);
	$("#listOfTestStepsForCase").html("");      // Start with clean slate
	items.push('<table id="Step_table_display" class="table" >');
	items.push('<thead>');
	items.push('<tr id="StepRow"><th>Step</th><th>Arguments</th>\
		<th>Description</th><th>OnError</th><th>Execute</th><th>Other</th><th/><th/></tr>');
	items.push('</thead>');
	items.push('<tbody>');
	for (var s=0; s<Object.keys(xdata).length; s++ ) {  // for s in xdata
		var oneCaseStep = xdata[s];             // for each step in case
		//console.log(oneCaseStep['path']);
		items.push('<tr><td>'+s+'</td>');        // ID 
		// -------------------------------------------------------------------------
		// Validation and default assignments 
		// Create empty elements with defaults if none found. ;-)
		// -------------------------------------------------------------------------
		fillStepDefaults(oneCaseStep);
		// Now create HTML elements for the relevant items - 

		var outstr = oneCaseStep['@Driver'] + "<br>" + oneCaseStep['@Keyword'] + "<br>" +oneCaseStep['@TS'] ;
		items.push('<td>'+outstr+'</td>'); 

		// Show arguments for each step in the UI div tag. 
		var arguments = oneCaseStep['Arguments']['argument'];

		var out_array = [] 
		var ta = 0; 
		
		for (xarg in arguments) {
			var xstr = "Args " + arguments[xarg]['@name']+"="+arguments[xarg]['@value'];
			console.log(xstr);
			out_array.push(xstr); 
			ta  = ta + 1; 
			}
		outstr = out_array.join("");
		console.log("LOOK"+outstr);
		/*

			var bid = "deleteArgumentText-"+ s + "-" + ta;
			items.push('<div><input type="text" value="'+xstr+'" id="'+bid+'" />');
			bid = "deleteArgument-"+ s + "-" + ta + "-" + getRandomCaseID();
			items.push('<input type="button" class="btn-danger" value="Delete Me" id="'+bid+'"/></div>');

			$('#'+bid).off('click');   //unbind and bind are deprecated. 
			$(document).on('click','#'+bid,function(  ) {
				var names = this.id.split('-');
				var sid = parseInt(names[1]);
				var aid = parseInt(names[2]);
				removeOneArgument(sid,aid);
				});

		*/
		items.push('<td>'+outstr+'</td>'); 
	
		outstr =  oneCaseStep['Description'];
		items.push('<td>'+outstr+'</td>'); 

		outstr = "Action=" + oneCaseStep['onError']['@action'] + "<br>" +
			"Value=" + oneCaseStep['onError']['@value']+"<br>" +  
			"ExecType=" + oneCaseStep['step']['@ExecType'] + "<br>" + 
			"Condition="+oneCaseStep['step']['Rule']['@Condition']+ "<br>" + 
			"Condvalue="+oneCaseStep['step']['Rule']['@Condvalue']+ "<br>" + 
			"Else="+oneCaseStep['step']['Rule']['@Else']+ "<br>" +
			"Elsevalue="+oneCaseStep['step']['Rule']['@Elsevalue'];

		items.push('<td>'+outstr+'</td>'); 

		outstr = "RMT=" + oneCaseStep['rmt'] + "<br>Context=" + oneCaseStep['context']['$'] +
			"<br>Impact=" + oneCaseStep['impact'];
		items.push('<td>'+outstr+'</td>'); 
		var bid = "deleteTestStep-"+s+"-id-"+getRandomCaseID();
		items.push('<td><input type="button" class="btn-danger" value="Delete Step" id="'+bid+'"/></td>');
		$('#'+bid).off('c<td>lick');   //unbind and bind are deprecated. 
		$(document).on('click','#'+bid,function(  ) {
			alert(this.id);
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			removeTestStep(sid);
		});

		bid = "editTestStep-"+s+"-id-"+getRandomCaseID();
		items.push('<td><input type="button" class="btn" value="Edit Step" id="'+bid+'"/></td>');
		$('#'+bid).off('c<td>lick');   //unbind and bind are deprecated. 
		$(document).on('click','#'+bid,function(  ) {
			alert(this.id);
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			removeTestStep(sid);
		});
		items.push('</tr>');

	}

	items.push('</tbody>');
	items.push('</table>'); // 
	katana.$activeTab.find("#listOfTestStepsForCase").html( items.join(""));
	katana.$activeTab.find('#Step_table_display tbody').sortable();
	katana.$activeTab.find('#Step_table_display').on('click',"td",   function() { 
	});

	/*
	if (jsonCaseDetails['Datatype'] == 'Custom') {
		$(".arguments-div").hide();
	} else {

		$(".arguments-div").show();
	}
	*/
	//$('#fileName').html("");
	
}  // end of function 


// Removes a test suite by its ID and refresh the page. 
function removeTestStep( sid ){
			jsonCaseSteps['step'].splice(sid,1);
			console.log("Removing test cases "+sid+" now " + Object.keys(jsonCaseSteps).length);
			mapCaseJsonToUi(jsonCaseSteps);
}


function addStepToCase(){
	// Add an entry to the jsonTestSuites....
	var newCaseStep = {
		"step": {  "$": "", "@Driver": "demo_driver", "@Keyword": "" , "@TS": "0" },
		"Arguments" : { },
		"onError": {  "$": "", "@action" : "next" } ,
		"iteration_type": { "$": "",  "@type" : "" } ,
		"Description": { "$": " "} ,
		"Execute": {  "$": "", "@ExecType": "Yes",
			"Rule": { "$": "", "@Condition": "","@Condvalue": "","@Else": "next", "@Elsevalue": "" }
		}, 
		"context": { "$": "positive"}, 
		"impact" : { "$": "impact"},
		"rmt" : {  "$": " "} ,
		"retry": { "$": "", "@type": "if not", "@Condition": "testsuite_1_result", "@Condvalue": "PASS", "@count": "6", "@interval": "0"}, 
	 };
	if (!jQuery.isArray(jsonCaseSteps['step'])) {
		jsonCaseSteps['step'] = [jsonCaseSteps['step']];
		}

	jsonCaseSteps['step'].push(newCaseStep);
	mapCaseJsonToUi(jsonCaseSteps);
}



function createRequirementsTable(rdata){
	var items =[]; 
	katana.$activeTab.find("#tableOfCaseRequirements").html("");
	
	items.push('<table id="Case_table_display" class="table" >');
	items.push('<thead>');
	items.push('<tr id="ReqRow"><th>Num</th><th>Requirement</th><th/><th/></tr>');
	items.push('</thead>');
	items.push('<tbody>');
	console.log(rdata);
	for (var s=0; s<Object.keys(rdata).length; s++ ) {
		var oneReq = rdata[s];
		items.push('<tr><td>'+s+'</td>');
		//items.push('<td>'+oneReq['$']+'</td>');
		var bid = "textRequirement-"+s+"-id"+activePageID;	
		if (!jQuery.isArray(oneReq)) oneReq = { '$': oneReq } ; 
		items.push('<td><input type="text" value="'+oneReq['$'] +'" id="'+bid+'"/></td>');
		
		bid = "deleteRequirement-"+s+"-id"+getRandomCaseID();
		//alert(bid);
		items.push('<td><input type="button" class="btn-danger" value="Delete" id="'+bid+'"/></td>');
		katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
		$(document).on('click','#'+bid,function( ) {
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			//removeTestcase(sid,xdata);
		});
		bid = "editRequirement-"+s+"-id"+getRandomCaseID();;
		items.push('<td><input type="button" class="btn" value="Save" id="'+bid+'"/></td>');
		katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
		$(document).on('click','#'+bid,function(  ) {
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			console.log("xdata --> "+ rdata);  // Get this value and update your json. 
			var txtIn = katana.$activeTab.find("#textRequirement-"+sid+"-id"+activePageID).val();
			console.log(katana.$activeTab.find("#textRequirement-"+sid+"-id"+activePageID));
			console.log(sid);
			console.log(jsonCaseObject['Requirements'][sid])
			jsonCaseObject['Requirements'][sid]['$'] = txtIn;

			createRequirementsTable(jsonCaseObject['Requirements']);	
			event.stopPropagation();
			//This is where you load in the edit form and display this row in detail. 
		});
	}
	items.push('</tbody>');
	items.push('</table>');

	bid = "addRequirement-"+getRandomCaseID();
	items.push('<td><input type="button" class="btn" value="Add Requirement" id="'+bid+'"/></td>');
	katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
	$(document).on('click','#'+bid,function( event  ) {
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			console.log("Add Requirement... ");
			if (!jsonCaseObject['Requirements']) jsonCaseObject['Requirements'] = [];
			rdata = jsonCaseObject['Requirements'];
			rdata.push({"Requirement" : { "$": ""},});
			console.log(jsonCaseObject);
			createRequirementsTable(jsonCaseObject['Requirements']);	
			event.stopPropagation();
		});

	katana.$activeTab.find("#tableOfTestRequirements").html( items.join(""));
	katana.$activeTab.find('#Case_table_display tbody').sortable();
	katana.$activeTab.find('#Case_table_display').on('click',"td",   function() { 
	});

}