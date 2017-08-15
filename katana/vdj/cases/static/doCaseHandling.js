var caseSteps = []; 

function addStepToCase() { 
	
	caseSteps.push($("input[name=newStepForCase]").val());
	showCaseSteps();
	
}

function showCaseSteps(){
	$('#listOfCaseSteps').empty();
	for (vl in caseSteps) { 
		$('#listOfCaseSteps').append('<li>' + caseSteps[vl] + '</li>');
	}
}

