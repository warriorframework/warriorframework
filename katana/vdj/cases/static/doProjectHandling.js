var testSuitesForProject = []; 

function addSuiteToProject() { 
	
	//testSuitesForProject.push($("input[name=newStepForCase]").val());

	var tso = { 
		'path': "",
		'Execute': {
			"ExecType": "Yes", 
		}, 
		"onError": {
			"action": "next",
			"value": "",
			}, 
		}, 
		"impact": "impact",
	};
	testSuitesForProject.push(tso);
	showtestSuitesForProject();
	
}

function showProjectSuites(){
	$('#listOftestSuitesForProject').empty();
	for (vl in testSuitesForProject) { 

		var xstr = "<li>"; 
		xstr += "<input>" + vl.path + "</input>";
		xstr += "<input>" + vl.impact + "</input>";
		xstr += "</li>";


		$('#listOftestSuitesForProject').append(xstr);
	}
}

