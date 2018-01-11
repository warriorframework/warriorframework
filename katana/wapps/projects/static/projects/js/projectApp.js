//
//
/*
/// -------------------------------------------------------------------------------

Project File Data Handler 

Author: 
Date: 

The functions in this module are designed specifically for handling project XML files
for the warrior framework. 

It is expected to work with the editProject.html file and the calls to editProject in 
the views.py python for Django. 
/// -------------------------------------------------------------------------------

*/
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
      return string.toLowerCase();
}

var projectApp = { 


	lastPopup : null, 
	jsonProjectObject : [],
	jsonTestSuites : [],			// for all Suites


	initProjectTree: function() {


		jQuery.getJSON("./projects/getProjectListTree/").done(function(data) {
			var sdata = data['treejs'];
			console.log("tree ", sdata);
			var jdata = { 'core' : { 'data' : sdata }}; 
			katana.$activeTab.find('#myProjectTree').jstree(jdata); 
		});

		katana.$activeTab.find('#myProjectTree').on("select_node.jstree", function (e, data) { 
		      var thePage = data.node.li_attr['data-path'];
		      var extn = thePage.indexOf(".xml");
		      if (extn < 4){
		        return;
		      }
		      katana.$view.one('tabAdded', function(){
		      projectApp.mapFullProjectJson(thePage);
		  });
		  //
		  var xref="./projects/editProject/?fname=" + thePage; 
		  katana.templateAPI.load(xref, null, null, 'Project') ;
		});
},

/// -------------------------------------------------------------------------------
// 
/// -------------------------------------------------------------------------------
startNewProject : function() {
  var xref="./projects/editProject/?fname=NEW" ;
  katana.templateAPI.load(xref, null, null, 'NEW') ;
},

/// -------------------------------------------------------------------------------
// Sets up the global project data holder for the UI. 
// This is called from the correspoding HTML file onLoad event 
// or when a new XML file is loaded into the interface.
// 
// Two variables are set when this function is called; 
// 1. jsonProjectObject 
// 2. jsonTestSuites is set to point to the Testsuites data structure in
//    the jsonProjectObject
//
/// -------------------------------------------------------------------------------
	mapFullProjectJson: function (){
	//var sdata = katana.$activeTab.find("#listOfTestSuitesForProject").text();
	//katana.$activeTab.find('#savefilepath').hide();  // To remove later...
	var myfile = katana.$activeTab.find('#fullpathname').text();
	jQuery.getJSON("./projects/getJSONProjectData/?fname="+myfile).done(function(data) {
			var sdata = data['fulljson'];
			console.log("from views.py call=", sdata);
			//projectApp.jsonProjectObject = JSON.parse(sdata); 
			projectApp.jsonProjectObject = sdata['Project'];
			projectApp.jsonTestSuites = projectApp.jsonProjectObject['Testsuites']; 
			projectApp.mapProjectJsonToUi(projectApp.jsonTestSuites);  // This is where the table and edit form is created. 
			projectApp.fillProjectDefaultGoto();
			console.log("Adding defaults ");
			katana.$activeTab.find('#default_onError').on('change',projectApp.fillProjectDefaultGoto );
			katana.$activeTab.find('#Execute-at-ExecType').on('change',function() { 
				if (this.value == 'if' || this.value == 'if not')
				{
					katana.$activeTab.find('.rule-condition').hide();
				} else {
					katana.$activeTab.find('.rule-condition').show();
				}
			});
		});

	}, 

	resetUIfromFile : function() {
	  	var thePage = katana.$activeTab.find('#fullpathname').text();
	  	var xref="./projects/editProject/?fname=" + thePage; 
	  	katana.templateAPI.load(xref, null, null, 'Project') ;
	},
/// -------------------------------------------------------------------------------
// Dynamically create a new TestSuite object and append to the jsonTestSuites 
// array. Default values are used to fill in a complete structure. If there is 
// no default value, a null value is inserted for the keyword
/// -------------------------------------------------------------------------------
	makeNewSuite: function() { 
		var newTestSuite = {	
		"path": "path/to/suite", 
		"Execute": { "@ExecType": "yes",
			"Rule": {"@Condition": "","@Condvalue": "","@Else": "next", "@Elsevalue": "" }
		}, 
		"runmode": {
			"@type": "standard", "@value": "2"
		},
		"retry": {
			"@type": "if not", 
			"@Condition": 
			"testsuite_1_result", 
			"@Condvalue": "PASS", 
			"@count": "6", 
			"@interval": "0"
		}, 
		"onError": { 
			"@action": "next",
			 "@value": "" }, 
		"impact": "impact" 
		};
		return newTestSuite;
	},

	addSuiteToProject: function(){
	var newTestSuite = projectApp.makeNewSuite();
	if (!jQuery.isArray(projectApp.jsonTestSuites['Testsuite'])) {
		projectApp.jsonTestSuites['Testsuite'] = [projectApp.jsonTestSuites['Testsuite']];
		}

	projectApp.jsonTestSuites['Testsuite'].push(newTestSuite);
	projectApp.mapProjectJsonToUi(projectApp.jsonTestSuites);

	},


	fillProjectSuitePopupDefaultGoto: function(popup) {

		var gotoStep =popup.find('#default_onError').val();
		console.log("Step ", gotoStep);
		var defgoto = popup.find('#default_onError_goto'); 
			defgoto.hide();

		if (gotoStep.trim() == 'goto'.trim()) { 
			defgoto.show();
		} else {
			defgoto.hide();
			
		}
		//var sid = popup.find('#CaseRowToEdit').val();
		defgoto.empty(); 
		var xdata = jsonProjectObject['Testsuites']; 
		if (!jQuery.isArray(xdata)) xdata = [xdata]; 
		for (var s=0; s<Object.keys(xdata).length; s++ ) {
			defgoto.append($('<option>',{ value: s,  text: s}));
		}
	},


	setupProjectPopupDialog: function(s,popup) {
	console.log(s);
	var oneSuite = projectApp.jsonProjectObject['Testsuites']['Testsuite'][s];
	console.log(oneSuite);
	popup.find("#suiteRowToEdit").val(s); 
	popup.find("#suitePath").val(oneSuite['path']);
	popup.find("#Execute-at-ExecType").val(jsUcfirst(oneSuite['Execute']['@ExecType'])); 
	popup.find("#executeRuleAtCondition").val(oneSuite['Execute']['Rule']['@Condition']); 
	popup.find("#executeRuleAtCondvalue").val(oneSuite['Execute']['Rule']['@Condvalue']); 
	popup.find("#executeRuleAtElse").val(oneSuite['Execute']['Rule']['@Else']); 
	popup.find("#executeRuleAtElsevalue").val(oneSuite['Execute']['Rule']['@Elsevalue']); 
	popup.find("#onError-at-action").val(oneSuite['onError']['@action']); 
	popup.find("#onError-at-value").val(oneSuite['onError']['@value']); 
	popup.find("#runmode-at-type").val(oneSuite['runmode']['@type'].toLowerCase()); 
	popup.find("#runmode-at-value").val(oneSuite['runmode']['@value']); 
	popup.find("#impact").val(oneSuite['impact']); 
	projectApp.fillProjectSuitePopupDefaultGoto(popup);
	popup.find('#onError-at-action').on('change', function(){ 
			var popup = $(this).closest('.popup');
			projectApp.fillProjectSuitePopupDefaultGoto(popup);
	});
	popup.find('.rule-condition').hide();
	if (oneSuite["Execute"]['@ExecType']) {
		console.log("FOUND EXECT TYPE ",oneSuite["Execute"]['@ExecType'] )
		if (oneSuite["Execute"]['@ExecType'] == 'if' || oneSuite["Execute"]['@ExecType'] == 'if not') {
			popup.find('.rule-condition').show();
		}	
	}
	popup.find("#runmode-at-type").on('change', function() {
		var popup = $(this).closest('.popup');
		var sid = popup.find("#suiteRowToEdit").val();
		console.log(projectApp.jsonProjectObject['Testsuites'], sid); 
		var oneSuite = projectApp.jsonProjectObject['Testsuites']['Testsuite'][sid];
		console.log(oneSuite);
		console.log("Runmode in popup ", oneSuite, oneSuite['runmode']['@type'] );
	//alert(this.value);
		oneSuite['runmode']['@type'] = this.value; 
		popup.find("#runmode-at-value").show();
		if (oneSuite['runmode']['@type'] == 'standard') {
		popup.find("#runmode-at-value").hide();
		}
		
	});
	popup.find("#runmode-at-value").show();
	if (oneSuite['runmode']['@type'] == 'standard') {
		
		popup.find("#runmode-at-value").hide();

	}


	popup.find("#Execute-at-ExecType").on('change',function() {
			if (this.value == 'if' || this.value == 'if not') {
				popup.find('.rule-condition').show();			
			} else {
				popup.find('.rule-condition').hide();
			}
		});

	},



	mapProjectSuiteToUI: function(s,xdata) {

	// This is called from an event handler ... 
	// console.log(xdata);
	// console.log(s);
	// var oneSuite = xdata[s];
		var oneSuite = projectApp.jsonProjectObject['Testsuites']['Testsuite'][s];
		console.log(oneSuite);
		katana.$activeTab.find("#suiteRowToEdit").val(s); 
		katana.$activeTab.find("#suitePath").val(oneSuite['path']);
		katana.$activeTab.find("#Execute-at-ExecType").val(oneSuite['Execute']['@ExecType']); 
		katana.$activeTab.find("#executeRuleAtCondition").val(oneSuite['Execute']['Rule']['@Condition']); 
		katana.$activeTab.find("#executeRuleAtCondvalue").val(oneSuite['Execute']['Rule']['@Condvalue']); 
		katana.$activeTab.find("#executeRuleAtElse").val(oneSuite['Execute']['Rule']['@Else']); 
		katana.$activeTab.find("#executeRuleAtElsevalue").val(oneSuite['Execute']['Rule']['@Elsevalue']); 
		
		katana.$activeTab.find("#onError-at-action").val(oneSuite['onError']['@action']); 
		katana.$activeTab.find("#onError-at-value").val(oneSuite['onError']['@value']); 
		katana.$activeTab.find("#runmode-at-type").val(oneSuite['runmode']['@type'].toLowerCase()); 
		katana.$activeTab.find("#runmode-at-value").val(oneSuite['runmode']['@value']); 
		katana.$activeTab.find("#impact").val(oneSuite['impact']); 
		projectApp.fillProjectDefaultGoto();

	},

	fillProjectDefaultGoto : function() {
	
		var gotoStep = katana.$activeTab.find('#default_onError').val();
		var defgoto = katana.$activeTab.find('#default_onError_goto'); 
		
		if (gotoStep.trim() == 'goto'.trim()) { 
			defgoto.show();
		} else {
			defgoto.hide();
			
		}
		var listSuites = katana.$activeTab.find('#tableOfTestSuitesForProject tbody').children(); 
		defgoto.empty(); 
		for (xi=0; xi < listSuites.length; xi++) {
			defgoto.append($('<option>',{ value: xi,  text: xi+1}));
		}
	},

	fillProjectSuitePopupDefaultGoto : function(popup) {

		var gotoStep =popup.find('#onError-at-action').val();
		//console.log("Step ", gotoStep);
		var defgoto = popup.find('#onError-at-value'); 
		defgoto.hide();

		if (gotoStep.trim() == 'goto'.trim()) { 
			defgoto.show();
		} 
		//var sid = popup.find('#CaseRowToEdit').val();
		defgoto.empty(); 
		var xdata = projectApp.jsonProjectObject['Testsuites'] // ['Testcase'];
		if (!jQuery.isArray(xdata)) xdata = [xdata]; 
		for (var s=0; s<Object.keys(xdata).length; s++ ) {
			defgoto.append($('<option>',{ value: s,  text: s+1}));
		}
	},

/// -------------------------------------------------------------------------------
// This function is called to map the currently edited project suite to 
// the field being edited. 
// Note that this function is calld from an event handler which catches the 
// row number from the table.
/// -------------------------------------------------------------------------------
	mapUItoProjectSuite: function(popup, xdata){
	if (popup.find("#suitePath").val().length < 1) {
		alert("Please specify a suite path name");
		return
	}

	var s = parseInt(popup.find("#suiteRowToEdit").val());
	var oneSuite = projectApp.jsonProjectObject['Testsuites']['Testsuite'][s];
	oneSuite['path'] = popup.find("#suitePath").val(); 
	oneSuite['Execute'] = {}
	oneSuite['Execute']['@ExecType'] = popup.find("#Execute-at-ExecType").val(); 
	oneSuite['Execute']['Rule'] = {}
	oneSuite['Execute']['Rule']['@Condition']= popup.find("#executeRuleAtCondition").val(); 
	oneSuite['Execute']['Rule']['@Condvalue'] = popup.find("#executeRuleAtCondvalue").val(); 
	oneSuite['Execute']['Rule']['@Else'] = popup.find("#executeRuleAtElse").val(); 
	oneSuite['Execute']['Rule']['@Elsevalue'] = popup.find("#executeRuleAtElsevalue").val(); 
	oneSuite['impact'] = popup.find("#impact").val(); 
	oneSuite['onError']['@action'] = popup.find("#onError-at-action").val(); 
	oneSuite['onError']['@value'] = popup.find("#onError-at-value").val(); 
	oneSuite['runmode']['@type'] = popup.find("#runmode-at-type").val().toLowerCase(); 
	oneSuite['runmode']['@value'] = popup.find("#rumode-at-value").val(); 
	console.log("Saving", oneSuite);
},




	getSuiteDataFileForProject: function (tag) {
      var callback_on_accept = function(selectedValue) { 
      		console.log(selectedValue);
      		// Convert to relative path.
      		var pathToBase = katana.$activeTab.find('#savefilepath').text();
      		console.log("File path ==", pathToBase);
      		//var nf = katana.fileExplorerAPI.prefixFromAbs(pathToBase, selectedValue);
      		var nf = prefixFromAbs(pathToBase, selectedValue);
      		katana.$activeTab.find(tag).attr("value", nf);
      		katana.$activeTab.find(tag).attr("fullpath", selectedValue);
            };
      var callback_on_dismiss =  function(){ 
      		console.log("Dismissed");
	 };
     katana.fileExplorerAPI.openFileExplorer("Select a file", false , $("[name='csrfmiddlewaretoken']").val(), false, callback_on_accept, callback_on_dismiss);
},

getSuiteDataForProject: function () {
		  var popup = projectApp.lastPopup;
		  var tag = popup.find('#suitePath');
	      var callback_on_accept = function(selectedValue) { 
	      		console.log(selectedValue);
	      		var popup = projectApp.lastPopup;
		 		var tag = popup.find('#suitePath');
		 		console.log(tag);
	      		// Convert to relative path.
	      		var pathToBase = katana.$activeTab.find('#savefilepath').text();
	      		var nf = prefixFromAbs(pathToBase, selectedValue);
	      		console.log("File path ==", pathToBase, nf);
	      		popup.find("#suitePath").val(nf);
	      		//katana.$activeTab.find("#suitePath").val(nf);
	      		tag.attr("value", nf);
	      		tag.attr("fullpath", selectedValue);
	            };
	      var callback_on_dismiss =  function(){ 
	      		console.log("Dismissed");
		 };
	     katana.fileExplorerAPI.openFileExplorer("Select a file", false , $("[name='csrfmiddlewaretoken']").val(), false, callback_on_accept, callback_on_dismiss);
	},


	getResultsDirForProject: function() {
      var callback_on_accept = function(selectedValue) { 
      		console.log(selectedValue);
      		// Convert to relative path.
      		var pathToBase = katana.$activeTab.find('#savefilepath').text();
      		console.log("File path ==", pathToBase);
      		var nf = prefixFromAbs(pathToBase, selectedValue);
      		katana.$activeTab.find("#projectResultsDir").attr("value", nf);
      		katana.$activeTab.find("#projectResultsDir").attr("fullpath", selectedValue);

            };
      var callback_on_dismiss =  function(){ 
      		console.log("Dismissed");
	 };
     katana.fileExplorerAPI.openFileExplorer("Select a file", false , $("[name='csrfmiddlewaretoken']").val(), false, callback_on_accept, callback_on_dismiss);

	},
 


/*
Collects data into the global project data holder from the UI 

NOTE: At the time of writing I am using jQuery and Bootstrap to show the data.

Two global variables are heavily used when this function is called; 
1. jsonProjectObject 
2. jsonTestSuites which is set to point to the Testsuites data structure in
   the jsonProjectObject

*/
	 mapUiToProjectJson: function() {

	if (katana.$activeTab.find('#projectName').val().length < 1) {
		alert("Please Specify a Project Name ");
		return; 
	}

	if (katana.$activeTab.find('#projectTitle').val().length < 1) {
		alert("Please Specify a Project Title ");
		return; 
	}

	if (katana.$activeTab.find('#projectEngineer ').val().length < 1) {
		alert("Please Specify a Project Engineer  ");
		return; 
	}

	
	projectApp.jsonProjectObject['Details']['Name'] = katana.$activeTab.find('#projectName').val();
	projectApp.jsonProjectObject['Details']['Title'] = katana.$activeTab.find('#projectTitle').val();
	projectApp.jsonProjectObject['Details']['Engineer'] = katana.$activeTab.find('#projectEngineer').val();
	projectApp.jsonProjectObject['Details']['State'] = katana.$activeTab.find('#projectState').val();
	projectApp.jsonProjectObject['Details']['Date'] = katana.$activeTab.find('#projectDate').val();
	projectApp.jsonProjectObject['Details']['default_onError']['@action'] = katana.$activeTab.find('#default_onError').val();
	projectApp.jsonProjectObject['Details']['default_onError']['@value'] = katana.$activeTab.find('#default_onError_goto').val();
	projectApp.jsonProjectObject['Details']['Datatype'] = katana.$activeTab.find('#projectDatatype').val();
	projectApp.jsonProjectObject['SaveToFile'] = katana.$activeTab.find('#my_file_to_save').val();
	//
	// Now walk the DOM ..
	// Create dynamic ID values based on the Suite's location in the UI. 

	// Note that if we implement drag and drop we'll have to re-index the entire 
	// visual display to reflect the movements of the order of objects on display 
	// That would require a refresh after a drop anyway. 
	//;
	var url = "./projects/getProjectDataBack";
	var csrftoken = $("[name='csrfmiddlewaretoken']").val();

	$.ajaxSetup({
			function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
    	}
	});
	
	var topNode  = { 'Project' : projectApp.jsonProjectObject};


	$.ajax({
	    url : url,
	    type: "POST",
	    data : { 
	    	'json': JSON.stringify(topNode),
	    	//'Project': ns,
	    	'filetosave': katana.$activeTab.find('#filesavepath').text() + "/" + $('#my_file_to_save').val()
	    	},
	    headers: {'X-CSRFToken':csrftoken},
    
    success: function( data ){
        alert("Saved "+katana.$activeTab.find('#filesavepath').text() + "/" + $('#my_file_to_save').val());
    	}
	});

},

