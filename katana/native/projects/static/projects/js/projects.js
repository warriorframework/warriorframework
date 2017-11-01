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


class projectDetailsObject{

	mapJSONdataToSelf(jsonDetailsData) {
			console.log(jsonDetailsData);
				
			this.fillDefaults();           // Fills internal values only
			console.log(jsonDetailsData);
				
			if (jsonDetailsData) {         // Overridden by incoming data.
				this.Name = jsonDetailsData['Name'];  
				this.Title = jsonDetailsData['Title']; 
				this.State = jsonDetailsData['State']; 
				this.Engineer = jsonDetailsData['Engineer']; 
				this.cDate = jsonDetailsData['Date']; 
				this.cTime = jsonDetailsData['Time']; 
				
				if (jsonDetailsData['default_onError']) {
					if ( jsonDetailsData['default_onError']['@action']) this.onError_action = jsonDetailsData['default_onError']['@action'].toLowerCase(); 
					if ( jsonDetailsData['default_onError']['@value'] ) this.onError_value = jsonDetailsData['default_onError']['@value']; 			
				}
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
			'default_onError': { '@action': this.onError_action, '@value': this.onError_value},
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
		this.onError_action = ''; 
		this.onError_value = ''; 
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


class projectSuiteObject {
	constructor(inputJsonData) {
		var jsonData = inputJsonData;
		this.setupFromJSON(jsonData);
	}

	setupFromJSON(jsonData) { 
		if (!jsonData) {
			jsonData = 	this.createEmptySuite(); 
		}
		// Fill defaults here. 
		this.fillDefaults(jsonData);
		this.path = jsonData['path'];
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


		if (!jsonData['path']) {
			jsonData['path'] =  "New";
		}

		if (!jsonData['impact']) {
			jsonData['impact'] =  "impact";
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
		if (!jsonData['onError']['@value']) {
			jsonData['onError']['@value'] = "";
		}
		if (!jsonData['onError']['@action']) {
			jsonData['onError']['@action'] = "";
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

	createEmptySuite() {
		return {
			'path': '',
			'impact': '',
			'runmode' : { "@value": "standard", "@type": "" },
			'onError': { "@action": "next", "@value": "" },
			'Execute': { "@ExecType": "yes", 
				"Rule": { "@Condition": "", "@Condvalue": "", "@Else": "next", "@Elsevalue": "" } 
			},
		};

	}
}


class projectsObject{
	constructor(jsonData){
		this.mapJsonData(jsonData);
		
	}
	mapJsonData(jsonData){ 
			console.log("In constructor", jsonData);
			if (!jsonData['Details']) {
				this.Details = new projectDetailsObject(null);
			} else {
				this.Details = new projectDetailsObject(jsonData['Details'])
			}

			
			if (!jsonData['Testsuites']) {
				jsonData['Testsuites']['Testsuite'] = [] 
			} 
			if (!jsonData['Testsuites']['Testsuite']) {
				jsonData['Testsuites']['Testsuite'] = [] 
			} 
			//
			if (!jQuery.isArray(jsonData['Testsuites']['Testsuite'])) {
			 jsonData['Testsuites']['Testsuite'] = [ jsonData['Testsuites']['Testsuite'] ];
			}

			this.Testsuites = [];
			for (var k=0; k<jsonData['Testsuites']['Testsuite'].length; k++) {	
				var ts = new projectSuiteObject(jsonData['Testsuites']['Testsuite'][k]);
				this.Testsuites.push(ts);
				}
			// 
			}

		getJSON(){
			var testsuitesJSON = [];
			for (var ts =0; ts< this.Testsuites.length; ts++ ) {
				testsuitesJSON.push(this.Testsuites[ts].getJSON());
			}
			console.log(this);

			return { 'Details': this.Details.getJSON(), 
				'Testsuites' :  testsuitesJSON };
		}

	}


var treeData = [
  {
    "name": "Top Level",
    "parent": "null",
    "children": [
      {
        "name": "Level 2: A",
        "parent": "Top Level",
        "children": [
          {
            "name": "Son of A",
            "parent": "Level 2: A"
          },
          {
            "name": "Daughter of A",
            "parent": "Level 2: A"
          }
        ]
      },
      {
        "name": "Level 2: B",
        "parent": "Top Level"
      }
    ]
  }
];


 var projects = {

 	treeData : [], 
 	treeView  : 0,

	closeProject: function(){
		katana.closeSubApp();
	},

// Toggle children.
	toggle: function(d) {
	  if (d.children) {
	    d._children = d.children;
	    d.children = null;
	  } else {
	    d.children = d._children;
	    d._children = null;
	  }
	},


	filesOnlycreateChildrenData: function(tnode, td) {
		if (!tnode.children) return []; 
		var mykids = [];              // create kids for this d3 node 
		var kids = tnode['children']; // from incoming tree node.
		for (var xc in kids){
			var thisnode = { "name": kids[xc].text, 
    			"data-path": kids[xc]["li_attr"]["data-path"], "parent": td , "children": []}
			children = projects.createChildrenData(kids[xc], thisnode);
			thisnode.children = children;
			mykids.push(thisnode );
		}
		return mykids;
	},

	filesOnlyc3DData: function(tdata) {
		var td = {
		"name": "Projects",
    	"parent": "null", 
    	"children": [],
    	};
    	var prj = tdata['children'];
    	for (var xc in prj) {
    		mykids = projects.createChildrenData(prj[xc], td);
    		td.children.push({ "name": prj[xc].text, 
    			"data-path": prj[xc]["li_attr"]["data-path"], "parent": td , "children": mykids} );
    	}
    	projects.treeData = [td]; 
	},


	createD3treeData: function(tdata) {
		var projectSummary = projects.jsonProjectObject.Details.getSummary();
		var td = {
		"name": projects.jsonProjectObject.Details.Name,
    	"parent": "null", 
    	"children": [],
    	"ntype": 'project',
    	"displayStr": projectSummary,
    	};
    	projects.jsonTestSuites = projects.jsonProjectObject['Testsuites']; 
			
    	var slen = projects.jsonTestSuites.length;
		for (var s=0; s<slen; s++ ) {
    		var oneSuite = projects.jsonProjectObject.Testsuites[s];
    		var items = [];
    		items.push('Condition='+oneSuite.Execute_ExecType+'<br>');
			//console.log("Pushing ", oneSuite, items);
			if (oneSuite.Execute_ExecType == 'if' || oneSuite.Execute_ExecType == 'if not') {
				items.push('Condition='+oneSuite.Execute_Rule_Condition+'<br>');
				items.push('Condvalue='+oneSuite.Execute_Rule_Condvalue+'<br>');
				items.push('Else='+oneSuite.Execute_Rule_Else+'<br>');
				items.push('Elsevalue='+oneSuite.Execute_Rule_Elsevalue+'<br>');
			}
			var execStr = items.join("");
			var displayStr = "" + oneSuite.path + "<br>runmode:" + oneSuite.runmode_type + " " + oneSuite.runmode_value + 
					"<br>onError:" + oneSuite.onError_action + " " + oneSuite.onError_value + 
					"<br>" + execStr + "</div>"; 

    		td.children.push({ "name": oneSuite.path, 
    			'ntype': 'suite',
    			"rowid" : s,
    			'displayStr' : displayStr,
    			"exectype" : execStr, 
    			"runmode" : oneSuite.runmode_type + " " + oneSuite.runmode_value,
    			'on-error' : oneSuite.onError_action + " " + oneSuite.onError_value,
    			"data-path": oneSuite.InputDataFile , "parent": td , "children": []} );
    	}
    	projects.treeData = [td]; 
    	console.log("Tree Data ....", td);
    	
	},




	createD3tree: function() {
		var optimalHt = projects.jsonTestSuites.length * 100 + 200; 
		var margin = {top: 20, right: 120, bottom: 20, left: 120},
		 width = 1080- margin.right - margin.left,
		 height = optimalHt - margin.top - margin.bottom;
		 
		projects.tree = d3.layout.tree()
		 .size([height, width]);
		//console.log("Creating ....", projects.tree, height, width );
		
		projects.diagonal = d3.svg.diagonal()
		 .projection(function(d) { return [d.y, d.x]; });

		katana.$activeTab.find("[g3did='projects-3d-tree']").attr('id', projects.jsonProjectObject.Details.Name);

		console.log("Creating ....",  );
		
		var useID = '#' + projects.jsonProjectObject.Details.Name;
		console.log("Changing ID ", useID, );
		// Delete any element 

		d3.select("[useID='" + useID + "']").remove();
		projects.svg = d3.select(useID).append("svg")
		 .attr("width", width + margin.right + margin.left)
		 .attr("height", height + margin.top + margin.bottom)
		 .attr("useID", useID)
		 .append("g")
		 .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
		
		projects.root = projects.treeData[0];
		projects.nodeCtr  = 1;   
		projects.updateTree();
		
		},


	  updateTree: function() { 
	  	var nodes = projects.tree.nodes(projects.root).reverse();
   		projects.links = projects.tree.links(nodes);
   		// Normalize for fixed-depth.
  		nodes.forEach(function(d) {
  			var optimalHt = projects.jsonTestSuites.length * 100 + 200; 
		
  			d.y = d.depth * 180; 
  			if (d.rowid > 5) {
  				d.x -= optimalHt / 2; 
  				d.y += 300;
  			}
			//console.log("DX set for ", d.rowid, d.x, d.y );
  			
  			});
		
  		// Declare the nodes
  		var node = projects.svg.selectAll("g.project-d3-node")
   			.data(nodes, function(d) { return d.id || (d.id = ++projects.nodeCtr); });

  // Enter the nodes.
  		var nodeEnter = node.enter().append("g")
   				.attr("class", "project-d3-node")
   				.attr("transform", function(d) { 
    			return "translate(" + d.y + "," + d.x + ")"; });

   				

   			var defs  = projects.svg.append('defs');
			var filter = defs.append("filter").attr("id","drop-shadow").attr("height","150%");
			filter.append("feGaussianBlur").attr("in","SourceAlpha").attr("stdDeviation",5)
			.attr("result","blur");
			filter.append("feOffset").attr("in","blur")
			.attr("dx",5)
			.attr("dy",5)
			.attr("result", "offsetBlur");
			var feMerge = filter.append("feMerge");
			feMerge.append("feMergeNode").attr("in","offsetBlur");
			feMerge.append("feMergeNode").attr("in","SourceGraphic");

			
 			
   			nodeEnter.append("rect")
   			.attr("width",100)
   			.attr("height",30)
   			.attr("fill", function(d) { 
   				if (d.ntype == 'project') return '#aaa';
   				return '#fff';
   			})
   			.style('stroke', function(d) { 
   				if (d.ntype == 'project') return 'blue';
   				return 'green';

   			})
   			.on("mouseover",function(d) {
   					// var el = d3.select("[tooltipid='"+d.rowid+"']");
   					// el.style("visibility", "visible");
   					var fobj = projects.svg.append('foreignObject')
   						.attr({
   							'x': d.y + 100,
   							'y': d.x - 30, 
   							'width': 450, 
   							'class' : 'projectSuiteTooltip',
   						})
   						.style({
   							'fill' : 'red',
   							'opacity': 1.0,
   							'border' : '2px solid "green"',
   						});
   						var div = fobj.append("xhtml:div").append('div');
   						div.append('p')
   							.style('border', '2px solid green')
   							//.style('fill','red')
   							//.style('color', 'white')
   							.html(d.displayStr);
   						var foHt = div[0][0].getBoundingClientRect().height;
   						var foWd =  div[0][0].getBoundingClientRect().width;
   						projects.svg.append("rect")
   							.attr({ 
							'x': d.y + 100,
   							'y': d.x - 30, 
   							'height': foHt ,
   							'width' : foWd , 
							'class' : 'projectSuiteTooltip',
   							})
   							.style({
							'fill': '#000',
   							'opacity': 0.2, 
   							});

   				})
   			.on("mouseout",function(d) {
   		 			projects.svg.selectAll('.projectSuiteTooltip').remove();
   				})
   			.style("filter","url(#drop-shadow");

			nodeEnter.append("text")
				.attr("x", 10)
				.attr("y", 20)
				.attr("dy", ".35em")
				.text(function(d) { 
					if (d.ntype == 'project') return "Project"
					return "TS=" + (parseInt(d.rowid) + 1); })
				.style("fill-opacity", 1);
   			 			
				nodeEnter.append("foreignObject")
	   				.attr("width", 50)
	   				.attr("height", 20)
	   				.attr("y", 30)
	   				.attr("class", "fa fa-trash")
	   				.attr("deleteNodeid",function(d) { return d.rowid; })
	   				.style("opacity", 1)
	   				.style("fill-opacity",1)
	   				.style("visibility", function(d) {
	   					if (d.ntype == 'project') {
	   						return "hidden";
	   					} else {
	   						return "visible";
	   					}
	   				})
	   				.html(function(d) { return " "; } )
	   				.on("click", function(d) { 
	   						console.log("cccc, ", d, this);
		   					if (this.hasAttribute('deleteNodeid')) {
	   							console.log("Clicked to delete " + d.rowid);
	   							projects.jsonTestSuites.splice(d.rowid,1);
								projects.mapProjectJsonToUi();	 
	   						}
	   						event.stopPropagation();
	   				});

	   				nodeEnter.append("foreignObject")
	   				.attr("width", 20)
	   				.attr("height", 20)
	   				.attr("y", 30)
	   				.attr("x", 30)
	   				.attr("class", "fa fa-plus")
	   				.attr("addNodeid",function(d) { return d.rowid; })
	   				.style("opacity", 1)
	   				.style("fill-opacity",1)
	   				.style("visibility", function(d) {
	   					if (d.ntype == 'project') {
	   						return "hidden";
	   					} else {
	   						return "visible";
	   					}
	   				})
	   				.html(function(d) { return " "; } )
	   				.on("click", function(d) { 
	   						console.log("cccc, ", d, this);
		   					if (this.hasAttribute('addNodeid')) {
	   							console.log("Clicked to add " + d.rowid);
	   							var nb = new projectSuiteObject();
								projects.jsonTestSuites.splice(d.rowid,0,nb);
								projects.mapProjectJsonToUi();	// Send in the modified array
	   						}
	   						event.stopPropagation();
	   				});
					nodeEnter.append("foreignObject")
	   				.attr("width", 20)
	   				.attr("height", 20)
	   				.attr("y", 30)
	   				.attr("x", 60)
	   				.attr("class", "fa fa-folder-open")
	   				.attr("folderNodeid",function(d) { return d.rowid; })
	   				.style("opacity", 1)
	   				.style("fill-opacity",1)
	   				.style("visibility", function(d) {
	   					if (d.ntype == 'project') {
	   						return "hidden";
	   					} else {
	   						return "visible";
	   					}
	   				})
	   				.html(function(d) { return " "; } )
	   				.on("click", function(d) { 
	   						console.log("cccc, ", d, this);
		   					if (this.hasAttribute('folderNodeid')) {
	   							console.log("Clicked to add " + d.rowid);
	   							var nb = new projectSuiteObject();
								katana.$activeTab.attr('project-suite-row',d.rowid);
								projects.getResultsDirForProjectRow('Suites');
								projects.mapProjectJsonToUi();	// Send in the modified array
	   						}
	   						event.stopPropagation();
	   				});

			// Declare the linksâ€¦
			var link = projects.svg.selectAll(".project-d3-link")
			   .data(projects.links, function(d) { return d.target.id; });

		  // Enter the links.
		  link.enter().insert("path", "g")
		   	.attr("class", "project-d3-link")
		   	.attr("d", projects.diagonal);
		   	projects.svg.selectAll(".project-d3-node").on("click", function(d) {
		   	//

		   		if (!this.hasAttribute('deleteNodeid') && d.ntype == 'suite') {
	   						
					console.log("Clicked ...", d, this, this.hasAttribute('deleteNodeid'));

					var sid = d.rowid;

					katana.popupController.open(katana.$activeTab.find("#editTestSuiteEntry").html(),"Edit..." , function(popup) {
					projects.lastPopup = popup; 
					console.log(katana.$activeTab.find("#editTestSuiteEntry"));
					projects.setupProjectPopupDialog(sid,popup);
					});
				}
			///
			});

	  },


	save: function(){
		katana.templateAPI.post.call( katana.$activeTab.find('.to-save'), null, null, katana.toJSON(), function( data ) {
			console.log('saved', data);
		});
	},

	lastPopup : null, 
	jsonProjectObject : [],
	jsonTestSuites : [],			// for all Suites


	initProjectTree: function() {
		jQuery.getJSON("./projects/getProjectListTree/").done(function(data) {
			var sdata = data['treejs'];
			//console.log("tree ", sdata);
			var jdata = { 'core' : { 'data' : sdata },
    					"plugins" : [ "sort" ],
    					}; 

			console.log("Tree", sdata);
			

			katana.$activeTab.find('#myProjectTree').on("select_node.jstree", function (e, data) { 
		      var thePage = data.node.li_attr['data-path'];
	
		      var extn = thePage.indexOf(".xml");
		      if (extn < 4){
		        return;
		      }
			  var xref="./projects/editProject/?fname=" + thePage; 
			  projects.thefile = thePage;

		  
			 	katana.templateAPI.subAppLoad(xref, null, function(thisPage) { 
			   			console.log("starting ...", this);
				  		projects.mapFullProjectJson(projects.thefile);
				  });
			 
			  });

			 // setTimeout(function(){ 
				// projects.createD3tree();
			 // }, 1000);




			create_jstree_search('#myProjectTree', '#jstreeFilterText' , sdata);
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
	mapFullProjectJson: function (myfile){
	//var sdata = katana.$activeTab.find("#listOfTestSuitesForProject").text();
	//katana.$activeTab.find('#savefilepath').hide();  // To remove later...
	//var myfile = katana.$activeTab.find('#fullpathname').text();
	jQuery.getJSON("./projects/getJSONProjectData/?fname="+myfile).done(function(data) {
			var sdata = data['fulljson'];
			console.log("from views.py call=", sdata);
			//projects.jsonProjectObject = JSON.parse(sdata); 
			projects.jsonProjectObject = new projectsObject(sdata['Project']);
			projects.jsonTestSuites = projects.jsonProjectObject['Testsuites']; 
			projects.mapProjectJsonToUi();  // This is where the table and edit form is created. 
			projects.fillProjectDefaultGoto();
			console.log("Adding defaults ");
			katana.$activeTab.find('#project_onError_action').on('change',projects.fillProjectDefaultGoto );
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

	addSuiteToProject: function(){
		var newTestSuite = new projectSuiteObject();
		projects.jsonTestSuites.push(newTestSuite);
		projects.mapProjectJsonToUi();
	},


	fillProjectSuitePopupDefaultGoto: function(popup) {

		var gotoStep =popup.find('#default_onError').val();
		console.log("Step ", gotoStep);
		var defgoto = popup.find('#default_onError_goto'); 
			defgoto.hide();

		if (gotoStep.trim() == 'goto') { 
			defgoto.show();
		} else {
			defgoto.hide();
			
		}
		defgoto.empty(); 
		var xdata = jsonProjectObject['Testsuites']; 
		if (!jQuery.isArray(xdata)) xdata = [xdata]; 
		for (var s=0; s<Object.keys(xdata).length; s++ ) {
			defgoto.append($('<option>',{ value: s,  text: s}));
		}
	},


	setupProjectPopupDialog: function(s,popup) {
	console.log(s);
	var oneSuite = projects.jsonProjectObject.Testsuites[s];
	console.log(oneSuite);
	popup.find("#suiteRowToEdit").val(s); 
	popup.find("#suitePath").val(oneSuite['path']);
	popup.find("#Execute-at-ExecType").val(jsUcfirst(oneSuite.Execute_ExecType)); 
	popup.find("#executeRuleAtCondition").val(oneSuite.Execute_Rule_Condition); 
	popup.find("#executeRuleAtCondvalue").val(oneSuite.Execute_Rule_Condvalue); 
	popup.find("#executeRuleAtElse").val(oneSuite.Execute_Rule_Else); 
	popup.find("#executeRuleAtElsevalue").val(oneSuite.Execute_Rule_Elsevalue); 
	popup.find("#onError-at-action").val(oneSuite.onError_action); 
	popup.find("#onError-at-value").val(oneSuite.onError_value); 
	popup.find("#runmode-at-type").val(oneSuite.runmode_type.toLowerCase()); 
	popup.find("#runmode-at-value").val(oneSuite.runmode_value); 
	popup.find("#impact").val(oneSuite.impact); 
	projects.fillProjectSuitePopupDefaultGoto(popup);
	popup.find('#onError-at-action').on('change', function(){ 
			var popup = $(this).closest('.popup');
			projects.fillProjectSuitePopupDefaultGoto(popup);
	});
	popup.find('.rule-condition').hide();
	if (oneSuite.Execute_ExecType) {
		if (oneSuite.Execute_ExecType == 'if' || oneSuite.Execute_ExecType == 'if not') {
			popup.find('.rule-condition').show();
		}	
	}
	popup.find("#runmode-at-type").on('change', function() {
		var popup = projects.lastPopup;
		var sid = popup.find("#suiteRowToEdit").val();
		console.log(projects.jsonProjectObject.Testsuites, sid); 
		var oneSuite = projects.jsonProjectObject.Testsuites[sid];
		console.log(oneSuite);
		oneSuite.runmode_type = this.value; 
		popup.find("#runmode-at-value").show();
		if (oneSuite.runmode_type == 'standard') {
		popup.find("#runmode-at-value").hide();
		}
		
	});
	popup.find("#runmode-at-value").show();
	if (oneSuite.runmode_type == 'standard') {
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
		var oneSuite = projects.jsonProjectObject.Testsuites[s];
		console.log(oneSuite);
		katana.$activeTab.find("#suiteRowToEdit").val(s); 
		katana.$activeTab.find("#suitePath").val(oneSuite['path']);
		katana.$activeTab.find("#Execute-at-ExecType").val(oneSuite.Execute_ExecType); 
		katana.$activeTab.find("#executeRuleAtCondition").val(oneSuite.Execute_Rule_Condition); 
		katana.$activeTab.find("#executeRuleAtCondvalue").val(oneSuite.Execute_Rule_Condvalue); 
		katana.$activeTab.find("#executeRuleAtElse").val(oneSuite.Execute_Rule_Else); 
		katana.$activeTab.find("#executeRuleAtElsevalue").val(oneSuite.Execute_ule_Elsevalue); 
		
		katana.$activeTab.find("#onError-at-action").val(oneSuite['onError_action']); 
		katana.$activeTab.find("#onError-at-value").val(oneSuite['onError_value']); 
		katana.$activeTab.find("#runmode-at-type").val(oneSuite['runmodetype'].toLowerCase()); 
		katana.$activeTab.find("#runmode-at-value").val(oneSuite['runmode_value']); 
		katana.$activeTab.find("#impact").val(oneSuite['impact']); 
		projects.fillProjectDefaultGoto();

	},

	fillProjectDefaultGoto : function() {
	
		var action = katana.$activeTab.find('#project_onError_action').val();
		var defgoto = katana.$activeTab.find('#project_onError_value'); 
		
		if (action.trim() == 'goto') { 
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
		var xdata = projects.jsonProjectObject['Testsuites'] // ['Testcase'];
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
		
		data = { 'heading': "Error", 'text' : "Please specify a suite path name"}
		katana.openAlert(data);
	
		return
	}

	var s = parseInt(popup.find("#suiteRowToEdit").val());
	var oneSuite = projects.jsonProjectObject.Testsuites[s];
	oneSuite['path'] = popup.find("#suitePath").val(); 
	oneSuite['Execute'] = {}
	oneSuite.Execute_ExecType = popup.find("#Execute-at-ExecType").val(); 
	oneSuite.Execute_Rule_Condition= popup.find("#executeRuleAtCondition").val(); 
	oneSuite.Execute_Rule_Condvalue = popup.find("#executeRuleAtCondvalue").val(); 
	oneSuite.Execute_Rule_Else = popup.find("#executeRuleAtElse").val(); 
	oneSuite.Execute_Rule_Elsevalue = popup.find("#executeRuleAtElsevalue").val(); 
	oneSuite['impact'] = popup.find("#impact").val(); 
	oneSuite.onError_action = popup.find("#onError-at-action").val(); 
	oneSuite.onError_value = popup.find("#onError-at-value").val(); 
	oneSuite.runmode_type = popup.find("#runmode-at-type").val().toLowerCase(); 
	oneSuite.runmode_value = popup.find("#runmode-at-value").val(); 
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
		  var popup = projects.lastPopup;
		  var tag = popup.find('#suitePath');
	      var callback_on_accept = function(selectedValue) { 
	      		console.log(selectedValue);
	      		var popup = projects.lastPopup;
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
      		katana.$activeTab.find("#projectResultsDir").val(nf);
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
		data = { 'heading': "Error", 'text' : "Please specific a project name "}
		katana.openAlert(data);
		return; 
	}

	if (katana.$activeTab.find('#projectTitle').val().length < 1) {
		data = { 'heading': "Error", 'text' : "Please specific a title "}
		katana.openAlert(data);
		return; 
	}

	if (katana.$activeTab.find('#projectEngineer ').val().length < 1) {
		data = { 'heading': "Error", 'text' : "Please specific a name for the engineer"}
		katana.openAlert(data);
		return;
	}

	projects.jsonProjectObject['Details']['Name'] = katana.$activeTab.find('#projectName').val();

	// 
	var xfname = katana.$activeTab.find('#projectName').val();
	if (xfname.indexOf(".xml") < 2) {
		xfname = xfname + ".xml";
	}

	console.log("Save to",xfname );
	
	projects.jsonProjectObject['Details']['Title'] = katana.$activeTab.find('#projectTitle').val();
	projects.jsonProjectObject['Details']['Engineer'] = katana.$activeTab.find('#projectEngineer').val();
	projects.jsonProjectObject['Details']['State'] = katana.$activeTab.find('#projectState').val();
	projects.jsonProjectObject['Details']['Date'] = katana.$activeTab.find('#projectDate').val();
	projects.jsonProjectObject['Details']['default_onError'] = {}
	projects.jsonProjectObject['Details']['default_onError']['@action'] = katana.$activeTab.find('#default_onError').val();
	projects.jsonProjectObject['Details']['default_onError']['@value'] = katana.$activeTab.find('#default_onError_goto').val();
	projects.jsonProjectObject['Details']['ResultsDir'] = katana.$activeTab.find('#projectResultsDir').val();
	
		var date = new Date();
	  
	   var year = date.getFullYear();
       var month = date.getMonth() + 1;// months are zero indexed
       var day = date.getDate();
       var hour = date.getHours();
       var minute = date.getMinutes();
       if (minute < 10) {
       	minute = "0" + minute; 
       }
     

	projects.jsonProjectObject['Details']['Date'] = month + "/" + day + "/" + year; 
	projects.jsonProjectObject['Details']['Time'] = hour + ":" + minute; 
	
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
	
	var topNode  = { 'Project' : projects.jsonProjectObject};
	console.log("Save to",xfname , projects.jsonProjectObject);

	$.ajax({
		url:url,
	    type: "POST",
	    data : { 
	    	'json': JSON.stringify(topNode),
	    	'filetosave': xfname
	    	},
	    headers: {'X-CSRFToken':csrftoken},
    	
    success: function( data ){
    	//var outstr = "Saved "+katana.$activeTab.find('#filesavepath').text() + "/" + katana.$activeTab.find('#projectName').val();
    	//xdata = { 'heading': "Saved", 'text' : outstr }
		//katana.openAlert(xdata);
		alert("Saved...");
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
		console.log("Create suites for ", projects.jsonProjectObject); 
		projects.jsonTestSuites = projects.jsonProjectObject['Testsuites']; 
		console.log("Create suites for ", projects.jsonProjectObject['Testsuites']); 
		
		console.log("Create suites for ", projects.jsonTestSuites); 
		var slen = projects.jsonTestSuites.length;
		katana.$activeTab.find("#tableOfTestSuitesForProject").html("");
		for (var s=0; s<slen; s++ ) {
			var oneSuite = projects.jsonProjectObject.Testsuites[s];
		
			items.push('<tr data-sid="'+s+'">');
			items.push('<td>'+(parseInt(s)+1)+'</td>');
			var tbid = "textTestSuiteFile-"+s+"-id";

			var bid = "fileSuitecase-"+s+"-id";
			items.push('<td><i title="ChangeFile" class="fa fa-folder-open" skey="'+bid+'" katana-click="projects.getFileForSuite" /></td>');
			
			//oneSuite.Execute_ExecType = jsUcfirst(oneSuite.Execute_ExecType); 
			items.push('<td id="'+tbid+'" katana-click="projects.showSuiteFromProject" skey="'+oneSuite.path+'">'+oneSuite.path+'</td>');
			items.push('<td>Type='+oneSuite.Execute_ExecType+'<br>');

			if (oneSuite.Execute_ExecType == 'if' || oneSuite.Execute_ExecType == 'if not') {
				items.push('Condition='+oneSuite.Execute_Rule_Condition+'<br>');
				items.push('Condvalue='+oneSuite.Execute_Rule_Condvalue+'<br>');
				items.push('Else='+oneSuite.Execute_Rule_Else+'<br>');
				items.push('Elsevalue='+oneSuite.Execute_Rule_Elsevalue+'<br>');
			}

			items.push('</td>');
			items.push('<td>'+oneSuite.onError_action+'</td>');
			if (oneSuite.onError_action == 'goto') {
				items.push('<td>'+oneSuite.onError_action+' '+oneSuite.onError_value+'</td>');
			} else {
				items.push('<td>'+oneSuite.onError_action+'</td>');
			}


			items.push('<td>'+oneSuite.impact+'</td>');

			var bid = "deleteTestSuite-"+s+"-id";
			items.push('<td><i  title="Delete" class="fa fa-trash" value="X" skey="'+bid+'" katana-click="projects.deleteTestSuiteCB"/>');

			bid = "editTestSuite-"+s+"-id";
			items.push('<i  title="Edit" class="fa fa-pencil" title="Edit" skey="'+bid+'" katana-click="projects.editTestSuiteCB"/>');

			bid = "InsertTestSuitebtn-"+s+"-id"
			items.push('<i  title="Insert" class="fa fa-plus" value="Insert" skey="'+bid+'" katana-click="projects.insertTestSuiteCB"/><br>');


			bid = "copyToStorage-"+s+"-id-";
			items.push('<i title="Copy to clipboard" class="fa fa-clipboard" theSid="'+s+'"   id="'+bid+'" katana-click="projects.copyToClipboardCB" skey="'+bid+'"/>');
			bid = "copyFromStorage-"+s+"-id-";
			items.push('<i title="Copy from clipboard" class="fa fa-outdent" theSid="'+s+'"   id="'+bid+'" katana-click="projects.insertFromClipboardCB" skey="'+bid+'"/>');

			bid = "DuplicateTestSuite-"+s+"-id"
			items.push('<i  title="Duplicate" class="fa fa-copy" value="Duplicate" skey="'+bid+'" katana-click="projects.duplicateTestSuiteCB"/></td>');

			items.push('</tr>');
			}
		items.push('</tbody>');
		items.push('</table>');

		katana.$activeTab.find("#tableOfTestSuitesForProject").html( items.join(""));
		katana.$activeTab.find('#suite_table_display tbody').sortable( { stop: projects.testProjectSortEventHandler});
		projects.fillProjectDefaultGoto();
		katana.$activeTab.find('#project_onError_action').on('change',projects.fillProjectDefaultGoto );
	},


	getFileForSuite: function() {
			var fname = this.attr('skey');
			var names = fname.split('-');
			var sid = parseInt(names[1]);
			katana.$activeTab.attr('project-suite-row',sid);
			projects.getResultsDirForProjectRow('Suites');
	},

	deleteTestSuiteCB : function(){
			var names = this.attr('skey').split('-');
			var sid = parseInt(names[1]);
			projects.jsonTestSuites.splice(sid,1);
			projects.mapProjectJsonToUi();	// Send in the modified array
		},

	editTestSuiteCB : function(){
			var names = this.attr('skey').split('-');
			var sid = parseInt(names[1]);
			katana.popupController.open(katana.$activeTab.find("#editTestSuiteEntry").html(),"Edit..." , function(popup) {
				projects.lastPopup = popup; 
				console.log(katana.$activeTab.find("#editTestSuiteEntry"));
				projects.setupProjectPopupDialog(sid,popup);
			});
		},

	insertTestSuiteCB : function(){
			var names = this.attr('skey').split('-');
			var sid = parseInt(names[1]);
			var nb = new projectSuiteObject();
			projects.jsonTestSuites.splice(sid,0,nb);
			projects.mapProjectJsonToUi();	// Send in the modified array
		},


	copyToDocument: function (tag, obj) {
		localStorage.setItem(tag, JSON.stringify(obj.getJSON()));
	},

	copyFromDocument: function(tag) {
		return JSON.parse(localStorage.getItem(tag));
	},

	copyToClipboardCB : function() { 
		var names = this.attr('skey').split('-');
		var sid = parseInt(names[1]);
		//projects.jsonTestSuites[sid].copytoDocument('lastSuiteCopied', projects.jsonTestSuites[sid]);
		projects.copyToDocument('lastSuiteCopied', projects.jsonTestSuites[sid]);

	},

	insertFromClipboardCB : function() { 
		var names = this.attr('skey').split('-');
		var sid = parseInt(names[1]);
		//jsonData = projects.jjsonTestSuites[sid].copyFromDocument('lastSuiteCopied');
		jsonData = projects.copyFromDocument('lastSuiteCopied');
		console.log("Retrieving ... ", jsonData);
		var nb  = new projectSuiteObject(jsonData);
		projects.jsonTestSuites.splice(sid,0,nb);
		projects.mapProjectJsonToUi();	// Send in the modified array
	},

	duplicateTestSuiteCB : function(){
			var names = this.attr('skey').split('-');
			var sid = parseInt(names[1]);
			var jsonData = projects.jsonTestSuites[sid].getJSON();
			var nb  = new projectSuiteObject(jsonData);
			projects.jsonTestSuites.splice(sid,0,nb);
			projects.mapProjectJsonToUi();	// Send in the modified array
		},

	getResultsDirForProjectRow: function() {
	      var callback_on_accept = function(selectedValue) { 
	      		console.log(selectedValue);
	      		var sid = katana.$activeTab.attr('project-suite-row');
	      		var pathToBase = katana.$activeTab.find('#savefilepath').text();
	      		console.log("File path ==", pathToBase);
	      		var nf = prefixFromAbs(pathToBase, selectedValue);
	      		projects.jsonTestSuites[sid]['path'] = nf;
	      		console.log("Path set to ",nf," for ", sid);
	      		console.log(projects.jsonTestSuites);
	      		projects.createSuitesTable();
	      		projects.createD3treeData();
				projects.createD3tree();
	            };
	      var callback_on_dismiss =  function(){ 
	      		console.log("Dismissed");
		 };
	     katana.fileExplorerAPI.openFileExplorer("Select a file", false , $("[name='csrfmiddlewaretoken']").val(), false, callback_on_accept, callback_on_dismiss);
	},

	swapViews: function(){
		console.log("Hellos!", projects.treeView);
		if (projects.treeView == 0) {
			katana.$activeTab.find("#projects-standard-edit").hide();
			katana.$activeTab.find("#projects-graphics-edit").show();
			projects.treeView = 1; 
		} else {
			projects.treeView = 0;
			katana.$activeTab.find("#projects-standard-edit").show();
			katana.$activeTab.find("#projects-graphics-edit").hide();

		}
	},

	showSuiteFromProject:function () {
		var fname = this.attr('skey');
		var href='/katana/suites';
		katana.templateAPI.load.call(this, href, '/static/suites/js/suites.js,', null, 'suite', function() { 
				var xref="./suites/editSuite/?fname="+fname; 
	    		katana.templateAPI.subAppLoad(xref,null,function(thisPage) {
						suites.mapFullSuiteJson(fname);
	    		});

		}); 
	},

	testProjectSortEventHandler : function(event, ui ) {
		var listSuites = katana.$activeTab.find('#tableOfTestSuitesForProject tbody').children(); 
		console.log(listSuites);
				if (listSuites.length < 2) {
		 return; 
		}
		console.log(projects.jsonProjectObject.Testsuites );
		var oldSuitesteps = projects.jsonProjectObject.Testsuites;
		var newSuitesteps = new Array(listSuites.length);
		console.log("List of ... "+listSuites.length);
		for (xi=0; xi < listSuites.length; xi++) {
			var xtr = listSuites[xi];
			var ni  = xtr.getAttribute("data-sid");
			console.log(xi + " => " + ni);
			newSuitesteps[ni] = oldSuitesteps[xi];
			}

		console.log(projects.jsonProjectObject);
		projects.jsonProjectObject.Testsuites = newSuitesteps;
		console.log(projects.jsonProjectObject.Testsuites);
		
		projects.jsonTestSuites = projects.jsonProjectObject.Testsuites;
		projects.mapProjectJsonToUi();

	},

	copyTestSuite: function (src,dst) { 
		var dst = jQuery.extend(true, {}, src); 
		return dst; 
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

		katana.$activeTab.find('#projectState').val(projects.jsonProjectObject.Details.State);
		katana.$activeTab.find('#projectDate').val(projects.jsonProjectObject.Details.cDate + " " + projects.jsonProjectObject.Details.cTime);
		katana.$activeTab.find('#project_onError_action').val(projects.jsonProjectObject.Details.onError_action);
		katana.$activeTab.find('#project_onError_value').val(projects.jsonProjectObject.Details.onError_value);
		katana.$activeTab.find('#projectResultsDir').val(katana.$activeTab.find("#projectResultsDir").val());
		projects.createSuitesTable();
		projects.fillProjectDefaultGoto();

		projects.createD3treeData();
		projects.createD3tree();

	},  // end of function 

	saveChangesToRowCB: function() {
			projects.mapUItoProjectSuite( projects.lastPopup);
			katana.popupController.close(projects.lastPopup);
			projects.mapProjectJsonToUi();
	},


};
