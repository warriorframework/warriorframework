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

// Belongs in main.js when ok. 
// Converts an absolute path to one that is relative to pathToBase 
//
function absToPrefix(pathToBase, pathToFile) {
	var stack = []; 
    var upem  = [];
    var bf = pathToBase.split('/');
	var rf = pathToFile.split('/');
	var nrf = pathToFile.split('/');
	
	for (var i=0;i< rf.length; i++) {
		if (rf[i] == "..")  { 
			stack.pop();
			nrf = nrf.splice(0,1);
		} else {
			break;
		}
	}
	return stack.join('/') + '/' + nrf.join('/');
}
// Belongs in main.js when ok. 
// Converts a path that is relative to pathToBase into an absolute path with .. constructs. 
//
function prefixFromAbs(pathToBase, pathToFile) {
	var stack = []; 
    var upem  = [];
	var bf = pathToBase.split('/');
	var rf = pathToFile.split('/');
	for (var i=0;i< rf.length; i++) {
		if (rf[i] == bf[i]) { 
			stack.push(bf[i]);
		} else {
			break;
		}
	}
	var tlen = rf.length - stack.length; 
    var blen = stack.length;
	for (var k=0;k < tlen-1; k++) {
		upem.push("..");
	}
	return upem.join("/") + "/" + bf.splice(blen).join('/') + "/" +  rf[rf.length - 1];
}

function jsUcfirst(string) 
{
    //return string.charAt(0).toUpperCase() + string.slice(1);
    return string.toLowerCase();
}

