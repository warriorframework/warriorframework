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
	katana.$activeTab.find('#savesubdir').hide();
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
	createEditStepPage(jsonCaseObject);

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
		jsonCaseObject['Requirements']['Requirement'].push(sx); 

	}

	
	// Now you have collected the user components...

	var url = "./cases/getCaseDataBack";
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

	alert(ns);

	$.ajax({
    url : url,
    type: "POST",
    data : { 
    	'json': JSON.stringify(topNode),
    	'Testcase': ns,
    	'filetosave': katana.$activeTab.find('#my_file_to_save').val(),
    	'savesubdir': katana.$activeTab.find('#savesubdir').text(),
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
	items.push('<tr id="StepRow"><th>#</th><th>Step</th><th>Arguments</th>\
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

		var outstr = "Driver="+oneCaseStep['@Driver'] + "<br>Keyword=" + oneCaseStep['@Keyword'] + "<br>TS=" +oneCaseStep['@TS'] ;
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

		items.push('<td>'+outstr+'</td>'); 
	
		outstr =  oneCaseStep['Description']['$'];
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
		//items.push('<td><input type="button" class="btn-danger" value="X" id="'+bid+'"/>');
		items.push('<td><input type="button" title="Delete" class="ui-icon ui-icon-trash ui-button-icon-only" value="X" id="'+bid+'"/>');
		
		$('#'+bid).off('click');   //unbind and bind are deprecated. 
		$(document).on('click','#'+bid,function(  ) {
			alert(this.id);
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			removeTestStep(sid);
		});

		bid = "editTestStep-"+s+"-id-"+getRandomCaseID();
		items.push('<input type="button" title="Edit" class="ui-icon ui-icon-pencil ui-button-icon-only" value="Edit" id="'+bid+'"/></td>');
		$('#'+bid).off('c<td>lick');   //unbind and bind are deprecated. 
		$(document).on('click','#'+bid,function(  ) {
			alert(this.id);
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			mapTestStepToUI(sid,xdata);
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

function mapTestStepToUI(sid, xdata) {
	// body...
	katana.$activeTab.find("#StepRowToEdit"+activePageID).val(sid);
	katana.$activeTab.find("#StepDriver"+activePageID).val(oneCaseStep['step'][ "@Driver"]);
	katana.$activeTab.find("#StepKeyword"+activePageID).val(oneCaseStep['step'][ "@Keyword"]);
	katana.$activeTab.find("#StepTS"+activePageID).val(oneCaseStep['step'][ "@TS"]);
	katana.$activeTab.find("#StepDescription"+activePageID).val(oneCaseStep["Description"]["$"]);
	katana.$activeTab.find("#StepContext"+activePageID).val(oneCaseStep["context"]['$']);
	katana.$activeTab.find("#SteponError-at-action"+activePageID).val(oneCaseStep['onError']["@action"]);
	katana.$activeTab.find("#SteponError-at-value"+activePageID).val(oneCaseStep['onError']["@value"]);
	katana.$activeTab.find("#runmode-at-type"+activePageID).val(oneCaseStep["runmode"]["@type"]);
	katana.$activeTab.find("#StepImpact"+activePageID).val(oneCaseStep["impact"]);
	var a_items = [] ;

	for (var i =0; i < oneCaseStep['Arguments'].length; i++)
	{
		varg = oneCaseStep[i];
		a_items.push(""+varg['@name']+"="+varg['@value']);
	}	
	katana.$activeTab.find("#arguments-textarea-"+activePageID).html( a_items.join("\n"));
}

// When the edit button is clicked, map step to the UI. 
function mapUItoTestStep(xdata) {
	var sid = ParseInt(katana.$activeTab.find("#StepRowToEdit"+activePageID).val());	

	// Validate whether sid 
	oneCaseStep = xdata[sid];
	fillStepDefaults(oneCaseStep);  // Takes care of missing values.... 
	oneCaseStep['step'][ "@Driver"] = katana.$activeTab.find("#StepDriver"+activePageID).val();
	oneCaseStep['step'][ "@Keyword"] = katana.$activeTab.find("#StepKeyword"+activePageID).val();
	oneCaseStep['step'][ "@TS"] = katana.$activeTab.find("#StepTS"+activePageID).val();
	oneCaseStep["Description"] = { "$" : katana.$activeTab.find("#StepDescription"+activePageID).val();
	oneCaseStep["context"] = { "$" : katana.$activeTab.find("#StepContext"+activePageID).val();
	oneCaseStep["Execute"]["@ExecType"]= katana.$activeTab.find("#Execute-at-ExecType"+activePageID).val();		
	oneCaseStep['onError'][ "@action"] = katana.$activeTab.find("#SteponError-at-action"+activePageID).val();
	oneCaseStep['onError'][ "@value"] = katana.$activeTab.find("#SteponError-at-value"+activePageID).val();
	oneCaseStep["runmode"] = { "@type" : katana.$activeTab.find("#runmode-at-type"+activePageID).val();
	oneCaseStep["impact"] = { "$" : katana.$activeTab.find("#StepImpact"+activePageID).val();
	// Now draw the table again....

	var a_str = katana.$activeTab.find("#arguments-textarea-"+activePageID).text();
	a_items = a_str.split("\n");
	oneCaseStep["Arguments"] = [];
	//
	for (var i =0; i < a_items.length; i++) {
	
			if (varg.length > 2) {
			v_items = varg.split("");
			nm = varg[0];
			vl = varg[1];
			oneCaseStep["Arguments"].push({ "argument" : { "@name": nm, "@value": vl }})
		}
	}
	createEditStepPage(xdata);
}

function addStepToCase(){
	// Add an entry to the jsonTestSuites....
	var newCaseStep = {
		"step": {  "$": "", "@Driver": "demo_driver", "@Keyword": "" , "@TS": "0" },
		"Arguments" : { 'Argument': { '$': "" } },
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
	if (!jsonCaseSteps['step']) {
		jsonCaseSteps['step'] = [];
		}
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
		//items.push('<td><input type="button" class="btn-danger" value="Delete" id="'+bid+'"/></td>');
		items.push('<td><input type="button" title="Delete" class="ui-icon ui-icon-trash ui-button-icon-only" value="X" id="'+bid+'"/>');
		
		katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
		$(document).on('click','#'+bid,function( ) {
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			//mapUI(sid,xdata);
		});
		bid = "editRequirement-"+s+"-id"+getRandomCaseID();;
		//items.push('<td><input type="button" class="btn" value="Save" id="'+bid+'"/></td>');
		items.push('<input type="button" title="Edit" class="ui-icon ui-icon-pencil ui-button-icon-only" value="Edit" id="'+bid+'"/></td>');
		
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
	items.push('<div><input type="button" class="btn" value="Add Requirement" id="'+bid+'"/></div>');
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
	//katana.$activeTab.find('#Case_table_display').on('click',"td",   function() { 
	//});

}

function createEditStepPage(xdata) {
	katana.$activeTab.find("#editCaseStepEntry").html( "");
	var items = []; 
	
	/// Yes, a for loop would be better. 
	var rows = [ 'StepRowToEdit', 'StepDriver', 'StepKeyword', 'StepTS', 'StepDescription ','StepContext' ] ;
	for (rw in rows) {
		items.push('<div class="field col-md-3">'); 
		var nm = rows[rw].slice(4,rows[rw].length);
		items.push('<label >'+nm+'</label>');
		items.push('<input type="text" id="'+rows[rw]+activePageID+'" value=""/>');
		items.push('</div>')
	}

	items.push('<div class="field col-md-3">');
	items.push('<label class=" text-right" >ExecType:</label>');
	items.push('<select type="text" class="text-right" id="Execute-at-ExecType'+activePageID+'" value="" >');
	items.push('<option value="If">If</option> ');
	items.push('<option value="If Not">If Not</option> ');
	items.push('<option value="Yes">Yes</option> ');
	items.push('<option value="No">No</option> ');
	items.push('</select>');
	items.push('</div>');

	items.push('<div class="field col-md-3">');
	items.push('<label class="col-md-2 text-right" >On Error Action </label>');
	items.push('<select type="text" class="text-right" id="SteponError-at-action'+activePageID+'" value="" >');
	items.push('<option value="next">next</option>');
	items.push('<option value="abort">abort</option>');
	items.push('<option value="abort_as_error">abort_as_error</option>');
	items.push('<option value="goto">goto</option>');
	items.push('</select>');
	items.push('</div>');
	items.push('<div class="field col-md-3">');
	items.push('<label class="col-md-2 text-right" >On Error Value </label>');
	items.push('<select type="text" class="text-right" id="SteponError-at-value'+activePageID+'" value="" >');
	items.push('<option value="next">next</option>');
	items.push('<option value="abort">abort</option>');
	items.push('<option value="abort_as_error">abort_as_error</option>');
	items.push('<option value="goto">goto</option>');
	items.push('</select>');
	items.push('</div>');

	items.push('	<div class="field col-md-3">');
	items.push('	<label class="text-right" >Run mode:</label>');
	items.push('	<label class="text-right" >runmode type:</label>');
	items.push('	<input type="text" class="text-right" id="runmode-at-type"'+activePageID + ' value="" />');
	items.push('	<label class="text-right" >runmode value:</label>');
	items.push('	<select type="text" class="text-right" id="runmode-at-value'+activePageID+'" value="" >');
	items.push('	<option value="RMT">RMT</option> ');
	items.push('	<option value="RUF">RUF</option> ');
	items.push('	<option value="RUP">RUP</option> ');
	items.push('	</select>');
	items.push('		</div>');
	items.push('	<div class="field col-md-3">');
	items.push('		<label class="text-right" >impact</label>');
	items.push('			<select type="text" id="StepImpact"'+activePageID + ' value="" >');
	items.push('			<option value="impact">impact</option> ');
	items.push('			<option value="noimpact">noimpact</option> ');
	items.push('			</select>');
	items.push('			<br>');
	items.push('		</div>');


	var bid = "editCaseStep-"+activePageID+"-id"+getRandomCaseID();;
	items.push('<td><input type="button" class="btn" value="Save Changes To Test Step" id="'+bid+'"/></td>');
	katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
	$(document).on('click','#'+bid,function(  ) {
			mapUItoTestStep(xdata);
			//createCasesTable(xdata);  //Refresh the screen.
			alert("Ouch");
		});

	items.push('<textarea id="arguments-textarea-"'+activePageID+'"> </textarea>'); 
	katana.$activeTab.find("#editCaseStepEntry").html( items.join(""));
}
