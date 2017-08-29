
var execution = {



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


	executeWarrior: function(){
		var execution_file_list = [];
		items = document.getElementsByName('execution_item');
		for (var i=0; i < items.length; i++){
			execution_file_list.push(items[i].dataset.flocn);
		}
		console.log('execution_file_list', execution_file_list)

		// var xhttp = new XMLHttpRequest();
		var url = 'execution/executeWarrior'
		var data = JSON.stringify({"execution_file_list": execution_file_list});


// {u'data': [u'{"execution_file_list":["/path/to/tc2","/path/to/tc2"]}']}
		katana.templateAPI.post.call(katana.$activeTab, url, null, data);

	},







};