var caseApp = {
	 lastPopup: null,
	 jsonCaseObject : [],
	 jsonCaseDetails : [],        		// A pointer to the Details   
	 jsonCaseSteps : [],          		// A pointer to the Steps object

	init: function () {

		console.log("Autoinit called for case app", this);

	},
//
// This function is called when the page loads in cases.js . 
//
	mapFullCaseJson: function(myobjectID, where){
	var myfile = katana.$activeTab.find('#xmlfilename').text();
	jQuery.getJSON("./cases/getJSONcaseDataBack/?fname="+myfile).done(function(data) {
			a_items = data['fulljson'];
			console.log("from views.py call=", a_items);
			});
	var sdata = katana.$activeTab.find(where).text();  // Get JSON data from server. 
	var jdata = sdata.replace(/'/g, '"');              // Fix any discrepancies in quotes 
	//caseApp.jsonAllCasePages[myobjectID] = JSON.parse(sdata);  // Keep unique JSON for this page. 
	console.log("Incoming data", myobjectID, jdata);  
	caseApp.jsonCaseObject = JSON.parse(sdata); 
	if (!jQuery.isArray(caseApp.jsonCaseObject["Steps"]['step'])) {
		caseApp.jsonCaseObject["Steps"]['step'] = [ caseApp.jsonCaseObject["Steps"]['step']];
	}
	caseApp.jsonCaseSteps  = caseApp.jsonCaseObject["Steps"];
	console.log("Steps --> ", caseApp.jsonCaseSteps);

	caseApp.jsonCaseDetails = caseApp.jsonCaseObject['Details'];
	katana.$activeTab.find("#editCaseStepDiv").hide();
	katana.$activeTab.find("#tableOfTestStepsForCase").removeClass();
	katana.$activeTab.find("#tableOfTestStepsForCase").addClass('col-md-12');
	katana.$activeTab.find("#tableOfTestStepsForCase").show();
	console.log("Here", caseApp.jsonCaseObject, caseApp.jsonCaseSteps);


	// fix null arguments: 
	for (vs in caseApp.jsonCaseSteps['step']) {
		var oneCaseStep = caseApp.jsonCaseSteps['step'][vs];
		console.log("Arguments", oneCaseStep, vs, caseApp.jsonCaseSteps['step']);
		if (!oneCaseStep['Arguments']) {
			oneCaseStep['Arguments'] = { 'argument': [] }; 
		}
		if (!oneCaseStep['Arguments']['argument']) {
			oneCaseStep['Arguments']['argument'] = []; 
		}
		var arguments = oneCaseStep['Arguments']['argument'];
		for (xarg in arguments) {
			if (!arguments[xarg]) {
				oneCaseStep['Arguments']['argument'][xarg] = { '@name': "", '@value': '' };
			}
		}
	}

	caseApp.mapCaseJsonToUi(caseApp.jsonCaseSteps);
	console.log("Here 2", caseApp.jsonCaseObject, caseApp.jsonCaseSteps);

	caseApp.createRequirementsTable();

	//$('#myform :checkbox').change(function()
	katana.$activeTab.find('#ck_dataPath').change(function() {
		if (this.checked) {
			katana.$activeTab.find('.case-results-dir').hide();
		} else {
			katana.$activeTab.find('.case-results-dir').show();
		}


  
	});

	caseApp.fillCaseDefaultGoto();

},




	mapUiToCaseJson: function() {

	if ( katana.$activeTab.find('#caseName').attr('value').length < 1) {
		alert("Please specific a case name ");
		return;
	}

	if ( katana.$activeTab.find('#caseTitle').attr('value').length < 1) {
		alert("Please specific a Title ");
		return;
	}
	if ( katana.$activeTab.find('#caseEngineer').attr('value').length < 1) {
		alert("Please specific an Engineer name ");
		return;
	}

	caseApp.jsonCaseObject['Details']['Name'] = katana.$activeTab.find('#caseName').attr('value');
	caseApp.jsonCaseObject['Details']['Title'] = katana.$activeTab.find('#caseTitle').attr('value');
	caseApp.jsonCaseObject['Details']['Category'] = katana.$activeTab.find('#caseCategory').attr('value');
	caseApp.jsonCaseObject['Details']['State'] = katana.$activeTab.find('#caseState').attr('value');
	caseApp.jsonCaseObject['Details']['Engineer'] = katana.$activeTab.find('#caseEngineer').attr('value');
	caseApp.jsonCaseObject['Details']['Title'] = katana.$activeTab.find('#caseTitle').attr('value');
	caseApp.jsonCaseObject['Details']['Date'] = katana.$activeTab.find('#caseDate').attr('value');
	caseApp.jsonCaseObject['Details']['default_onError'] = katana.$activeTab.find('#default_onError').attr('value');
	caseApp.jsonCaseObject['Details']['Datatype'] = katana.$activeTab.find('#caseDatatype').attr('value');
	caseApp.jsonCaseObject['dataPath'] =  katana.$activeTab.find('#caseInputDataFile').attr('value');
	caseApp.jsonCaseObject['resultsDir'] =  katana.$activeTab.find('#caseResultsDir').attr('value');
	caseApp.jsonCaseObject['logsDir'] =  katana.$activeTab.find('#caseLogsDir').attr('value');
	caseApp.jsonCaseObject['expectedDir'] =  katana.$activeTab.find('#caseExpectedResults').attr('value');
	caseApp.jsonCaseObject['SaveToFile'] =  katana.$activeTab.find('#my_file_to_save').attr('value');

	if (!caseApp.jsonCaseObject['Requirements']) {
		caseApp.jsonCaseObject['Requirements'] = []; 
	}
 
	// Now you have collected the user components...
	} ,

// Start the WDF editor. 
	start_wdfEditor: function() { 
	var tag = '#caseInputDataFile';
	var filename = katana.$activeTab.find(tag).attr("fullpath");
	dd = { 'path' : filename}; 
	katana.templateAPI.postTabRequest("WDF", "/katana/wdf/index", dd);
	},



// Get Results directory from the case on the main page.
	getResultsDirForCase: function () {
		var tag = '#StepInputDataFile';
    		var callback_on_accept = function(selectedValue) { 
      		console.log(selectedValue);
      		// Convert to relative path.
      		var savefilepath = katana.$activeTab.find('#savefilepath').text();
      		console.log("File path ==", savefilepath);
      		//var nf = katana.fileExplorerAPI.prefixFromAbs(pathToBase, selectedValue);
      		var nf = prefixFromAbs(savefilepath, selectedValue);
      		katana.$activeTab.find(tag).attr("value", nf);
      		katana.$activeTab.find(tag).attr("fullpath", selectedValue);

            };
      var callback_on_dismiss =  function(){ 
      		console.log("Dismissed");
	 };
     katana.fileExplorerAPI.openFileExplorer("Select a file", false , $("[name='csrfmiddlewaretoken']").val(), false, callback_on_accept, callback_on_dismiss);
},


// Get Results directory from the case on a popup dialog
// The dialog is shown BELOW the popup. BUG. 
	getResultsDirForCaseStep: function() {
	  var tag = "#StepInputDataFile";
      var callback_on_accept = function(selectedValue) { 
      		console.log(selectedValue);
      		var popup = katana.$activeTab.find("#editCaseStepDiv").attr('popup-id');

      		// Convert to relative path.
      		var pathToBase = katana.$activeTab.find('#savefilepath').text();
      		console.log("File path ==", pathToBase);
      		// var nf = katana.fileExplorerAPI.prefixFromAbs(pathToBase, selectedValue);
      		var nf = prefixFromAbs(pathToBase, selectedValue);
      		
      		popup.find(tag).attr("value", nf);
      		popup.find(tag).attr("fullpath", selectedValue);

            };
      var callback_on_dismiss =  function(){ 
      		console.log("Dismissed");
	 };
	 //var popup = katana.$activeTab.find("#editCaseStepDiv").attr('popup-id');
     katana.fileExplorerAPI.openFileExplorer("Select a file", false , $("[name='csrfmiddlewaretoken']").val(), false, callback_on_accept, callback_on_dismiss);
},

				
// Fills in the drop down based on the number of steps you have 
// in the case. 

	 fillCaseDefaultGoto: function() {
	var gotoStep = katana.$activeTab.find('#default_onError').val();
	console.log("Step ", gotoStep);
	var defgoto = katana.$activeTab.find('#default_onError_goto'); 
		defgoto.hide();

	if (gotoStep.trim() == 'goto'.trim()) { 
		defgoto.show();
	} else {
		defgoto.hide();
		
	}

	defgoto.empty(); 
	var xdata = caseApp.jsonCaseObject["Steps"]['step']; // ['Testcase']; 
	console.log("Step....",Object.keys(xdata).length, xdata);
	for (var s=0; s<Object.keys(xdata).length; s++ ) {
		defgoto.append($('<option>',{ value: s,  text: s+1}));
	}
},

// Saves the UI to memory and sends to server as a POST request
	sendCaseToServer: function () {
	caseApp.mapUiToCaseJson();
	var url = "./cases/getCaseDataBack";
	var csrftoken = $("[name='csrfmiddlewaretoken']").attr('value');

	$.ajaxSetup({
			function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
    	}
	});

	var topNode  = { 'Testcase' : caseApp.jsonCaseObject};

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
},

// Case steps that are incomplete in an XML file can cause havoc on the UI. 
// Fill in defaults for missing fields. 
	fillStepDefaults: function(oneCaseStep) {

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
		if (! oneCaseStep['InputDataFile']) {
			oneCaseStep['InputDataFile'] = "";
		}

},

/*
Maps the data from a Testcase object to the UI. 
The UI currently uses jQuery and Bootstrap to display the data.
*/
 mapCaseJsonToUi: function(data){
	//
	// This gives me ONE object - The root for test cases
	// The step tag is the basis for each step in the Steps data array object.
	// 
	var items = []; 
	var xdata = data['step'];
	if (!jQuery.isArray(xdata)) xdata = [xdata]; // convert singleton to array


	//console.log("xdata =" + xdata);
	katana.$activeTab.find("#tableOfTestStepsForCase").html("");      // Start with clean slate
	items.push('<table class="case-configuration-table table-striped" id="Step_table_display"  width="100%" >');
	items.push('<thead>');
	items.push('<tr id="StepRow"><th>#</th><th>Driver</th><th>Keyword</th><th>Description</th><th>Arguments</th>\
		<th>OnError</th><th>Execute</th><th>Run Mode</th><th>Context</th><th>Impact</th><th>Other</th></tr>');
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
		caseApp.fillStepDefaults(oneCaseStep);
		items.push('<td>'+oneCaseStep['@Driver'] +'</td>'); 
		var outstr; 
		items.push('<td>'+oneCaseStep['@Keyword'] + "<br>TS=" +oneCaseStep['@TS']+'</td>'); 
		outstr =  oneCaseStep['Description'];
		items.push('<td>'+outstr+'</td>'); 

		var arguments = oneCaseStep['Arguments']['argument'];
		var out_array = [] 
		var ta = 0; 
		for (xarg in arguments) {

			if (!arguments[xarg]) {
				continue;
			}
			var argvalue = arguments[xarg]['@value'];
			console.log("argvalue", argvalue);
				if (argvalue) {
				if (argvalue.length > 1) {
					var xstr =  arguments[xarg]['@name']+" = "+arguments[xarg]['@value'] + "<br>";
					//console.log(xstr);
					out_array.push(xstr); 
					}
				ta  = ta + 1; 
				}
			}
		outstr = out_array.join("");
		//console.log("Arguments --> "+outstr);
		items.push('<td>'+outstr+'</td>'); 
		outstr = oneCaseStep['onError']['@action'] 
			//"Value=" + oneCaseStep['onError']['@value']+"<br>"; 
		items.push('<td>'+oneCaseStep['onError']['@action'] +'</td>'); 
		oneCaseStep['Execute']['@ExecType'] = jsUcfirst( oneCaseStep['Execute']['@ExecType']);
		outstr = "ExecType=" + oneCaseStep['Execute']['@ExecType'] + "<br>";
		if (oneCaseStep['Execute']['@ExecType'] == 'If' || oneCaseStep['Execute']['@ExecType'] == 'If Not') {
			outstr = outstr + "Condition="+oneCaseStep['Execute']['Rule']['@Condition']+ "<br>" + 
			"Condvalue="+oneCaseStep['Execute']['Rule']['@Condvalue']+ "<br>" + 
			"Else="+oneCaseStep['Execute']['Rule']['@Else']+ "<br>" +
			"Elsevalue="+oneCaseStep['Execute']['Rule']['@Elsevalue'];
		}
		 
			
		items.push('<td>'+outstr+'</td>'); 
		items.push('<td>'+oneCaseStep['runmode']['@type']+'</td>');
		items.push('<td>'+oneCaseStep['context']+'</td>');
		items.push('<td>'+oneCaseStep['impact']+'</td>'); 
		var bid = "deleteTestStep-"+s+"-id-"
		items.push('<td><i title="Delete" class="fa fa-trash" theSid="'+s+'" id="'+bid+'" katana-click="caseApp.deleteCaseFromLine()" key="'+bid+'"/>');

		bid = "editTestStep-"+s+"-id-";
		items.push('<i title="Edit" class="fa fa-pencil" theSid="'+s+'"  id="'+bid+'" katana-click="caseApp.editCaseFromLine()" key="'+bid+'"/>');

		bid = "addTestStepAbove-"+s+"-id-";
		items.push('<i title="Insert" class="fa fa-plus" theSid="'+s+'"   id="'+bid+'" katana-click="caseApp.addCaseFromLine()" key="'+bid+'"/>');

		bid = "dupTestStepAbove-"+s+"-id-";
		items.push('<i title="Duplicate" class="fa fa-copy" theSid="'+s+'"  id="'+bid+'" katana-click="caseApp.duplicateCaseFromLine()" key="'+bid+'"/>');

	}

	items.push('</tbody>');
	items.push('</table>'); // 
	katana.$activeTab.find("#tableOfTestStepsForCase").html( items.join(""));
	katana.$activeTab.find('#Step_table_display tbody').sortable( { stop: caseApp.testCaseSortEventHandler});
	
	caseApp.fillCaseDefaultGoto();
	katana.$activeTab.find('#default_onError').on('change',caseApp.fillCaseDefaultGoto );

	/*
	if (caseApp.jsonCaseDetails['Datatype'] == 'Custom') {
		$(".arguments-div").hide();
	} else {

		$(".arguments-div").show();
	}
	*/
	
	}, // end of function 

	deleteCaseFromLine : function() {
	var names = this.attr('key').split('-');
	var sid = parseInt(names[1]);
	caseApp.removeTestStep(sid);
	},

	editCaseFromLine: function() { 
	var names = this.attr('key').split('-');
	var sid = parseInt(names[1]);
	katana.popupController.open(katana.$activeTab.find("#editCaseStepDiv").html(),"Edit..." + sid, function(popup) {
		katana.$activeTab.find("#editCaseStepDiv").attr('popup-id',popup);
		caseApp.setupPopupDialog(sid,caseApp.jsonCaseSteps['step'] ,popup);
	});
	},	

	addCaseFromLine: function() {
	var names = this.attr('key').split('-');
	var sid = parseInt(names[1]);
	caseApp.addTestStepAboveToUI(sid,caseApp.jsonCaseSteps['step'],0);
	},

	duplicateCaseFromLine :function() { 
		var names = this.attr('key').split('-');
		var sid = parseInt(names[1]);
		caseApp.addTestStepAboveToUI(sid,caseApp.jsonCaseSteps['step'],1);
	},

	makePopupArguments: function(popup,  oneCaseStep) {
		caseApp.lastPopup = popup; 
		var a_items = [] ;
		var xstr;
		var bid;
		var arguments = oneCaseStep['Arguments']['argument'];
		var ta = 0; 
		var sid = parseInt(popup.find("#StepRowToEdit").attr('value'));	
		
		for (xarg in arguments) {
				//console.log(arguments[xarg]);
			a_items.push('<div class="row">');
			a_items.push('<label class="col-md-2">Name</label><input  type="text" argid="caseArgName-'+ta+'" value="'+arguments[xarg]["@name"]+'"/>');
			a_items.push('<label class="col-md-2">Value</label><input  type="text" argid="caseArgValue-'+ta+'" value="'+arguments[xarg]["@value"]+'"/>');
			// Now a button to edit or delete ... 
			bid = "deleteCaseArg-"+sid+"-"+ta+"-id"
			a_items.push('<td><i title="Delete" class="fa fa-eraser" value="X" id="'+bid+'" key="'+bid+'"  katana-click="caseApp.deletePopupArgument"/>');
			
			bid = "saveCaseArg-"+sid+"-"+ta+"-id"
			a_items.push('<td><i  title="Save Argument Change" class="fa fa-pencil" value="Save" id="'+bid+'" key="'+bid+'"  katana-click="caseApp.savePopupArgument"/>');

			bid = "insertCaseArg-"+sid+"-"+ta+"-id";
			a_items.push('<td><i  title="Insert one" class="fa fa-plus" value="Save" id="'+bid+'" key="'+bid+'" katana-click="caseApp.insertPopupArgument"/>');
			
			ta += 1
			a_items.push('</div>');
			
		}
		popup.find("#arguments-textarea").html( a_items.join("\n"));	
		if (!jQuery.isArray(caseApp.jsonCaseSteps['step'])) {
			caseApp.jsonCaseSteps['step'] = [caseApp.jsonCaseSteps['step']];
			}
		caseApp.fillCaseStepDefaultGoto(popup);
			popup.find('#SteponError-at-action').on('change', function(){ 
				var popup = $(this).closest('.popup');
				fillCaseStepDefaultGoto(popup);
		});

	},


