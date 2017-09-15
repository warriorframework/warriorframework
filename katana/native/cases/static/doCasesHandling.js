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
var jsonCaseDetails = [];         // A pointer to the Details   
var jsonCaseSteps = [];           
var jsonCaseRequirements = []; 	  // This is the JSON model for the UI requirements
var activePageID = getRandomCaseID();   // for the page ID 
var jsonFilesInfo = null; 

function mapFullCaseJson(myobjectID){
	activePageID = getRandomCaseID();
	katana.$activeTab.find("#listOfTestStepsForCase").hide();
	katana.$activeTab.find('#savesubdir').hide();
	var sdata = katana.$activeTab.find("#listOfTestStepsForCase").text();
	var jdata = sdata.replace(/'/g, '"');
	jsonAllCasePages[myobjectID] = JSON.parse(sdata);               
	jsonCaseObject = jsonAllCasePages[myobjectID]
	jsonCaseSteps  = jsonCaseObject["Steps"];
	jsonCaseRequirements = jsonCaseObject['Requirements'];
	//if (!jQuery.isArray(jsonCaseRequirements)) jsonCaseObject['Requirements'] = []; 
	jsonCaseRequirements = jsonCaseObject['Requirements'];
	jsonCaseDetails = jsonCaseObject['Details'];
	katana.$activeTab.find("#editCaseStepDiv").hide();
	katana.$activeTab.find("#tableOfTestStepsForCase").removeClass();
	katana.$activeTab.find("#tableOfTestStepsForCase").addClass('col-md-12');
	katana.$activeTab.find("#tableOfTestStepsForCase").show();
	mapCaseJsonToUi(jsonCaseSteps);
	//mapRequirementsToUI(jsonCaseRequirements);
	createRequirementsTable(jsonCaseRequirements);
	/*
	katana.$activeTab.find('#saveEditCaseStep').off('click');  // unbind is deprecated - debounces the click event. 
	$(document).on('click','#saveEditCaseStep',function(  ) {
			mapUItoTestStep();
			//k//atana.$activeTab.find("#editCaseStepDiv").hide();
			//katana.$activeTab.find("#tableOfTestStepsForCase").removeClass();
			//katana.$activeTab.find("#tableOfTestStepsForCase").addClass('col-md-12');
			//katana.$activeTab.find("#tableOfTestStepsForCase").style.width='100%';
			//katana.$activeTab.find("#tableOfTestStepsForCase").show();
			mapCaseJsonToUi(jsonCaseSteps);	
		});
	katana.$activeTab.find('#editCaseStepClose').off('click');  // unbind is deprecated - debounces the click event. 
	$(document).on('click','#editCaseStepClose',function(  ) {
			katana.$activeTab.find("#editCaseStepDiv").hide();
			katana.$activeTab.find("#tableOfTestStepsForCase").removeClass();
			katana.$activeTab.find("#tableOfTestStepsForCase").addClass('col-md-12');
			katana.$activeTab.find("#tableOfTestStepsForCase").style.width='100%';
			katana.$activeTab.find("#tableOfTestStepsForCase").show();
			mapCaseJsonToUi(jsonCaseSteps);	
		});

	katana.$activeTab.find("#StepDriver").on('change',function() {
		alert("Ouch");
		sid  = katana.$activeTab.find("#StepDriver").attr('theSid');   // 
		var oneCaseStep = jsonCaseSteps['step'][sid];
		console.log(oneCaseStep);
		//console.log("------");
		console.log(katana.$activeTab.find("#StepDriver").attr('value'));

		var driver = katana.$activeTab.find("#StepDriver").attr('value');
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
		console.log(katana.$activeTab.find("#StepKeyword").attr('value'));

		var keyword = katana.$activeTab.find("#StepKeyword").attr('value');  // 
		var driver  = katana.$activeTab.find("#StepDriver").attr('value');   // 
		var opts = jQuery.getJSON("./cases/getListOfComments/?driver="+driver+"&keyword="+keyword).done(function(data) {
 			a_items = opts.responseJSON['fields'];
 			console.log(opts);
 			console.log(a_items);
 			// fill in the form....
 			out_array = a_items[0]['comment'];
 			//console.log(out_array);
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
	*/

}




function mapUiToCaseJson() {
	
	jsonCaseObject['Details']['Name'] = katana.$activeTab.find('#caseName').attr('value');
	jsonCaseObject['Details']['Title'] = katana.$activeTab.find('#caseTitle').attr('value');
	jsonCaseObject['Details']['Category'] = katana.$activeTab.find('#caseCategory').attr('value');
	jsonCaseObject['Details']['State'] = katana.$activeTab.find('#caseState').attr('value');
	jsonCaseObject['Details']['Engineer'] = katana.$activeTab.find('#caseEngineer').attr('value');
	jsonCaseObject['Details']['Title'] = katana.$activeTab.find('#caseTitle').attr('value');
	jsonCaseObject['Details']['Date'] = katana.$activeTab.find('#caseDate').attr('value');
	//jsonCaseObject['Details']['Time'] = $('#suiteTime').attr('value');
	jsonCaseObject['Details']['default_onError'] = katana.$activeTab.find('#default_onError').attr('value');
	jsonCaseObject['Details']['Datatype'] = katana.$activeTab.find('#caseDatatype').attr('value');
	jsonCaseObject['dataPath'] =  katana.$activeTab.find('#caseInputDataFile').attr('value');
	jsonCaseObject['resultsDir'] =  katana.$activeTab.find('#caseResultsDir').attr('value');
	jsonCaseObject['logsDir'] =  katana.$activeTab.find('#caseLogsDir').attr('value');
	jsonCaseObject['expectedDir'] =  katana.$activeTab.find('#caseExpectedResults').attr('value');
	jsonCaseObject['SaveToFile'] =  katana.$activeTab.find('#my_file_to_save').attr('value');

	if (!jsonCaseObject['Requirements']) {
		jsonCaseObject['Requirements'] = []; 
	}

	saveUItoRequirements();  // Save Requirements table. 
	// Now you have collected the user components...
} 


// Saves the UI to memory and sends to server. 
function writeUItoCaseJSON() {
	mapUiToCaseJson();
	var url = "./cases/getCaseDataBack";
	var csrftoken = $("[name='csrfmiddlewaretoken']").attr('value');

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
    	'filetosave': katana.$activeTab.find('#my_file_to_save').attr('value'),
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
	katana.$activeTab.find("#tableOfTestStepsForCase").html("");      // Start with clean slate
	items.push('<table class="configuration_table table-striped" id="Step_table_display"  width="100%" >');
	items.push('<thead>');
	items.push('<tr id="StepRow"><th>#</th><th>Driver</th><th>Keyword</th><th>Description</th><th>Arguments</th>\
		<th>OnError</th><th>Execute</th><th>Run Mode</th><th>Impact</th><th>Other</th></tr>');
	items.push('</thead>');
	items.push('<tbody>');
	for (var s=0; s<Object.keys(xdata).length; s++ ) {  // for s in xdata
		var oneCaseStep = xdata[s];             // for each step in case
		//console.log(oneCaseStep['path']);
		var showID = parseInt(s)+1;
		items.push('<tr data-sid="'+s+'"><td>'+showID+'</td>');        // ID 
		// -------------------------------------------------------------------------
		// Validation and default assignments 
		// Create empty elements with defaults if none found. ;-)
		// -------------------------------------------------------------------------
		fillStepDefaults(oneCaseStep);
	
		items.push('<td>'+oneCaseStep['@Driver'] +'</td>'); 
		var outstr; // = oneCaseStep['@Keyword'] + "<br>TS=" +oneCaseStep['@TS'] ;
		items.push('<td>'+oneCaseStep['@Keyword'] + "<br>TS=" +oneCaseStep['@TS']+'</td>'); 
	// Show arguments for each step in the UI div tag. 

			outstr =  oneCaseStep['Description'];
		items.push('<td>'+outstr+'</td>'); 

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
	

		outstr = "Action=" + oneCaseStep['onError']['@action'] + "<br>" +
			"Value=" + oneCaseStep['onError']['@value']+"<br>" +  
			"ExecType=" + oneCaseStep['step']['@ExecType'] + "<br>" + 
			"Condition="+oneCaseStep['step']['Rule']['@Condition']+ "<br>" + 
			"Condvalue="+oneCaseStep['step']['Rule']['@Condvalue']+ "<br>" + 
			"Else="+oneCaseStep['step']['Rule']['@Else']+ "<br>" +
			"Elsevalue="+oneCaseStep['step']['Rule']['@Elsevalue'];

		items.push('<td>'+outstr+'</td>'); 
		outstr = oneCaseStep['rmt'] + "<br>Context=" + oneCaseStep['context']; 
		items.push('<td>'+outstr+'</td>');
		items.push('<td>'+oneCaseStep['impact']+'</td>'); 
		var bid = "deleteTestStep-"+s+"-id-"+getRandomCaseID();
		//items.push('<td><input type="button" class="btn-danger" value="X" id="'+bid+'"/>');
		items.push('<td><i class="delete-item-32" title="Delete"  value="X" id="'+bid+'" />');
		
		$('#'+bid).off('click');   //unbind and bind are deprecated. 
		$(document).on('click','#'+bid,function(  ) {
			//alert(this.id);
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			removeTestStep(sid);
		});

		bid = "editTestStep-"+s+"-id-"+getRandomCaseID();
		//items.push('<i type="button" title="Edit" class="edit-32" value="Edit" id="'+bid+'"/></td>');
		items.push('<i  title="Edit" class="edit-32"  id="'+bid+'"/>');
		$('#'+bid).off('click');   //unbind and bind are deprecated. 
		$('#'+bid).attr('theSid', s);  //Set tthe name


		$(document).on('click','#'+bid,function(  ) {
			//alert(this.id);
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			//mapTestStepToUI(sid,xdata);
			//katana.$activeTab.find("#editCaseStepDiv").show();
			//katana.$activeTab.find('#tableOfTestStepsForCase').removeClass();
			//katana.$activeTab.find('#tableOfTestStepsForCase').addClass('col-md-8');
			var ooo = katana.$activeTab.find("#editCaseStepDiv").html();
			console.log("lllll Before the POPUP LLLLLLL")
			console.log(ooo);
			// Here is the code to start the HTML only - no js
			katana.popupController.open(katana.$activeTab.find("#editCaseStepDiv").html(),"Edit..." + sid, function(popup) {

				setupPopupDialog(sid,xdata,popup);
				//mapTestStepToUI(sid,xdata); // no workee. 
			});
		 	
		}); 

		bid = "addTestStepAbove-"+s+"-id-"+getRandomCaseID();
		items.push('<i  title="Insert" class="add-item-32" value="Insert" id="'+bid+'"/></td>');
		
		$('#'+bid).off('c<td>lick');   //unbind and bind are deprecated. 
		$(document).on('click','#'+bid,function(  ) {
			//alert(this.id);
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			addTestStepAboveToUI(sid,xdata);
		});
		items.push('</tr>');

	}

	items.push('</tbody>');
	items.push('</table>'); // 
	katana.$activeTab.find("#tableOfTestStepsForCase").html( items.join(""));
	katana.$activeTab.find('#Step_table_display tbody').sortable( { stop: testCaseSortEventHandler});
	
	// Based on the options
	/*
 	katana.$activeTab.find('table#Step_table_display thead tr th').each(function(index) {
    		var thisWidth = $(this).width();
    		if ( index == 0 ) { thisWidth = 40; }
    		console.log(thisWidth + "  "+ index);
    		katana.$activeTab.find('table#Step_table_display tbody tr td').each(function(xindex) {	
    				if ( index == 0 ) { 
    					$(this).css('width',thisWidth);
    				 }

    				
    		});
  	});
	*/
  	/*
	if (jsonCaseDetails['Datatype'] == 'Custom') {
		$(".arguments-div").hide();
	} else {

		$(".arguments-div").show();
	}
	*/
	//$('#fileName').html("");
	
}  // end of function 


function setupPopupDialog(sid,xdata,popup) {
	console.log(popup);  // Merely returns the div tag
	var dd_driver = popup.find('#StepDriver');
	console.log(dd_driver);
	oneCaseStep = xdata[sid]
	var driver = oneCaseStep[ "@Driver"]  // 
	var keyword  = oneCaseStep[ "@Keyword"]   // 
	var a_items = []; 
	console.log("---- oneCase ---- ");
	console.log(oneCaseStep["@Driver"]);
 	console.log(oneCaseStep);
	
	jQuery.getJSON("./cases/getListOfActions").done(function(data) {
			a_items = data['actions'];
			console.log("a_items ");
			console.log(a_items);
			dd_driver.empty();  // Empty all the options....
			for (var x =0; x < a_items.length; x++) {
					dd_driver.append($('<option>',{ value: a_items[x],  text: a_items[x]}));
				}
			console.log(dd_driver.html());
	});
	console.log(xdata);
	popup.find("#StepRowToEdit").attr("value",sid);

	popup.find("#StepDriver").attr("value",oneCaseStep[ "@Driver"]);
	popup.find("#StepKeyword").attr("value",oneCaseStep[ "@Keyword"]);
	popup.find("#StepTS").attr("value",oneCaseStep["@TS"]);
	popup.find("#StepDescription").attr("value",oneCaseStep["Description"]);
	popup.find("#StepContext").attr("value",oneCaseStep["context"]);
	popup.find("#SteponError-at-action").attr("value",oneCaseStep['onError']["@action"]);
	popup.find("#SteponError-at-value").attr("value",oneCaseStep['onError']["@value"]);
	popup.find("#runmode-at-type").attr("value",oneCaseStep["runmode"]["@type"]);
	popup.find("#StepImpact").attr("value",oneCaseStep["impact"]);
	var a_items = [] ;
	var xstr;
	var bid;
	var arguments = oneCaseStep['Arguments']['argument'];

	var ta = 0; 
	for (xarg in arguments) {
			//console.log(arguments[xarg]);
			a_items.push('<div class="row">');
			a_items.push('<label class="col-md-2">Name</label><input  type="text" argid="caseArgName-'+ta+'" value="'+arguments[xarg]["@name"]+'"/>');
			a_items.push('<label class="col-md-2">Value</label><input  type="text" argid="caseArgValue-'+ta+'" value="'+arguments[xarg]["@value"]+'"/>');
			// Now a button to edit or delete ... 
			bid = "deleteCaseArg-"+sid+"-"+ta+"-id"
			a_items.push('<td><i title="Delete" class="fa fa-erase" value="X" id="'+bid+'"/>');
			
			bid = "saveCaseArg-"+sid+"-"+ta+"-id"
			a_items.push('<td><i  title="Save Argument Change" class="fa fa-pencil" value="Save" id="'+bid+'"/>');

			bid = "insertCaseArg-"+sid+"-"+ta+"-id";
			a_items.push('<td><i  title="Insert one" class="fa fa-plus" value="Save" id="'+bid+'"/>');
			
			ta += 1
			a_items.push('</div>');
			
	}
	//  -------- 

	
	//popup.find('#'+bid).off('click'); 
	//console.log(a_items);
	popup.find("#arguments-textarea").html( a_items.join("\n"));	

	console.log(popup);
	// Now  set the callbacks once the DOM has new HTML elements in it.
	var arguments = oneCaseStep['Arguments']['argument'];

	var ta = 0; 
	for (xarg in arguments) {

			var bid = "deleteCaseArg-"+sid+"-"+ta+"-id"
			popup.find('#'+bid).on('click','#'+bid,function( ) {
				var names = this.id.split('-');
				var sid = parseInt(names[1]);
				var aid = parseInt(names[2]);
				removeOneArgument(sid,aid,xdata);
			});
			bid = "saveCaseArg-"+sid+"-"+ta+"-id"
			popup.find('#'+bid).on('click',function( ) {
				var names = this.id.split('-');
				var sid = parseInt(names[1]);
				var aid = parseInt(names[2]);
				saveOneArgument(sid,aid,xdata);
			});

			bid = "insertCaseArg-"+sid+"-"+ta+"-id";
			popup.find('#'+bid).on('click',function( ) {
				var names = this.id.split('-');
				var sid = parseInt(names[1]);
				var aid = parseInt(names[2]);
				insertOneArgument(sid,aid,xdata);
			});
			ta += 1
	}
	
	popup.find('#addOneArgument').on('click',function( ) {
				var names = this.id.split('-');
				var sid = parseInt(names[1]);
				addOneArgument(sid,xdata);
			});
	

	var opts = jQuery.getJSON("./cases/getListOfComments/?driver="+driver+"&keyword="+keyword).done(function(data) {
 			a_items = opts.responseJSON['fields'];
 			out_array = a_items[0]['comment'];
 			var outstr = out_array.join("<br>");
 			console.log(outstr);
 			popup.find("#sourceFileText").html(""); 
 			popup.find("#sourceFileText").html(outstr);

 		});

	popup.find("#StepDriver").on('change',function() {
		alert("Ouch");
		sid  = popup.find("#StepDriver").attr('theSid');   // 
		var oneCaseStep = jsonCaseSteps['step'][sid];
		console.log(oneCaseStep);
		//console.log("------");
		console.log(popup.find("#StepDriver").attr('value'));

		var driver =popup.find("#StepDriver").attr('value');
		var xopts = jQuery.getJSON("./cases/getListOfKeywords/?driver="+driver).done(function(data) {
 			popup.find("#StepKeyword").empty();
 			a_items = xopts.responseJSON['keywords'];
 			console.log(xopts);
 			console.log(a_items);
 			for (let x of a_items) {
 				popup.find("#StepKeyword").append($('<option>',{ value: x,  text: x }));
 			}
 		});
	});

	popup.find("#StepKeyword").on('change',function() {
		sid  = popup.find("#StepKeyword").attr('theSid');   // 
		var oneCaseStep = jsonCaseSteps['step'][sid];
		var keyword = popup.find("#StepKeyword").attr('value');  // 
		var driver  = popup.find("#StepDriver").attr('value');   // 
		jQuery.getJSON("./cases/getListOfComments/?driver="+driver+"&keyword="+keyword).done(function(data) {
 			a_items = opts.responseJSON['fields'];
 			out_array = a_items[0]['comment'];
 			var outstr = out_array.join("<br>");
 			console.log(outstr);
 			popup.find("#sourceFileText").html(""); 
 			popup.find("#sourceFileText").html(outstr);

 		});
	});

	popup.find('#saveEditCaseStep').on('click',function(  ) {
			mapUItoTestStep(sid,xdata,popup);	
			mapCaseJsonToUi(jsonCaseSteps);	
			katana.popupController.close();
		});

	popup.find('#editCaseStepClose').on('click',function(  ) {
			katana.popupController.close();
		});


}


var testCaseSortEventHandler = function(event, ui ) {

	var listItems = [] ; 
	var listCases = katana.$activeTab.find('#Step_table_display tbody').children(); 
	console.log(listCases);

	var oldCaseSteps = jsonCaseObject["Steps"]['step'];
	var newCaseSteps = new Array(listCases.length);
		
	for (xi=0; xi < listCases.length; xi++) {
		var xtr = listCases[xi];
		var ni  = xtr.getAttribute("data-sid");
		console.log(xi + " => " + ni);
		newCaseSteps[ni] = oldCaseSteps[xi];
	}

	jsonCaseObject["Steps"]['step'] = newCaseSteps;
	jsonCaseSteps  = jsonCaseObject["Steps"]
	mapCaseJsonToUi(jsonCaseSteps);
	
};

// Removes a test suite by its ID and refresh the page. 
function removeTestStep( sid ){
		jsonCaseSteps['step'].splice(sid,1);
		console.log("Removing test cases "+sid+" now " + Object.keys(jsonCaseSteps).length);
		mapCaseJsonToUi(jsonCaseSteps);
}

function addTestStepAboveToUI(sid,xdata) {
	var newObj = createNewStep();
	if (sid < 1) { 
		sid = 0 ;
	} else {
		sid = sid - 1;                // One below the current one. 
	}
	if (!jsonCaseSteps['step']) {
		jsonCaseSteps['step'] = [];
		}
	if (!jQuery.isArray(jsonCaseSteps['step'])) {
		jsonCaseSteps['step'] = [jsonCaseSteps['step']];
		}

	jsonCaseSteps['step'].splice(sid,0,newObj);  // Don't delete anything
	mapCaseJsonToUi(jsonCaseSteps);		
}


function mapTestStepToUI(sid, xdata) {
	// body...
	console.log("Calling mapTestStepToUI "+ sid);
	console.log(xdata);

	katana.$activeTab.find("#editCaseStepDiv").show();
	// TODO: -- ma
	//katana.$activeTab.find("#StepRowToEdit").val(sid); // attr("sid");
	katana.$activeTab.find("#StepRowToEdit").attr("value",sid);
	oneCaseStep = xdata[sid]
	console.log(oneCaseStep);
	katana.$activeTab.find("#StepDriver").attr("value",oneCaseStep[ "@Driver"]);
	katana.$activeTab.find("#StepKeyword").attr("value",oneCaseStep[ "@Keyword"]);
	console.log("LOOK~");
	console.log(oneCaseStep["@Driver"]);
	console.log(oneCaseStep["@Keyword"]);
	console.log(oneCaseStep["@TS"]);
	console.log(oneCaseStep['step']);
	console.log(oneCaseStep['step'][ "@Driver"]);
	console.log(oneCaseStep['step'][ "@Keyword"]);
	console.log(oneCaseStep['step'][ "@TS"]);
	katana.$activeTab.find("#StepTS").attr("value",oneCaseStep["@TS"]);
	katana.$activeTab.find("#StepDescription").attr("value",oneCaseStep["Description"]);
	katana.$activeTab.find("#StepContext").attr("value",oneCaseStep["context"]);
	katana.$activeTab.find("#SteponError-at-action").attr("value",oneCaseStep['onError']["@action"]);
	katana.$activeTab.find("#SteponError-at-value").attr("value",oneCaseStep['onError']["@value"]);
	katana.$activeTab.find("#runmode-at-type").attr("value",oneCaseStep["runmode"]["@type"]);
	katana.$activeTab.find("#StepImpact").attr("value",oneCaseStep["impact"]);
	var a_items = [] ;
	var xstr;
	var bid;
	var arguments = oneCaseStep['Arguments']['argument'];

	var ta = 0; 
	for (xarg in arguments) {
			//console.log(arguments[xarg]);
			a_items.push('<div class="row">');
			a_items.push('<label class="col-md-2">Name</label><input class="col-md-2" type="text" argid="caseArgName-'+ta+'" value="'+arguments[xarg]["@name"]+'"/>');
			a_items.push('<label class="col-md-2">Value</label><input class="col-md-2" type="text" argid="caseArgValue-'+ta+'" value="'+arguments[xarg]["@value"]+'"/>');
			// Now a button to edit or delete ... 
			bid = "deleteCaseArg-"+sid+"-"+ta+"-id"+getRandomCaseID();;
			a_items.push('<td><i title="Delete" class="delete-item-32" value="X" id="'+bid+'"/>');
			katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
			$(document).on('click','#'+bid,function( ) {
				var names = this.id.split('-');
				var sid = parseInt(names[1]);
				var aid = parseInt(names[2]);
				removeOneArgument(sid,aid,xdata);
			});
			bid = "saveCaseArg-"+sid+"-"+ta+"-id"+getRandomCaseID();;
			a_items.push('<td><i  title="Save Argument Change" class="edit-32" value="Save" id="'+bid+'"/>');
			katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
			$(document).on('click','#'+bid,function( ) {
				var names = this.id.split('-');
				var sid = parseInt(names[1]);
				var aid = parseInt(names[2]);
				saveOneArgument(sid,aid,xdata);
			});
			bid = "insertCaseArg-"+sid+"-"+ta+"-id"+getRandomCaseID();;
			a_items.push('<td><i  title="Insert one" class="add-item-32" value="Save" id="'+bid+'"/>');
			katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
			$(document).on('click','#'+bid,function( ) {
				var names = this.id.split('-');
				var sid = parseInt(names[1]);
				var aid = parseInt(names[2]);
				insertOneArgument(sid,aid,xdata);
			});
			ta += 1
			a_items.push('</div>');
			
	}
	//  -------- 

	bid = "addCaseArg-"+sid+"-id"+getRandomCaseID();;
	a_items.push('<td><i type="button" title="Add Argument" class="add-item-32" value="Add Argument" id="'+bid+'"/>');
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
						console.log(a_items[x]);
						katana.$activeTab.find("#StepDriver").append($('<option>',{ value: a_items[x],  text: a_items[x]}));
					}
					
			console.log(sid);
			console.log(jsonCaseSteps['step']);
			var oneCaseStep = jsonCaseSteps['step'][sid];
			console.log(oneCaseStep);
			katana.$activeTab.find("#StepDriver").attr("value",oneCaseStep["@Driver"]);
			console.log(data['filesinfo'])
			jsonFilesInfo = data['filesinfo'];
			var keyword = oneCaseStep["@Driver"]; 
			katana.$activeTab.find("#StepKeyword").empty();  // Empty all the options....
			var k_items = data['filesinfo'][keyword][0];
			console.log(k_items);
			console.log(k_items.length);
			for (var ki =0; ki < k_items.length; ki++) {
				//console.log(k_items[ki]);
				var v = k_items[ki]['fn']; 
				//console.log(v);
				katana.$activeTab.find("#StepKeyword").append($('<option>',{ value:v,  text: v}));
			
			}
			katana.$activeTab.find("#StepKeyword").attr('value',oneCaseStep[ "@Keyword"]);
	});	
}

