var jsonCaseSteps = []; 
var jsonCaseRequirements = []; 


function addRequirementToCase(){
	var xstr = $('#newRequirementText').val();
	if (xstr.length < 1){
		alert("Bad Requirement string");
		return;
	}
	var newReq = { 
		"Requirement" :  xstr 	};

	if (!jQuery.isArray(jsonCaseRequirements['Requirement'])) {
		jsonCaseRequirements['Requirement'] = [jsonCaseRequirements['Requirement']];
		}

	jsonCaseRequirements['Requirement'].push(newReq);
	mapRequirementsToUI(jsonCaseRequirements);	// Send in the modified array
}

function removeRequirement( sid,xdata ){
			// From an array of objects, remove the item. 
			// For some reason the xdata argument gets whacked so use the proper 
			// reference to the array instead. 
			//
			// Future: Add exception handling here for other actions when deleting 
			// one item here. 
			jsonCaseRequirements['Requirement'].splice(sid,1);
			console.log("Removing requirement "+sid+" now " + Object.keys(jsonCaseRequirements.length));
			mapRequirementsToUI(jsonCaseRequirements);	// Send in the modified array
}

function mapRequirementsToUI(data) {
	//
	// This gives me ONE object - An array of requirements 
	// Show them in an accordion along with a delete button. 
	//
	var items = [];                  // placeholder for HTML elements. 
	var xdata = data['Requirement']; // One level below the requirements ...
	if (!jQuery.isArray(xdata)) xdata = [xdata]; // Convert singleton to array.
	items.push('<div id="accordion_requirement_display" class="col-md-12">');
	//console.log("xdata =" + xdata);
	$("#listOfRequirements").html("");
	for (var s=0; s<Object.keys(xdata).length; s++ ) {
		var oneCaseStep = xdata[s];     //console.log(oneCaseStep['path']);
		items.push('<h3>Requirement'+s+"</h3>");  // Perhaps a class here?
		items.push('<div class="collapse">');     // for the accordion 
		items.push('<p> Some things here for the requirements <br>');  // TBD
		var bid = "deleteRequirement-"+s;
		items.push("<input type=\"button\" value=\"Delete\" id='"+bid+"'/>");
		$('#'+bid).off('click');
		$(document).on('click','#'+bid,function(  ) {
			var names = this.id.split('-');  // Get the ID from the object you are deleting 
			var sid = parseInt(names[1]);    // Use as reference to array
			removeRequirement(sid,xdata);    // Now remove it. 
		});
		items.push('</div>');   //  End of this widget.

	}
	items.push("</div>");  // End of Accordion widget.

	$('<div/>', { class: "col-md-12" , collapsible: "true" , html: items.join("")}).appendTo("#listOfRequirements");
	$("#accordion_requirement_display").accordion();

}


function addOneArgument( sid, arguments ) {
	var xx = { 'Requirement': { "@name": "" , "@value": " " } };
	//arguments.push(xx);
	mapCaseJsonToUi(jsonCaseSteps);

}

function removeOneArgument( sid, arguments) {

	//delete arguements[sid];
	
	mapCaseJsonToUi(jsonCaseSteps);
}

