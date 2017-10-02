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
function absToPrefix(pathToBase, pathToFile) {
	// Converts an absolute path to one that is relative to pathToBase 
	// Input: 
	// 		
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


 var cases = {

 	init: function() { 
 		cases.displayTreeOfCases();
			katana.$activeTab.find(".linkToCase").click(function() { 
				var $elem = $(this);
				var thePage = $elem.attr('href');
				var theID   = $elem.attr('fname');
				katana.templateAPI.load( thePage, null, null, 'case') ;
			});
 	},

	startNewCase: function() {
	  var xref="./cases/editCase/?fname=NEW"; 
	     katana.$view.one('tabAdded', function(){
	        cases.mapFullCaseJson(); // ("NEW",'#emptyTestCaseData');
	    });
	  katana.templateAPI.load(xref, null, null, 'Case') ;;
	},

	displayTreeOfCases: function() {
			jQuery.getJSON("./cases/getCaseListTree").done(function(data) {
				var sdata = data['treejs'];
				console.log(sdata);
				//var jdata = { 'core' : { 'data' : [ JSON.parse(sdata)]}};
				var jdata = { 'core' : { 'data' : sdata }}; 
				katana.$activeTab.find('#myCaseTree').on("select_node.jstree", function (e, data) { 
			      var thePage = data.node.li_attr['data-path'];
			      console.log(thePage);
			      // If there is no XML extension return immediately
			      var extn = thePage.indexOf(".xml");
			      if (extn < 4){
			      	return;
			      }
				  var xref="./cases/editCase/?fname=" + thePage; 
				  cases.thefile = thePage; 
				  // Load the response here. ...	
				  	katana.$activeTab.find(".case-single-toolbar").hide()
				  	katana.$activeTab.find("#OverwriteCaseHere").load(xref, function() {
				  		cases.mapFullCaseJson(); // (cases.thefile, null);
				  });
				  //katana.templateAPI.load(xref, null, null, 'Case') ;
				});
				katana.$activeTab.find('#myCaseTree').jstree(jdata);
			});
		//katana.$activeTab.find('#mmm').hide();
	},

	closeCase: function(){
		katana.closeSubApp();
	},





	 lastPopup: null,
	 jsonCaseObject : [],
	 jsonCaseDetails : [],				// A pointer to the Details   
	 jsonCaseSteps : [],		  		// A pointer to the Steps object
//
// This function is called when the page loads in cases.js . 
//
	mapFullCaseJson: function(){
		var myfile = katana.$activeTab.find('#fullpathname').text();
		jQuery.getJSON("./cases/getJSONcaseDataBack/?fname="+myfile).done(function(data) {
			a_items = data['fulljson']['Testcase'];
			//console.log("from views.py call=", a_items);
			cases.jsonCaseObject = a_items; // JSON.parse(sdata); 
			console.log("Incoming data",cases.jsonCaseObject, a_items); // instead of jdata.
			if (!jQuery.isArray(cases.jsonCaseObject["Steps"]['step'])) {
				cases.jsonCaseObject["Steps"]['step'] = [ cases.jsonCaseObject["Steps"]['step']];
			}
			cases.jsonCaseSteps  = cases.jsonCaseObject["Steps"];
			console.log("Steps --> ", cases.jsonCaseSteps);
			cases.jsonCaseDetails = cases.jsonCaseObject['Details'];
			katana.$activeTab.find("#editCaseStepDiv").hide();
			katana.$activeTab.find("#tableOfTestStepsForCase").removeClass();
			katana.$activeTab.find("#tableOfTestStepsForCase").addClass('col-md-12');
			katana.$activeTab.find("#tableOfTestStepsForCase").show();
			console.log("Here", cases.jsonCaseObject, cases.jsonCaseSteps);
			for (vs in cases.jsonCaseSteps['step']) {
				var oneCaseStep = cases.jsonCaseSteps['step'][vs];
				console.log("Arguments", oneCaseStep, vs, cases.jsonCaseSteps['step']);
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

		cases.mapCaseJsonToUi(cases.jsonCaseSteps);
		//console.log("Here 2", cases.jsonCaseObject, cases.jsonCaseSteps);
		cases.createRequirementsTable();

	//$('#myform :checkbox').change(function()
		katana.$activeTab.find('#ck_dataPath').change(function() {
				if (this.checked) {
					katana.$activeTab.find('.case-results-dir').hide();
				} else {
					katana.$activeTab.find('.case-results-dir').show();
				}
		  	});

		cases.fillCaseDefaultGoto();

		});
	},





	mapUiToCaseJson: function() {

	if ( katana.$activeTab.find('#caseName').attr('value').length < 1) {
		data = { 'heading': "Error", 'text' : "Please specific a case name "}
		katana.openAlert(data);
		return;
	}

	if ( katana.$activeTab.find('#caseTitle').attr('value').length < 1) {
		data = { 'heading': "Error", 'text' : "Please specific a title "}
		katana.openAlert(data);
		return;
	}
	if ( katana.$activeTab.find('#caseEngineer').attr('value').length < 1) {
		data = { 'heading': "Error", 'text' : "Please specific a name for the engineer"}
		katana.openAlert(data);
		return;
	}

	cases.jsonCaseObject['Details']['Name'] = katana.$activeTab.find('#caseName').attr('value');
	cases.jsonCaseObject['Details']['Title'] = katana.$activeTab.find('#caseTitle').attr('value');
	cases.jsonCaseObject['Details']['Category'] = katana.$activeTab.find('#caseCategory').attr('value');
	cases.jsonCaseObject['Details']['State'] = katana.$activeTab.find('#caseState').attr('value');
	cases.jsonCaseObject['Details']['Engineer'] = katana.$activeTab.find('#caseEngineer').attr('value');
	cases.jsonCaseObject['Details']['Title'] = katana.$activeTab.find('#caseTitle').attr('value');
	cases.jsonCaseObject['Details']['Date'] = katana.$activeTab.find('#caseDate').attr('value');
	cases.jsonCaseObject['Details']['default_onError'] = katana.$activeTab.find('#default_onError').attr('value');
	cases.jsonCaseObject['Details']['Datatype'] = katana.$activeTab.find('#caseDatatype').attr('value');
	cases.jsonCaseObject['dataPath'] =  katana.$activeTab.find('#caseInputDataFile').attr('value');
	cases.jsonCaseObject['resultsDir'] =  katana.$activeTab.find('#caseResultsDir').attr('value');
	cases.jsonCaseObject['logsDir'] =  katana.$activeTab.find('#caseLogsDir').attr('value');
	cases.jsonCaseObject['expectedDir'] =  katana.$activeTab.find('#caseExpectedResults').attr('value');
	cases.jsonCaseObject['SaveToFile'] =  katana.$activeTab.find('#my_file_to_save').attr('value');

	if (!cases.jsonCaseObject['Requirements']) {
		cases.jsonCaseObject['Requirements'] = []; 
	}
 
	// Now you have collected the user components...
	} ,

// Start the WDF editor. 
	start_wdfEditor: function() { 
	var tag = '#caseInputDataFile';
	var filename = katana.$activeTab.find(tag).attr("fullpath");
	dd = { 'path' : filename}; 
	katana.templateAPI.load( "/katana/wdf/index", null, null, "WDF", null, { type: 'POST', data:  dd}) ;
	},

	getFileSavePath: function () {
			var tag = '#caseName';
			var callback_on_accept = function(selectedValue) { 
	  		console.log(selectedValue);
	  		var savefilepath = katana.$activeTab.find('#savefilepath').text();
	  		console.log("File path ==", savefilepath);
	  		var nf = prefixFromAbs(savefilepath, selectedValue);
	  		katana.$activeTab.find(tag).attr("value", nf);
	  		katana.$activeTab.find(tag).attr("fullpath", selectedValue);
			//katana.$activeTab.find(tag).text('');
			};
	  var callback_on_dismiss =  function(){ 
	  		console.log("Dismissed");
	 };
	 katana.fileExplorerAPI.openFileExplorer("Select a file", false , $("[name='csrfmiddlewaretoken']").val(), false, callback_on_accept, callback_on_dismiss);
},

// Get Results directory from the case on the main page.
	getCaseInputDataFile: function () {

			var callback_on_accept = function(selectedValue) { 
	  		console.log(selectedValue);
	  		var tag = '#caseInputDataFile'
	  		var savefilepath = katana.$activeTab.find('#savefilepath').text();
	  		
	  		console.log("File path ==", savefilepath);
	  		var nf = prefixFromAbs(savefilepath, selectedValue);
	  		katana.$activeTab.find(tag).attr("value", nf);
	  		katana.$activeTab.find(tag).attr("fullpath", selectedValue);
			katana.$activeTab.find(tag).text(nf); // 
			};
	  var callback_on_dismiss =  function(){ 
	  		console.log("Dismissed");
	 };
	 katana.fileExplorerAPI.openFileExplorer("Select a file", false , $("[name='csrfmiddlewaretoken']").val(), false, callback_on_accept, callback_on_dismiss);
},


	getStepInputDataFile: function() {
		
			var callback_on_accept = function(selectedValue) { 
			  		var sid = katana.$activeTab.find("#editCaseStepDiv").attr('row-id');
			  		console.log("Got this file" , selectedValue, names, sid);
			  		var popup = katana.$activeTab.find("#editCaseStepDiv").attr('data-popup-id');
			  		var savefilepath = katana.$activeTab.find('#savefilepath').text();  
			  		console.log("File path ==", savefilepath);
					var nf = prefixFromAbs(savefilepath, selectedValue);
					var oneCaseStep = cases.jsonCaseSteps['step'][sid];
					oneCaseStep["InputDataFile"] = nf;
					};
			 var callback_on_dismiss = function(){ 
			  		var popup = katana.$activeTab.find("#editCaseStepDiv").attr('data-popup-id');
			  		console.log("Dismissed", popup);

			 	};
			var popup = katana.$activeTab.find("#editCaseStepDiv").attr('data-popup-id');
			katana.fileExplorerAPI.openFileExplorer("Select a file", false , $("[name='csrfmiddlewaretoken']").val(), popup, callback_on_accept, callback_on_dismiss)

	},

// Get Results directory from the case on a popup dialog
// The dialog is shown BELOW the popup. BUG. 

				
// Fills in the drop down based on the number of steps you have 
// in the case. 

	fillCaseDefaultGoto: function() {
		var gotoStep = katana.$activeTab.find('#default_onError').val();
		console.log("Step ", gotoStep);
		var defgoto = katana.$activeTab.find('#default_onError_goto'); 
			defgoto.hide();

		if (gotoStep.trim() == 'goto') { 
			defgoto.show();
		} else {
			defgoto.hide();
			
		}

	defgoto.empty(); 
	var xdata = cases.jsonCaseObject["Steps"]['step']; // ['Testcase']; 
	console.log("Step....",Object.keys(xdata).length, xdata);
	for (var s=0; s<Object.keys(xdata).length; s++ ) {
		defgoto.append($('<option>',{ value: s,  text: s+1}));
	}
},

// Saves the UI to memory and sends to server as a POST request
	sendCaseToServer: function () {
	cases.mapUiToCaseJson();
	var url = "./cases/getCaseDataBack";
	var csrftoken = $("[name='csrfmiddlewaretoken']").attr('value');

	$.ajaxSetup({
			function(xhr, settings) {
			xhr.setRequestHeader("X-CSRFToken", csrftoken)
		}
	});

	var topNode  = { 'Testcase' : cases.jsonCaseObject};

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

		xdata = { 'heading': "Sent", 'text' : "sent the file... "+data}
		katana.openAlert(xdata);
	
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
	katana.$activeTab.find("#tableOfTestStepsForCase").html("");	  // Start with clean slate
	items.push('<table class="case-configuration-table table-striped" id="Step_table_display"  width="100%" >');
	items.push('<thead>');
	items.push('<tr id="StepRow"><th>#</th><th>Driver</th><th>Keyword</th><th>Description</th><th>Arguments</th>\
		<th>OnError</th><th>Execute</th><th>Run Mode</th><th>Context</th><th>Impact</th><th>Other</th></tr>');
	items.push('</thead>');
	items.push('<tbody>');
	for (var s=0; s<Object.keys(xdata).length; s++ ) {  // for s in xdata
		var oneCaseStep = xdata[s];			 // for each step in case
		//console.log(oneCaseStep['path']);
		var showID = parseInt(s)+1;
		items.push('<tr data-sid="'+s+'"><td>'+showID+'</td>');		// ID 
		// -------------------------------------------------------------------------
		// Validation and default assignments 
		// Create empty elements with defaults if none found. ;-)
		// -------------------------------------------------------------------------
		cases.fillStepDefaults(oneCaseStep);
		items.push('<td>'+oneCaseStep['@Driver'] +'</td>'); 
		var outstr; 
		items.push('<td>'+oneCaseStep['@Keyword'] + "<br>TS=" +oneCaseStep['@TS']+'</td>'); 
		outstr =  oneCaseStep['Description'];
		bid = "SelectStepInputData-"+s+"-id-";
		var fileExp = '<i title="Select Warrior Input Data" class="fa fa-plus" theSid="'+s+'" id="'+bid+'" katana-click="cases.getStepInputDataFile()" key="'+bid+'"/>';

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
		items.push('<td><i title="Delete" class="fa fa-trash" theSid="'+s+'" id="'+bid+'" katana-click="cases.deleteCaseFromLine()" key="'+bid+'"/>');

		bid = "editTestStep-"+s+"-id-";
		items.push('<i title="Edit" class="fa fa-pencil" theSid="'+s+'"  id="'+bid+'" katana-click="cases.editCaseFromLine()" key="'+bid+'"/>');

		bid = "addTestStepAbove-"+s+"-id-";
		items.push('<i title="Insert" class="fa fa-plus" theSid="'+s+'"   id="'+bid+'" katana-click="cases.addCaseFromLine()" key="'+bid+'"/>');

		bid = "dupTestStepAbove-"+s+"-id-";
		items.push('<i title="Duplicate" class="fa fa-copy" theSid="'+s+'"  id="'+bid+'" katana-click="cases.duplicateCaseFromLine()" key="'+bid+'"/></td>');

	}

	items.push('</tbody>');
	items.push('</table>'); // 
	katana.$activeTab.find("#tableOfTestStepsForCase").html( items.join(""));
	katana.$activeTab.find('#Step_table_display tbody').sortable( { stop: cases.testCaseSortEventHandler});
	
	cases.fillCaseDefaultGoto();
	katana.$activeTab.find('#default_onError').on('change',cases.fillCaseDefaultGoto );

	/*
	if (cases.jsonCaseDetails['Datatype'] == 'Custom') {
		$(".arguments-div").hide();
	} else {

		$(".arguments-div").show();
	}
	*/
	
	}, // end of function 

	deleteCaseFromLine : function() {
	var names = this.attr('key').split('-');
	var sid = parseInt(names[1]);
	cases.removeTestStep(sid);
	},

	editCaseFromLine: function() { 
	var names = this.attr('key').split('-');
	var sid = parseInt(names[1]);
	katana.popupController.open(katana.$activeTab.find("#editCaseStepDiv").html(),"Edit..." + sid, function(popup) {
		cases.setupPopupDialog(sid,cases.jsonCaseSteps['step'] ,popup);
	});
	},	

	addCaseFromLine: function() {
	var names = this.attr('key').split('-');
	var sid = parseInt(names[1]);
	cases.addTestStepAboveToUI(sid,cases.jsonCaseSteps['step'],0);
	},

	duplicateCaseFromLine :function() { 
		var names = this.attr('key').split('-');
		var sid = parseInt(names[1]);
		cases.addTestStepAboveToUI(sid,cases.jsonCaseSteps['step'],1);
	},





	makePopupArguments: function(popup,  oneCaseStep) {
		cases.lastPopup = popup; 
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
			a_items.push('<td><i title="Delete" class="fa fa-eraser" value="X" id="'+bid+'" key="'+bid+'"  katana-click="cases.deletePopupArgument"/>');
			
			bid = "saveCaseArg-"+sid+"-"+ta+"-id"
			a_items.push('<td><i  title="Save Argument Change" class="fa fa-floppy-o" value="Save" id="'+bid+'" key="'+bid+'"  katana-click="cases.savePopupArgument"/>');

			bid = "insertCaseArg-"+sid+"-"+ta+"-id";
			a_items.push('<td><i  title="Insert one" class="fa fa-plus" value="Save" id="'+bid+'" key="'+bid+'" katana-click="cases.insertPopupArgument"/>');
			
			ta += 1
			a_items.push('</div>');
			
		}
		popup.find("#arguments-textarea").html( a_items.join("\n"));	
		if (!jQuery.isArray(cases.jsonCaseSteps['step'])) {
			cases.jsonCaseSteps['step'] = [cases.jsonCaseSteps['step']];
			}
		cases.fillCaseStepDefaultGoto(popup);
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
		//var sid = popup.find('#CaseRowToEdit').val();
		defgoto.empty(); 
		var xdata = cases.jsonCaseObject["Steps"]['step']; // ['Testcase']; 
		console.log("Step....",Object.keys(xdata).length, xdata);
		for (var s=0; s<Object.keys(xdata).length; s++ ) {
			defgoto.append($('<option>',{ value: s,  text: s+1}));
		}
	},


// Show a popup dialog with items from a case.
	setupPopupDialog: function (sid,xdata,popup) {
		katana.$activeTab.find("#editCaseStepDiv").attr('data-popup-id',popup);
		katana.$activeTab.find("#editCaseStepDiv").attr('row-id',sid);
		
		console.log(popup);  					// Merely returns the div tag
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
		 				var outstr = out_array.join("\n");
		 				console.log(outstr);
		 				cases.lastPopup.find("#sourceCaseFileText").html(""); 
		 				cases.lastPopup.find("#sourceCaseFileText").html(outstr);
		 				cases.lastPopup.find("#sourceCaseFileDef").html(""); 
						if (a_items[0]['def']) {
							
			 				outstr = a_items[0]['def'];
							cases.lastPopup.find("#sourceCaseFileDef").html(outstr);	
			 				}

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

	cases.makePopupArguments(popup, oneCaseStep);

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
		var oneCaseStep = cases.jsonCaseSteps['step'][sid];
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
		var oneCaseStep = cases.jsonCaseSteps['step'][sid];
		var keyword = popup.find("#StepKeyword").val();  // 
		var driver  = popup.find("#StepDriver").val();   // 
		var xopts = jQuery.getJSON("./cases/getListOfComments/?driver="+driver+"&keyword="+keyword).done(function(data) {
 			//console.log(data);
 			a_items = data['fields'];
 			//console.log(a_items);
 			out_array = a_items[0]['comment'];
 			var outstr = out_array.join("<br>");
 			var hhh = popup.find("#sourceCaseFileText");
 			hhh.empty(); 
 			hhh.append(outstr);
 			});
		});
	},


	closeEditedCaseStep: function() {
		// Close the popup contrller 
			katana.popupController.close(popup);
			cases.mapCaseJsonToUi(cases.jsonCaseSteps);
	},

	saveTestCaseChanges: function() { 
			// Save popup ui to json object.
			var popup = cases.lastPopup;
			var sid = parseInt(popup.find("#StepRowToEdit").attr('value'));	
			cases.mapUItoTestStep(sid,popup);	
			cases.mapCaseJsonToUi(cases.jsonCaseSteps);
	},

	deletePopupArgument: function( ) {
			// Delete selected argument and save popup ui to json object.
				var names = this.attr("key").split('-');
				var sid = parseInt(names[1]);
				var aid = parseInt(names[2]);
				cases.removeOneArgument(sid,aid,cases.lastPopup);
			}, 

	savePopupArgument: function() {  
				var names = this.attr("key").split('-');
				var sid = parseInt(names[1]);
				var aid = parseInt(names[2]);
				cases.saveOneArgument(sid,aid,cases.lastPopup);
			},

	insertPopupArgument: function() {  
				var names = this.attr("key").split('-');
				var sid = parseInt(names[1]);
				var aid = parseInt(names[2]);
				cases.insertOneArgument(sid,aid,cases.lastPopup);
			},

	appendPopupArgument: function( ) {
				//lert("add One Argument");

				var sid = cases.lastPopup.find('#StepRowToEdit').attr('value');
				var xdata = cases.lastPopup.find('#StepRowToEdit').attr('xdata');
				cases.addOneArgument(sid,xdata, cases.lastPopup);
			},

	insertRequirementIntoLine: function() {
		var names = this.attr('key').split('-');
		var sid = parseInt(names[1]);
		cases.adjustRequirementsTable();
		cases.jsonCaseObject['Requirements']['Requirement'].splice(sid - 1, 0, "");
		cases.createRequirementsTable();	
	},
			
	saveRequirementToLine : function(){

		var names = this.attr('key').split('-');
		var sid = parseInt(names[1]);
		var txtVl = katana.$activeTab.find("#textRequirement-name-"+sid+"-id").val();
		console.log("Editing ..." + sid, txtVl);
		cases.adjustRequirementsTable();
		rdata = cases.jsonCaseObject['Requirements']['Requirement'];
		rdata[sid] = txtVl;
		cases.createRequirementsTable();	
	},

	deleteOneRequirementToLine : function() {
		var names = this.attr('key').split('-');
		var sid = parseInt(names[1]);
		
		cases.adjustRequirementsTable();
		rdata = cases.jsonCaseObject['Requirements']['Requirement'];
		rdata.splice(sid,1); 
		cases.createRequirementsTable();
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
		var oldCaseSteps = cases.jsonCaseObject["Steps"]['step'];
		var newCaseSteps = new Array(listCases.length);
			
		for (xi=0; xi < listCases.length; xi++) {
			var xtr = listCases[xi];
			var ni  = xtr.getAttribute("data-sid");
			console.log(xi + " => " + ni);
			newCaseSteps[ni] = oldCaseSteps[xi];
		}

		cases.jsonCaseObject["Steps"]['step'] = newCaseSteps;
		cases.jsonCaseSteps  = cases.jsonCaseObject["Steps"]
		cases.mapCaseJsonToUi(cases.jsonCaseSteps);
		
	},

