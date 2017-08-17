
var jsonTestSuites=[];


function addSuiteToProject(){

	// Add an entry to the jsonTestSuites....
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

function mapProjectJsonToUi(data){
	var items = []; 
	//alert("Length"+Object.keys(data));
	// This gives me ONE object - The root for test suites
	
	var xdata = data['Testsuite'];
	if (!jQuery.isArray(xdata)) xdata = [xdata];
	items.push('<div id="accordion_display" class="col-md-12">');
	console.log("xdata =" + xdata);
	$("#listOfTestSuitesForProject").html("");
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


		items.push('<label class="col-md-2 text-right" >ExecType:</label>');
		items.push('<select type="text" class="col-md-4 text-right" id="'+s+':"Execute-ExecType" value="'+oneSuite['Execute']['@ExecType']+'" >');
		items.push('<option value="If">If</option>'); 
		items.push('<option value="If Not">If Not</option>'); 
		items.push('<option value="Yes">Yes</option>'); 
		items.push('<option value="No">No</option>'); 
		items.push('</select>'); 
		items.push('<br><span class="label label-primary">Rules</span><br>');



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
		items.push('<br><span class="label label-primary">Impact</span><br>');

		items.push('<label class="col-md-2 text-right" >impact</label>');
		items.push('<select type="text" id="'+s+':"impact" value="'+oneSuite['impact']+'" >');
		items.push('<option value="impact">impact</option>'); 
		items.push('<option value="noimpact">noimpact</option>'); 
		items.push('</select>');
		items.push("<br>");
		var bid = "deleteTestSuite-"+s;
		items.push("<input type=\"button\" value=\"Delete\" id='"+bid+"'>"+bid+"/>");
		$('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
		$(document).on('click','#'+bid,function(  ) {
			//alert(this.id);
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			removeTestSuite(sid,xdata);
		});
		items.push("</div>");
	}
	$('<div/>', { class: "col-md-12" , collapsible: "true" , html: items.join("")}).appendTo("#listOfTestSuitesForProject");
	$("#accordion_display").accordion();
}  // end of function 

// Removes a test suite by its ID and refresh the page. 
function removeTestSuite( sid,xdata ){
			jsonTestSuites['Testsuite'].splice(sid,1);
			console.log("Removing test suites "+sid+" now " + Object.keys(jsonTestSuites).length);
			mapProjectJsonToUi(jsonTestSuites);	// Send in the modified array
}


function openAllSuites() {
	// This function does not work at the moment. I have to debug it later. 
	// Kamran
	$('.collapse').collapse('show');
	$("#accordion_display").collapse('show');
}



