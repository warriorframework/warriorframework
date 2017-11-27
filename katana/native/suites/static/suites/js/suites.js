//
//
/*
/// -------------------------------------------------------------------------------

Suite File Data Handler 

Author: 
Date: 

The functions in this module are designed specifically for handling Suite XML files
for the warrior framework. 

It is expected to work with the editSuite.html file and the calls to editSuite in 
the views.py python for Django. 
/// -------------------------------------------------------------------------------

*/ 

class suiteDetailsObject{

	mapJSONdataToSelf(jsonDetailsData) {
			console.log(jsonDetailsData);
				
			this.fillDefaults();           // Fills internal values only
			console.log(jsonDetailsData);
				
			if (jsonDetailsData) {         // Overridden by incoming data.
				this.Name = jsonDetailsData['Name'];  
				this.Title = jsonDetailsData['Title']; 
				this.Category = jsonDetailsData['Category']; 
				this.Engineer = jsonDetailsData['Engineer']; 
				this.Resultsdir = jsonDetailsData['Resultsdir']; 
				this.State = jsonDetailsData['State']; 
				this.InputDataFile = jsonDetailsData['InputDataFile'];
				// Fill only if they exist...
				if (jsonDetailsData['default_onError']) {
					if ( jsonDetailsData['default_onError']['@action']) this.default_onError_action = jsonDetailsData['default_onError']['@action']; 
					if ( jsonDetailsData['default_onError']['@value'] ) this.default_onError_value = jsonDetailsData['default_onError']['@value']; 			
				}
				if ( jsonDetailsData['type']['@exectype'] )this.ExecType = jsonDetailsData['type']['@exectype']; 
				if ( jsonDetailsData['type']['@Num_attempts']) this.ExecType_num_attempts = jsonDetailsData['type']['@Num_attempts']; 
				if ( jsonDetailsData['type']['@Max_attempts']) this.ExecType_max_attempts = jsonDetailsData['type']['@Max_attempts']; 
			}
	}

	getJSON(){
		return { 
			'Name': this.Name, 
			'Title': this.Title,
			'Category' : this.Category, 
			'Engineer' : this.Engineer, 
			'Resultsdir' : this.Resultsdir, 
			'State' : this.State,
			'Time': this.cDate,
			'Date' : this.cTime,

			'default_onError': { '@action': this.default_onError_action, '@value': this.default_onError_value},
			'InputDataFile' : this.InputDataFile,
			'type' : { "@exectype":this.ExecType,'@Number_Attempts': this.ExecType_num_attempts, '@Max_Attempts':  this.ExecType_max_attempts}
		};
	}

	constructor(jsonDetailsData) {
			this.mapJSONdataToSelf(jsonDetailsData);
	}

	setTimeStamp() { 
		var date = new Date();
	   	var year = date.getFullYear();
	   	var month = date.getMonth() + 1;// months are zero indexed
	   	var day = date.getDate();
	   	var hour = date.getHours();
	   	var minute = date.getMinutes();
	   	if (minute < 10) {
	       	minute = "0" + minute; 
	       }
		this.cDate = month + "/" + day + "/" + year; 
		this.cTime = hour + ":" + minute; 
	}


	fillDefaults() {
		this.Name = '';  
		this.Title = ''; 
		this.Category = ''; 
		this.Engineer = ''; 
		this.Resultsdir = ''; 
		this.State = ''; 
		this.default_onError_action = ''; 
		this.default_onError_value = ''; 
		this.InputDataFile = '';
		
		this.ExecType = ''; 
		this.ExecType_num_attempts = ''; 
		this.ExecType_max_attempts = ''; 
		this.setTimeStamp();
	}

	duplicateSelf() { 
		return jQuery.extend(true, {}, this); 
	}

	getSummary(){
		var rstr = "Name: "+this.Name+"<br>Title: " + this.Title + "<br>Category: " + this.Category + "<br>Engineer: " + this.Engineer + "<br>State: " + this.State; 
		return rstr; 
	}
}



class suiteRequirementsObject{

	constructor (jsonRequirements) { 
		this.aRequirements = [];
		if (!jsonRequirements) return this; 
		for (var k =0; k < jsonRequirements.length; k++ ) {
			this.aRequirements.push(jsonRequirements[k]);
		}
	}

	getJSONdata() {
		return this.aRequirements; 
		// var r = [];
		// for (var k=0; k < this.aRequirements.length; k++) {
		// 	r.push( this.aRequirements[k] );
		// }
		// return r ;  // this matches the XML ... 
	}

	insertRequirement(where,what){
		this.aRequirements.splice(where,0,what);
	}

	getRequirements() {
		return this.aRequirements;
	}



	getLength() {
		return this.aRequirements.length; 
	}

	setRequirement(s,v){
		this.aRequirements[s]=v;
	}

	deleteRequirement(s) {
		this.aRequirements.splice(s,1);
	}
}

class suiteCaseObject {
	constructor(inputJsonData) {
		var jsonData = inputJsonData;
		this.setupFromJSON(jsonData);
	}

	setupFromJSON(jsonData) { 
		if (!jsonData) {
			jsonData = 	this.createEmptyCase(); 
		}
		// Fill defaults here. 
		this.fillDefaults(jsonData);
		this.path = jsonData['path'];
		this.context = jsonData['context'].toLowerCase();
		this.runtype = jsonData['runtype'].toLowerCase();
		this.impact = jsonData['impact'].toLowerCase();
		this.InputDataFile = jsonData['InputDataFile'];
		this.runmode_value = jsonData['runmode']['@value'].toLowerCase();
		this.runmode_type = jsonData['runmode']['@type'].toLowerCase();
		this.Execute_ExecType = jsonData['Execute']['@ExecType'].toLowerCase();
		this.Execute_Rule_Condition = jsonData['Execute']['Rule']['@Condition'].toLowerCase();
		this.Execute_Rule_Condvalue = jsonData['Execute']['Rule']['@Condvalue'];
		this.Execute_Rule_Else = jsonData['Execute']['Rule']['@Else'].toLowerCase();
		this.Execute_Rule_Elsevalue = jsonData['Execute']['Rule']['@Elsevalue'];
		this.onError_action = jsonData['onError']['@action'];
		this.onError_value = jsonData['onError']['@value'];	

	}

	getJSON(){
		return {
			'path': this.path,
			'context': this.context,
			'runtype': this.runtype,
			'impact': this.impact,
			'InputDataFile' : this.InputDataFile,
			'runmode' : { "@value": this.runmode_value, "@type": this.runmode_type },
			'onError': { "@action": this.onError_action, "@value": this.onError_value },
			'Execute': { "@ExecType": this.Execute_ExecType, 
				"Rule": { "@Condition": this.Execute_Rule_Condition, "@Condvalue": this.Execute_Rule_Condvalue , 
					"@Else": this.Execute_Rule_Else , "@Elsevalue": this.Execute_Rule_Elsevalue } 
			},
		};

	}

	copyToDocument(tag, obj) {
		localStorage.setItem(tag, JSON.stringify(obj.getJSON()));
	}

	copyFromDocument(tag) {
		return JSON.parse(localStorage.getItem(tag));
	}

	fillDefaults(jsonData){

		if (!jsonData['path'] ) {
			jsonData['path'] = "";
		}
		if (!jsonData['context'] ) {
			jsonData['context'] = 'postive'; 
		}
		if (!jsonData['runtype']) {
			jsonData['runtype'] = 'sequential_keywords'; 
		}
		if (!jsonData['impact'] ) {
			jsonData['impact'] = 'impact';
		}

		if (! jsonData['runmode']) {
			jsonData['runmode'] = { "@type": "standard", "@value": "" };
		}
		if (! jsonData['runmode']['@value']) {
			jsonData['runmode'] = { "@type": "standard", "@value": "" };
		}
		if (! jsonData['runmode']['@type']) {
			jsonData['runmode'] = { "@type": "standard", "@value": "" };
		}

		if (!jsonData['onError']) {
			jsonData['onError'] = { "@action": "next", "@value": "" };
		}
		if (!jsonData['onError']['@action']) {
			jsonData['onError']['@action'] = "";
		}
		if (!jsonData['onError']['@value']) {
			jsonData['onError']['@value'] = "";
		}

		if (!jsonData['Execute']) {
			jsonData['Execute'] = { "@ExecType": "yes", "Rule": { "@Condition": "", "@Condvalue": "", "@Else": "next", "@Elsevalue": "" } };
		}
		if (!jsonData['Execute']['@ExecType']) {
			jsonData['Execute'] = { "@ExecType": "yes", "Rule": { "@Condition": "", "@Condvalue": "", "@Else": "next", "@Elsevalue": "" } };
		}
		if (!jsonData['Execute']['Rule']) {
			jsonData['Execute'][ "Rule"] = { "@Condition": "", "@Condvalue": "", "@Else": "next", "@Elsevalue": "" } ;
		}
		return jsonData;

	}