// Fill in default GoTo steps for a popup window for a case step. 
	fillCaseStepDefaultGoto : function(popupx) {
	var popup = $(this).closest('.popup');
	var gotoStep =popup.find('#SteponError-at-action').val();
	console.log("Step ", gotoStep, popup.find('#SteponError-at-action'));
	var defgoto = popup.find('#SteponError-at-value'); 
	defgoto.hide();

		// if (gotoStep.trim() == 'goto'()) { 
		// 	defgoto.show();
		// } else {
		// 	defgoto.hide();
			
		// }


		//var sid = popup.find('#CaseRowToEdit').val();
		defgoto.empty(); 
		var xdata = caseApp.jsonCaseObject["Steps"]['step']; // ['Testcase']; 
		console.log("Step....",Object.keys(xdata).length, xdata);
		for (var s=0; s<Object.keys(xdata).length; s++ ) {
			defgoto.append($('<option>',{ value: s,  text: s+1}));
		}
	},


// Show a popup dialog with items from a case.
	setupPopupDialog: function (sid,xdata,popup) {
		console.log(popup);  // Merely returns the div tag
		var dd_driver = popup.find('#StepDriver');
		oneCaseStep = xdata[sid]
		var driver = oneCaseStep[ "@Driver"]  // 
		var keyword  = oneCaseStep[ "@Keyword"]   // 
		var a_items = []; 
		console.log("---- oneCase ---- ", oneCaseStep["@Driver"], oneCaseStep[ "@Keyword"] , oneCaseStep);
		popup.attr("caseStep", oneCaseStep);
		popup.attr("sid", sid);
		jQuery.getJSON("./cases/getListOfActions").done(function(data) {
				a_items = data['actions'];
				dd_driver.empty();  // Empty all the options....
				for (var x =0; x < a_items.length; x++) {
						dd_driver.append($('<option>',{ value: a_items[x],  text: a_items[x]}));
					}
				//console.log(dd_driver.html());
				popup.find('#StepDriver').val(oneCaseStep["@Driver"]);
				popup.find("#StepKeyword").val(oneCaseStep["@Keyword"]);
				// Now set up the keywords
				var driver = oneCaseStep[ "@Driver"]  ;
				var keyword  = oneCaseStep[ "@Keyword"];
				console.log("Collecting ...", driver, keyword);

				jQuery.getJSON("./cases/getListOfKeywords/?driver="+driver).done(function(data) {
 						popup.find("#StepKeyword").empty();
 						a_items = data['keywords'];
 						console.log(a_items);
 						for (let x of a_items) {
 							popup.find("#StepKeyword").append($('<option>',{ value: x,  text: x }));
 						}
 					popup.find('#StepKeyword').val(oneCaseStep["@Keyword"]);
				
					jQuery.getJSON("./cases/getListOfComments/?driver="+driver+"&keyword="+keyword).done(function(data) {
	 					a_items = data['fields'];
		 				console.log("received", data, a_items);

		 				out_array = a_items[0]['comment'];
		 				var outstr = out_array.join("<br>");
		 				console.log(outstr);

		 				caseApp.lastPopup.find("#sourceCaseFileText").html(""); 
		 				caseApp.lastPopup.find("#sourceCaseFileText").html(outstr);

					});
			});
		});
		//console.log(xdata);
		console.log(oneCaseStep);
		popup.find("#StepRowToEdit").attr("value",sid);

		//popup.find("#StepDriver").attr("value",oneCaseStep[ "@Driver"]);
		popup.find("#StepDriver").val(oneCaseStep[ "@Driver"]);
		console.log(popup.find("#StepDriver").val());
		//popup.find("#StepKeyword").attr("value",oneCaseStep[ "@Keyword"]);
		popup.find("#StepKeyword").val(oneCaseStep[ "@Keyword"]);

		
		//alert("Keyword = "+keyword+" driver = "+ driver + " values = "+ popup.find("#StepDriver").val(oneCaseStep[ "@Driver"]));
		popup.find("#StepTS").attr("value",oneCaseStep["@TS"]);
		popup.find("#StepDescription").attr("value",oneCaseStep["Description"]);
		popup.find("#StepContext").attr("value",oneCaseStep["context"]);
		popup.find("#SteponError-at-action").attr("value",oneCaseStep['onError']["@action"]);
		popup.find("#SteponError-at-value").attr("value",oneCaseStep['onError']["@value"]);
		popup.find("#runmode-at-type").attr("type",oneCaseStep["runmode"]["@type"]);
		popup.find("#runmode-at-value").attr("value",oneCaseStep["runmode"]["@value"]);
		popup.find("#StepImpact").attr("value",oneCaseStep["impact"]);
		popup.find("#StepInputDataFile").attr("value",oneCaseStep["InputDataFile"]);
		popup.find('.rule-condition').hide();
		if (oneCaseStep["Execute"]['@ExecType']) {
			console.log("FOUND EXECT TYPE ",oneCaseStep["Execute"]['@ExecType'] )
			if (oneCaseStep["Execute"]['@ExecType'] == 'If' || oneCaseStep["Execute"]['@ExecType'] == 'If Not') {
				popup.find('.rule-condition').show();
			}
			
		}
		if (oneCaseStep["Execute"]['Rule']) {
			popup.find('#executeRuleAtCondition').attr('value',oneCaseStep["Execute"]['Rule']['@Condition']);
			popup.find('#executeRuleAtCondvalue').attr('value',oneCaseStep["Execute"]['Rule']['@Condvalue']);
			popup.find('#executeRuleAtElse').attr('value',oneCaseStep["Execute"]['Rule']['@Else']);
			popup.find('#executeRuleAtElsevalue').attr('value',oneCaseStep["Execute"]['Rule']['@Elsevalue']);
		}
	//katana.popupController.updateActiveWindow(popup);

	caseApp.makePopupArguments(popup, oneCaseStep);

	// Now  set the callbacks once the DOM has new HTML elements in it
	
	// Fill in the value based on keyword and action 
	var opts = jQuery.getJSON("./cases/getListOfComments/?driver="+driver+"&keyword="+keyword).done(function(data) {
 			a_items = data['fields'];
 			console.log(data, a_items);
 			out_array = a_items[0]['comment'];
 			var outstr = out_array.join("<br>");
 			console.log(outstr);
 			popup.find("#sourceCaseFileText").html(""); 
 			popup.find("#sourceCaseFileText").html(outstr);
 		});
	
	popup.find("#StepDriver").on('change',function() {
		sid  = popup.find("#StepDriver").attr('theSid');   // 
		var oneCaseStep = caseApp.jsonCaseSteps['step'][sid];
		console.log(oneCaseStep);
		//console.log("------");
		console.log(popup.find("#StepDriver").val());

		var driver =popup.find("#StepDriver").val();
		var xopts = jQuery.getJSON("./cases/getListOfKeywords/?driver="+driver).done(function(data) {
 			popup.find("#StepKeyword").empty();
 			a_items = data['keywords'];
 			console.log(xopts);
 			console.log(a_items);
 			for (let x of a_items) {
 				popup.find("#StepKeyword").append($('<option>',{ value: x,  text: x }));
 			}
 		});
	});


	popup.find("#Execute-at-ExecType").on('change',function() {
		if (this.value == 'If' || this.value == 'If Not') {
			popup.find('.rule-condition').show();			
		} else {
			popup.find('.rule-condition').hide();
			
		}
	});


	popup.find("#runmode-at-value").on('change',function() {
		if (this.value == 'Standard' ) {
			popup.find('.runmode-value').hide();			
		} else {
			popup.find('.runmode-value').show();
			
		}
	});


	popup.find("#StepKeyword").on('change',function() {
		sid  = popup.find("#StepKeyword").attr('theSid');   // 
		var oneCaseStep = caseApp.jsonCaseSteps['step'][sid];
		var keyword = popup.find("#StepKeyword").val();  // 
		var driver  = popup.find("#StepDriver").val();   // 
		var xopts = jQuery.getJSON("./cases/getListOfComments/?driver="+driver+"&keyword="+keyword).done(function(data) {
 			console.log(data);

 			a_items = data['fields'];
 			console.log(a_items);
 			out_array = a_items[0]['comment'];
 			var outstr = out_array.join("<br>");
 			var hhh = popup.find("#sourceCaseFileText");
 			//console.log('hello', hhh, keyword, driver);
	
 			hhh.empty(); 
 			hhh.append(outstr);
 				
 			});
		});
	},


	closeEditedCaseStep: function() {
			katana.popupController.close(popup);
			caseApp.mapCaseJsonToUi(caseApp.jsonCaseSteps);

	},

	saveTestCaseChanges: function() { 
			var popup = caseApp.lastPopup;
			var sid = parseInt(popup.find("#StepRowToEdit").attr('value'));	
			caseApp.mapUItoTestStep(sid,popup);	
			//katana.popupController.close();  <-- NO
			//katana.popupController.closePopup(); <-- No
			//katana.popupController.close(popup); <--- Yes. 
			caseApp.mapCaseJsonToUi(caseApp.jsonCaseSteps);
	},

	deletePopupArgument: function( ) {
				var names = this.attr("key").split('-');
				var sid = parseInt(names[1]);
				var aid = parseInt(names[2]);
				caseApp.removeOneArgument(sid,aid,caseApp.lastPopup);
			}, 

	savePopupArgument: function() {  
				var names = this.attr("key").split('-');
				var sid = parseInt(names[1]);
				var aid = parseInt(names[2]);
				caseApp.saveOneArgument(sid,aid,caseApp.lastPopup);
			},

	insertPopupArgument: function() {  
				var names = this.attr("key").split('-');
				var sid = parseInt(names[1]);
				var aid = parseInt(names[2]);
				caseApp.insertOneArgument(sid,aid,caseApp.lastPopup);
			},

	appendPopupArgument: function( ) {
				//lert("add One Argument");

				var sid = caseApp.lastPopup.find('#StepRowToEdit').attr('value');
				var xdata = caseApp.lastPopup.find('#StepRowToEdit').attr('xdata');
				caseApp.addOneArgument(sid,xdata, caseApp.lastPopup);
			},

	insertRequirementIntoLine: function() {
		var names = this.attr('key').split('-');
		var sid = parseInt(names[1]);
		caseApp.adjustRequirementsTable();
		caseApp.jsonCaseObject['Requirements']['Requirement'].splice(sid - 1, 0, "");
		caseApp.createRequirementsTable();	
	},
			
	saveRequirementToLine : function(){

	var names = this.attr('key').split('-');
	var sid = parseInt(names[1]);
	var txtVl = katana.$activeTab.find("#textRequirement-name-"+sid+"-id").val();
	console.log("Editing ..." + sid, txtVl);
	adjustRequirementsTable();
	rdata = caseApp.jsonCaseObject['Requirements']['Requirement'];
	rdata[sid] = txtVl;
	createRequirementsTable();	
	},

	deleteOneRequirementToLine : function() {
		var names = this.attr('key').split('-');
		var sid = parseInt(names[1]);
		
		adjustRequirementsTable();
		rdata = caseApp.jsonCaseObject['Requirements']['Requirement'];
		rdata.splice(sid,1); 
		createRequirementsTable();
	},



