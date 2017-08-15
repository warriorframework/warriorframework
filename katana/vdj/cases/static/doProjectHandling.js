
var jsonTestSuites=[];


function addSuiteToProject(){

	// Add an entry to the jsonTestSuites....
	var newTestSuite = {	"path": "../suites/framework_tests/seq_par_execution/seq_ts_seq_tc.xml", 
	"Execute": { "@ExecType": "Yes",
			"Rule": {"@Condition": "","@Condvalue": "","@Else": "next", "@Elsevalue": "" }
		}, "runmode": {"@type": "ruf", "@value": "2"},
		"retry": {"@type": "if not", "@Condition": "testsuite_1_result", "@Condvalue": "PASS", "@count": "6", "@interval": "0"}, 
	"onError": { "@action": "next", "@value": "" }, "impact": "impact" };

	jsonTestSuites['Testsuite'].push(newTestSuite);
	mapProjectJsonToUi(jsonTestSuites);
}

function mapProjectJsonToUi(data){
	var items = []; 
	//alert("Length"+Object.keys(data));
	// This gives me ONE object - The root for test suites
	items.push('<thead class="thead-inverse"><tr>');
	items.push('<th>path</th>');
	items.push('<th>Execute</th>');
	items.push('<th>Rule Condition</th>');
	items.push('<th>value</th>');
	items.push('<th>Else</th>');
	items.push('<th>ElseValue</th>');	
	items.push('<th>OnError</th>');
	items.push('<th>Value</th>');
	items.push('<th>impact</th>');
	items.push('<th>Action</th>');
	items.push('<th></th>');
	items.push('<th></th>');
	
	var xdata = data['Testsuite'];
	if (!jQuery.isArray(xdata)) xdata = [xdata];
	items.push('</tr></thead>');
	console.log("xdata =" + xdata);
	$("#listOfTestSuitesForProject").html("");
	for (var s=0; s<Object.keys(xdata).length; s++ ) {
		var oneSuite = xdata[s];
		console.log(oneSuite['path']);
		items.push('<tr/>');
		items.push("<td>"+oneSuite['path']+"</td>");
		if (! oneSuite['Execute']){
			oneSuite['Execute'] = { "@ExecType": "Yes", 
					"Rule": { "@Condition": "", "@Condvalue": "", "@Else": "next", "@Elsevalue": "" }
				}; 
		}
		items.push("<td>"+oneSuite['Execute']['@ExecType']+"</td>");
		if (oneSuite['Execute']['Rule']) {
			items.push("<td>"+oneSuite['Execute']['Rule']['@Condition']+"</td>");
			items.push("<td>"+oneSuite['Execute']['Rule']['@Condvalue']+"</td>");
			items.push("<td>"+oneSuite['Execute']['Rule']['@Else']+"</td>");
			items.push("<td>"+oneSuite['Execute']['Rule']['@Elsevalue']+"</td>");
		} else { 
			items.push("<td>undefined</td>");
			items.push("<td>undefined</td>");
			items.push("<td>undefined</td>");
			items.push("<td>undefined</td>");
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


		items.push("<td>"+oneSuite['onError']['@action']+"</td>");
		items.push("<td>"+oneSuite['onError']['@value']+"</td>");
		items.push("<td>"+oneSuite['runmode']['@type']+"</td>");
		items.push("<td>"+oneSuite['runmode']['@value']+"</td>");

		items.push("<td>"+oneSuite['retry']['@type']+"</td>");
		items.push("<td>"+oneSuite['retry']['@Condition']+"</td>");
		items.push("<td>"+oneSuite['retry']['@Condvalue']+"</td>");
		items.push("<td>"+oneSuite['retry']['@count']+"</td>");
		items.push("<td>"+oneSuite['retry']['@interval']+"</td>");

		items.push("<td>"+oneSuite['impact']+"</td>");
		items.push("<td><input type=\"button\" value=\"Delete\"/></td>");

	}
	$('<table />', { class: "table table-sm table-hover" , html: items.join("")}).appendTo("#listOfTestSuitesForProject");
}  // end of function 



