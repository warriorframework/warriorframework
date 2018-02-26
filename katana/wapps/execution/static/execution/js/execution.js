
var execution = {



	setCmdCreatorObject: function(){
		var elem = $(this);
		elem.data('cmdCreatorObject', cmdBuilder.cmdCreator);
	},

	cleanupDataLiveDir: function(){
		// clean up the .data/live dir of the app on start up
		get_call_args = 				{
				'url': 'execution/cleanupDataLiveDir', 
				'csrf':null, 
				'toSend':null, 
				'dataType':'html', 
				'callBack':null, 
				'fallBack':null, 
				'callBackData':null, 
				'fallBackData':null
			}
		katana.templateAPI.get.call(katana.$activeTab, get_call_args);
		
	},

	layoutViewer: {
			/* layoutViewer:
			- Has functions related to viewing or changing the layout in execution app.
			*/

			initConfig: function(){
				var execution_layout_container =  katana.$activeTab.find('#execution_layout_container');
				var startdir = $(execution_layout_container).attr('data-startdir');
				var elems = execution.layoutViewer.setWs(startdir);
				return elems;
			},
			openExplorer: function(){
				// open the file browser to select a non-default warriorspace
				var dialog = katana.$activeTab.find('#configure_layout_dialog');
				var ws = dialog.find('[name="warriorspace"]');
				var dir = ws.attr('value');
				var csrf = katana.$activeTab.find('.csrf-container > input').val();
				katana.fileExplorerAPI.openFileExplorer('Select a directory', dir, csrf, null, execution.layoutViewer.setWs);
			},
			
			setWs: function(dirPath){
				// sets warrirospace directory to the configure layout dialog
				var dialog = katana.$activeTab.find('#configure_layout_dialog');
				var ws = dialog.find('[name="warriorspace"]');
				ws.val(dirPath);
				ws.attr('value', dirPath);
				return {'ws': ws, 'dialog': dialog};
			},
		
			loadWs: function(){
				/*
				 *function to load the jstree in the layout panel
				 *uses the start dir attribue of execution_layout_container to load the jstree
				 *first clears the existing tree
				 *makes a call to the server to get the drectory json
				 *the directory json is sent as data to the build tree function to create a new tree				 * 
				 * */
				var dataToSend = JSON.stringify({'start_dir': katana.$activeTab.find('#execution_layout_container').attr('data-startdir')});
				var url = 'execution/getWs';
				var dataType = 'json';
				execution.layoutViewer.clearTree();
				get_call_args = 				{
						'url': url, 
						'csrf':'null', 
						'toSend':dataToSend, 
						'dataType':dataType, 
						'callBack':execution.layoutViewer.buildTree, 
						'fallBack':null, 
						'callBackData':null, 
						'fallBackData':null
					}
				katana.templateAPI.get.call(katana.$activeTab, get_call_args);

				
				
			},


			clearTree: function(){
				// clears an exisitng js tree in the layout panel
				
				execution_layout_container = katana.$activeTab.find('#execution_layout_container');

				//remove all contents of execution layout container
				execution_layout_container.empty();

				/*remove all attributes except id, data-startDir from the execution layout container
				get the atributes node name map
				convert the attributes node name map to an array*/
				var attributes_node_map = execution_layout_container[0].attributes;
				attr_node_list = Array.prototype.slice.call(attributes_node_map);
				for (var i = 0; i < attr_node_list.length; i++ ){
					var retain_list = ['id', 'data-startdir'];
					attr_name = attr_node_list[i].name
					if ($.inArray(attr_name, retain_list) == -1){
						execution_layout_container.removeAttr(attr_name);
					}
				}
			},

			buildTree: function(data){
				/*build a new jstree in the layout panel
				 * the data is the json of directory tree recieved form the server
				 * */ 
				katana.$activeTab.find('#execution_layout_container').jstree({
					'core': {
						'data': [data],
					},
				});
				katana.$activeTab.find('#execution_layout_container').jstree().hide_dots();
			},

			configureLayout: function(){
				// show the configure layout dialog, have checks to see if warriospace field is epty or not.
				var elems = execution.layoutViewer.initConfig();
				var ws = elems['ws'];

				// on keyup of warriospace field, if field is empty disable confirm else enable confirm
				ws.keyup(function(){execution.layoutViewer.enableDisableConfirm(ws.val().length ===0 ? 'disable' : 'enable');})
				ws.change(function(){execution.layoutViewer.enableDisableConfirm(ws.val().length ===0 ? 'disable' : 'enable');})

				// if value of ws is empty then disable submit buttom this is a safety measure
				execution.layoutViewer.enableDisableConfirm(ws.val().length ===0 ? 'disable' : 'enable');
				execution.layoutViewer.showHideDialog('show');
			},

			close_configuration_dialog: function(){
				execution.layoutViewer.showHideDialog('hide');
			},

			confirm: function(){
				// Build a new jstree using the non default warriorspace enetered y the user
				 
				var execution_layout_container = katana.$activeTab.find('#execution_layout_container');
				var $inputs = $(katana.$activeTab.find('#configure_layout_form :input'));
				var values = {}
				for (var i = 0; i < $inputs.length; i++ ){
					values[$inputs[i].name] = $inputs[i].value;
				}
				execution_layout_container.attr('data-startdir', values['warriorspace']);
				execution.layoutViewer.showHideDialog('hide');
				execution.layoutViewer.loadWs();
			},

			clear: function(){
				execution.layoutViewer.enableDisableConfirm('disable');
				var elems = execution.layoutViewer.initConfig();
				var ws = elems['ws'];
				execution.layoutViewer.enableDisableConfirm(ws.attr('value').length ===0 ? 'disable' : 'enable');
			},

			enableDisableConfirm: function(val){
				// enable or disable the configure layout save button
				var dialog = katana.$activeTab.find('#configure_layout_dialog');
				var state = true ? val == 'disable' : false ;
				btn = dialog.find('[name="configure_layout_confirm"]');
				btn.prop('disabled', state);
			},

			showHideDialog: function(val){
				// show or hide the configure layout dialog
				var dialog = katana.$activeTab.find('#configure_layout_dialog');
				var panel_container = katana.$activeTab.find('.execution.exec-container')
				if (val == 'hide'){
					panel_container.removeClass('is-blurred');
					panel_container.css('pointer-events', 'auto');
					dialog.hide();
				}
				else {
					panel_container.addClass('is-blurred');
					panel_container.css('pointer-events', 'none');
					dialog.show();
				}
			},


	},



	selectionViewer: {

		erase: function(){
			// erase all items from the selection panel
			ul_elem = katana.$activeTab.find('#execution_items');
			ul_elem.empty();
		},

		add_selected: function(){
			// copy items from layout panel to the selections panel
			var arr = new Array();
			var selected = katana.$activeTab.find('#execution_layout_container').jstree('get_selected', true);
			
			// for each item in the layout panel get the file name, full path
			// create a li element of each with label as file name and data-path=full path to the file.
			for (i = 0; i < selected.length; ++i) {
				var tree_el = selected[i];
				var id = tree_el['id'];
				var text = tree_el['text'];
				var data_path = tree_el['li_attr']['data-path'];
				var html = 	"<li class='execution selection-group-item' name='execution_item' data-path='"+ data_path  +  "' >" +
										"<span class='execution selections-handle' style='float:pull-left;'> </span>" +
										"<label>" + text +"</label>" + "<i class='fa fa-times js-remove' ></i>" + "</li>"
				ul_elem = katana.$activeTab.find('#execution_items');

				ul_elem.append(html);
			};
		},

		createSelectionsSort: function(){Sortable.create(katana.$activeTab.find('#execution_items')[0], {
			// create a sortale ul for the files to be executed in the selections panel.
			group: {
				name: 'execution_items',
				put: ['layout_items'],
			},
			sort: true,
			handle: '.execution.selections-handle',
			animation: 150,
			draggable:'.execution.selection-group-item',
			ghostClass: 'ghost',
			filter: '.js-remove',
			scroll: true,
			scrollSensitivity: 500,
			scrollSpeed: 10,
			onFilter: function (evt) {
		    var el = evt.item; // get dragged item
		    el && el.parentNode.removeChild(el);
		  },
		})
		},

	},

	resultsViewer: {
		/*Results viewer object
		 * the num attribute is for testing purposes to check if the correct logs are written to the corect popup
		 * */
		
		execution_list : '',
		num: 1,

		execute: function(){
			/* Entry point for execution to begin
			 * forms the list of items to be executed, alerts if selections is empty.
			 * if selections is not empty gets the ResultsIndex html from the server and 
			 * calls startExecution method as call back to continue further
			*/
				execution.resultsViewer.execution_list = [];
				var items = katana.$activeTab.find('[name="execution_item"]');
				if(items.length === 0){
					katana.openAlert({'alert_type': 'warning',
									'heading': 'Selections is Empty',
									'text':'Select atleast one item to execute form the Layout and copy it to the Selections.'}
									);
				}else{
					for (var i=0; i < items.length; i++){
						execution.resultsViewer.execution_list.push(items[i].dataset.path);
					}

					get_call_args = 				{
							'url': 'execution/getResultsIndex', 
							'csrf':null, 
							'toSend':null, 
							'dataType':'html', 
							'callBack':execution.resultsViewer.startExecution, 
							'fallBack':null, 
							'callBackData':null, 
							'fallBackData':null
						}
					
					katana.templateAPI.get.call(katana.$activeTab, get_call_args);

				}
		},
		
		startExecution: function(data){
			/*Starts execution inside a popup
			 * Opens a popup and writes the ResultsIndex.html red from the server as data into the popup
			 * The ResultsIndex.html returned by the server inside the popup will have the path to the live html results file,
			 * as a data-liveHtmlFpath to the execution-results-container
			 * Opening a popup will return an array having the 1. popup element 2. console_div to write console logs to 3. html_div to write html results to
			 * Creates a new object o ExecutionClass and and attaches it to the execution-results-container as well.
			 * The executin object is initialized using the console_div, html_div, liveHtmlFpath, execution_file_list, execution.resultsViewer.num
			 * Set the command options to the execution object
			 * Once command options are set execute warrior command
			 * Executing warrior will atomatically stream the consle logs to the console_div
			 * The live html results are read by sending periodic ajax calls to read the live html results file.
			 * */

			var resultArray = execution.resultsViewer.openExecutionPopup(data);

			// If openin popup is successful, add an executionResultsObject to the execution-results-containerof the popup
			if(! $.isEmptyObject(resultArray)){
				num = execution.resultsViewer.num;
				popup = resultArray['popup'];
				console_div  = resultArray['console_div'];
				html_div = resultArray['html_div'];
				execution_results_container = popup.find('.execution-results-container');
				liveHtmlFpath = execution_results_container.attr('data-liveHtmlFpath');
				execution_file_list = execution.resultsViewer.execution_list;
				var executionObject = new ExecutionClass(console_div, html_div, liveHtmlFpath, execution_file_list, execution.resultsViewer.num);
				execution_results_container.data('executionResultsObject', executionObject);
				execution.resultsViewer.num += 1;
				executionObject.setCmdOptions();
				executionObject.executeWarrior();
				executionObject.getHtml();


			}
			else{
				console.log('error opening popup');
			}
		},
		
		openExecutionPopup: function(initial_html){
			/* function to open a popup , call function to initialize tab states in the popup
			 * returns an array having the popup, console_div, htmlresults as div elements*/
			popup = katana.popupController.open(initial_html, 'Execution');
			result = execution.resultsViewer.initalizeTabStates(popup);
			return result;
		},
		
		initalizeTabStates: function(popup){
			// Intializes tab states inside the popup i.e. makes console logs as active and shown initially
			// returns an array having the popup, console_div, htmlresults as div elements
			console_logs_button = popup.find('.execution.results-tab').find('#console-logs-button');
			console_logs_button.addClass('active');
			console_div = popup.find('#console-logs-container').find('#console-logs-content');
			console_div.show();
			html_div = popup.find('#html-results-container').find('#html-results-content');

			return {'popup': popup, 'console_div': console_div, 'html_div': html_div};
		},
		switchTabs: function(){
			// funciton to handle display on switching between tabs
			var el = $(this);
			execution_results_tab = el.parent();
			tablinks = execution_results_tab.find('.tablinks');
			contents = execution_results_tab.parent().find('.execution.tab-content');
			content = execution_results_tab.parent().find('#'+el.attr('data-content'));
			//disable display of all contents
			for (i = 0; i < contents.length; i++) {
			     contents[i].style.display = "none";
			}

			// remove all tablinks from active
			for (i = 0; i < tablinks.length; i++) {
			     tablinks[i].className = tablinks[i].className.replace("active", "");
			}

			// set the button active state
			// set the display of its content to block.
			el.addClass('active');
			content[0].style.display = 'block';

		},

		openDefectsJson: function(){
			elem = $(this);
			logpath = elem.attr('data-logpath');
			
			//make a ajax call to get the contents of the json file
			var data_to_send = JSON.stringify({'logpath': logpath, 'logtype': 'defects'});
			get_call_args = 				{
					'url': 'execution/getLogFileContents', 
					'csrf':null, 
					'toSend':data_to_send, 
					'dataType':'html', 
					'callBack':execution.resultsViewer.openDefectsJsonInPopup, 
					'fallBack':null, 
					'callBackData':null, 
					'fallBackData':null
				}
			
			
			katana.templateAPI.get.call(katana.$activeTab, get_call_args);
		},
		openConsoleLogFile: function(){
			elem = $(this);
			logpath = elem.attr('data-logpath');
			
			//make a ajax call to get the contents of the json file
			var data_to_send = JSON.stringify({'logpath': logpath, 'logtype': 'console_logs'});
			
			get_call_args = 				{
					'url': 'execution/getLogFileContents', 
					'csrf':null, 
					'toSend':data_to_send, 
					'dataType':'html', 
					'callBack':execution.resultsViewer.openDefectsJsonInPopup, 
					'fallBack':null, 
					'callBackData':null, 
					'fallBackData':null
				}
			
			katana.templateAPI.get.call(katana.$activeTab, get_call_args);
		},
		openDefectsJsonInPopup: function(data){
			data = JSON.parse(data);
			popupName = data.logfile_name;
			popupContent = JSON.stringify(data.contents, undefined, 2);
//			textArea = '<textarea id="myTextArea" cols=50 rows=10>' +popupContent + '</textarea>'
			html = '<pre>' + popupContent + '</pre>'
			popup = katana.popupController.open(html, popupName);
		},
		openXmlInApp: function(){
			elem = $(this);
			fpath = elem.attr('data-path');
			ftype = elem.attr('data-type');
			
			if (ftype.toLowerCase() === 'case'){
				var appName = 'Case';
				var xref="./cases/editCase/?fname=" + fpath;
			}else if (ftype.toLowerCase() === 'suite'){
				var appName = 'Suite';
				var xref="./suites/editSuite/?fname=" + fpath;
			}else if (ftype.toLowerCase() === 'project'){
				var appName = 'Project';
				var xref="./projects/editProject/?fname=" + fpath;
			}
			
			// open the app to edit the file
			
			katana.templateAPI.load(xref, null, null, appName) ;
			
		},
		openAccordian: function() {
			var $elem = this;
			var closest_table = $elem.closest('table');
			var closest_tr = $elem.closest('tr');
			var isActive = closest_tr.hasClass('active');
			closest_table.find('.active').removeClass('active');
			if (!isActive && !closest_table.hasClass('filtering')) {
				closest_tr.addClass('active');
				
			}
		},
		htmlFilter: function(){
			var $elem = this;
			var closest_table = $elem.closest('table');
			var closest_headingNav = $elem.closest('.headingnav');
			var name = $elem.text();
			$elem.toggleClass('up');
			execution.printFormater.sortingAPI.filterBar(execution.printFormater.statusFitlers, name, closest_headingNav, closest_table);
		},
		
	},
	
	printFormater: {
			  tables: '',
			  table: '',
			  //bar: '',
			  levels: ['KeywordRecord', 'TestcaseRecord', 'TestsuiteRecord', 'ProjectRecord'],
			  statusFitlers: ['FAIL', 'ERROR', 'SKIPPED', 'PASS'],
			  init: function(html_div) {
				var tables = html_div.find('#liveTables table');
				execution.printFormater.tables = tables;
				execution.printFormater.table = tables.last();			    
			    
			  },

			  sortingAPI: {
			    filterBar: function(filterList, filterScope, headingNav, table) {
			      if (headingNav.children('.filterBar').length != 0) {
			        table.removeClass('filtering');
			        execution.printFormater.sortingAPI.filter(null, table);
			        setTimeout(function() {
			        	headingNav.children('.filterBar').remove();
			        }, 300);
			        table.find('tr[name]').off('mouseover mouseleave');
			      } else {
			        table.addClass('filtering');
			        var bar = $('<div class="filterBar" filterScope="' + (headingNav.find('tr th:contains("' + filterScope + '")').prevAll().length + 1) + '"></div>');
			        for (var i = 0; filterList.length > i; i++) {
			          var filter = $('<span>'  + '<input type="checkbox" value="' + filterList[i] + '">' + filterList[i] + '</span>').appendTo(bar);
			          filter.find('input').on('change', function() {
			            execution.printFormater.sortingAPI.filter(bar, table);
			          });
			        }
			        bar.appendTo(headingNav);
			        table.find('tr[name]').on('mouseover', 'td[rowspan]:nth-child(1)', function() {
			          var $elem = $(this).closest('tr');
			          if($elem) $elem.addClass('hover').data().appendTo($elem);
			        }).on('mouseleave', 'td[rowspan]:nth-child(1)', function() {
			          var $elem = $(this).closest('tr');
			          $elem.removeClass('hover').find('.hoverConainer').remove();
			        });
			      }
			    },
			    filter: function(bar, table) {
			      if (bar) {
			        var activeFilters = bar.find('input:checked').map(function() {
			          return $(this).val();
			        }).get();
			        var filterScope = bar.attr('filterScope');
			        table.find('td[rowspan]:nth-child(' + filterScope + ')').each(function() {
			          var $elem = $(this);
			          if (activeFilters.indexOf($elem.text()) != -1 || activeFilters.length == 0) execution.printFormater.sortingAPI.filterAdd($elem.closest('tr'));
			          else execution.printFormater.sortingAPI.filterRemove($elem.closest('tr'));
			        });
			      } else table.find('tr').each(function() {
			        execution.printFormater.sortingAPI.filterAdd($(this));
			      });
			    },
			    filterAdd: function(row) {
			      row.removeClass('hidden');
			    },
			    filterRemove: function(row) {
			      row.addClass('hidden');
			    },
			  },
			},
	
	
};
	
	class ExecutionClass{
		/*Execution class
		 * New object of this class has to be created for each execution 
		 * so that the results and logs are reported separately for each execution and to avoid overlap*/
		constructor(console_div, html_div, liveHtmlFpath, fileList, num){
			// constructor, self explanatory
			this.console_div = console_div;
			this.html_div = html_div;
			this.cmd = '';
			this.liveHtmlFpath = liveHtmlFpath;
			this.execution_file_list = fileList;
			this.num = num;

		}
		setCmdOptions(){
			/*Set the command options of the instance of this class
			 * this done by grabbing the command creator object attached to the cmd-options-dialog of the active tab
			 * and reading the command from that object*/
			var cmd = ' ';
			var cmdBuilderElement = katana.$activeTab.find("#cmd-options-dialog");
			var cmdCreatorObject = cmdBuilderElement.data('cmdCreatorObject');
			if (cmdCreatorObject){cmd = cmdCreatorObject.getCmd(this.execution_file_list);}
			this.cmd = cmd;
		}
		executeWarrior(){
			/*Make an ajax call to the server and pass the 1. list of file, 2. cmd options, 3. liveHtmlFpath
			 * The server would use the use execution file list for priting purposes.
			 * would append the live htmlpath tag to the start of the cmd and execute warriro using the thus formed command
			 * the server would not print the liveHtml tag to the consle logs as the user need not know about it.
			 * 
			 * */
			var url = 'execution/executeWarrior';
			var data_to_send = JSON.stringify({"execution_file_list": this.execution_file_list, 'cmd_string':this.cmd, 'liveHtmlFpath': this.liveHtmlFpath});
			var console_div = this.console_div;
			// making ajax call to get live console logs in a streaming fashion
			$.ajax({
				xhr: function(){
					var xhr = new window.XMLHttpRequest();
					//Download progress
					xhr.addEventListener("progress", function(evt){
						console_div.html(evt.currentTarget.response);
						var page_content_inner = console_div.parent().parent();
						console.log('page_content_inner: ', page_content_inner);
						var scroll_height = page_content_inner.prop("scrollHeight");
						page_content_inner.scrollTop(scroll_height);
					}, false);
					return xhr;
					},
					url : url,
					dataType : 'html',
					type : 'GET',
					data : { data: data_to_send },
					success : function(data){
						//console.log('success');
					},
					error : function(xhr,errmsg,err) {
							 console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
					 }
			});
			// console.log("complete");
		}// executeWarrior ends

		getHtml(){
			/*Make an ajax call to get the live html results from the server
			 * this is done by passing the location of live html results file to the server
			 * periodically and the server returns the html string by reading the whole file
			 * When the html string returned by the server is not empty the html string is wrapped into a div
			 * the setHtml function is called
			 * to print the table to the div.*/
			var html_div = this.html_div;
			var executionObject = this;
			var liveHtmlFpath = this.liveHtmlFpath;
			//console.log("making an ajax call to get live html results");
			//console.log('liveHtmlFpath: ', liveHtmlFpath);
			var data_to_send = JSON.stringify({"liveHtmlFpath": liveHtmlFpath});
			$.ajax({
				url : 'execution/getHtmlResults',
				dataType : 'html',
				type : 'GET',
				data: { data: data_to_send },
				success : function(data){
					if (data != "") {
						 var $html = $('<div/>').append(data);

						if ($html.find('.eoc').length == 0){
							//console.log('did not find eoc, try again')
							var currentTimeout = window.setTimeout(function(){
								executionObject.getHtml();
							}, 5000);
						} else{
							//console.log('found eoc clearing timeout')
							// on finding eoc delete the live html file
							executionObject.deleteLiveHtmlFile();
							window.clearTimeout(currentTimeout);
						}
						//console.log('setting html')
						executionObject.setHtml($html);
					}
						else{
						//console.log('empty data rxed');
						currentTimeout = window.setTimeout(function(){
						executionObject.getHtml();
					}, 5000);
				};

				},
				error : function(xhr,errmsg,err) {
						 console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
				 }
			 });

		 }
		 setHtml($html){
			 /*takes the live html string wrapped in a div and calls the print formatter
			  * method to adjust styles and fit into the popup*/
//			 var $table = $html.find('table');
//			 var $style = $html.find('style');
//			 this.html_div.html($table);
//			 this.html_div.append($style);
			 //console.log($html);
			 //console.log(this);
			 this.html_div.html($html);
			 this.disableHref();
			 this.barRelocate();
			 this.placeData();
			 setTimeout(function() {
				 execution.printFormater.init(this.html_div);
			 }, 100);
		 }
		 deleteLiveHtmlFile(){
			 /*Deletes the live html file post find eoc*/
			 var data_to_send = JSON.stringify({'liveHtmlFpath': this.liveHtmlFpath});
			 
				get_call_args = 				{
						'url': 'execution/deleteLiveHtmlFile', 
						'csrf':null, 
						'toSend':data_to_send, 
						'dataType':'html', 
						'callBack':execution.resultsViewer.openDefectsJsonInPopup, 
						'fallBack':null, 
						'callBackData':null, 
						'fallBackData':null
					}
			 
			 katana.templateAPI.get.call(katana.$activeTab, get_call_args);

		 }
		 disableHref(){
			  var tables = this.html_div.find('#liveTables table');
			  $.each(tables, function(index, table){
				  var table = $(table);
				  var aList =   table.find('a');
					$.each(aList, function(index, element){
						var href = $(element)[0].hasAttribute('href');
						if(href){
							$(element).attr('onclick', 'return false;')
						}
					});
			  });
		  }
		 barRelocate(){
			  var tables = this.html_div.find('#liveTables table');
			  //console.log('tables 1: ',tables);
			  // wrap each heading row in a heading nav div
			  $.each(tables, function(index, table){
					var headingRow = $(table).find('[name=HeadingRow]');
					headingRow.wrap('<div class="headingnav"></div>');
			  });
		  }
		  placeData(){
			  	var tables = this.html_div.find('#liveTables table');
			    setTimeout(function() {			    	
			    	//console.log('tables 2: ',tables);
			    	$.each(tables, function(index, table){
			    		// console.log(table);
			    		var dynamicTdList = $(table).find('tr[name] td:not([rowspan])')
			    		//console.log('dnamic list:', dynamicTdList);
			    		$.each(dynamicTdList, function(index, elem){
			    			var elem = $(elem);
			                //var $elem = $(this);
			                //console.log('element', $elem);
			                //console.log('paren.next: ', $elem.parent().next('tr:not([name])'));
			                //console.log('prev all: ',$elem.prevAll('tr[name] td:not([rowspan])'));
			                var useData = elem.parent().next('tr:not([name])').find('td:nth-child( ' + (elem.prevAll('tr[name] td:not([rowspan])').length + 1) + ' )').text();
			                elem.append('<span class="useData">' + useData + '</span>');
			                // console.log($elem.html())
			                // var html = $elem.html()
			                // console.log('use data: ',useData);
			                // $elem.html(html +  '<span class="useData">' + useData + '</span>');
			              });   		
			    		});
			      }, 60);
			  }

}//ExecutionClass ENDS
	