// Removes a test suite by its ID and refresh the page. 
	removeTestStep: function ( sid ){
		cases.jsonCaseSteps['step'].splice(sid,1);
		console.log("Removing testcases "+sid+" now " + Object.keys(cases.jsonCaseSteps).length);
		cases.mapCaseJsonToUi(cases.jsonCaseSteps);
	},

// Create a fresh step at the end of the table.
	addNewTestStepToUI: function() {
		var newObj = cases.createNewStep();

		if (!cases.jsonCaseSteps['step']) {
			cases.jsonCaseSteps['step'] = [];
			}
		if (!jQuery.isArray(cases.jsonCaseSteps['step'])) {
			cases.jsonCaseSteps['step'] = [cases.jsonCaseSteps['step']];
			}

		console.log("Adding new step", cases.jsonCaseSteps,cases.jsonCaseSteps['step']);
		cases.jsonCaseSteps['step'].push(newObj);  // Don't delete anything
		cases.mapCaseJsonToUi(cases.jsonCaseSteps);		
	},

// Inserts a new test step 
	addTestStepAboveToUI: function (sid,xdata,copy) {
		var newObj = cases.createNewStep();
		var aid = 0;   // Insert here. 
		if (sid < 1) { 
			aid = 0 ;
		} else {
			aid = sid;				// One below the current one. 
		}

		if (!cases.jsonCaseSteps['step']) {
			cases.jsonCaseSteps['step'] = [];
			}
		if (!jQuery.isArray(cases.jsonCaseSteps['step'])) {
			cases.jsonCaseSteps['step'] = [cases.jsonCaseSteps['step']];
			}

		if (copy == 1){
			console.log("Copying..., ", sid, " from ", cases.jsonCaseSteps['step'][sid]);
			newObj = jQuery.extend(true, {}, cases.jsonCaseSteps['step'][sid]); 
			}
		cases.jsonCaseSteps['step'].splice(aid,0,newObj);  // Don't delete anything
		cases.mapCaseJsonToUi(cases.jsonCaseSteps);		
		},

	// for a popup 
	redrawArguments: function(sid, oneCaseStep,popup) {
		var arguments = oneCaseStep['Arguments']['argument'];
		cases.makePopupArguments(popup, oneCaseStep);
	},


	saveOneArgument: function( sid, aid, xdata) {
		var obj = cases.jsonCaseSteps['step'][sid]['Arguments']['argument'][aid]; 	
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
		console.log("sid = ", sid, cases.jsonCaseSteps, cases.jsonCaseSteps['step'][sid]['Arguments'] );
		if (! jQuery.isArray(cases.jsonCaseSteps['step'][sid]['Arguments']['argument']))  {
			cases.jsonCaseSteps['step'][sid]['Arguments']['argument'] = [ cases.jsonCaseSteps['step'][sid]['Arguments']['argument'] ];
		}
		cases.jsonCaseSteps['step'][sid]['Arguments']['argument'].push(xx);
		oneCaseStep = cases.jsonCaseSteps['step'][sid];
		cases.redrawArguments(sid, oneCaseStep,popup);
	},

	// Empty argument into location aid, for step sid in popup
 	insertOneArgument: function( sid , aid,  popup ) {
		var xx = { "@name": "" , "@value": " " };
		if (! jQuery.isArray(cases.jsonCaseSteps['step'][sid]['Arguments']['argument']))  {
			cases.jsonCaseSteps['step'][sid]['Arguments']['argument'] = [ cases.jsonCaseSteps['step'][sid]['Arguments']['argument'] ];
		}
		cases.jsonCaseSteps['step'][sid]['Arguments']['argument'].splice(aid,0,xx);
		oneCaseStep = cases.jsonCaseSteps['step'][sid];
		cases.redrawArguments(sid, oneCaseStep,popup);
	},

	// remove argument into location aid, for step sid in popup
 	
	removeOneArgument: function( sid, aid, popup ) {
		if (cases.jsonCaseSteps['step'][sid]['Arguments']) { 
			cases.jsonCaseSteps['step'][sid]['Arguments']['argument'].splice(aid,1);	
			console.log("sid =" + sid);
			console.log("aid =" + aid);
			console.log(popup);
			}
		oneCaseStep = cases.jsonCaseSteps['step'][sid];
		cases.redrawArguments(sid, oneCaseStep,popup);
	},

