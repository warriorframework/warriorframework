var jsonCaseSteps = []; 


function addStepToCase(){

	// Add an entry to the jsonTestSuites....
	var newStep = {
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

	jsonCaseSteps['Testsuite'].push(newCaseStep);
	mapProjectJsonToUi(jsonTCaseSteps);
}

function mapCaseJsonToUi(data){
	var items = []; 
	//alert("Length"+Object.keys(data));
	// This gives me ONE object - The root for test suites
	
	var xdata = data['step'];
	if (!jQuery.isArray(xdata)) xdata = [xdata];
	items.push('<div id="accordion_case_display" class="col-md-12">');
	console.log("xdata =" + xdata);
	$("#listOfTestCasesForSuite").html("");
	for (var s=0; s<Object.keys(xdata).length; s++ ) {
		var oneCaseStep = xdata[s];
		console.log(oneCaseStep['path']);
		items.push('<h3>TestStep'+s+"</h3>");
		items.push('<div class="collapse">');

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

		items.push('<label class="col-md-2 text-right" >Driver:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-Step-Driver" value="'+oneCaseStep['@Driver']+'" />');
		items.push('<label class="col-md-2 text-right" >Keyword:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-Step-Keyword" value="'+oneCaseStep['@Keyword']+'" />');
		items.push('<label class="col-md-2 text-right" >TS:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-Step-TS" value="'+oneCaseStep['@TS']+'" />');
		
		// Arguments to be defined here. TODO 


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
		
		items.push("<input type=\"button\" value=\"Delete\"/>");

		items.push("</div>");
		

	}
	$('<div/>', { class: "col-md-12" , collapsible: "true" , html: items.join("")}).appendTo("#listOfTestCasesForSuite");
	$("#accordion_case_display").accordion();
	
}  // end of function 