// For sorting the test case steps table. 
// Renumbers the IDs on the table and redraws it. 
	testCaseSortEventHandler : function(event, ui ) {

	var listItems = [] ; 
	var listCases = katana.$activeTab.find('#Step_table_display tbody').children(); 
	console.log(listCases);
	if (listCases.length < 2) {
	 return; 
	}
	var oldCaseSteps = caseApp.jsonCaseObject["Steps"]['step'];
	var newCaseSteps = new Array(listCases.length);
		
	for (xi=0; xi < listCases.length; xi++) {
		var xtr = listCases[xi];
		var ni  = xtr.getAttribute("data-sid");
		console.log(xi + " => " + ni);
		newCaseSteps[ni] = oldCaseSteps[xi];
	}

	caseApp.jsonCaseObject["Steps"]['step'] = newCaseSteps;
	caseApp.jsonCaseSteps  = caseApp.jsonCaseObject["Steps"]
	caseApp.mapCaseJsonToUi(caseApp.jsonCaseSteps);
		
	},

// Removes a test suite by its ID and refresh the page. 
	removeTestStep: function ( sid ){
		caseApp.jsonCaseSteps['step'].splice(sid,1);
		console.log("Removing testcases "+sid+" now " + Object.keys(caseApp.jsonCaseSteps).length);
		caseApp.mapCaseJsonToUi(caseApp.jsonCaseSteps);
	},

