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
var jsonFilesInfo = null; 

function mapFullCaseJson(myobjectID){
	activePageID = getRandomCaseID();
	var sdata = katana.$activeTab.find("#listOfTestStepsForCase").text();
	katana.$activeTab.find("#listOfTestcasesForSuite").hide();
	katana.$activeTab.find('#savesubdir').hide();
	var jdata = sdata.replace(/'/g, '"');
	jsonAllCasePages[myobjectID] = JSON.parse(sdata);               
	jsonCaseObject = jsonAllCasePages[myobjectID]
	jsonCaseSteps  = jsonCaseObject["Steps"];
	jsonCaseRequirements = jsonCaseObject['Requirements'];
	//if (!jQuery.isArray(jsonCaseRequirements)) jsonCaseObject['Requirements'] = []; 
	jsonCaseRequirements = jsonCaseObject['Requirements'];
	jsonCaseDetails = jsonCaseObject['Details'];
	mapCaseJsonToUi(jsonCaseSteps);
	//mapRequirementsToUI(jsonCaseRequirements);
	createRequirementsTable(jsonCaseRequirements);
	
	katana.$activeTab.find('#editCaseStep').off('click');  // unbind is deprecated - debounces the click event. 
	$(document).on('click','#editCaseStep',function(  ) {
			mapUItoTestStep(xdata);
			//createCasesTable(xdata);  //Refresh the screen.
		});


	katana.$activeTab.find("#StepDriver").on('change',function() {
		sid  = katana.$activeTab.find("#StepDriver").attr('theSid');   // 
		var oneCaseStep = jsonCaseSteps['step'][sid];
		console.log(oneCaseStep);
		//console.log("------");
		console.log(katana.$activeTab.find("#StepDriver").val());

		var driver = katana.$activeTab.find("#StepDriver").val();
		var opts = jQuery.getJSON("./cases/getListOfKeywords/?driver="+driver).done(function(data) {
 			katana.$activeTab.find("#StepKeyword").empty();
 			a_items = opts.responseJSON['keywords'];
 			console.log(opts);
 			console.log(a_items);
 			for (let x of a_items) {
 				katana.$activeTab.find("#StepKeyword").append($('<option>',{ value: x,  text: x }));
 			}
 		});
	});


	katana.$activeTab.find("#StepKeyword").on('change',function() {
		sid  = katana.$activeTab.find("#StepKeyword").attr('theSid');   // 
		var oneCaseStep = jsonCaseSteps['step'][sid];
		console.log(oneCaseStep);
		//console.log("------");
		console.log(katana.$activeTab.find("#StepKeyword").val());

		var keyword = katana.$activeTab.find("#StepKeyword").val();  // 
		var driver  = katana.$activeTab.find("#StepDriver").val();   // 
		var opts = jQuery.getJSON("./cases/getListOfComments/?driver="+driver+"&keyword="+keyword).done(function(data) {
 			a_items = opts.responseJSON['fields'];
 			console.log(opts);
 			console.log(a_items);
 			// fill in the form....
 			out_array = a_items[0]['comment'];
 			console.log(out_array);
 			var outstr = out_array.join("<br>");
 			katana.$activeTab.find("#sourceFileText").html(outstr);

 		});
	});


	// Must define handlers inside this function ... 

	$('#caseDatatype').change(function(e){	
		jsonCaseDetails['Datatype'] = this.value; 
		katana.$activeTab.find(".iteration-div").hide();
		katana.$activeTab.find("#arguments-textarea").show();

		if (this.value == 'Custom') {
			katana.$activeTab.find("#arguments-textarea").hide();
		} 
		// Iterative tag is show only for Hybird. 
		if (this.value == 'Hybrid') {
			katana.$activeTab.find(".iteration-div").show();
		}
		//mapCaseJsonToUi(jsonCaseSteps);
	});

}




function mapUiToCaseJson() {
	
	jsonCaseObject['Details']['Name'] = katana.$activeTab.find('#caseName').val();
	jsonCaseObject['Details']['Title'] = katana.$activeTab.find('#caseTitle').val();
	jsonCaseObject['Details']['Category'] = katana.$activeTab.find('#caseCategory').val();
	jsonCaseObject['Details']['State'] = katana.$activeTab.find('#caseState').val();
	jsonCaseObject['Details']['Engineer'] = katana.$activeTab.find('#caseEngineer').val();
	jsonCaseObject['Details']['Title'] = katana.$activeTab.find('#caseTitle').val();
	jsonCaseObject['Details']['Date'] = katana.$activeTab.find('#caseDate').val();
	//jsonCaseObject['Details']['Time'] = $('#suiteTime').val();
	jsonCaseObject['Details']['default_onError'] = katana.$activeTab.find('#default_onError').val();
	jsonCaseObject['Details']['Datatype'] = katana.$activeTab.find('#caseDatatype').val();
	jsonCaseObject['dataPath'] =  katana.$activeTab.find('#caseInputDataFile').val();
	jsonCaseObject['resultsDir'] =  katana.$activeTab.find('#caseResultsDir').val();
	jsonCaseObject['logsDir'] =  katana.$activeTab.find('#caseLogsDir').val();
	jsonCaseObject['expectedDir'] =  katana.$activeTab.find('#caseExpectedResults').val();
	jsonCaseObject['SaveToFile'] =  katana.$activeTab.find('#my_file_to_save').val();

	if (!jsonCaseObject['Requirements']) {
		jsonCaseObject['Requirements'] = []; 
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

	$.ajax({
    url : url,
    type: "POST",
    data : { 
    	'json': JSON.stringify(topNode),
    	
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
		if (! oneCaseStep['Arguments']) {
			oneCaseStep['Arguments'] = { 'argument': [] }
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
	katana.$activeTab.find("#listOfTestStepsForCase").html("");      // Start with clean slate
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
			var xstr =  arguments[xarg]['@name']+" = "+arguments[xarg]['@value'] + "<br>";
			//console.log(xstr);
			out_array.push(xstr); 
			ta  = ta + 1; 
			}
		outstr = out_array.join("");
		//console.log("Arguments --> "+outstr);

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

		outstr = "RMT=" + oneCaseStep['rmt'] + "<br>Context=" + oneCaseStep['context'] +
			"<br>Impact=" + oneCaseStep['impact'];
		items.push('<td>'+outstr+'</td>'); 
		var bid = "deleteTestStep-"+s+"-id-"+getRandomCaseID();
		//items.push('<td><input type="button" class="btn-danger" value="X" id="'+bid+'"/>');
		items.push('<td><i type="button" title="Delete" class="fa fa-eraser" value="X" id="'+bid+'"/>');
		
		$('#'+bid).off('click');   //unbind and bind are deprecated. 
		$(document).on('click','#'+bid,function(  ) {
			//alert(this.id);
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			removeTestStep(sid);
		});

		bid = "editTestStep-"+s+"-id-"+getRandomCaseID();
		items.push('<i type="button" title="Edit" class="fa fa-pencil" value="Edit" id="'+bid+'"/></td>');
		$('#'+bid).off('c<td>lick');   //unbind and bind are deprecated. 
		$(document).on('click','#'+bid,function(  ) {
			//alert(this.id);
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


	// Based on the options

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
	console.log("Calling mapTestStepToUI "+ sid);
	console.log("Calling mapTestStepToUI "+ xdata);
	
	katana.$activeTab.find("#StepRowToEdit").val(sid);
	oneCaseStep = xdata[sid]
	console.log(oneCaseStep);
	katana.$activeTab.find("#StepDriver").val(oneCaseStep['step'][ "@Driver"]);
	katana.$activeTab.find("#StepKeyword").val(oneCaseStep['step'][ "@Keyword"]);
	
	katana.$activeTab.find("#StepDriver").attr('theSid',sid);  // Track the object you are on. 


	katana.$activeTab.find("#StepTS").val(oneCaseStep['step'][ "@TS"]);
	katana.$activeTab.find("#StepDescription").val(oneCaseStep["Description"]);
	katana.$activeTab.find("#StepContext").val(oneCaseStep["context"]);
	katana.$activeTab.find("#SteponError-at-action").val(oneCaseStep['onError']["@action"]);
	katana.$activeTab.find("#SteponError-at-value").val(oneCaseStep['onError']["@value"]);
	katana.$activeTab.find("#runmode-at-type").val(oneCaseStep["runmode"]["@type"]);
	katana.$activeTab.find("#StepImpact").val(oneCaseStep["impact"]);
	var a_items = [] ;
	var xstr;
	var bid;
	var arguments = oneCaseStep['Arguments']['argument'];

	var ta = 0; 
	for (xarg in arguments) {
			a_items.push('<label>Name</label><input type="text" argid="caseArgName-'+ta+'" value="'+[xarg]["@name"]+'"/>');
			a_items.push('<label>Value</label><input type="text" argid="caseArgValue-'+ta+'" value="'+[xarg]["@value"]+'"/>');
			// Now a button to edit or delete ... 
			bid = "deleteCaseArg-"+sid+"-"+ta+"-id"+getRandomCaseID();;
			a_items.push('<td><i  type="button" title="Delete" class="fa fa-eraser" value="X" id="'+bid+'"/>');
			katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
			$(document).on('click','#'+bid,function( ) {
				var names = this.id.split('-');
				var sid = parseInt(names[1]);
				var aid = parseInt(names[2]);
				removeOneArgument(sid,aid,xdata);
			});
			bid = "saveCaseArg-"+sid+"-"+ta+"-id"+getRandomCaseID();;
			a_items.push('<td><i  type="button" title="Save Argument Change" class="fa fa-pencil" value="Save" id="'+bid+'"/>');
			katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
			$(document).on('click','#'+bid,function( ) {
				var names = this.id.split('-');
				var sid = parseInt(names[1]);
				var aid = parseInt(names[2]);
				saveOneArgument(sid,aid,xdata);
			});


			ta += 1
	}
	//  -------- 
	bid = "addCaseArg-"+sid+"-id"+getRandomCaseID();;
	a_items.push('<td><i type="button" title="Add Argument" class="fa fa=plus" value="Add Argument" id="'+bid+'"/>');
	katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
	$(document).on('click','#'+bid,function( ) {
				var names = this.id.split('-');
				var sid = parseInt(names[1]);
				addOneArgument(sid,xdata);
			});
	//console.log(a_items);
	katana.$activeTab.find("#arguments-textarea").html( a_items.join("\n"));


	// Load in the actions names. 
	var opts = jQuery.getJSON("./cases/getListOfActions").done(function(data) { 		 
	var a_items = data['actions'];			 
	katana.$activeTab.find("#StepDriver").empty();  // Empty all the options....
	for (var x =0; x < a_items.length; x++) {
				katana.$activeTab.find("#StepDriver").append($('<option>',{ value: a_items[x],  text: a_items[x]}));
			}
			sid  = katana.$activeTab.find("#StepDriver").attr('theSid');
			var oneCaseStep = jsonCaseSteps['step'][sid];
			katana.$activeTab.find("#StepKeyword").attr('theSid', sid);
			katana.$activeTab.find("#StepDriver").val(oneCaseStep["@Driver"]);
			console.log(data['filesinfo'])
			jsonFilesInfo = data['filesinfo'];
			var keyword = oneCaseStep["@Driver"]; 
			katana.$activeTab.find("#StepKeyword").empty();  // Empty all the options....
			var k_items = data['filesinfo'][keyword][0];
			console.log("k-items=" + k_items);
			console.log(k_items.length);
			for (var ki =0; ki < k_items.length; ki++) {
				console.log(k_items[ki]);
				var v = k_items[ki]['fn']; 
				console.log(v);
				katana.$activeTab.find("#StepKeyword").append($('<option>',{ value:v,  text: v}));
			
			}
			katana.$activeTab.find("#StepKeyword").val(oneCaseStep['step'][ "@Keyword"]);
	});
	//console.log("Returning actions");
	//console.log(opts);
	//console.log("Returned actions");

}

function saveOneArgument( sid, aid, xdata) {
	var obj = jsonCaseSteps['step'][sid]['Arguments']['argument'][aid]; 	
	obj['@name'] = katana.$activeTab.find('#caseArgName-'+aid).val();
	obj['@value'] = katana.$activeTab.find('#caseArgValue-'+aid).val();
	mapTestStepToUI(sid, xdata);
}

function addOneArgument( sid , xdata ) {
	var xx = { "@name": "" , "@value": " " };
	jsonCaseSteps['step'][sid]['Arguments']['argument'].push(xx);
	//mapCaseJsonToUi(jsonCaseSteps);
	mapTestStepToUI(sid, xdata);
}

function removeOneArgument( sid, aid, xdata ) {
	jsonCaseSteps['step'][sid]['Arguments']['argument'].splice(aid,1);	
	//mapCaseJsonToUi(jsonCaseSteps);
	mapTestStepToUI(sid, xdata);
}

// When the edit button is clicked, map step to the UI. 
function mapUItoTestStep(xdata) {
	var sid = ParseInt(katana.$activeTab.find("#StepRowToEdit").val());	

	// Validate whether sid 
	oneCaseStep = xdata[sid];
	fillStepDefaults(oneCaseStep);  // Takes care of missing values.... 
	oneCaseStep['step'][ "@Driver"] = katana.$activeTab.find("#StepDriver").val();
	oneCaseStep['step'][ "@Keyword"] = katana.$activeTab.find("#StepKeyword").val();
	oneCaseStep['step'][ "@TS"] = katana.$activeTab.find("#StepTS").val();
	oneCaseStep["Description"] =  katana.$activeTab.find("#StepDescription").val();
	oneCaseStep["context"] =  katana.$activeTab.find("#StepContext").val();
	oneCaseStep["Execute"]["@ExecType"]= katana.$activeTab.find("#Execute-at-ExecType").val();		
	oneCaseStep['onError'][ "@action"] = katana.$activeTab.find("#SteponError-at-action").val();
	oneCaseStep['onError'][ "@value"] = katana.$activeTab.find("#SteponError-at-value").val();
	oneCaseStep["runmode"] = { "@type" : katana.$activeTab.find("#runmode-at-type").val()};
	oneCaseStep["impact"] =  katana.$activeTab.find("#StepImpact").val();
	// Now draw the table again....
	/*
	var a_str = katana.$activeTab.find("#arguments-textarea").text();
	a_items = a_str.split("\n");
	oneCaseStep["Arguments"] = [];

	for (var i =0; i < a_items.length; i++) {
			if (varg.length > 2) {
			v_items = varg.split("");
			nm = varg[0];
			vl = varg[1];
			oneCaseStep["Arguments"].push({ "argument" : { "@name": nm, "@value": vl }})
		}
	}
	*/
	
}

function addStepToCase(){
	// Add an entry to the jsonTestSuites....
	var newCaseStep = {
		"step": {  "@Driver": "demo_driver", "@Keyword": "" , "@TS": "0" },
		"Arguments" : { 'Argument': ""  },
		"onError": {  "@action" : "next", "@value" : "" } ,
		"iteration_type": {   "@type" : "" } ,
		"Description":"",
		"Execute": {   "@ExecType": "Yes",
			"Rule": {   "@Condition": "","@Condvalue": "","@Else": "next", "@Elsevalue": "" }
		}, 
		"context": "positive", 
		"impact" :  "impact",
		"rmt" :  " " ,
		"retry": { "@type": "if not", "@Condition": "testsuite_1_result", "@Condvalue": "PASS", "@count": "6", "@interval": "0"}, 
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



function createRequirementsTable(i_data){
	var items =[]; 
	katana.$activeTab.find("#tableOfCaseRequirements").html("");  // This is a blank div. 
	items.push('<table id="Requirements_table_display" class="table" >');
	items.push('<thead>');
	items.push('<tr id="ReqRow"><th>Num</th><th>Requirement</th><th/><th/></tr>');
	items.push('</thead>');
	items.push('<tbody>');
	console.log("createRequirementsTable");
	console.log(i_data);
	if (i_data['Requirement']) {
			rdata= i_data['Requirement'];
			
			for (var s=0; s<Object.keys(rdata).length; s++ ) {
				var oneReq = rdata[s];
				//console.log(oneReq);
				items.push('<tr><td>'+s+'</td>');
				var bid = "textRequirement-"+s+"-id";	
				items.push('<td><input type="text" value="'+oneReq +'" id="'+bid+'"/></td>');
				
				bid = "deleteRequirement-"+s+"-id"+getRandomCaseID();
				items.push('<td><i type="button" title="Delete" class="fa fa-eraser" value="X" id="'+bid+'"/>');
				
				katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
				$(document).on('click','#'+bid,function( ) {
					var names = this.id.split('-');
					var sid = parseInt(names[1]);
					rdata.slice(sid,1); 
					createRequirementsTable(i_data);
				});
				bid = "editRequirement-"+s+"-id"+getRandomCaseID();;
				//items.push('<td><input type="button" class="btn" value="Save" id="'+bid+'"/></td>');
				items.push('<i type="button" title="Edit" class="fa fa-pencil" value="Edit" id="'+bid+'"/></td>');
				
				katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
				$(document).on('click','#'+bid,function() {
					var names = this.id.split('-');
					var sid = parseInt(names[1]);
					console.log("xdata --> "+ rdata);  // Get this value and update your json. 
					var txtIn = katana.$activeTab.find("#textRequirement-"+sid+"-id").val();
					console.log(katana.$activeTab.find("#textRequirement-"+sid+"-id").val());
					//console.log(sid);
					console.log(rdata[sid])
					rdata[sid] = txtIn;
					createRequirementsTable(i_data);	
					event.stopPropagation();
					//This is where you load in the edit form and display this row in detail. 
				});
			}
			items.push('</tbody>');
			items.push('</table>');
		}
	bid = "addRequirement-"+getRandomCaseID();
	items.push('<div><input type="button" class="btn" value="Add Requirement" id="'+bid+'"/></div>');
	katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
	$(document).on('click','#'+bid,function( event  ) {
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			console.log("Add Requirement... ");
			console.log(jsonCaseObject['Requirements']);
			if (!jsonCaseObject['Requirements']) jsonCaseObject['Requirements']= { 'Requirement' : [] }
			if (!jQuery.isArray(jsonCaseObject['Requirements']['Requirement'])) {
				jsonCaseObject['Requirements']['Requirement'] = []
			}
			rdata = jsonCaseObject['Requirements']['Requirement'];
			
			rdata.push( "" );
			console.log(jsonCaseObject);
			createRequirementsTable(jsonCaseObject['Requirements']);	
			event.stopPropagation();
		});
	
	katana.$activeTab.find("#tableOfCaseRequirements").html( items.join(""));
	katana.$activeTab.find('#Requirements_table_display tbody').sortable();
	//katana.$activeTab.find('#Case_table_display').on('click',"td",   function() { 
	//});

}
