var editor = {



  filesEditor:{
    loadSelectFile: function(){
      var selected = katana.$activeTab.find('#editor_layout_container').jstree('get_selected', true);
      //find the file name in which the user selected from the file tree (Json object), reference get_files function in Editor class in Views.py

      var data = JSON.stringify(selected);  //
      var obj = JSON.parse(data);
      var filePath = obj[0]['li_attr']['data-path'];
      //find the json property thats holds the full file path to be passed to get_file_content function in Editor class in Views.py
      //****This path needs to be saved globally or passed to the saveFile function
      var url = 'editor/getFileContent';
      var dataType = 'string';

      //POST request to send filepath and receve contents of the specific file - data will be file contents
      katana.templateAPI.post(url,katana.$activeTab.find(".csrf-container input").val(),filePath, function(data){

        mode_type = editor.filesEditor.fileExtension(filePath);
        console.log(mode_type)
  //function to create codemirror instance

     if(!editor.codeEditor){    //check to see if a codemirror instance is already alive, if so just se the new data selected

       //*********Need to add function to allow multiple codemirror instance to be created in different tabs***********

       //Regex function to check the extension of the file, changes the mode for codemirror
       console.log("WHERE")
      editor.codeEditor = CodeMirror.fromTextArea(katana.$activeTab.find('#code')[0], {
        lineNumbers: true,
        mode: mode_type,
     });

        editor.codeEditor.setValue(data);
      }
        else {

          editor.codeEditor.setOption("mode",mode_type);
          editor.codeEditor.setValue(data);
        }
//end function
      });
    },

    fileExtension: function(filePath){
      ext = filePath.split('.').pop();
        if(ext == 'py'){
          mode = 'python'
        }else if(ext =='js'){
          mode = 'javascript'
        }
        else if(ext == 'txt'){
          mode = ''
        }else {
          mode = 'text/html'
        }
//add other languages here
        return mode
    },
    saveFile: function(){
      var selected = katana.$activeTab.find('#editor_layout_container').jstree('get_selected', true);
      var data = JSON.stringify(selected);
      var obj = JSON.parse(data);
      var filePath = obj[0]['li_attr']['data-path'];
      var newFileContent = editor.codeEditor.getValue();
      var url = 'editor/saveFile';
      var dataType = 'json';
      var json_data = {'filePath' : filePath, 'Text' : newFileContent};
      //console.log(json_data);
      katana.templateAPI.post(url,katana.$activeTab.find(".csrf-container input").val(),json_data, function(data){
        alert("Saved File");
      });

      //katana.templateAPI.post(url,katana.$activeTab.find(".csrf-container input").val(),json_data, function(data){ alert("Saved...");}
      //katana.templateAPI.post( url,katana.$activeTab.find(".csrf-container input").val(), newFileContent, funcion(data){ });


    }

  },

  filesViewer:{

    setWs: function(dirPath){
      // sets warrirospace directory to the configure layout dialog
      var dialog = katana.$activeTab.find('#configure_layout_dialog');
      var ws = dialog.find('[name="warriorspace"]');
      ws.val(dirPath);
      ws.attr('value', dirPath);
      return {'ws': ws, 'dialog': dialog};
    },


    initConfig: function(){
      var editor_layout_container =  katana.$activeTab.find('#editor_layout_container');
      var startdir = $(editor_layout_container).attr('data-startdir');
      var elems = editor.filesViewer.setWs(startdir);
      return elems;
    },

    openExplorer: function(){
      // open the file browser to select a non-default warriorspace
      var dialog = katana.$activeTab.find('#configure_layout_dialog');
      var ws = dialog.find('[name="warriorspace"]');
      var dir = ws.attr('value');
      var csrf = katana.$activeTab.find('.csrf-container > input').val();
      katana.fileExplorerAPI.openFileExplorer('Select a directory', dir, csrf, null, editor.filesViewer.setWs);
    },

    configureLayout: function(){
      // show the configure layout dialog, have checks to see if warriospace field is epty or not.
      var elems = editor.filesViewer.initConfig();
      var ws = elems['ws'];
      // on keyup of warriospace field, if field is empty disable confirm else enable confirm
      ws.keyup(function(){editor.filesViewer.enableDisableConfirm(ws.val().length ===0 ? 'disable' : 'enable');})
      ws.change(function(){editor.filesViewer.enableDisableConfirm(ws.val().length ===0 ? 'disable' : 'enable');})

      // if value of ws is empty then disable submit buttom this is a safety measure
      editor.filesViewer.enableDisableConfirm(ws.val().length ===0 ? 'disable' : 'enable');
      editor.filesViewer.showHideDialog('show');
    },

    confirm: function(){
      // Build a new jstree using the non default warriorspace enetered y the user

      var editor_layout_container = katana.$activeTab.find('#editor_layout_container');
      var $inputs = $(katana.$activeTab.find('#configure_layout_form :input'));
      var values = {}
      for (var i = 0; i < $inputs.length; i++ ){
        values[$inputs[i].name] = $inputs[i].value;
      }
      editor_layout_container.attr('data-startdir', values['warriorspace']);
      editor.filesViewer.showHideDialog('hide');
      editor.filesViewer.loadFilesTree();
    },

    clear: function(){
      editor.filesViewer.enableDisableConfirm('disable');
      var elems = editor.filesViewer.initConfig();
      var ws = elems['ws'];
      editor.filesViewer.enableDisableConfirm(ws.attr('value').length ===0 ? 'disable' : 'enable');
    },

    close_configuration_dialog: function(){
      editor.filesViewer.showHideDialog('hide');
    },

    showHideDialog: function(val){
      // show or hide the configure layout dialog
      var dialog = katana.$activeTab.find('#configure_layout_dialog');
      var panel_container = katana.$activeTab.find('.editor.edit-container')
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

    enableDisableConfirm: function(val){
      // enable or disable the configure layout save button
      var dialog = katana.$activeTab.find('#configure_layout_dialog');
      var state = true ? val == 'disable' : false ;
      btn = dialog.find('[name="configure_layout_confirm"]');
      btn.prop('disabled', state);
    },

    loadFilesTree: function(){
      var dataToSend = JSON.stringify({'start_dir': katana.$activeTab.find('#editor_layout_container').attr('data-startdir')});
      console.log(dataToSend);
      var url = 'editor/getFiles';
      var dataType = 'json';
      editor.filesViewer.clearTree();
      katana.templateAPI.get.call(katana.$activeTab, url, null, dataToSend, dataType, editor.filesViewer.buildTree);
    },

    buildTree: function(data){
      katana.$activeTab.find('#editor_layout_container').jstree({
        'core': {
          'data': [data],
        },
      });
      katana.$activeTab.find('#editor_layout_container').jstree().hide_dots();
      $(katana.$activeTab.find('#editor_layout_container')).bind("dblclick.jstree", function (event) {
          editor.filesEditor.loadSelectFile();
      });
    },
    clearTree: function(){
      // clears an exisitng js tree in the layout panel

      editor_layout_container = katana.$activeTab.find('#editor_layout_container');

      //remove all contents of editor layout container
      editor_layout_container.empty();

      /*remove all attributes except id, data-startDir from the editor layout container
      get the atributes node name map
      convert the attributes node name map to an array*/
      var attributes_node_map = editor_layout_container[0].attributes;
      attr_node_list = Array.prototype.slice.call(attributes_node_map);
      for (var i = 0; i < attr_node_list.length; i++ ){
        var retain_list = ['id', 'data-startdir'];
        attr_name = attr_node_list[i].name
        if ($.inArray(attr_name, retain_list) == -1){
          editor_layout_container.removeAttr(attr_name);
        }
      }
    },
  }



}