function saveOneArgument( sid, aid, xdata) {
	var obj = jsonCaseSteps['step'][sid]['Arguments']['argument'][aid]; 	
	obj['@name'] = katana.$activeTab.find('[argid=caseArgName-'+aid+']').attr('value');
	//obj['@value'] = katana.$activeTab.find('#caseArgValue-'+aid).attr('value');
	obj['@value'] = katana.$activeTab.find('[argid=caseArgValue-'+aid+']').attr('value');
	console.log("Saving..arguments-div "+ sid + " aid = "+ aid);
	console.log(katana.$activeTab.find('[argid=caseArgValue-'+aid+']'));
	console.log(katana.$activeTab.find('[argid=caseArgValue-'+aid+']'));
	console.log(obj);
	mapTestStepToUI(sid, xdata);
}

function addOneArgument( sid , xdata ) {
	var xx = { "@name": "" , "@value": " " };
	console.log("sid =" + sid);
	console.log(xdata);
	jsonCaseSteps['step'][sid]['Arguments']['argument'].push(xx);
	//mapCaseJsonToUi(jsonCaseSteps);
	mapTestStepToUI(sid, xdata);
}


function insertOneArgument( sid , aid,  xdata ) {
	var xx = { "@name": "" , "@value": " " };
	jsonCaseSteps['step'][sid]['Arguments']['argument'].splice(aid,0,xx);
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
	var sid = parseInt(katana.$activeTab.find("#StepRowToEdit").attr('value'));	
	console.log(jsonCaseSteps);
		
	// Validate whether sid 
	var xdata = jsonCaseSteps['step'];
		
	console.log(xdata);
	oneCaseStep = xdata[sid];
	fillStepDefaults(oneCaseStep);  // Takes care of missing values.... 
	oneCaseStep["@Driver"] = katana.$activeTab.find("#StepDriver").attr('value');
	oneCaseStep["@Keyword"] = katana.$activeTab.find("#StepKeyword").attr('value');
	oneCaseStep["@TS"] = katana.$activeTab.find("#StepTS").attr('value');
	oneCaseStep["Description"] =  katana.$activeTab.find("#StepDescription").attr('value');
	oneCaseStep["context"] =  katana.$activeTab.find("#StepContext").attr('value');
	oneCaseStep["Execute"]["@ExecType"]= katana.$activeTab.find("#Execute-at-ExecType").attr('value');		
	oneCaseStep['onError'][ "@action"] = katana.$activeTab.find("#SteponError-at-action").attr('value');
	oneCaseStep['onError'][ "@value"] = katana.$activeTab.find("#SteponError-at-value").attr('value');
	oneCaseStep["runmode"] = { "@type" : katana.$activeTab.find("#runmode-at-type").attr('value')};
	oneCaseStep["impact"] =  katana.$activeTab.find("#StepImpact").attr('value');

}




