 var cases = {

	startNewCase: function() {
	  var xref="./cases/editCase/?fname=NEW"; 
	     katana.$view.one('tabAdded', function(){
	        mapFullCaseJson("NEW",'#emptyTestCaseData');
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
			      katana.$view.one('tabAdded', function(){
			      //var jdata = sdata.replace(/'/g, '"');
			      //var jsdata = JSON.parse(jdata)
			     caseApp.mapFullCaseJson(thePage,'#listOfTestStepsForCase');
				  });
				  var xref="./cases/editCase/?fname=" + thePage; 
				  katana.templateAPI.load(xref, null, null, 'Case') ;
					});
				katana.$activeTab.find('#myCaseTree').jstree(jdata);
			});
		//katana.$activeTab.find('#mmm').hide();
	},

	closeCase: function(){
		katana.closeSubApp();
	},

};
