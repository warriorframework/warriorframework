
var execution = {

	// closeDialog: function(){
	// 	var panel_container = katana.$activeTab.find('.execution.exec-container');
	// 	var dialog = katana.$activeTab.find('.execution.dialog_container');
	// 	panel_container.removeClass('is-blurred');
	// 	panel_container.css('pointer-events', 'auto');
	// 	dialog.hide();
	// },
	//
	//
	// resetForm: function(form){
	// 	//reset a form , takes in jquery form element as input as input
	// 	form[0].reset();
	// },

	setCmdCreatorObject: function(){
		var elem = $(this);
		elem.data('cmdCreatorObject', cmdBuilder.cmdCreator);
	},


	layoutViewer: {
			/* layoutViewer:
			- Has functions related to viewing or changing the layout in execution app.
			*/
			loadWs: function(){
				var dataToSend = JSON.stringify({'start_dir': katana.$activeTab.find('#execution_layout_container').attr('data-startdir')});
				var url = 'execution/getWs';
		    var dataType = 'json';
				execution.layoutViewer.clearTree();
				katana.templateAPI.get.call(katana.$activeTab, url, null, dataToSend, dataType, execution.layoutViewer.buildTree);
			},


			clearTree: function(){
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
				katana.$activeTab.find('#execution_layout_container').jstree({
					'core': {
						'data': [data],
					},
				});
				katana.$activeTab.find('#execution_layout_container').jstree().hide_dots();
			},


			initConfig: function(){
				var execution_layout_container =  katana.$activeTab.find('#execution_layout_container');
				var startdir = $(execution_layout_container).attr('data-startdir');
				var dialog = katana.$activeTab.find('#configure_layout_dialog');
				var ws = dialog.find('[name="warriorspace"]');

				ws.val(startdir);
				ws.attr('value', startdir);
				return {'ws': ws, 'dialog': dialog};
			},

			configureLayout: function(){
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
				var dialog = katana.$activeTab.find('#configure_layout_dialog');
				var state = true ? val == 'disable' : false ;
				btn = dialog.find('[name="configure_layout_confirm"]');
				btn.prop('disabled', state);
			},

			showHideDialog: function(val){
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
			ul_elem = katana.$activeTab.find('#execution_items');
			ul_elem.empty();
		},

		add_selected: function(){
			var arr = new Array();
			var selected = katana.$activeTab.find('#execution_layout_container').jstree('get_selected', true);
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

		onAdd: function (evt){
			// console.log('Added:', evt.item, 'From:', evt.from );
			var added_el = evt.item;
			var label_text = added_el.innerText;

			// remove text from added element
			added_el.innerHTML = '';

			// assign name to the added element
			added_el.setAttribute("name", "execution_item");

			// assign class name to the added element
			added_el.className = 'execution selection-group-item';

			//  create span and add to added_element
			span_el = document.createElement('span');
			span_el.innerHTML = '::';
			span_el.className = 'execution selections-handle';
			added_el.append(span_el);

			// create label and add to added_element
			label_el = document.createElement('label');
			label_el.innerHTML = label_text;
			added_el.append(label_el);
			// create handle and add to added_element
			handle_el = document.createElement('i');
			handle_el.innerHTML = 'x';
			handle_el.className = 'js-remove';
			added_el.append(handle_el);
		},

	},








	resultsViewer: {

		execution_list : '',

		execute: function(){
				execution.resultsViewer.execution_list = [];
				var items = katana.$activeTab.find('[name="execution_item"]');
				if(items.length === 0){
					katana.openAlert({'alert_type': 'warning', 
														'heading': 'Selections is Empty',
														'text':'Select atleast one item to execute form the Layout and copy it to the Selections.'}
													);
					// alert("Select atleast one item to execute form the Layout and copy it to the Selections.");
				}else{
					for (var i=0; i < items.length; i++){
						execution.resultsViewer.execution_list.push(items[i].dataset.path);
					}
					execution.resultsViewer.openExecution();
				}
		},

		openExecution: function(){
					// open pop up
					// find page-content and add page-content inner to it


					$.ajax({
						url: "execution/getResultsIndex",
						dataType : 'html',
						type : 'GET',
						success : function(data){
								execution.resultsViewer.openExecutionPopup(data);
							},
						error : function(xhr,errmsg,err) {
								console.log('error loading results skeleton');
							}
						});
		},

		openExecutionPopup: function(initial_html){
			popup = katana.popupController.open(initial_html, 'Execution');
			execution.resultsViewer.initalizeTabStates(popup);
		},

		initalizeTabStates: function(popup){
			console_logs_button = popup.find('.execution.results-tab').find('#console-logs-button');
			console_logs_button.addClass('active');
			console_div = popup.find('#console-logs-container').find('#console-logs-content');
			console.log(console_div);
			console_div.show();
			execution.resultsViewer.executeWarrior(console_div);
			htmlResultsApi.init(popup);

		},

		switchTabs: function(){
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


		executeWarrior: function(console_div){
			var execution_file_list = execution.resultsViewer.execution_list;
			// items = document.getElementsByName('execution_item');
			// items = katana.$activeTab.find('[name="execution_item"]')
			// for (var i=0; i < items.length; i++){
			// 	execution_file_list.push(items[i].dataset.path);
			// }
			// console.log('execution_file_list', execution_file_list);
			cmdOptions = ' ';
			var url = 'execution/executeWarrior'
			var cmdBuilderElement = katana.$activeTab.find("#cmd-options-forms-container");
			var cmdCreatorObject = cmdBuilderElement.data('cmdCreatorObject');
			if (cmdCreatorObject){
				var cmdOptions = cmdCreatorObject.getCmd(execution_file_list);
				console.log('cmdOptions', cmdOptions);
			}
			console.log("cmdObject", cmdCreatorObject);
			console.log('coooooo:', cmdOptions);

			var data_to_send = JSON.stringify({"execution_file_list": execution_file_list, 'cmd_string':cmdOptions});


			//data_to_send = {"execution_file_list":["/path/to/tc2","/path/to/tc2"]}'
			//katana.templateAPI.post.call(katana.$activeTab, url, null, data);

			// making ajax call to get live console logs in a streaming fashion
			$.ajax({
				xhr: function(){
			    var xhr = new window.XMLHttpRequest();
			    //Download progress
			    xhr.addEventListener("progress", function(evt){
						console_div.html(evt.currentTarget.response);

			      if (evt.lengthComputable) {
			        var percentComplete = evt.loaded / evt.total;
			        //Do something with download progress
			      }
			    }, false);
					return xhr;
					},
			    url : url,
			    dataType : 'html',
			    type : 'GET',
					data : { data: data_to_send },
			    success : function(data){
						console.log('success');
						// execution.resultsViewer.getHtml(html_div);
						// console.log(data);
						// console_div.append(data)
					},
					error : function(xhr,errmsg,err) {
			         console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
			     }
			});

			console.log("complete");

		},

	 },
};





/* Below are methods imported from old katana for html results display*/



var htmlResultsApi = {
	popup : '' ,
	html_div: '' ,
	init: function(popup) {
		htmlResultsApi.popup = popup;
		htmlResultsApi.html_div = htmlResultsApi.popup.find('#html-results-content');
		htmlResultsApi.getHtml(htmlResultsApi.html_div);

	},

	// making an ajax call to get live html results
	getHtml: function(html_div){
		console.log("making an ajax call to get live html results");
		$.ajax({
			url : 'execution/getHtmlResults',
			dataType : 'html',
			type : 'GET',
			// data : { data: data_to_send },
			success : function(data){
				console.log('success:');
				// console.log("data form server: ", data);
				if (data != "") {
					// html_body = /<body.*?>([\s\S]*)<\/body>/.exec(data)[1];
					//console.log(html_body);
					// html_div.html(html_body);

					///
					var $html = $('<div/>').append(data);
					console.log($html);

					if ($html.find('.complete').length == 0){
						console.log('did not find complete, try again')
						htmlResultsApi.currentTimeout = window.setTimeout(function(){
							htmlResultsApi.getHtml(html_div);
						}, 1000);
					} else{
						console.log('clearing timeout')
						window.clearTimeout(htmlResultsApi.currentTimeout);
					}
					console.log('setting html')
					htmlResultsApi.setHtml($html, html_div);
				}
					else{
					console.log('empty data rxed');
					htmlResultsApi.currentTimeout = window.setTimeout(function(){
					htmlResultsApi.getHtml(html_div);
				}, 1000);

			};

			},
			error : function(xhr,errmsg,err) {
					 console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
			 }
		 });

	 },

	 setHtml: function($html, html_div){
		 console.log($html);
		 var $table = $html.find('table');
		 var $style = $html.find('style');
		 console.log($table);
		 console.log(html_div);
		 html_div.html($table);
		 html_div.append($style);
		 setTimeout(function() {
			 printFormater.init(html_div);
		 }, 100);
	 },




};



var printFormater = {
  table: '',
  bar: '',
  levels: ['KeywordRecord', 'TestcaseRecord', 'TestsuiteRecord', 'ProjectRecord'],
  statusFitlers: ['FAIL', 'ERROR', 'SKIPPED', 'PASS'],
  init: function(popup) {
    printFormater.table = popup.find('table');
    printFormater.barRelocate();
    printFormater.initAccordian();
    printFormater.sortingAPI.init();
    printFormater.justifyOrder();
    printFormater.placeData();
  },
  barRelocate: function() {
    printFormater.bar = printFormater.table.find('tr:first-child').insertBefore(printFormater.table).wrap('<div class="headingnav"></div>');
  },
  placeData: function() {
    setTimeout(function() {
      printFormater.table.find('tr[name] td:not([rowspan])').each(function() {
        var $elem = $(this);
        var useData = $elem.parent().next('tr:not([name])').find('td:nth-child( ' + ($elem.prevAll('tr[name] td:not([rowspan])').length + 1) + ' )').text();
        $elem.append('<span class="useData">' + useData + '</span>');
      });
    }, 60);
  },
  initAccordian: function() {
    printFormater.table.find('tr[name="TestcaseRecord"]').on('click', function() {
      printFormater.openAccordian.call($(this));
    });
    $(window).on('keydown', function(e) {
      if (e.keyCode == 40 && printFormater.table.find('.active').length) {
        e.preventDefault();
        printFormater.openAccordian.call(printFormater.table.find('.active').nextAll('tr[name="TestcaseRecord"]:first'));
      } else if (e.keyCode == 38 && printFormater.table.find('.active').length) {
        e.preventDefault();
        printFormater.openAccordian.call(printFormater.table.find('.active').prevAll('tr[name="TestcaseRecord"]:first'));
      }
    });
  },
  justifyOrder: function() {
    setTimeout(function() {
      printFormater.table.find('tr[name]').each(function() {
        var $elem = $(this);
        var container = $('<div class="hoverConainer"></div>');
        var level = $elem.attr('name');
        for (var i = printFormater.levels.indexOf(level) + 1; printFormater.levels.length > i; i++) container.prepend($elem.prevAll('tr[name="' + printFormater.levels[i] + '"]:first').clone());
        $elem.data(container);
      });
    }, 30);
  },
  openAccordian: function() {
    var $elem = this;
    var isActive = $elem.hasClass('active');
    $elem.parent().find('.active').removeClass('active');
    if (!isActive && !printFormater.table.hasClass('filtering')) $elem.addClass('active');
  },
  sortingAPI: {
    init: function() {
      printFormater.bar.find('th').on('click', function() {
        var $elem = $(this);
        var name = $elem.text();
        $elem.toggleClass('up');
        if (name == 'Status') printFormater.sortingAPI.filterBar(printFormater.statusFitlers, name);
      });
    },
    filterBar: function(filterList, filterScope) {
      if (printFormater.bar.siblings('.filterBar').length != 0) {
        printFormater.table.removeClass('filtering');
        printFormater.sortingAPI.filter();
        setTimeout(function() {
          printFormater.bar.siblings('.filterBar').remove();
        }, 300);
        printFormater.table.find('tr[name]').off('mouseover mouseleave');
      } else {
        printFormater.table.addClass('filtering');
        var bar = $('<div class="filterBar" filterScope="' + ($('.headingnav tr th:contains("' + filterScope + '")').prevAll().length + 1) + '"></div>');
        for (var i = 0; filterList.length > i; i++) {
          var filter = $('<span>' + filterList[i] + '<input type="checkbox" value="' + filterList[i] + '"></span>').appendTo(bar);
          filter.find('input').on('change', function() {
            printFormater.sortingAPI.filter(bar);
          });
        }
        bar.appendTo('.headingnav');
        printFormater.table.find('tr[name]').on('mouseover', 'td[rowspan]:nth-child(1)', function() {
          var $elem = $(this).closest('tr');
          $elem.addClass('hover').data().appendTo($elem);
        }).on('mouseleave', 'td[rowspan]:nth-child(1)', function() {
          var $elem = $(this).closest('tr');
          $elem.removeClass('hover').find('.hoverConainer').remove();
        });
      }
    },
    filter: function(bar) {
      if (bar) {
        var activeFilters = bar.find('input:checked').map(function() {
          return $(this).val();
        }).get();
        var filterScope = bar.attr('filterScope');
        printFormater.table.find('td[rowspan]:nth-child(' + filterScope + ')').each(function() {
          var $elem = $(this);
          if (activeFilters.indexOf($elem.text()) != -1 || activeFilters.length == 0) printFormater.sortingAPI.filterAdd($elem.closest('tr'));
          else printFormater.sortingAPI.filterRemove($elem.closest('tr'));
        });
      } else printFormater.table.find('tr').each(function() {
        printFormater.sortingAPI.filterAdd($(this));
      });
    },
    filterAdd: function(row) {
      row.removeClass('hidden');
    },
    filterRemove: function(row) {
      row.addClass('hidden');
    },
  },
};