function mapCaseJsonToUi(data){
	//
	// This gives me ONE object - The root for test cases
	// The step tag is the basis for each step in the Steps data array object.
	// 
	var items = []; 
	var xdata = data['step'];
	if (!jQuery.isArray(xdata)) xdata = [xdata]; // convert singleton to array
	items.push('<div id="accordion_case_display" class="col-md-12">');
	//console.log("xdata =" + xdata);
	$("#listOfTestCasesForSuite").html("");      // Start with clean slate
	for (var s=0; s<Object.keys(xdata).length; s++ ) {  // for s in xdata
		var oneCaseStep = xdata[s];             // for each step in case
		//console.log(oneCaseStep['path']);
		items.push('<h3>TestStep '+s+"</h3>");   // Perhaps a 1 numbered array?
		items.push('<div class="collapse">');    // for the accordion
		items.push('<label class="col-md-2 text-right" for="defaultOnError>'+oneCaseStep['path']+'</label><br>');
		// -------------------------------------------------------------------------
		// Validation and default assignments 
		// Create empty elements with defaults if none found. ;-)
		// -------------------------------------------------------------------------
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

		// Now create HTML elements for the relevant items - 
		items.push('<label class="col-md-2 text-right" >Driver:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-Step-Driver" value="'+oneCaseStep['@Driver']+'" />');
		items.push('<label class="col-md-2 text-right" >Keyword:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-Step-Keyword" value="'+oneCaseStep['@Keyword']+'" />');
		items.push('<label class="col-md-2 text-right" >TS:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-Step-TS" value="'+oneCaseStep['@TS']+'" />');
		
		//
		// Arguments to be defined here. TODO 
		//
		items.push('<br><label class="col-md-2 text-right" >Arguments:</label><br>');
		bid = "addArgument-"+s;
			
		items.push('<input type="button" class="col-md-2" value="Add" id="'+bid+'"/>');
		var arguments = oneCaseStep['Arguments']['argument'];

		$('#'+bid).off('click');   //unbind and bind are deprecated. 
		$(document).on('click','#'+bid,function(  ) {
			alert(this.id);
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			addOneArgument(sid,oneCaseStep['Arguments']['argument']);
			});

		for (xarg in arguments) {
			items.push('<br>');
			items.push('<label class="col-md-1 text-right">Name</label>');
			items.push('<input type="text" class="col-md-4 text-right" value="'+arguments[xarg]['@name']+'"/>');
			items.push('<label class="col-md-1 text-right">Value</label>');
			items.push('<input type="text" class="col-md-4 text-right" value="'+arguments[xarg]['@value']+'"/>');
			bid = "deleteArgument-"+ xarg;
			items.push('<input type="button" class="col-md-2" value="Delete" id="'+bid+'"/>');

			$('#'+bid).off('click');   //unbind and bind are deprecated. 
			$(document).on('click','#'+bid,function(  ) {
			alert(this.id);
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			removeOneArgument(sid,oneCaseStep['Arguments']);
		});

		}
		items.push('<br>');
			

		//
		//
		items.push('<label class="col-md-2 text-right" >OnError-at-action:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-onError-at-action" value="'+oneCaseStep['onError']['@action']+'" />');
		items.push('<label class="col-md-2 text-right" >OnError-at-value:</label>');
		items.push('<select type="text" class="col-md-4 text-right" id="'+s+'-onError-at-value" value="'+oneCaseStep['onError']['@value']+'" >');
		items.push('<option value="next">next</option>'); 
		items.push('<option value="abort">abort</option>'); 
		items.push('<option value="abort_as_error">abort_as_error</option>'); 
		items.push('<option value="goto">goto</option>'); 
		items.push('</select>');

		items.push('<label class="col-md-2 text-right" >Description:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-Step-Description" value="'+oneCaseStep['Description']+'" />');
		items.push('<label class="col-md-2 text-right" >Iteration Type:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-onError-at-action" value="'+oneCaseStep['onError']['@action']+'" />');


		items.push('<br><span class="label label-primary">Execution</span><br>');

		items.push('<label class="col-md-2 text-right" >ExecType:</label>');
		items.push('<select type="text" class="col-md-4 text-right" id="'+s+':"Execute-ExecType" value="'+oneCaseStep['step']['@ExecType']+'" >');
		items.push('<option value="If">If</option>'); 
		items.push('<option value="If Not">If Not</option>'); 
		items.push('<option value="Yes">Yes</option>'); 
		items.push('<option value="No">No</option>'); 
		items.push('</select>'); 
		items.push('<br><span class="label label-primary">Rules</span><br>');

		items.push('<label class="col-md-2 text-right" >Rule-Condition:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-Execute-Rule-at-Condition" value="'+oneCaseStep['step']['Rule']['@Condition']+'" />');
		items.push('<label class="col-md-2 text-right" f>Rule-Condvalue:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-Execute-Rule-at-Condvalue" value="'+oneCaseStep['step']['Rule']['@Condvalue']+'" />');
		items.push('<label class="col-md-2 text-right" >Rule-Else:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-Execute-Rule-at-Else"  value="'+oneCaseStep['step']['Rule']['@Else']+'" />');
		items.push('<label class="col-md-2 text-right" >Rule-at-Elsevalue:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-Execute-Rule-at-Elsevalue"  value="'+oneCaseStep['step']['Rule']['@Elsevalue']+'" />');
		items.push('<br><span class="label label-primary">OnError</span><br>');

		items.push('<label class="col-md-2 text-right" >Context:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-context" value="'+oneCaseStep['context']+'" />');

		items.push('<label class="col-md-2 text-right" >Context:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-rmt" value="'+oneCaseStep['rmt']+'" />');

		/*
		** Keep these around for reference. 
		**

		items.push('<br><span class="label label-primary">Run mode</span><br>');
		items.push('<label class="col-md-2 text-right" >runmode-at-type:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-runmode-at-type" value="'+oneCaseStep['runmode']['@type']+'" />');
		items.push('<label class="col-md-2 text-right" >runmode-at-value:</label>');
		items.push('<select type="text" class="col-md-4 text-right" id="'+s+'-runmode-at-value" value="'+oneCaseStep['runmode']['@value']+'" >');
		items.push('<option value="RMT">RMT</option>'); 
		items.push('<option value="RUF">RUF</option>'); 
		items.push('<option value="RUP">RUP</option>'); 
		items.push('</select>');

		items.push('<br><span class="label label-primary">Retry</span><br>');
		items.push('<label class="col-md-2 text-right" >retry-at-type:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-retry-at-type" value="'+oneCaseStep['retry']['@type']+'" />');
		items.push('<label class="col-md-2 text-right" >retry-at-Condition:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-retry-at-Condition" value="'+oneCaseStep['retry']['@Condition']+'" />');
		items.push('<label class="col-md-2 text-right" >retry-at-Condvalue:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-retry-at-Condvalue" value="'+oneCaseStep['retry']['@Condvalue']+'" />');
		items.push('<label class="col-md-2 text-right" >retry-at-count:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-retry-at-count" value="'+oneCaseStep['retry']['@count']+'" />');
		items.push('<label class="col-md-2 text-right" >retry-at-interval:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-retry-at-interval" value="'+oneCaseStep['retry']['@interval']+'" />');
		items.push('<br><span class="label label-primary">Impact</span><br>');
		*/

		items.push('<label class="col-md-2 text-right" >impact</label>');
		items.push('<select type="text" id="'+s+':"impact" value="'+oneCaseStep['impact']+'" >');
		items.push('<option value="impact">impact</option>'); 
		items.push('<option value="noimpact">noimpact</option>'); 
		items.push('</select>');
		items.push("<br>");
		
		
		var bid = "deleteTestStep-"+s;
		items.push('<input type="button" value="Delete" id="'+bid+'"/>');
		$('#'+bid).off('click');   //unbind and bind are deprecated. 
		$(document).on('click','#'+bid,function(  ) {
			alert(this.id);
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			removeTestStep(sid,xdata,data);
		});
		items.push("</div>");
		

	}
	$('<div/>', { class: "col-md-12" , collapsible: "true" , html: items.join("")}).appendTo("#listOfTestCasesForSuite");
	$("#accordion_case_display").accordion();
	
}  // end of function 