// When the edit button is clicked, map step to the UI. 
	mapUItoTestStep: function(sid,popup) {
	//var sid = parseInt(katana.$activeTab.find("#StepRowToEdit").attr('value'));	
	console.log(cases.jsonCaseSteps);
		
	// Validate whether sid 
	var xdata = cases.jsonCaseSteps['step'];

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
	if (!cases.jsonCaseSteps['step']) {
		cases.jsonCaseSteps['step'] = [];
		}
	if (!jQuery.isArray(cases.jsonCaseSteps['step'])) {
		cases.jsonCaseSteps['step'] = [cases.jsonCaseSteps['step']];
		}
	cases.jsonCaseSteps['step'].push(newCaseStep);
	cases.mapCaseJsonToUi(cases.jsonCaseSteps);
},

// Save UI Requirements to JSON table. 
	saveUItoRequirements: function(){
	rdata= cases.jsonCaseObject['Requirements']['Requirement'];
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
	cases.adjustRequirementsTable();
	rdata = cases.jsonCaseObject['Requirements']['Requirement'];
	console.log(rdata, Object.keys(rdata).length, cases.jsonCaseObject, cases.jsonCaseObject['Requirements']['Requirement']);
					
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
			items.push('<td><i  class="fa fa-trash"  title="Delete" id="'+bid+'" katana-click="cases.deleteOneRequirementToLine()" key="'+bid+'"/>');
			bid = "saveOneRequirement-"+s+"-id";
			var tbid = "textRequirement-name-"+s+"-id";	
			items.push('<i class="fa fa-floppy-o" title="Save Edit" id="'+bid+'" txtId="'+tbid+'" katana-click="cases.saveRequirementToLine()" key="'+bid+'"/>');
			bid = "insertRequirement-"+s+"-id";
			items.push('<i class="fa fa-plus"  title="Insert" id="'+bid+'" katana-click="cases.insertRequirementIntoLine()" key="'+bid+'"/></td>');

		}
	
	items.push('</tbody>');
	items.push('</table>');
		
	katana.$activeTab.find("#tableOfCaseRequirements").html(items.join(""));  //
},

	adjustRequirementsTable: function(){
	if (!cases.jsonCaseObject['Requirements']) cases.jsonCaseObject['Requirements'] =  { 'Requirement': [] } ;
	if (!jQuery.isArray(cases.jsonCaseObject['Requirements']['Requirement'])) {
			cases.jsonCaseObject['Requirements']['Requirement'] = [cases.jsonCaseObject['Requirements']['Requirement']];
	}
},


	addRequirementToCase: function() {
			cases.adjustRequirementsTable();
			rdata = cases.jsonCaseObject['Requirements']['Requirement'];
			//var newReq = {"Requirement" :  ""};
			rdata.push( "" );
			console.log(cases.jsonCaseObject);
			cases.createRequirementsTable();	
		},

};