//
// This creates the table for viewing data in a sortable view. 
// 
	createSuitesTable: function() {
	var items = []; 
	items.push('<table id="suite_table_display" class="project-configuration-table striped" width="100%">');
	items.push('<thead>');
	items.push('<tr id="suiteRow"><th>Num</th><th/><th>Suite</th><th>Execute</th><th>OnError</th><th>Impact</th><th/></tr>');
	items.push('</thead>');
	items.push('<tbody>');
	console.log("Create suites for ", projectApp.jsonProjectObject); 
	projectApp.jsonTestSuites = projectApp.jsonProjectObject['Testsuites']; 
	console.log("Create suites for ", projectApp.jsonProjectObject['Testsuites']); 
	
	xdata = projectApp.jsonTestSuites['Testsuite'];
	console.log("Create suites for ", xdata, projectApp.jsonTestSuites); 
	katana.$activeTab.find("#tableOfTestSuitesForProject").html("");
	for (var s=0; s<Object.keys(xdata).length; s++ ) {
		var oneSuite = projectApp.jsonProjectObject['Testsuites']['Testsuite'][s];
	
		//console.log(xdata);
		if (oneSuite == null) {
			projectApp.jsonProjectObject['Testsuites']['Testsuite'][s] = {} ;
			oneSuite = projectApp.jsonProjectObject['Testsuites']['Testsuite'][s];
		}
		//console.log(oneSuite);
		projectApp.fillSuiteDefaults(s,projectApp.jsonProjectObject['Testsuites']['Testsuite']);
		//console.log(oneSuite);
		//console.log(oneSuite['path']);
		
		items.push('<tr data-sid="'+s+'">');
		items.push('<td>'+(parseInt(s)+1)+'</td>');
		var tbid = "textTestSuiteFile-"+s+"-id";

		var bid = "fileSuitecase-"+s+"-id";
		items.push('<td><i title="ChangeFile" class="fa fa-folder-open" key="'+bid+'" katana-click="projectApp.getFileForSuite" /></td>');
		
		oneSuite['Execute']['@ExecType'] = jsUcfirst(oneSuite['Execute']['@ExecType']); 
		items.push('<td id="'+tbid+'" katana-click="projectApp.showSuiteFromProject" key="'+oneSuite['path']+'">'+oneSuite['path']+'</td>');
		items.push('<td>Type='+oneSuite['Execute']['@ExecType']+'<br>');

		if (oneSuite['Execute']['@ExecType'] == 'if' || oneSuite['Execute']['@ExecType'] == 'if not') {
			items.push('Condition='+oneSuite['Execute']['Rule']['@Condition']+'<br>');
			items.push('Condvalue='+oneSuite['Execute']['Rule']['@Condvalue']+'<br>');
			items.push('Else='+oneSuite['Execute']['Rule']['@Else']+'<br>');
			items.push('Elsevalue='+oneSuite['Execute']['Rule']['@Elsevalue']+'<br>');
		}

		items.push('</td>');
		items.push('<td>'+oneSuite['onError']['@action']+'</td>');
		items.push('<td>'+oneSuite['impact']+'</td>');

		var bid = "deleteTestSuite-"+s+"-id";
		items.push('<td><i  title="Delete" class="fa fa-trash" value="X" key="'+bid+'" katana-click="projectApp.deleteTestSuiteCB"/>');

		bid = "editTestSuite-"+s+"-id";
		items.push('<i  title="Edit" class="fa fa-pencil" title="Edit" key="'+bid+'" katana-click="projectApp.editTestSuiteCB"/>');


		bid = "InsertTestSuite-"+s+"-id"
		items.push('<i  title="Insert" class="fa fa-plus" value="Insert" key="'+bid+'" katana-click="projectApp.insertTestSuiteCB"/>');

		bid = "DuplicateTestSuite-"+s+"-id"
		items.push('<i  title="Duplicate" class="fa fa-cc" value="Duplicate" key="'+bid+'" katana-click="projectApp.duplicateTestSuiteCB"/></td>');

		items.push('</tr>');
		}
		items.push('</tbody>');
		items.push('</table>');

		katana.$activeTab.find("#tableOfTestSuitesForProject").html( items.join(""));
		katana.$activeTab.find('#suite_table_display tbody').sortable( { stop: projectApp.testProjectSortEventHandler});
		projectApp.fillProjectDefaultGoto();
		katana.$activeTab.find('#default_onError').on('change',projectApp.fillProjectDefaultGoto );
	},


	getFileForSuite: function() {
			var fname = this.attr('key');
			var names = fname.split('-');
			var sid = parseInt(names[1]);
			katana.$activeTab.attr('project-suite-row',sid);
			projectApp.getResultsDirForProjectRow();
	},

	deleteTestSuiteCB : function(){
			var names = this.attr('key').split('-');
			var sid = parseInt(names[1]);
			projectApp.removeTestSuite(sid,xdata);
		},

	editTestSuiteCB : function(){
			var names = this.attr('key').split('-');
			var sid = parseInt(names[1]);
			console.log("xdata --> ", xdata);
			katana.popupController.open(katana.$activeTab.find("#editTestSuiteEntry").html(),"Edit..." + sid, function(popup) {
				projectApp.lastPopup = popup; 
				console.log(katana.$activeTab.find("#editTestSuiteEntry"));
				projectApp.setupProjectPopupDialog(sid,popup);
			});
		},

	insertTestSuiteCB : function(){
			var names = this.attr('key').split('-');
			var sid = parseInt(names[1]);
			console.log("xdata --> "+ xdata);
			projectApp.insertTestSuite(sid,xdata,0);
		},

	duplicateTestSuiteCB : function(){
			var names = this.attr('key').split('-');
			var sid = parseInt(names[1]);
			console.log("xdata --> "+ xdata);
			projectApp.insertTestSuite(sid,xdata,1);
		},

	getResultsDirForProjectRow: function() {
	      var callback_on_accept = function(selectedValue) { 
	      		console.log(selectedValue);
	      		// Convert to relative path.
	      		var sid = katana.$activeTab.attr('project-suite-row');
	      		var pathToBase = katana.$activeTab.find('#savefilepath').text();
	      		console.log("File path ==", pathToBase);
	      		var nf = prefixFromAbs(pathToBase, selectedValue);
	      		projectApp.jsonTestSuites['Testsuite'][sid]['path'] = nf;
	      		console.log("Path set to ",nf," for ", sid);
	      		console.log(projectApp.jsonTestSuites);
	      		projectApp.createSuitesTable();
	            };
	      var callback_on_dismiss =  function(){ 
	      		console.log("Dismissed");
		 };
	     katana.fileExplorerAPI.openFileExplorer("Select a file", false , $("[name='csrfmiddlewaretoken']").val(), false, callback_on_accept, callback_on_dismiss);
	},


	showSuiteFromProject:function () {
		var fname = katana.$activeTab.find('#showSuiteFromProject').attr('key');
	  	var xref="./suites/editSuite/?fname="+fname; 
	  	console.log("Calling suite ", fname, xref);
	    katana.$view.one('tabAdded', function(){
	        projectApp.mapFullSuiteJson(fname);
	    });
	  katana.templateAPI.load(xref, null, null, 'suite') ;;
	},

	testProjectSortEventHandler : function(event, ui ) {
		var listSuites = katana.$activeTab.find('#tableOfTestSuitesForProject tbody').children(); 
		console.log(listSuites);
				if (listSuites.length < 2) {
		 return; 
		}
		console.log(projectApp.jsonProjectObject["Testsuites"] );
		var oldSuitesteps = projectApp.jsonProjectObject["Testsuites"]['Testsuite'];
		var newSuitesteps = new Array(listSuites.length);
		console.log("List of ... "+listSuites.length);
		for (xi=0; xi < listSuites.length; xi++) {
			var xtr = listSuites[xi];
			var ni  = xtr.getAttribute("data-sid");
			console.log(xi + " => " + ni);
			newSuitesteps[ni] = oldSuitesteps[xi];
			}

		console.log(projectApp.jsonProjectObject);
		projectApp.jsonProjectObject["Testsuites"]['Testsuite']= newSuitesteps;
		console.log(projectApp.jsonProjectObject["Testsuites"] );
		
		projectApp.jsonTestSuites = projectApp.jsonProjectObject['Testsuites'] 
		projectApp.mapProjectJsonToUi();

	},

	copyTestSuite: function (src,dst) { 
		var dst = jQuery.extend(true, {}, src); 
		return dst; 
	},

	fillSuiteDefaults: function(s, data){
		if(data[s] == null) {
			data[s] = {} ;
		}    
		oneSuite = data[s];

		if (!oneSuite['path']) {
			oneSuite['path'] =  "New";
		}

		if (!oneSuite['impact']) {
			oneSuite['impact'] =  "impact";
		}

		if (! oneSuite['Execute']){
			oneSuite['Execute'] = { "@ExecType": "yes", 
					"Rule": { "@Condition": "", "@Condvalue": "", "@Else": "next", "@Elsevalue": "" }
				}; 
		}
		if (! oneSuite['Execute']['@ExecType']){
				oneSuite['Execute']['@ExecType'] = "yes";
		}
		if (!oneSuite['Execute']['Rule']) {
				oneSuite['Execute']['Rule'] = { "Rule": { "@Condition": "", "@Condvalue": "", "@Else": "next", "@Elsevalue": "" } };
		}
		if (! oneSuite['onError']) {
			oneSuite['onError'] = { "@action": "next", "@value": "" };
		}
		if (! oneSuite['runmode']) {
			oneSuite['runmode'] = { "@type": "standard", "@value": "" };
		}
		if (! oneSuite['retry']) {
			oneSuite['retry'] = { "@type": "next", "@Condition": "", "@Condvalue": "", "@count": "" , "@interval": ""};
		}

	},