// Create a fresh step at the end of the table.
	addNewTestStepToUI: function() {
	var newObj = caseApp.createNewStep();

	if (!caseApp.jsonCaseSteps['step']) {
		caseApp.jsonCaseSteps['step'] = [];
		}
	if (!jQuery.isArray(caseApp.jsonCaseSteps['step'])) {
		caseApp.jsonCaseSteps['step'] = [caseApp.jsonCaseSteps['step']];
		}

	console.log("Adding new step", caseApp.jsonCaseSteps,caseApp.jsonCaseSteps['step']);
	caseApp.jsonCaseSteps['step'].push(newObj);  // Don't delete anything
	caseApp.mapCaseJsonToUi(caseApp.jsonCaseSteps);		
	},

// Inserts a new test step 
	addTestStepAboveToUI: function (sid,xdata,copy) {
		var newObj = caseApp.createNewStep();
		var aid = 0;   // Insert here. 
		if (sid < 1) { 
			aid = 0 ;
		} else {
			aid = sid;                // One below the current one. 
		}

		if (!caseApp.jsonCaseSteps['step']) {
			caseApp.jsonCaseSteps['step'] = [];
			}
		if (!jQuery.isArray(caseApp.jsonCaseSteps['step'])) {
			caseApp.jsonCaseSteps['step'] = [caseApp.jsonCaseSteps['step']];
			}

		if (copy == 1){
			console.log("Copying..., ", sid, " from ", caseApp.jsonCaseSteps['step'][sid]);
			newObj = jQuery.extend(true, {}, caseApp.jsonCaseSteps['step'][sid]); 
			}
		caseApp.jsonCaseSteps['step'].splice(aid,0,newObj);  // Don't delete anything
		caseApp.mapCaseJsonToUi(caseApp.jsonCaseSteps);		
		},

	// for a popup 
	redrawArguments: function(sid, oneCaseStep,popup) {
		var arguments = oneCaseStep['Arguments']['argument'];
		caseApp.makePopupArguments(popup, oneCaseStep);
	},


	saveOneArgument: function( sid, aid, xdata) {
		var obj = caseApp.jsonCaseSteps['step'][sid]['Arguments']['argument'][aid]; 	
		obj['@name'] = katana.$activeTab.find('[argid=caseArgName-'+aid+']').attr('value');
		obj['@value'] = katana.$activeTab.find('[argid=caseArgValue-'+aid+']').attr('value');
		console.log("Saving..arguments-div "+ sid + " aid = "+ aid);
		console.log(katana.$activeTab.find('[argid=caseArgValue-'+aid+']'));
		console.log(katana.$activeTab.find('[argid=caseArgValue-'+aid+']'));
		console.log(obj);
	//mapTestStepToUI(sid, xdata);
	},

 	addOneArgument: function( sid , xdata, popup ) {
		var xx = { "@name": "New" , "@value": "New" };
		console.log("sid = ", sid, caseApp.jsonCaseSteps, caseApp.jsonCaseSteps['step'][sid]['Arguments'] );
		if (! jQuery.isArray(caseApp.jsonCaseSteps['step'][sid]['Arguments']['argument']))  {
			caseApp.jsonCaseSteps['step'][sid]['Arguments']['argument'] = [ caseApp.jsonCaseSteps['step'][sid]['Arguments']['argument'] ];
		}
		caseApp.jsonCaseSteps['step'][sid]['Arguments']['argument'].push(xx);
		oneCaseStep = caseApp.jsonCaseSteps['step'][sid];
		caseApp.redrawArguments(sid, oneCaseStep,popup);
	},

	// Empty argument into location aid, for step sid in popup
 	insertOneArgument: function( sid , aid,  popup ) {
		var xx = { "@name": "" , "@value": " " };
		if (! jQuery.isArray(caseApp.jsonCaseSteps['step'][sid]['Arguments']['argument']))  {
			caseApp.jsonCaseSteps['step'][sid]['Arguments']['argument'] = [ caseApp.jsonCaseSteps['step'][sid]['Arguments']['argument'] ];
		}
		caseApp.jsonCaseSteps['step'][sid]['Arguments']['argument'].splice(aid,0,xx);
		oneCaseStep = caseApp.jsonCaseSteps['step'][sid];
		caseApp.redrawArguments(sid, oneCaseStep,popup);
	},

	// remove argument into location aid, for step sid in popup
 	
	removeOneArgument: function( sid, aid, popup ) {
		if (caseApp.jsonCaseSteps['step'][sid]['Arguments']) { 
			caseApp.jsonCaseSteps['step'][sid]['Arguments']['argument'].splice(aid,1);	
			console.log("sid =" + sid);
			console.log("aid =" + aid);
			console.log(popup);
			}
		oneCaseStep = caseApp.jsonCaseSteps['step'][sid];
		caseApp.redrawArguments(sid, oneCaseStep,popup);
	},