// Removes a test suite by its ID and refresh the page. 
function removeTestStep( sid,xdata,jj ){
			jsonCaseSteps['step'].splice(sid,1);
			console.log("Removing test cases "+sid+" now " + Object.keys(jsonCaseSteps).length);
			mapCaseJsonToUi(jsonCaseSteps);
}


function addStepToCase(){
	// Add an entry to the jsonTestSuites....
	var newCaseStep = {
		"step": { "@Driver": "demo_driver", "@Keyword": "" , "@TS": "0" },
		"Arguments" : { },
		"onError": { "@action" : "next" } ,
		"iteration_type": { "@type" : "" } ,
		"Description":" ",
		"Execute": { "@ExecType": "Yes",
			"Rule": {"@Condition": "","@Condvalue": "","@Else": "next", "@Elsevalue": "" }
		}, 
		"context": "positive", 
		"impact" : "impact",
		"rmt" : {} ,
		"retry": {"@type": "if not", "@Condition": "testsuite_1_result", "@Condvalue": "PASS", "@count": "6", "@interval": "0"}, 
	 };
	if (!jQuery.isArray(jsonCaseSteps['step'])) {
		jsonCaseSteps['step'] = [jsonCaseSteps['step']];
		}

	jsonCaseSteps['step'].push(newCaseStep);
	mapCaseJsonToUi(jsonCaseSteps);
}
