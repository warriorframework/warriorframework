	for (var s=0; s<Object.keys(xdata).length; s++ ) {
		var oneSuite = xdata[s];
		fillSuiteDefaults(oneSuite);


		console.log(oneSuite['path']);
		items.push('<h3>Edit TestSuite '+s+"</h3>");
		items.push('<div class="collapse">');

		items.push('<label class="col-md-2 text-right" for="defaultOnError>'+oneSuite['path']+'</label><br>');


		items.push('<label class=" text-right" >ExecType:</label>');
		items.push('<select type="text" class="text-right"id="'+s+'-Execute-at-ExecType"  value="'+oneSuite['Execute']['@ExecType']+'" >');
		items.push('<option value="If">If</option>'); 
		items.push('<option value="If Not">If Not</option>'); 
		items.push('<option value="Yes">Yes</option>'); 
		items.push('<option value="No">No</option>'); 
		items.push('</select>'); 
		items.push('<br><span class="label label-primary">Rules</span><br>');

		// Show Ruls for the ExecType
		items.push('<label class="col-md-2 text-right" >Rule-Condition:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-Execute-Rule-at-Condition" value="'+oneSuite['Execute']['Rule']['@Condition']+'" />');
		items.push('<label class="col-md-2 text-right" f>Rule-Condvalue:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-Execute-Rule-at-Condvalue" value="'+oneSuite['Execute']['Rule']['@Condvalue']+'" />');
		items.push('<label class="col-md-2 text-right" >Rule-Else:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-Execute-Rule-at-Else"  value="'+oneSuite['Execute']['Rule']['@Else']+'" />');
		items.push('<label class="col-md-2 text-right" >Rule-at-Elsevalue:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-Execute-Rule-at-Elsevalue"  value="'+oneSuite['Execute']['Rule']['@Elsevalue']+'" />');
		items.push('<br><span class="label label-primary">OnError</span><br>');


		items.push('<label class="col-md-2 text-right" >OnError-at-action:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-onError-at-action" value="'+oneSuite['onError']['@action']+'" />');
		items.push('<label class="col-md-2 text-right" >OnError-at-value:</label>');
		items.push('<select type="text" class="col-md-4 text-right" id="'+s+'-onError-at-value" value="'+oneSuite['onError']['@value']+'" >');
		items.push('<option value="next">next</option>'); 
		items.push('<option value="abort">abort</option>'); 
		items.push('<option value="abort_as_error">abort_as_error</option>'); 
		items.push('<option value="goto">goto</option>'); 
		items.push('</select>');


		items.push('<label class="col-md-2 text-right" >Run mode:</label>');
		items.push('<label class="col-md-2 text-right" >runmode-at-type:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-runmode-at-type" value="'+oneSuite['runmode']['@type']+'" />');
		items.push('<label class="col-md-2 text-right" >runmode-at-value:</label>');
		items.push('<select type="text" class="col-md-4 text-right" id="'+s+'-runmode-at-value" value="'+oneSuite['runmode']['@value']+'" >');
		items.push('<option value="RMT">RMT</option>'); 
		items.push('<option value="RUF">RUF</option>'); 
		items.push('<option value="RUP">RUP</option>'); 
		items.push('</select>');

		items.push('<label class="col-md-2 text-right" >retry-at-type:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-retry-at-type" value="'+oneSuite['retry']['@type']+'" />');
		items.push('<label class="col-md-2 text-right" >retry-at-Condition:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-retry-at-Condition" value="'+oneSuite['retry']['@Condition']+'" />');
		items.push('<label class="col-md-2 text-right" >retry-at-Condvalue:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-retry-at-Condvalue" value="'+oneSuite['retry']['@Condvalue']+'" />');
		items.push('<label class="col-md-2 text-right" >retry-at-count:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-retry-at-count" value="'+oneSuite['retry']['@count']+'" />');
		items.push('<label class="col-md-2 text-right" >retry-at-interval:</label>');
		items.push('<input type="text" class="col-md-4 text-right" id="'+s+'-retry-at-interval" value="'+oneSuite['retry']['@interval']+'" />');
		items.push('<br>');

		items.push('<label class="col-md-2 text-right" >impact</label>');
		items.push('<select type="text" id="'+s+':"impact" value="'+oneSuite['impact']['$']+'" >');
		items.push('<option value="impact">impact</option>'); 
		items.push('<option value="noimpact">noimpact</option>'); 
		items.push('</select>');
		items.push("<br>");

		// Allow user to delete the UI object;
		// Create handler to destroy the object and then refresh the display. 
		bid = "deleteTestSuite-"+s;
		items.push('<input type="button" class="btn-danger" value="Delete" id="'+bid+'"/>');
		$('#'+bid).off('click');  // unbind is deprecated - debounces the click event. 
		$(document).on('click','#'+bid,function(  ) {
			//alert(this.id);
			var names = this.id.split('-');
			var sid = parseInt(names[1]);
			removeTestSuite(sid,xdata);
		});
		items.push("</div>");
	}

	katana.$activeTab.find("#listOfTestSuitesForProject").html("");







	//$('<div/>', {  collapsible: "true" , html: items.join("")}).appendTo(katana.$activeTab.find("#listOfTestSuitesForProject"));
	//katana.$activeTab.find("#listOfTestSuitesForProject").html( items.join(""));


	katana.$activeTab.find("#accordion_display").accordion();
	katana.$activeTab.find("#accordion_display").hide();