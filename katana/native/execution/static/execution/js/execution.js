
var execution = {


	layoutViewer: {

			/* layoutViewer:
			- Has functions related to viewing or changing the layout in execution app.
			*/

			loadWs: function(){
				console.log('loading warriorspace');
				var dataToSend = JSON.stringify({'start_dir': katana.$activeTab.find('#execution_layout_container').attr('data-startdir')});

				var url = 'execution/getWs';
		    var dataType = 'json';
				execution.layoutViewer.clearTree();
				katana.templateAPI.get.call(katana.$activeTab, url, null, dataToSend, dataType, execution.layoutViewer.buildTree);
			},


			clearTree: function(){
				console.log('clearing existing layout')
				execution_layout_container = katana.$activeTab.find('#execution_layout_container');

				//remove all contents of execution layout container
				execution_layout_container.empty();

				/*remove all attributes except id, data-startDir from the execution layout container
				get the atributes node name map
				convert the attributes node name map to an array*/
				var attributes_node_map = execution_layout_container[0].attributes;
				attr_node_list = Array.prototype.slice.call(attributes_node_map);
				console.log(attr_node_list);
				for (var i = 0; i < attr_node_list.length; i++ ){
					var retain_list = ['id', 'data-startdir'];
					attr_name = attr_node_list[i].name
					if ($.inArray(attr_name, retain_list) == -1){
						console.log(attr_name);
						execution_layout_container.removeAttr(attr_name);
					}
				}
			},

			buildTree: function(data){
				console.log('building layout');
				console.log(data);
				katana.$activeTab.find('#execution_layout_container').jstree({
					'core': {
						'data': [data],
					},
				})
			},

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
									"<span class='execution selections-handle' style='float:pull-left;'> :: </span>" +
									"<label>" + text +"</label>" + "<i class='js-remove' > x </i>" + "</li>"
			ul_elem = katana.$activeTab.find('#execution_items');

			ul_elem.append(html);
		};
	},


	createLayoutSort: function(){Sortable.create(layout_items, {
		group: {
			name: 'layout_items',
			pull: 'clone',
		},
		sort: false,
	})
	},

	createSelectionsSort: function(){Sortable.create(execution_items, {
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
		onFilter: function (evt) {
	    var el = evt.item; // get dragged item
	    el && el.parentNode.removeChild(el);
	  },

		onAdd: function (evt){
			console.log('Added:', evt.item, 'From:', evt.from );
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

	})
	},


	resultsViewer: {
		openExecution: function(openExecutionPopup){
					// open pop up
					// find page-content and add page-content inner to it
					$.ajax({
						url: "execution/getResultsIndex",
						dataType : 'html',
						type : 'GET',
						success : function(data){
								console.log('loaded results html skeleton to popup successfully');
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
			console_div = popup.find('#console-logs-content');
			console_div.show();
			execution.resultsViewer.executeWarrior(console_div);
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
			var execution_file_list = [];
			items = document.getElementsByName('execution_item');
			for (var i=0; i < items.length; i++){
				execution_file_list.push(items[i].dataset.path);
			}
			console.log('execution_file_list', execution_file_list);
			var url = 'execution/executeWarrior'
			var data_to_send = JSON.stringify({"execution_file_list": execution_file_list});

			//{u'data': [u'{"execution_file_list":["/path/to/tc2","/path/to/tc2"]}']}
			//katana.templateAPI.post.call(katana.$activeTab, url, null, data);
			$.ajax({
				xhr: function(){
			    var xhr = new window.XMLHttpRequest();
			    //Download progress
			    xhr.addEventListener("progress", function(evt){
						console_div.html(evt.currentTarget.response)
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
						// console.log(data);
						// console_div.append(data)
					},
					error : function(xhr,errmsg,err) {
			         console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
			     }
			});
		},

	},












};