	createEmptyCase() {
		return {
			'path': '',
			'context': 'positive',
			'runtype': 'sequential_keywords',
			'impact' : 'impact',
			'runmode' : { "@value": "standard", "@type": "" },
			'onError': { "@action": "next", "@value": "" },
			'Execute': { "@ExecType": "yes", 
				"Rule": { "@Condition": "", "@Condvalue": "", "@Else": "next", "@Elsevalue": "" } 
			},
		};

	}
}


class testSuiteObject{
	constructor(jsonData){
		this.mapJsonData(jsonData);
	}
	mapJsonData(jsonData){ 
			console.log("In constructor", jsonData);
			if (!jsonData['Details']) {
				this.Details = new suiteDetailsObject(null);
			} else {
				this.Details = new suiteDetailsObject(jsonData['Details'])
			}

			if (!jsonData['Requirements']) {
				jsonData['Requirements'] = [] 
			} 
			if (!jsonData['Requirements']['Requirement']) {
				jsonData['Requirements']['Requirement']= [] 
			}
			if (!jQuery.isArray(jsonData['Requirements']['Requirement'] )) {
				jsonData['Requirements']['Requirement'] = [jsonData['Requirements']['Requirement']];
			}

			this.Requirements = new suiteRequirementsObject(jsonData['Requirements']['Requirement']);
			console.log("After", jsonData['Testcases']);
			
			if (!jsonData['Testcases']) {
				jsonData['Testcases']['Testcase'] = [] 
			} 
			if (!jsonData['Testcases']['Testcase']) {
				jsonData['Testcases']['Testcase'] = [] 
			} 
			//
			if (!jQuery.isArray(jsonData['Testcases']['Testcase'])) {
			 jsonData['Testcases']['Testcase'] = [ jsonData['Testcases']['Testcase'] ];
			}

			this.Testcases = [];
			for (var k=0; k<jsonData['Testcases']['Testcase'].length; k++) {	
				var ts = new suiteCaseObject(jsonData['Testcases']['Testcase'][k]);
				this.Testcases.push(ts);
				}
			// 
			}

		getJSON(){
			var testcasesJSON = [];
			for (var ts =0; ts< this.Testcases.length; ts++ ) {
				testcasesJSON.push(this.Testcases[ts].getJSON());
			}
			console.log("testCases", testcasesJSON);

			return { 'Details': this.Details.getJSON(), 
				'Requirements' : { 'Requirement': this.Requirements.getJSONdata() },
				'Testcases' : { 'Testcase':  testcasesJSON } };
		}

	}