function createNewStep(){
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
	 return newCaseStep;
}

function addStepToCase(){
	// Add an entry to the jsonTestSuites....
	var newCaseStep = createNewStep();
	if (!jsonCaseSteps['step']) {
		jsonCaseSteps['step'] = [];
		}
	if (!jQuery.isArray(jsonCaseSteps['step'])) {
		jsonCaseSteps['step'] = [jsonCaseSteps['step']];
		}
	jsonCaseSteps['step'].push(newCaseStep);
	mapCaseJsonToUi(jsonCaseSteps);
}

// Save UI Requirements to JSON table. 
function saveUItoRequirements( ){
	rdata= jsonCaseRequirements['Requirement'];
	rlen = Object.keys(rdata).length;
	console.log("Number of Requirements = " + rlen );
	console.log(rdata);
	for (var s=0; s<Object.keys(rdata).length; s++ ) {
				console.log("Requirements before save "+rdata[s]);
				rdata[s] = katana.$activeTab.find("#textRequirement-"+s+"-id").attr('value');
				console.log("Requirements after save "+rdata[s]);
		}

}

function createRequirementsTable(i_data){
	var items =[]; 
	katana.$activeTab.find("#tableOfCaseRequirements").html("");  // This is a blank div. 
	items.push('<table id="Requirements_table_display" class="configuration_table" >');
	items.push('<thead>');
	items.push('<tr><th>Num</th><th>Requirement</th><th/></tr>');
	items.push('</thead>');
	items.push('<tbody>');
	console.log("createRequirementsTable");
	console.log(i_data);
	if (i_data['Requirement']) {
			rdata= i_data['Requirement'];
			
			for (var s=0; s<Object.keys(rdata).length; s++ ) {
				var oneReq = rdata[s];
				var oneID = parseInt(s) + 1; 
				//console.log(oneReq);
				items.push('<tr><td>'+oneID+'</td>');
				var bid = "textRequirement-"+s+"-id";	
				items.push('<td><input type="text" value="'+oneReq +'" id="'+bid+'"/></td>');
				
				bid = "deleteRequirement-"+s+"-id"+getRandomCaseID();
				items.push('<td><i  title="Delete" class="delete-item-32" value="X" id="'+bid+'"/>');
				
				katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
				$(document).on('click','#'+bid,function( ) {
					var names = this.id.split('-');
					var sid = parseInt(names[1]);
					rdata.slice(sid,1); 
					createRequirementsTable(i_data);
				});
				bid = "editRequirement-"+s+"-id"+getRandomCaseID();;
				//items.push('<td><input type="button" class="btn" value="Save" id="'+bid+'"/></td>');
				items.push('<i  title="Edit" class="edit-32" value="Edit" id="'+bid+'"/></td>');	
				katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
				$(document).on('click','#'+bid,function() {
					var names = this.id.split('-');
					var sid = parseInt(names[1]);
					//console.log("xdata --> "+ rdata);  // Get this value and update your json. 
					var txtIn = katana.$activeTab.find("#textRequirement-"+sid+"-id").attr('value');
					console.log(katana.$activeTab.find("#textRequirement-"+sid+"-id").attr('value'));
					//console.log(sid);
					//console.log(rdata[sid])
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
	items.push('<div><input type="button" class="btn btn-success" value="Add Requirement" id="'+bid+'"/></div>');
	katana.$activeTab.find('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
	$(document).on('click','#'+bid,function( event  ) {
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			//console.log("Add Requirement... ");
			//console.log(jsonCaseObject['Requirements']);
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
	//katana.$activeTab.find('#Requirements_table_display tbody').sortable();
	//katana.$activeTab.find('#Case_table_display').on('click',"td",   function() { 
	//});

}
