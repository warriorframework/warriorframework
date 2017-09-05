kkkk
		//
		//
	;
		items.push('<select type="text" class="text-right" id="'+s+'-onError-at-value" value="'+oneCaseStep['onError']['@value']+'" >');
		items.push('<option value="next">next</option>'); 
		items.push('<option value="abort">abort</option>'); 
		items.push('<option value="abort_as_error">abort_as_error</option>'); 
		items.push('<option value="goto">goto</option>'); 
		items.push('</select>');

		items.push('<label class="text-right" >Description:</label>');
		items.push('<input type="text" class="text-right" id="'+s+'-Step-Description" value="'+oneCaseStep['Description']+'" />');
		items.push('<div class="iteration-div">');
		items.push('<label class="text-right" >Iteration Type:</label>');
		items.push('<input type="text" class="text-right" id="'+s+'-onError-at-action" value="'+oneCaseStep['onError']['@action']+'" />');
		items.push('</div>');

		items.push('<br><span class="label label-primary">Execution</span><br>');

		items.push('<label class="text-right" >ExecType:</label>');
		items.push('<select type="text" class="text-right" id="'+s+':"Execute-ExecType" value="'+oneCaseStep['step']['@ExecType']+'" >');
		items.push('<option value="If">If</option>'); 
		items.push('<option value="If Not">If Not</option>'); 
		items.push('<option value="Yes">Yes</option>'); 
		items.push('<option value="No">No</option>'); 
		items.push('</select>'); 
		items.push('<br><span class="label label-primary">Rules</span><br>');

		items.push('<label class="text-right" >Rule-Condition:</label>');
		items.push('<input type="text" class="text-right" id="'+s+'-Execute-Rule-at-Condition" value="'+oneCaseStep['step']['Rule']['@Condition']+'" />');
		items.push('<label class="text-right" f>Rule-Condvalue:</label>');
		items.push('<input type="text" class="text-right" id="'+s+'-Execute-Rule-at-Condvalue" value="'+oneCaseStep['step']['Rule']['@Condvalue']+'" />');
		items.push('<label class="text-right" >Rule-Else:</label>');
		items.push('<input type="text" class="text-right" id="'+s+'-Execute-Rule-at-Else"  value="'+oneCaseStep['step']['Rule']['@Else']+'" />');
		items.push('<label class="text-right" >Rule-at-Elsevalue:</label>');
		items.push('<input type="text" class="text-right" id="'+s+'-Execute-Rule-at-Elsevalue"  value="'+oneCaseStep['step']['Rule']['@Elsevalue']+'" />');
		items.push('<br><span class="label label-primary">OnError</span><br>');

		items.push('<label class="text-right" >Context:</label>');