// When the edit button is clicked, map step to the UI. 
	mapUItoTestStep: function(sid,popup) {
	//var sid = parseInt(katana.$activeTab.find("#StepRowToEdit").attr('value'));	
	console.log(caseApp.jsonCaseSteps);
		
	// Validate whether sid 
	var xdata = caseApp.jsonCaseSteps['step'];

	console.log(xdata);
	console.log(sid);
	oneCaseStep = xdata[sid];
	//fillStepDefaults(oneCaseStep);  // Takes care of missing values.... 
	oneCaseStep["@Driver"] = popup.find("#StepDriver").val();
	oneCaseStep["@Keyword"] = popup.find("#StepKeyword").val();
	oneCaseStep["@TS"] =popup.find("#StepTS").val();
	oneCaseStep["Description"] = popup.find("#StepDescription").val();
	oneCaseStep["context"] =  popup.find("#StepContext").val();
	oneCaseStep["Execute"] = { '@ExecType': '' , 'Rule': {} }
	oneCaseStep["Execute"]["@ExecType"] = popup.find("#Execute-at-ExecType").val();	
	//oneCaseStep["Execute"]["@ExecType"]['Rule'] = {} 
	oneCaseStep["Execute"]['Rule']['@Condition'] = popup.find("#executeRuleAtCondition").val();	
	oneCaseStep["Execute"]['Rule']['@Condvalue'] = popup.find("#executeRuleAtCondvalue").val();	
	oneCaseStep["Execute"]['Rule']['@Else'] = popup.find("#executeRuleAtElse").val();	
	oneCaseStep["Execute"]['Rule']['@Elsevalue'] = popup.find("#executeRuleAtElsevalue").val();	
	oneCaseStep['onError'][ "@action"] = popup.find("#SteponError-at-action").val();
	oneCaseStep['onError'][ "@value"] = popup.find("#SteponError-at-value").val();
	oneCaseStep["runmode"] = { "@type" : popup.find("#runmode-at-type").val(),  "@value" : popup.find("#runmode-at-value").val()   };
	oneCaseStep["impact"] =  popup.find("#StepImpact").val();
	oneCaseStep["InputDataFile"] =  popup.find("#StepInputDataFile").val();

	// Now all the arguments have 
	console.log("after saving ",oneCaseStep);
},

	createNewStep(){
	var newCaseStep = {
		"step": {  "@Driver": "demo_driver", "@Keyword": "" , "@TS": "0" },
		"Arguments" : { 'Argument': [] },
		"onError": {  "@action" : "next", "@value" : "" } ,
		"iteration_type": {   "@type" : "" } ,
		"Description":"",
		"Execute": {   "@ExecType": "yes",
			"Rule": {   "@Condition": "","@Condvalue": "","@Else": "next", "@Elsevalue": "" }
		}, 
		"context": "positive", 
		"impact" :  "impact",
		"runmode" : { '@type': 'Standard', '@value': ""},
		"InputDataFile" : "", 
		"retry": { "@type": "If", "@Condition": "", "@Condvalue": "", "@count": "0", "@interval": "0"}, 
	 };
	 return newCaseStep;
},



	addStepToCase: function(){
	// Add an entry to the jsonTestSuites....
	var newCaseStep = createNewStep();
	if (!caseApp.jsonCaseSteps['step']) {
		caseApp.jsonCaseSteps['step'] = [];
		}
	if (!jQuery.isArray(caseApp.jsonCaseSteps['step'])) {
		caseApp.jsonCaseSteps['step'] = [caseApp.jsonCaseSteps['step']];
		}
	caseApp.jsonCaseSteps['step'].push(newCaseStep);
	caseApp.mapCaseJsonToUi(caseApp.jsonCaseSteps);
},