var suites= {

	treeView : 0,
	jsonSuiteObject : null,
	jsonTestcases : null,			// for all Cases
	
	startNewSuite: function() {
	  var xref="./suites/editSuite/?fname=NEW"; 
	  katana.templateAPI.load(xref, null, null, 'SuiteNew') ;
	   katana.$view.one('tabAdded', function(){
	      suites.mapFullSuiteJson("NEW");
	  });
	},


	initSuiteTree: function(){
		//console.log("Starting suite ");
		jQuery.getJSON("./suites/getSuiteListTree/").done(function(data) {
			var sdata = data['treejs'];
			console.log("tree ", sdata);
			//var jdata = { 'core' : { 'data' : sdata }}; 
			var jdata = { 'core' : { 
    			'data' : sdata },
    		"plugins" : [ "sort" ],
    		}; 
			
			
			katana.$activeTab.find('#mySuiteTree').on("select_node.jstree", function (e, data) { 
			      var thePage = data.node.li_attr['data-path'];
			      console.log(thePage);
			      var extn = thePage.indexOf(".xml");
			      if (extn < 4){
			        return;
			      }
			 	//     katana.$view.one('tabAdded', function(){
			 	//     suites.mapFullSuiteJson(thePage);
		  		// });
		  	  	suites.thefile = thePage; 
		  		var xref="./suites/editSuite/?fname=" + thePage; 
			  	//katana.$activeTab.find("#OverwriteSuiteHere").load(xref, function() {
			  		katana.templateAPI.subAppLoad(xref, null, function(thisPage) { 
		
			   			console.log("starting ...", this);
				  		suites.mapFullSuiteJson(suites.thefile);
				  });


		  		//katana.templateAPI.load(xref, null, null, 'Suite') ;
				});
			create_jstree_search('#mySuiteTree', '#jstreeFilterText' , sdata);
		
			//katana.$activeTab.find('#mySuiteTree').jstree(jdata); 
		});

	},



	createD3treeData: function(tdata) {
		suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
		suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
		
		existingCases = katana.$activeTab.data('allExistingCases');

		pjDataSet = { 
			'nodes': [],
			'edges': [],

		};

		pjExistingSuites = { 
			'nodes': [],
			'edges': []
		};
		var nodeCtr = 0;
		var suiteSummary = suites.jsonSuiteObject.Details.getSummary();
		var td = {
		"name": suites.jsonSuiteObject.Details.Name,
		"id": nodeCtr++,
		"rowid": 0,
    	"parent": "null", 
    	"children": [],
    	"ntype": 'suite',
    	"displayStr": suiteSummary,
    	};
    	pjDataSet.nodes.push(td);
    	var slen = suites.jsonTestcases.length;
		for (var s=0; s<slen; s++ ) {
			var sid = parseInt(s) + 1; 
    		var oneCase = suites.jsonSuiteObject.Testcases[s];
    		var items = [];
    		items.push('ExecType='+oneCase.Execute_ExecType+'<br>');
			if (oneCase.Execute_ExecType == 'if' || oneCase.Execute_ExecType == 'if not') {
				items.push('Condition='+oneCase.Execute_Rule_Condition+'<br>');
				items.push('Condvalue='+oneCase.Execute_Rule_Condvalue+'<br>');
				items.push('Else='+oneCase.Execute_Rule_Else+'<br>');
				items.push('Elsevalue='+oneCase.Execute_Rule_Elsevalue+'<br>');
			}
			var execStr = items.join("");
			var displayStr = "" + oneCase.path + "<br>runmode:" + oneCase.runmode_type + " " + oneCase.runmode_value + 
					"<br>onError:" + oneCase.onError_action + " " + oneCase.onError_value + 
					"<br>" + execStr + "</div>"; 

    		var st = { "name": oneCase.path, 
    			'ntype': 'suite',
    			'type': 'suite',
    			"id": nodeCtr,
    			"rowid" : sid,
    			"width" : 100, 
    			'displayStr' : displayStr,
    			"exectype" : execStr, 
    			"runmode" : oneCase.runmode_type + " " + oneCase.runmode_value,
    			'on-error' : oneCase.onError_action + " " + oneCase.onError_value,
    			"data-path": oneCase.InputDataFile 
    			} ;
    		pjDataSet.nodes.push(st);
    		
			var ed = { 'source': pjDataSet.nodes[nodeCtr - 1], 'target': pjDataSet.nodes[nodeCtr], 'value' : 3 };
    		
    		pjDataSet.edges.push(ed);
    		nodeCtr++;
    		}
  
    	katana.$activeTab.data('pjDataSet', pjDataSet);
    	katana.$activeTab.data('pjExistingSuites', pjExistingSuites);
    	suites.createD3tree();
	},
	

	createD3tree: function() {

		var px_suite_column = 200; 
		var px_row_height = 60; 
		var px_y_icon_offset = 35;
		var px_text_x_offset = 10; 
		var px_text_y_offset = 30;
		var px_rect_width = 200; 
		var px_rect_height = 35;
		var px_trash_x_offset = px_rect_width  - 20; 
		var px_trash_y_offset = 20; 
		var px_folder_offset = 25;
		var px_edit_x_offset = px_rect_width  - 20;
		var px_edit_y_offset = 0;
		var px_insert_x_offset = 0;
		var px_insert_y_offset = 20;
		var px_existing_column = 700;

		suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
		suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 

		suites.treeData = katana.$activeTab.data('suitesTreeData');
		existingSuites= katana.$activeTab.data('allExistingSuites');
		
    	var pjDataSet = katana.$activeTab.data('pjDataSet');
    	var pjExistingSuites = katana.$activeTab.data('pjExistingSuites');
		var optimalHt = existingSuites.length * px_row_height + (px_row_height * 2); 
		if (optimalHt < 2000) { optimaalHt = 2000; }
		var optimalWd = katana.$activeTab.find("#suitesMasterPage").width();
		var margin = {top: 20, right: 120, bottom: 20, left: 120},
					 width = optimalWd - margin.right - margin.left,
					 height = optimalHt - margin.top - margin.bottom;
		var linkDistance = 100; 

		katana.$activeTab.find("[g3did='suites-3d-tree']").attr('id', suites.jsonSuiteObject.Details.Name);
		var useID = '#' + suites.jsonSuiteObject.Details.Name;
		console.log("Creating for ", useID);
		
		d3.select("[useID='" + useID + "']").remove();  // Clear the screen. 
		suites.svg = d3.select(useID).append("svg")
			 .attr("width", width + margin.right + margin.left)
			 .attr("height", height + margin.top + margin.bottom)
			 .attr("useID", useID)
			 .append("g")
			 .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
		katana.$activeTab.data('suitesSVG', suites.svg);
	
		// suites.svg.append('defs').append('marker')
  //       	.attr({'id':'arrowhead',
  //              'viewBox':'-0 -5 10 10',
  //              'refX':25,
  //              'refY':0,
  //              'orient':'auto',
  //              'markerWidth':10,
  //              'markerHeight':10,
  //              'xoverflow':'visible'})
  //       	.append('svg:path')
  //           .attr('d', 'M 0,-5 L 10 ,0 L 0,5')
  //           .attr('fill', '#666')
  //           .attr('stroke','#ccc');

  //      	defs  = suites.svg.append('defs');

		// suites.filter = defs.append("filter").attr("id","drop-shadow").attr("height","150%");
		// suites.filter.append("feGaussianBlur").attr("in","SourceAlpha").attr("stdDeviation",5)
		// 	.attr("result","blur");
		// suites.filter.append("feOffset").attr("in","blur")
		// 	.attr("dx",5)
		// 	.attr("dy",5)
		// 	.attr("result", "offsetBlur");
		// suites.feMerge = suites.filter.append("feMerge");
		// suites.feMerge.append("feMergeNode").attr("in","offsetBlur");
		// suites.feMerge.append("feMergeNode").attr("in","SourceGraphic");

		suites.dragSuite = d3.behavior.drag()
			  		.on('drag', function(d,i) {
			  			if (d.id == 0) return;

		 				d.x = d3.event.x;
		            	d.y = d3.event.y;
		            	//console.log('x =', d3.event.x, ", y=", d3.event.y)
		            	d3.select(this).attr("transform", function(d,i){
		                return "translate(" + [ d.x,d.y ] + ")"
		            	})
			  		}).on('dragend', function(d,i) {
						if (d.id == 0) return;

	  					suites.jsonSuiteObject = katana.$activeTab.data('suiteJSON');
						suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
						suites.treeData = katana.$activeTab.data('suitesTreeData');
						existingSuites= katana.$activeTab.data('allExistingSuites');
			  			console.log("Drag end", d, i);

			  		
						if ((d.type == 'file'  ) && (d.x < (-px_rect_width))) {
								var loc = parseInt( 0.5 + ( d.y / px_row_height)); 
								//console.log("Location = ", loc, " fname = ", d.name);
								console.log("Location", loc, d);
								var pathToBase = katana.$activeTab.find('#savefilepath').text();
	      						var nf = prefixFromAbs(pathToBase, d.path);
	      						console.log("Adding ..", nf);
								suites.jsonSuiteObject = katana.$activeTab.data('suiteJSON');
								suites.jsonTestSuites = suites.jsonSuiteObject['Testcases']; 
								var sid  = suites.jsonTestSuites.length;
								if (loc > sid) loc = sid 
								var nb = new suiteCaseObject();
								nb.path = nf; 
								suites.jsonTestSuites.splice(loc,0,nb);
								suites.mapSuiteJsonToUi();  // This is where the table and edit form is created. 
								return ;
			  				}
			  			

			  			// 	if (d.id > suites.jsonTestSuites.length  && d.ntype == 'existingSuite') {
								// console.log("You are inserting ...", d);
								// // Location??
								// var loc = parseInt( 0.5 + ( d.y / px_row_height)); 
								// console.log("Location = ", loc, " fname = ", d.name);
								// var pathToBase = katana.$activeTab.find('#savefilepath').text();
      		// 					var nf = prefixFromAbs(pathToBase, d.name);
      		// 					console.log("Adding ..", nf);
								// suites.jsonSuiteObject = katana.$activeTab.data('suitesJSON');
								// suites.jsonTestSuites = suites.jsonSuiteObject['Testcases']; 
								// var sid  = suites.jsonTestSuites.length;
								// if (loc > sid) loc = sid 
								// var nb = new projectSuiteObject();
								// nb.path = nf; 
								// suites.jsonTestSuites.splice(loc,0,nb);
								// suites.mapProjectJsonToUi();	// Send in the modified array
			  			// 	}
			  			if (d.x < (px_existing_column -px_rect_width) && d.ntype == 'suite' && (d.x >px_suite_column )){
							var theId = d.id -1;
							if (theId < suites.jsonTestSuites.length  && d.ntype == 'suite') {
								// d points to the location ... 
								suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
								suites.treeData = katana.$activeTab.data('suitesTreeData');
								var loc = parseInt( 0.5 + ( d.y / px_row_height)); 
								var sid  = suites.jsonTestSuites.length;
								if (loc > sid) loc = sid 
								console.log("You are rearranging nodes. ...", d.id, loc);
								var oldSuite = jQuery.extend(true, {},suites.jsonSuiteObject.Testsuites[theId]);
								suites.jsonSuiteObject.Testsuites[theId] = suites.jsonSuiteObject.Testsuites[loc]
								suites.jsonSuiteObject.Testsuites[loc] = oldSuite
							suites.mapSuiteJsonToUi();  // This is where the table and edit form is created. 
								return ;
			  				}

		
			  				
			  			}
			  			if ((d.type =='file')||(d.type =='directory')) {
			  				suites.svg.select(".existingSuiteNode").remove();
			  				suites.createExistingTree();
			  			}
			  			
			  			
			  	});





		var gnodes = suites.svg.selectAll('g')
				.data(pjDataSet.nodes)
				.enter()
				.append('g')
				.attr("transform",function(d) { 
					var py = (d.rowid - 1) * px_row_height;
					if (d.ntype == "project") return "translate("+10+","+px_rect_height*2+")";
					if (d.ntype == 'existingSuite') {
						var i = d.rowid - 1;
						var xlen = Math.floor(pjExistingSuites.nodes.length / 3); 
						var px = px_existing_column + ((i%3)*px_rect_width + 50); 
						py = Math.floor(i/3)%xlen * px_row_height;


						return "translate("+px+","+py+")";
					} 
					return "translate("+px_suite_column+","+py+")";
					})
				.attr('class', 'masternode')
				.call(suites.dragSuite);

		//var eNodes = suites.svg.selectAll(".project-d3-existing-type");

		suites.createExistingTree();

		// force.on('end', function() {
		// 			var mNodes = suites.svg.selectAll(".project-d3-existing-type");
		
		// 			mNodes.attr("x", function(d) { return d.x; })
  //       				  .attr('y', function(d) { return d.y; });
 
		// 			mylinks.attr('x1', function(d) { return d.source.x; })
		// 			        .attr('y1', function(d) { return d.source.y; })
		// 			        .attr('x2', function(d) { return d.target.x; })
		// 			        .attr('y2', function(d) { return d.target.y; });
		// 		});
		


		gnodes.append("rect")
	   		.attr("width",function(d){ 
					if (d.ntype == 'project') return px_rect_width * 0.6;
   					return px_rect_width; 
   			})
   			.attr("height",function(d){ 
					if (d.ntype == 'project') return px_rect_height * 4;
   					return px_rect_height; 
   			})
   			.attr("x", 0)
   			.attr("y", 0)
   			.attr("rx", function(d){ 
					if (d.ntype == 'project') return 5;
   					if (d.ntype == 'existingSuite') return 8;
   					return 3; 
   			})
   			.attr('fill', function(d){ 
					if (d.ntype == 'project') return '#42f49b';
   					if (d.ntype == 'suite') return 'steelblue';
   					return 'white'; 
   			})
   			.attr('class',function(d) { 
   						//console.log("Setting circle", d);	
						if (d.ntype == 'existingSuite') { 
								return "project-d3-existing-type";
							}
						return "project-d3-node";})
   			.style('stroke-width', 3)
   			.style('stroke', function(d) { 
   				if (d.ntype == 'project') return 'blue';
   				return 'darkblue';

   			})
   			.on("mouseover",function(d) {
   					// var dx = d3.mouse(this)[0];
   					// var dy = d3.mouse(this)[1];
   					// console.log(dx,dy, "x=", d3.event.pageX, " y=", d3.event.pageY, "d.x", d.x, ",", d.y , d.rowid, d.id);
   					var py = (d.rowid - 1) * px_row_height;
   					var px = px_suite_column + px_rect_width;

   					if (d.rowid == 0) {
   						py = px_row_height;
   						px = px_suite_column - px_rect_width/2;
   					}

					if (d.ntype == 'existingSuite') {
						var i = d.rowid - 1;
						var xlen = Math.floor(pjExistingSuites.nodes.length / 3); 
						var px = px_existing_column + ((i%3)*px_rect_width + 50); 
						py = Math.floor(i/3)%xlen * px_row_height;
					}



   					var fobj = suites.svg.append('foreignObject')
						.attr('x', px+20)
						.attr('y', py+20)
						.attr('width', 450)
						.attr('class', 'projectSuiteTooltip')
						;
						var div = fobj.append("xhtml:div")
						.append('div')
						.attr('border-bottom-width', 10)
   						.attr('border-right-width', 10)
   			
						.attr('x',  0)
						.attr('y',  0)					
						.style({
							'opacity': 1.0,
							'border' : '2px solid "green"',
						});
						div.append('p')
						.style('border', '2px solid green')
						.style('background-color','white')
						.style('opacity', 1)
						.html(d.displayStr);
					//var foHt = div[0][0].getBoundingClientRect().height;
					//var foWd = div[0][0].getBoundingClientRect().width;
   				})
   			.on("mouseout",function(d) {
   		 			suites.svg.selectAll('.projectSuiteTooltip').remove();
   				})
   			.on("click",function(d) {
   		 			if (d.ntype == 'project') {
   		 				//suites.editDetailsAsPopup();
   		 			}
   				});


 		gnodes.append("foreignObject")
	   				.attr("width", 20)
	   				.attr("height", 20)
	   				.attr("y", px_trash_y_offset)
	   				.attr("x", px_trash_x_offset)
	   				.attr("class", "fa fa-trash")
	   				.attr("deleteNodeid",function(d) { return d.rowid - 1; })
	   				.style("opacity", 1)
	   				.style("fill-opacity",1)
	   				.style("visibility", function(d) {
	   					if (d.ntype != 'suite') {
	   						return "hidden";
	   					} else {
	   						return "visible";
	   					}
	   				})
	   				.html(function(d) { return " "; } )
	   				.on("click", function(d) { 
	   						//console.log("cccc, ", d, this);
		   					if (this.hasAttribute('deleteNodeid')) {
	   							//console.log("Clicked to delete " + d.rowid);


	   							suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
								suites.jsonTestcases = suites.jsonSuiteObject.Testcases	
								suites.jsonTestcases.splice(d.rowid-1,1);
								console.log(suites.jsonTestcases);
								suites.createCasesTable();
								suites.createD3treeData(); 
								suites.createD3tree();
	   					
	   							
							
	   						}
	   						event.stopPropagation();
	   				});

 			
	   			gnodes.append("foreignObject")
	   				.attr("width", 20)
	   				.attr("height", 20)
	   				.attr("y", px_insert_y_offset)
	   				.attr("x", px_insert_x_offset)
	   				
	   				// .attr("y", function(d) {  return px_y_icon_offset + ( d.rowid * px_row_height); })
	   				// .attr("x", function(d) { 
	   				// 	if (d.ntype == 'project') return 10; 
	   				// 	return px_suite_column + px_insert_offset; 
	   				// })
	   				.attr("class", "fa fa-plus")
	   				.attr("addNodeid",function(d) { return d.rowid - 1; })
	   				.style("opacity", 1)
	   				.style("fill-opacity",1)
	   				.style("visibility", function(d) {
	   					if (d.ntype != 'suite') {
	   						return "hidden";
	   					} else {
	   						return "visible";
	   					}
	   				})
	   				.html(function(d) { return " "; } )
	   				.on("click", function(d) { 
	   						//console.log("cccc, ", d, this);
		   					if (this.hasAttribute('addNodeid')) {
	   							//console.log("Clicked to add " + d.rowid);
								var newTestcase =	new suiteCaseObject(); 
								suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
								suites.jsonTestcases = suites.jsonSuiteObject.Testcases	
								console.log(suites.jsonTestcases);
								suites.jsonTestcases.push(newTestcase);	
								suites.createCasesTable();
								suites.createD3treeData(); 
								suites.createD3tree();
	   						}
	   						event.stopPropagation();
	   				});



	   			gnodes.append("foreignObject")
	   				.attr("width", 20)
	   				.attr("height", 20)
	   				.attr("y", px_edit_y_offset)
	   				.attr("x", px_edit_x_offset)
	   				
	   				.attr("class", "fa fa-pencil")
	   				.attr("editNodeid",function(d) { return d.rowid; })
	   				.style("opacity", 1)
	   				.style("fill-opacity",1)
	   				.style("visibility", function(d) {
	   					if (d.ntype != 'suite') {
	   						return "hidden";
	   					} else {
	   						return "visible";
	   					}
	   				})
	   				.html(function(d) { return " "; } )
	   				.on("click", function(d) { 
	   						// console.log("cccc, ", d, this);
		   					if (this.hasAttribute('editNodeid')) {
	   							// console.log("Clicked ...", d, this, this.hasAttribute('deleteNodeid'));
									var sid = d.rowid-1;
								katana.popupController.open(katana.$activeTab.find("#editTestSuiteEntry").html(),"Edit..." , function(popup) {
									suites.lastPopup = popup; 
									// console.log(katana.$activeTab.find("#editTestSuiteEntry"));
									suites.mapSuiteCaseToUI(sid,popup);
								});
	   						}
	   						event.stopPropagation();
	   				});



    	var nodelabels = gnodes.append("text")
	       .attr("class","nodelabel")
	       .attr("x", 10)
		   .attr("y", px_rect_height / 2)
	       .attr("stroke","black")
	       .text(function(d){
	       		if (d.ntype == 'existingSuite') return  d.displayStr.substring(0,20);
	       		if (d.ntype == 'project') return d.name.substring(0,20);
	       		return "(" + d.rowid + ") ..." + d.name.substr(d.name.length - 15);})

		suites.nodelabels = nodelabels;
		console.log(suites.nodelabels);

		console.log("here2...", pjDataSet);

		// var mylinks = suites.svg.selectAll('.project-d3-link')
		// 	.data(pjDataSet.edges)
		// 	.enter().append('line')
		// 	.attr('class','project-d3-link')
		// 	.attr("id",function(d,i) {return 'edge'+i})
		//     .attr("x1", function(d) { return  px_suite_column +  px_rect_width/2; } )
		//    	.attr("y1", function(d) { return  (d.source.id) * px_row_height + px_row_height/2 } )
		//     .attr("x2", function(d) { return  px_suite_column +  px_rect_width/2; } )
		//    	.attr("y2", function(d) { return  (d.target.id ) * px_row_height + px_row_height/2; } )
		//     .style("stroke","#ccc")
		//     .attr('marker-end','url(#arrowhead)')
		//     .style("pointer-events", "none");

		
	   	
 	   
		
		},


	createExistingTree: function() {

		var stree = katana.$activeTab.data('existingSuiteTree');
		console.log("stree ", stree);
		var sroot = stree; 
		var tree = d3.layout.tree()
 					.size([700, 1000]);
 		var diagonal = d3.svg.diagonal()
 					.projection(function(d) { return [d.y, d.x]; });

 		var nodes = tree.nodes(sroot).reverse(),
   		links = tree.links(nodes);


   		var eNodes = suites.svg.append('g')
   			.attr('class','existingSuiteNode')
   			.attr("transform", "translate(500,0)");


   		suites.eNodes = eNodes;  // Very important for drag end.
   		suites.diagonal = diagonal; // Sa
  		// Normalize for fixed-depth.
  		var n = 0;
  		nodes.forEach(function(d) { d.y = d.depth * 180; d.id = ++n;});
   		console.log("suites svg->", suites.svg.selectAll(".existingSuiteNode"), nodes);
   		n= 0;
		//var nodeEnter = suites.svg.selectAll("g.existingSuiteNode")
		var nodeEnter = eNodes.selectAll("node")
				.data(nodes)
				.enter()
				.append("g")
				.attr("class", "node")
				.attr("transform", function(d) { 
				 return "translate(" + d.y  + "," + d.x + ")"; })
				.on("mouseover", function(d) {
					console.log("mouseover-->", d)

				 })
				.call(suites.dragSuite);

		  nodeEnter.append("circle")
		   .attr("r", 10)
		   .style("fill", function(d) {
		   		if (d.type == 'directory') return "#aaa";
		   		return "#fff";
		   });

		  nodeEnter.append("text")
		   .attr("x", function(d) { 
		    return d.children || d._children ? -13 : 13; })
		   .attr("dy", ".35em")
		   .attr("text-anchor", function(d) { 
		    return d.children || d._children ? "end" : "start"; })
		   .text(function(d) { return d.name; })
		   .style("fill-opacity", 1);

		  // Declare the linksâ€¦
		  //var link = suites.svg.selectAll("path.link")
		  var link = eNodes.selectAll("path.link")
		   .data(links, function(d) { return d.target.id; });

		  // Enter the links.
		  link.enter().insert("path", "g")
		   .attr("class", "link")
		   .attr("d", diagonal);
		   suites.link = link;
	},
	  




	swapViews: function(){
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
		console.log("Hellos!", suites.treeView);
		if (suites.treeView == 0) {
			katana.$activeTab.find("#suites-standard-edit").hide();
			katana.$activeTab.find("#suites-graphics-edit").show();
			suites.treeView = 1; 
		} else {
			suites.treeView = 0;
			katana.$activeTab.find("#suites-standard-edit").show();
			katana.$activeTab.find("#suites-graphics-edit").hide();

		}
	},


/// -------------------------------------------------------------------------------
// Sets up the global Suite data holder for the UI. 
// This is called from the correspoding HTML file onLoad event 
// or when a new XML file is loaded into the interface.
// 
// Two variables are set when this function is called; 
// 1. suites.jsonSuiteObject 
// 2. suites.jsonTestcases is set to point to the Testcases data structure in
//    the suites.jsonSuiteObject
//
/// -------------------------------------------------------------------------------
	mapFullSuiteJson: function(incomingFile){
	var myfile = katana.$activeTab.find('#fullpathname').text();
	if (incomingFile) {
		myFile = incomingFile; 
	}
	
	jQuery.getJSON("./suites/getJSONSuiteData/?fname="+myfile).done(function(data) {
			var sdata = data['fulljson'];
			console.log("from views.py call=", sdata, data);
			suites.jsonSuiteObject = new testSuiteObject(sdata['TestSuite']);
			katana.$activeTab.data("suiteJSON", suites.jsonSuiteObject);

			katana.$activeTab.data('allExistingSuites', data['cases']);	
			katana.$activeTab.data('existingSuiteTree', data['stree']);	


			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
			suites.mapSuiteJsonToUi();  // This is where the table and edit form is created. 
			katana.$activeTab.find('#default_onError').on('change',suites.fillSuiteDefaultGoto );
			katana.$activeTab.find('#suiteState').on('change',suites.fillSuiteState );
			katana.$activeTab.find('#suiteDatatype').on('change',suites.fillSuiteDataOptions);
		});
	} ,

	fillSuiteDataOptions: function() { 
		var datatype = this.value; 
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
		datatype = datatype.toLowerCase(); 
		katana.$activeTab.find('#data_type_max_attempts').hide();
		katana.$activeTab.find('#data_type_num_attempts').hide();
		if (datatype == 'ruf' || datatype=='rup') {
			katana.$activeTab.find('#data_type_max_attempts').show();
		}
		if (datatype =='rmt'){
			katana.$activeTab.find('#data_type_num_attempts').show();
		}
	},


	fillSuiteState: function (){
		var state = this.value; 
		if (state == 'Add Another') {
			var name = prompt("Please Enter New State");
			if (name) {
			katana.$activeTab.find('#suiteState').append($("<option></option>").attr("value", name).text(name));
			}
		}
	},


/// -------------------------------------------------------------------------------
// Dynamically create a new Testcase object and append to the suites.jsonTestcases 
// array. Default values are used to fill in a complete structure. If there is 
// no default value, a null value is inserted for the keyword
/// -------------------------------------------------------------------------------
	addExistingCaseToSuite: function(){

		var callback_on_accept = function(selectedValue) { 
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
      		var pathToBase = katana.$activeTab.find('#savefilepath').text();
      		var nf = prefixFromAbs(pathToBase, selectedValue);
			console.log("Adding ..", nf);
			var newTestcase =	new suiteCaseObject(); 
			newTestcase.path = nf; 
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases	
			console.log(suites.jsonTestcases);
			suites.jsonTestcases.push(newTestcase);
			suites.createCasesTable();
			var sid = suites.jsonTestcases.length - 1; 
				
			// Now open up the popup controller. 
			katana.popupController.open(katana.$activeTab.find("#editTestCaseEntry").html(),"Edit Case " + (sid + 1), function(popup) {
				suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
				suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
				suites.lastPopup = popup;
				var sid = suites.jsonTestcases.length - 1; 
				suites.mapSuiteCaseToUI(sid,popup);
				});

			};
     	 var callback_on_dismiss =  function(){ 
      		// console.log("Dismissed");
	 		};
     	katana.fileExplorerAPI.openFileExplorer("Select a Suite file", false , $("[name='csrfmiddlewaretoken']").val(), false, callback_on_accept, callback_on_dismiss);
	
	},

	addCaseToSuite: function(){
		suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
		suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
		var newTestcase =	new suiteCaseObject(); 
		
		suites.jsonTestcases = suites.jsonSuiteObject.Testcases	
		console.log(suites.jsonTestcases);
		suites.jsonTestcases.push(newTestcase);
		suites.createCasesTable();
		var sid = suites.jsonTestcases.length - 1; 
				
		// Now open up the popup controller. 
		katana.popupController.open(katana.$activeTab.find("#editTestCaseEntry").html(),"Edit Case " + (sid + 1), function(popup) {
				suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
				suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
				suites.lastPopup = popup;
				var sid = suites.jsonTestcases.length - 1; 
				suites.mapSuiteCaseToUI(sid,popup);
				});
	},



	 
	insertCaseToSuite: function(sid, copy){
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
		var newTestcase =new suiteCaseObject();
		suites.jsonTestcases = suites.jsonSuiteObject.Testcases	
		 		
		suites.jsonTestcases.splice(sid,0,newTestcase);
		suites.createCasesTable();
	},

	mapSuiteCaseToUI: function(s,popup) {
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 

	// This is called from an event handler ... 
	suites.jsonTestcases = suites.jsonSuiteObject.Testcases		
	var xdata = suites.jsonTestcases;
	console.log(s, xdata);
	var oneCase = xdata[s];
	console.log(oneCase);
	console.log(oneCase['path']);
	popup.find("#CaseRowToEdit").val(s); 
	katana.$activeTab.attr('suite_case_row',s);  // for the file dialog.
	console.log(popup.find("#CaseRowToEdit").val());
	//katana.$activeTab.find("CasePath").val(oneCase['path']);
	popup.attr('oneCase', s);
	popup.find('#CasePath').val(oneCase.path);
	popup.find('#CaseContext').val(oneCase.context);
	popup.find('#CaseRuntype').val(oneCase.runtype);
	popup.find('#CaseImpact').val(oneCase.impact);
	popup.find('#caseonError-at-action').val(oneCase.onError_action)
	popup.find('#caseonError-at-value').val(oneCase.onError_value)
	popup.find("#suiteExecuteAtExecType").val(oneCase.Execute_ExecType); 
	popup.find("#executeRuleAtCondition").val(oneCase.Execute_Rule_Condition); 
	popup.find("#executeRuleAtCondvalue").val(oneCase.Execute_Rule_Condvalue); 
	popup.find("#executeRuleAtElse").val(oneCase.Execute_Rule_Else); 
	popup.find("#executeRuleAtElsevalue").val(oneCase.Execute_Rule_Elsevalue); 
	popup.find("#StepInputDataFile").val(oneCase.InputDataFile); 

	suites.fillSuiteCaseDefaultGoto(popup);
	popup.find('#caseonError-at-action').on('change', function(){ 
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
			
			suites.fillSuiteCaseDefaultGoto(suites.lastPopup);
	});
	console.log("FOUND Run mode  TYPE ",oneCase.runmode_type )
	popup.find('.runmode_condition').show();
	oneCase.runmode_type = oneCase.runmode_type.toLowerCase();
	if (oneCase.runmode_type === 'standard') {
		console.log("Hiding... ",oneCase.runmode_type  )
		popup.find('.runmode_condition').hide();
	}

	popup.find('.rule-condition').hide();
	if (oneCase.Execute_ExecType) {
		console.log("FOUND EXECT TYPE ",oneCase.Execute_ExecType )
		if (oneCase.Execute_ExecType == 'if' || oneCase.Execute_ExecType == 'if not') {
			popup.find('.rule-condition').show();
		} else {
		console.log("FOUND EXECT TYPE as  ",oneCase.Execute_ExecType )
		}	
	}
	popup.find("#suiteExecuteAtExecType").on('change',function() {
			if (this.value == 'if' || this.value == 'if not') {
				popup.find('.rule-condition').show();			
			} else {
				popup.find('.rule-condition').hide();
				
			}
		});
	
	popup.find("#CaseRunmode").on('change',function() {
			var mode = this.value.toLowerCase();
			if ( mode === 'standard') {
				popup.find('.runmode_condition').hide();	
					
			} else {
				popup.find('.runmode_condition').show();
					
			}
		});


},


/// -------------------------------------------------------------------------------
// This function is called to map the currently edited Suite Case to 
// the field being edited. 
// Note that this function is calld from an event handler which catches the 
// row number from the table.
/// -------------------------------------------------------------------------------
	mapUItoSuiteCase: function(){
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
		var popup = suites.lastPopup; 
		var s = parseInt(popup.find("#CaseRowToEdit").val());
		var oneCase = suites.jsonTestcases[s];
		console.log("Item ",s, oneCase);
		oneCase.impact = popup.find('#CaseImpact').val();
		oneCase.path = popup.find('#CasePath').val();
		oneCase.context= popup.find('#CaseContext').val();
		oneCase.runtype= popup.find('#CaseRuntype').val();	
		oneCase.runmode_type= popup.find('#CaseRunmode').val();
		oneCase.runmode_value= popup.find('#CaseRunmodeAtValue').val();
		oneCase.onError_action= popup.find("#caseonError-at-action").val();
		oneCase.onError_value= popup.find("#caseonError-at-value").val();
		oneCase.Execute_Rule_Condition = popup.find("#executeRuleAtCondition").val(); 
		oneCase.Execute_Rule_Condvalue= popup.find("#executeRuleAtCondvalue").val(); 
		oneCase.Execute_Rule_Else= popup.find("#executeRuleAtElse").val(); 
		oneCase.Execute_Rule_Elsevalue= popup.find("#executeRuleAtElsevalue").val(); 
		
		var exectype = popup.find("#suiteExecuteAtExecType").val();
		oneCase.Execute_ExecType = exectype ; 
		console.log(popup.find('#suiteExecuteAtExecType').val(),popup.find('#CaseImpact').val());
		console.log("After saving", s, oneCase);
},
/*
Collects data into the global Suite data holder from the UI and returns the XML back 
NOTE: At the time of writing I am using jQuery and Bootstrap to show the data.

Two global variables are heavily used when this function is called; 
1. suites.jsonSuiteObject 
2. suites.jsonTestcases which is set to point to the Testcases data structure in
   the suites.jsonSuiteObject

*/
	mapUiToSuiteJson: function() {
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 

		if (katana.$activeTab.find("#suiteName").val().length < 1) {
			data = { 'heading': "Error", 'text' : "Please specific a suite name "}
			katana.openAlert(data);
			return
		}
		if (katana.$activeTab.find("#suiteTitle").val().length < 1) {
			data = { 'heading': "Error", 'text' : "Please specific a title "}
			katana.openAlert(data);
			return
		}

		if (katana.$activeTab.find("#suiteEngineer").val().length < 1) {
					data = { 'heading': "Error", 'text' : "Please specific a name for the engineer"}
			katana.openAlert(data);
			return
		}

	// Add an XML to saved file name 
		var xfname = katana.$activeTab.find('#suiteName').val();
		if (xfname.indexOf(".xml") < 0) {
			xfname = xfname + '.xml';
			}
		katana.$activeTab.find('#savefilepath').text(xfname);
		katana.$activeTab.find('#my_file_to_save').val(xfname);

		suites.jsonSuiteObject.Details.Name = katana.$activeTab.find('#suiteName').val();
		suites.jsonSuiteObject.Details.Title = katana.$activeTab.find('#suiteTitle').val();
		suites.jsonSuiteObject.Details.Engineer = katana.$activeTab.find('#suiteEngineer').val();
		suites.jsonSuiteObject.Details.Resultsdir = katana.$activeTab.find('#suiteResults').val();
		suites.jsonSuiteObject.Details.State = katana.$activeTab.find('#suiteState').val();
		suites.jsonSuiteObject.Details.default_onError_action = katana.$activeTab.find('#default_OnError').val();
		suites.jsonSuiteObject.Details.default_onError_value = katana.$activeTab.find('#default_OnError_goto').val();
		suites.jsonSuiteObject.Details.InputDataFile = katana.$activeTab.find('#suiteInputDataFile').val();
		suites.jsonSuiteObject.Details.ExecType = katana.$activeTab.find("#suiteDatatype").val();
		suites.jsonSuiteObject.Details.ExecType_num_Attempts = katana.$activeTab.find("#data_type_num_attempts").val();
		suites.jsonSuiteObject.Details.ExecType_max_Attempts = katana.$activeTab.find("#data_type_max_attempts").val();
		suites.jsonSuiteObject.Details.setTimeStamp();


		var xfname = suites.jsonSuiteObject.Details.Name;
		if (xfname.indexOf(".xml") < 2) {
			xfname = xfname + ".xml";
		}
		
		console.log(suites.jsonSuiteObject);
		console.log(suites.jsonSuiteObject['Testcases']);
		var url = "./suites/getSuiteDataBack";
		var csrftoken = $("[name='csrfmiddlewaretoken']").val();

		$.ajaxSetup({
				function(xhr, settings) {
	            xhr.setRequestHeader("X-CSRFToken", csrftoken)
	    	}
		});
	
		var topNode = { 'TestSuite' : suites.jsonSuiteObject.getJSON()};
		//var topNode = 
		$.ajax({
		    url : url,
		    type: "POST",
		    data : { 
		    	'json': JSON.stringify(topNode),
		    	'filetosave': xfname,
		    	'savefilepath': katana.$activeTab.find('#savefilepath').text()
		    	},
		    headers: {'X-CSRFToken':csrftoken},
	    
			success: function( data ){
			        var outstr = "Saved " + katana.$activeTab.find('#savefilepath').text() +katana.$activeTab.find('#my_file_to_save').val(); 
					xdata = { 'heading': "Saved", 'text' : outstr}
					katana.openAlert(xdata);
			        katana.$activeTab.find('#suiteName').val(suites.jsonSuiteObject.Details.Name);
			    	}
				});

	},

		start_wdfEditor: function() { 
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
			var tag = '#suiteInputDataFile';
			var filename = katana.$activeTab.find(tag).attr("fullpath");
			console.log("WDF editor opening...", filename); 
			var csrftoken = $("[name='csrfmiddlewaretoken']").val();
		
			var href='/katana/wdf/index';
			dd = { 'path' : filename}; 
			pd = { type: 'POST',
				   headers: {'X-CSRFToken':csrftoken},
				   data:  dd};
				  console.log("Pd = ", pd);
		  		   katana.templateAPI.load.call(this, href, '/static/wdf_edit/js/main.js,', null, 'wdf', function() { 
					//var xref="/katana/wdf/index"; 
		    		//katana.templateAPI.subAppLoad(xref,null,function(thisPage) {
					console.log("loaded wdf");
		    		//});
			}, pd);
		},

	getInputDataForSuite: function () {
      var callback_on_accept = function(selectedValue) { 
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
      		console.log(selectedValue);
      		var pathToBase = katana.$activeTab.find('#savefilepath').text();
      		console.log("File path ==", pathToBase);
      		var nf = prefixFromAbs(pathToBase, selectedValue);
      		suites.jsonSuiteObject.Details['InputDataFile']= nf;
      		console.log("Path set to ",nf);
      		var tag = '#suiteInputDataFile';
      		katana.$activeTab.find(tag).val(nf);
      		katana.$activeTab.find(tag).attr("value", nf);
	  		katana.$activeTab.find(tag).attr("fullpath", selectedValue);
            };
      var callback_on_dismiss = function(){ 
      		console.log("Dismissed");
	 };
     katana.fileExplorerAPI.openFileExplorer("Select a file", false , $("[name='csrfmiddlewaretoken']").val(), false, callback_on_accept, callback_on_dismiss);
	},


	getResultsDirForSuite: function () {
      var callback_on_accept = function(selectedValue) { 
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
      		console.log(selectedValue);
      		var popup = suites.lastPopup;
      		
      		var pathToBase = katana.$activeTab.find('#savefilepath').text();
      		console.log("File path ==", pathToBase);
      		var nf = prefixFromAbs(pathToBase, selectedValue);
      		suites.jsonSuiteObject.Details.Resultsdir = nf;
      		console.log("Path set to ",nf);
            katana.$activeTab.find('#suiteResults').val(nf);
            popup.find("#StepInputDataFile").val(nf); 
           };
      var callback_on_dismiss = function(){ 
      		console.log("Dismissed");
	 };
     katana.fileExplorerAPI.openFileExplorer("Select a file", false , $("[name='csrfmiddlewaretoken']").val(), false, callback_on_accept, callback_on_dismiss);
	},


	getDirForSuiteRow: function (where) {
      var callback_on_accept = function(selectedValue) { 
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
      		var sid = katana.$activeTab.attr('suite_case_row');
			var pathToBase = katana.$activeTab.find('#savefilepath').text();
      		console.log("File path ==", pathToBase, sid);
      		var nf = prefixFromAbs(pathToBase, selectedValue);
      		var oneCase = suites.jsonSuiteObject.Testcases[sid];
      		oneCase[where]= nf;
      		console.log("Path set to ",nf," for ", sid, oneCase);
      		suites.createCasesTable();
            };
      var callback_on_dismiss = function(){ 
      		console.log("Dismissed");
	 };
     katana.fileExplorerAPI.openFileExplorer("Select a file", false , $("[name='csrfmiddlewaretoken']").val(), false, callback_on_accept, callback_on_dismiss);
	},

	fillSuiteDefaultGoto :function() {
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 

	var gotoStep = katana.$activeTab.find('#default_onError').val();
	//console.log("Step ", gotoStep);
	var defgoto = katana.$activeTab.find('#default_onError_goto'); 
		defgoto.hide();

	if (gotoStep.trim() == 'goto') { 
		defgoto.show();
	} else {
		defgoto.hide();
		
	}

	defgoto.empty(); 
	var xdata = suites.jsonSuiteObject["Testcases"]; 
	if (!jQuery.isArray(xdata)) xdata = [xdata]; 
	for (var s=0; s<Object.keys(xdata).length; s++ ) {
		defgoto.append($('<option>',{ value: s,  text: s+1}));
	}
},

	fillSuiteCaseDefaultGoto : function(popup) {
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 

		var gotoStep =popup.find('#caseonError-at-action').val();
		var defgoto = popup.find('#caseonError-at-value'); 
		defgoto.hide();

		if (gotoStep.trim() == 'goto') { 
			defgoto.show();
		} else {
			defgoto.hide();
			
		}
		//var sid = popup.find('#CaseRowToEdit').val();
		defgoto.empty(); 
		var xdata = suites.jsonSuiteObject["Testcases"]; // ['Testcase'];
		if (!jQuery.isArray(xdata)) xdata = [xdata]; 
		for (var s=0; s<Object.keys(xdata).length; s++ ) {
			defgoto.append($('<option>',{ value: s,  text: s+1}));
		}
	},

//
// This creates the table for viewing data in a sortable view. 
// 
	createCasesTable: function() {
		var items = []; 
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 

		items.push('<table  id="Case_table_display" class="suite-configuration-table" width="100%">');
		items.push('<thead>');
		items.push('<tr id="CaseRow"><th>Num</th><th></th><th>Path</th><th></th><th>Input Data File</th><th>context</th><th>Run Type</th><th>Mode</th><th>OnError</th><th>Impact</th><th/></tr>');
		items.push('</thead>');
		items.push('<tbody>');

		//console.log(xdata);
		katana.$activeTab.find("#tableOfTestcasesForSuite").html("");

		var slen = suites.jsonSuiteObject.Testcases.length; 
		for (var s=0; s< slen; s++ ) {
			var oneCase = suites.jsonSuiteObject.Testcases[s];
			console.log("Drawing table", oneCase);
			var InputDataFileStr = oneCase['InputDataFile'];
			if (InputDataFileStr == undefined) InputDataFileStr = '';
			if (InputDataFileStr == 'undefined') InputDataFileStr = '';


			var showID = parseInt(s)+ 1; 
			items.push('<tr data-sid="'+s+'"><td>'+showID+'</td>');
			var bid = "fileTestcase-"+s+"-id";
			items.push('<td><i title="ChangeFile" class="fa fa-folder-open" id="'+bid+'" katana-click="suites.fileNewSuiteFromLine" key="'+bid+'"/></td>');
			items.push('<td katana-click="suites.showCaseFromSuite" skey="'+oneCase['path']+'" title="'+oneCase['path']+'"> '+oneCase['path']+'</td>');
			items.push('<td><i title="Change Input Data File" class="fa fa-folder-open" id="'+bid+'" katana-click="suites.fileNewInputFromLine" key="'+bid+'"/></td>');
			items.push('<td skey="'+InputDataFileStr+'"  title="'+InputDataFileStr+'"> '+InputDataFileStr+'</td>');
			items.push('<td title="'+oneCase.content+'">'+oneCase.context+'</td>');
			items.push('<td title="'+oneCase.runtype+'">'+oneCase.runtype+'</td>');
			items.push('<td title="'+oneCase.runmode_type+'">'+oneCase.runmode_type);
			if (oneCase.runmode_type != 'standard') {
				items.push('<br>'+oneCase.runmode_value.toLowerCase());
			}
			items.push('</td>');
			if (oneCase.onError_action != 'goto') {
					items.push('<td>'+oneCase.onError_action+'</td>');
			
			} else {
					items.push('<td>'+oneCase.onError_action+' '+oneCase.onError_value +'</td>');	
			}

			items.push('<td>'+oneCase.impact+'</td>');
			bid = "deleteTestcase-"+s+"-id";
			items.push('<td><i title="Delete" class="fa fa-trash" id="'+bid+'" katana-click="suites.deleteSuiteFromLine" key="'+bid+'"/>');
			bid = "editTestcaseRow-"+s+"-id";
			items.push('<i title="Edit" class="fa fa-pencil" title="Edit" id="'+bid+'" katana-click="suites.editNewSuiteIntoLine" key="'+bid+'"/> ');
			bid = "insertTestcase-"+s+"-id";
			items.push('<i title="Insert" class="fa fa-plus" title="Insert New Case" id="'+bid+'" katana-click="suites.insertNewSuiteIntoLine" key="'+bid+'"/><br>');
			bid = "copyToStorage-"+s+"-id-";
			items.push('<i title="Copy to clipboard" class="fa fa-clipboard" theSid="'+s+'"   id="'+bid+'" katana-click="suites.saveTestStep" key="'+bid+'"/>');
			bid = "copyFromStorage-"+s+"-id-";
			items.push('<i title="Copy from clipboard" class="fa fa-outdent" theSid="'+s+'"   id="'+bid+'" katana-click="suites.restoreTestStep" key="'+bid+'"/>');
			bid = "dupTestcase-"+s+"-id";
			items.push('<i title="Duplicate" class="fa fa-copy" title="Duplicate New Case" id="'+bid+'" katana-click="suites.duplicateNewSuiteIntoLine" key="'+bid+'"/></td>');
			items.push('</tr>');
		}
	items.push('</tbody>');
	items.push('</table>');
	katana.$activeTab.find("#tableOfTestcasesForSuite").html( items.join(""));
	katana.$activeTab.find('#Case_table_display tbody').sortable( { stop: suites.testSuiteSortEventHandler});
	suites.fillSuiteDefaultGoto();
},

	insertNewSuiteIntoLine : function() {
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
	console.log(this.attr('key'));
	var names = this.attr('key').split('-');
	console.log(this.attr('key'));
	var sid = parseInt(names[1]);
	suites.insertCaseToSuite(sid,0);
},

 	deleteSuiteFromLine :function() {
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
	var names = this.attr('key').split('-');
	var sid = parseInt(names[1]);
	suites.removeTestcase(sid);
	},

	duplicateNewSuiteIntoLine : function( ){
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
	var names = this.attr('key').split('-');
	var sid = parseInt(names[1]);
	suites.insertCaseToSuite(sid,1);
	},


	saveTestStep: function() {
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
		var names = this.attr('key').split('-');
		var sid = parseInt(names[1]);
		console.log("Saving ...", suites.jsonTestcases[sid] );
		suites.jsonTestcases[sid].copyToDocument('lastCaseCopied', suites.jsonTestcases[sid]);
		},


	restoreTestStep: function() {
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
			var names = this.attr('key').split('-');
			var sid = parseInt(names[1]);
			jsonData = suites.jsonTestcases[sid].copyFromDocument('lastCaseCopied');
			console.log("Retrieving ... ", jsonData);
			newTestcase = new suiteCaseObject(jsonData);
			suites.jsonTestcases.splice(sid,0,newTestcase);
			suites.createCasesTable();
		},


	editNewSuiteIntoLine : function() {
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
			var names = this.attr('key').split('-');
			var sid = parseInt(names[1]);
			katana.popupController.open(katana.$activeTab.find("#editTestCaseEntry").html(),"Edit Case " + (sid + 1), function(popup) {
			suites.lastPopup = popup;
			suites.mapSuiteCaseToUI(sid,popup);
			});

	},

	fileNewSuiteFromLine :function(){ 
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
			var names = this.attr('key').split('-');
			var sid = parseInt(names[1]);
			katana.$activeTab.attr('suite_case_row',sid);
			suites.getDirForSuiteRow('path');
	},

	fileNewInputFromLine:function(){ 
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
			var names = this.attr('key').split('-');
			var sid = parseInt(names[1]);
			katana.$activeTab.attr('suite_case_row',sid);
			suites.getDirForSuiteRow('InputDataFile');
	},

	showCaseFromSuite : function () {
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
			var fname = this.attr('skey');
			var xref="./cases/editCase/?fname="+fname; 
		  	console.log("Calling case ", fname, xref);
			var href='/katana/cases';
		  	katana.templateAPI.load.call(this, href, '/static/cases/js/cases.js,', null, 'case', function() { 
					var xref="./cases/editCase/?fname="+fname; 
	    			katana.templateAPI.subAppLoad(xref,null,function(thisPage) {
						cases.mapFullCaseJson(fname,'#listOfTestStepsForCase');
	    		});

		});
	},
//
	testSuiteSortEventHandler : function(event, ui ) {
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
			var listItems = [] ; 
			var listCases = katana.$activeTab.find('#Case_table_display tbody').children(); 
			console.log(listCases);
				if (listCases.length < 2) {
			 return; 
	}

	var oldCaseSteps = suites.jsonSuiteObject.Testcases;
	var newCaseSteps = new Array(listCases.length);

	for (xi=0; xi < listCases.length; xi++) {
		var xtr = listCases[xi];
		var ni  = xtr.getAttribute("data-sid");
		console.log(xi + " => " + ni);
		newCaseSteps[ni] = oldCaseSteps[xi];
		}

		suites.jsonSuiteObject.Testcases = newCaseSteps;
		suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
		suites.mapSuiteJsonToUi();  // This is where the table and edit form is created. 
	},






	createSuiteRequirementsTable : function(rdata){
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
		var items =[]; 
		katana.$activeTab.find("#tableOfTestRequirements").html("");
		
		items.push('<table id="Case_Req_table_display" class="suite-req-configuration-table  striped" width="100%" >');
		items.push('<thead>');
		items.push('<tr id="ReqRow"><th>#</th><th>Requirement</th><th>')
		items.push('<i title="Save Edit" katana-click="suites.saveAllRequirementsCB">Save All</i>')
		items.push('</th></tr>');
		items.push('</thead>');
		items.push('<tbody>');
		//console.log(rdata);
		var slen = rdata.getLength();
		var reqs = rdata.getRequirements();
		for (var s=0; s<slen; s++ ) {
		var idnumber = s + 1;
		items.push('<tr data-sid=""><td>'+idnumber+'</td>');
		var bid = "textRequirement-name-"+s+"-id";	
		items.push('<td><input type="text" value="'+reqs[s]+'" id="'+bid+'" /></td>');
		bid = "deleteRequirementbtn-"+s+"-id";
		
		items.push('<td><i  class="fa fa-trash"  title="Delete" skey="'+bid+'" katana-click="suites.deleteRequirementCB"/>');
		bid = "editRequirementbtn-"+s+"-id";
		items.push('<i class="fa fa-floppy-o" title="Save Edit" skey="'+bid+'" katana-click="suites.saveRequirementCB"/>');
		bid = "insertRequirementbtn-"+s+"-id";
		items.push('<i class="fa fa-plus"  title="Insert" skey="'+bid+'" katana-click="suites.insertRequirementCB"/></td>');
		
	}
	items.push('</tbody>');
	items.push('</table>');
	katana.$activeTab.find("#tableOfTestRequirements").html( items.join(""));
	

},

	saveAllRequirementsCB: function() { 
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
			var slen = suites.jsonSuiteObject.Requirements.getLength();
			//console.log("slen=", slen);
			for (var sid = 0; sid < slen; sid++ ) {
				var txtNm = katana.$activeTab.find("#textRequirement-name-"+sid+"-id").val();
			suites.jsonSuiteObject.Requirements.setRequirement( sid,  txtNm );
		}
		suites.createSuiteRequirementsTable(suites.jsonSuiteObject.Requirements);	

	},


	saveRequirementCB:function() {
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
			var names = this.attr('skey').split('-');
			var sid = parseInt(names[1]);
			var txtVl = katana.$activeTab.find("#textRequirement-name-"+sid+"-id").val();
			suites.jsonSuiteObject.Requirements.setRequirement( sid,  txtVl);
			suites.createSuiteRequirementsTable(suites.jsonSuiteObject.Requirements);	
		},

	deleteRequirementCB:	function() {
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
			var names = this.attr('skey').split('-');
			var sid = parseInt(names[1]);
			// console.log("Remove " + sid + " " + this.id ); 
			suites.jsonSuiteObject.Requirements.deleteRequirement(sid);
			suites.createSuiteRequirementsTable(suites.jsonSuiteObject.Requirements);	
			
		},
	
	insertRequirementCB:function( ) {
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
			var names = this.attr('skey').split('-');
			var sid = parseInt(names[1]);
			suites.jsonSuiteObject.Requirements.insertRequirement(sid,'');
			suites.createSuiteRequirementsTable(suites.jsonSuiteObject.Requirements);	
		},

	addRequirementToSuite() {
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
		suites.jsonSuiteObject.Requirements.insertRequirement(0,'');
		suites.createSuiteRequirementsTable(suites.jsonSuiteObject.Requirements);	
	},
/*
// Shows the global Suite data holder in the UI.

NOTE: At the time of writing I am using jQuery and Bootstrap to show the data.

Two global variables are heavily used when this function is called; 
1. suites.jsonSuiteObject 
2. suites.jsonTestcases which is set to point to the Testcases data structure in
   the suites.jsonSuiteObject

*/
 mapSuiteJsonToUi: function(data){
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
	if (!jQuery.isArray(suites.jsonTestcasesj)) suites.jsonTestcasesj = [suites.jsonTestcasesj]; 
	// if (!suites.jsonSuiteObject['Requirements']) suites.jsonSuiteObject['Requirements'] = [];
	// if (!jQuery.isArray(suites.jsonSuiteObject['Requirements'])) suites.jsonSuiteObject['Requirements'] = [suites.jsonSuiteObject['Requirements']]; 
	suites.createCasesTable();

	// Resolve the relative path for the wdf editor to get full path. ..
	if (!suites.jsonSuiteObject['InputDataFile']) {
		var tag = '#suiteInputDataFile';
		var nf = suites.jsonSuiteObject["Details"]['InputDataFile'];
		var pathToBase = katana.$activeTab.find('#savefilepath').text();
		var fpath = absFromPrefix(pathToBase, nf);
		//console.log("mapSuiteJsonToUi:", fpath, nf, pathToBase);
		
		katana.$activeTab.find(tag).val(nf);
      	katana.$activeTab.find(tag).attr("value", nf);
	  	katana.$activeTab.find(tag).attr("fullpath", fpath);

	  	suites.createD3treeData();
		suites.createD3tree();
	}


		datatype = suites.jsonSuiteObject.Details.ExecType;
		datatype = datatype.toLowerCase(); 
		katana.$activeTab.find('#data_type_max_attempts').hide();
		katana.$activeTab.find('#data_type_num_attempts').hide();
		if (datatype == 'ruf' || datatype=='rup') {
			katana.$activeTab.find('#data_type_max_attempts').show();
		}
		if (datatype =='rmt'){
			katana.$activeTab.find('#data_type_num_attempts').show();
		}
		suites.createSuiteRequirementsTable(suites.jsonSuiteObject.Requirements);		
},  

// Saves your suite to disk. 
	saveSuitesCaseUI : function() {	
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
			suites.mapUItoSuiteCase();
			suites.createCasesTable();
			//suites.mapSuiteJsonToUi();
			katana.popupController.close(suites.lastPopup);
	},




// Removes a test Case by its ID and refresh the page. 
	removeTestcase : function(sid ){
			suites.jsonSuiteObject = katana.$activeTab.data("suiteJSON");
			suites.jsonTestcases = suites.jsonSuiteObject.Testcases; 
		suites.jsonTestcases.splice(sid,1);
		console.log("Removing test Cases "+sid+" now " + Object.keys(suites.jsonTestcases).length);
		suites.mapSuiteJsonToUi();	// Send in the modified array
	},


};