/*
// Shows the global project data holder in the UI.

NOTE: At the time of writing I am using jQuery and Bootstrap to show the data.

Two global variables are heavily used when this function is called; 
1. jsonProjectObject 
2. jsonTestSuites which is set to point to the Testsuites data structure in
   the jsonProjectObject

*/
	mapProjectJsonToUi: function(){
		if (!jQuery.isArray(projectApp.jsonTestSuites)){
		 projectApp.jsonTestSuites = [projectApp.jsonTestSuites]; 
		}
		projectApp.createSuitesTable();
		projectApp.fillProjectDefaultGoto();
	},  // end of function 

	saveChangesToRowCB: function() {
			projectApp.mapUItoProjectSuite( projectApp.lastPopup, xdata );
			katana.popupController.close(projectApp.lastPopup);
			projectApp.mapProjectJsonToUi();
	},

// Removes a test suite by its ID and refresh the page. 
	removeTestSuite: function( sid,xdata ){
		projectApp.jsonTestSuites['Testsuite'].splice(sid,1);
		console.log("Removing test suites "+sid+" now " + Object.keys(projectApp.jsonTestSuites).length);
		mapProjectJsonToUi();	// Send in the modified array
	},
// Removes a test suite by its ID and refresh the page. 
	insertTestSuite: function( sid,xdata, copy ){
			var newTestSuite = projectApp.makeNewSuite();	
			if (copy == 1) {
				newTestSuite = jQuery.extend(true, {}, xdata[sid]); 
			}
		projectApp.jsonTestSuites['Testsuite'].splice(sid,0,newTestSuite);
		console.log("insertining test suites at"+sid+" now " + Object.keys(projectApp.jsonTestSuites).length);
		projectApp.mapProjectJsonToUi();	// Send in the modified array
	},

};