// Save UI Requirements to JSON table. 
	saveUItoRequirements: function(){
	rdata= caseApp.jsonCaseObject['Requirements']['Requirement'];
	rlen = Object.keys(rdata).length;
	console.log("Number of Requirements = " + rlen );
	console.log(rdata);
	for (var s=0; s<Object.keys(rdata).length; s++ ) {
				console.log("Requirements before save "+rdata[s]);
				rdata[s] = katana.$activeTab.find("#textRequirement-"+s+"-id").attr('value');
				console.log("Requirements after save "+rdata[s]);
		}

},

	 createRequirementsTable: function(){
	var items =[]; 
	katana.$activeTab.find("#tableOfCaseRequirements").html("");  // This is a blank div. 
	items.push('<table id="Requirements_table_display" class="case_req_configuration_table  striped" width="100%" >');
	items.push('<thead>');
	items.push('<tr id="ReqRow"><th>#</th><th>Requirement</th><th/><th/></tr>');
	items.push('</thead>');
	items.push('<tbody>');
	console.log("createRequirementsTable");
	caseApp.adjustRequirementsTable();
	rdata = caseApp.jsonCaseObject['Requirements']['Requirement'];
	console.log(rdata, Object.keys(rdata).length, caseApp.jsonCaseObject, caseApp.jsonCaseObject['Requirements']['Requirement']);
					
	for (var s=0; s<Object.keys(rdata).length; s++ ) {
				var oneReq = rdata[s];
				console.log("oneReq", oneReq);
				var idnumber = parseInt(s) + 1; 

				if (oneReq == null) {
					oneReq = '';
				}

			items.push('<tr data-sid=""><td>'+idnumber+'</td>');
			var bid = "textRequirement-name-"+s+"-id";	
				
			items.push('<td><input type="text" value="'+oneReq+'" id="'+bid+'"/></td>');
		
			bid = "deleteRequirement-"+s+"-id";
			items.push('<td><i  class="fa fa-trash"  title="Delete" id="'+bid+'" katana-click="caseApp.deleteOneRequirementToLine()" key="'+bid+'"/>');
			bid = "saveOneRequirement-"+s+"-id";
			var tbid = "textRequirement-name-"+s+"-id";	
			items.push('<i class="fa fa-pencil" title="Save Edit" id="'+bid+'" txtId="'+tbid+'" katana-click="caseApp.saveRequirementToLine()" key="'+bid+'"/>');
			bid = "insertRequirement-"+s+"-id";
			items.push('<i class="fa fa-plus"  title="Insert" id="'+bid+'" katana-click="caseApp.insertRequirementIntoLine()" key="'+bid+'"/></td>');

		}
	
	items.push('</tbody>');
	items.push('</table>');
		
	katana.$activeTab.find("#tableOfCaseRequirements").html(items.join(""));  //
},

	adjustRequirementsTable: function(){
	if (!caseApp.jsonCaseObject['Requirements']) caseApp.jsonCaseObject['Requirements'] =  { 'Requirement': [] } ;
	if (!jQuery.isArray(caseApp.jsonCaseObject['Requirements']['Requirement'])) {
			caseApp.jsonCaseObject['Requirements']['Requirement'] = [caseApp.jsonCaseObject['Requirements']['Requirement']];
	}
},


	addRequirementToCase: function() {
			caseApp.adjustRequirementsTable();
			rdata = caseApp.jsonCaseObject['Requirements']['Requirement'];
			//var newReq = {"Requirement" :  ""};
			rdata.push( "" );
			console.log(caseApp.jsonCaseObject);
			caseApp.createRequirementsTable();	
		},

};