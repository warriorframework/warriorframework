var requirements = []; 

function addRequirement() { 
	
	//alert($("input[name=newRequirement]").val()); 
	requirements.push($("input[name=newRequirement]").val())
	showRequirements();

	alert(requirements)
	
}

function showRequirements(){
	$('#listOfRequirements').empty();
	for (vl in requirements) { 
		$('#listOfRequirements').append('<li>' + requirements[vl] + '</li>');
	}
}

