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

  //function to create codemirror instance
     if(!editor.codeEditor){    //check to see if a codemirror instance is already alive, if so just se the new data selected

       //*********Need to add function to allow multiple codemirror instance to be created in different tabs***********

      editor.codeEditor = CodeMirror.fromTextArea(katana.$activeTab.find('#code')[0], {
        lineNumbers: true,
        mode: "xml"
     });

        editor.codeEditor.setValue(data);
      }
        else {

          editor.codeEditor.setValue(data);
        }
//end function
      });
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
      console.log(json_data);
    //  katana.templateAPI.post(url,katana.$activeTab.find(".csrf-container input").val(),json_data, function(data){});

      //katana.templateAPI.post(url,katana.$activeTab.find(".csrf-container input").val(),json_data, function(data){ alert("Saved...");}
      //katana.templateAPI.post( url,katana.$activeTab.find(".csrf-container input").val(), newFileContent, funcion(data){ });


    }

  },

  filesViewer:{

    loadFilesTree: function(){
      var dataToSend = JSON.stringify({'start_dir': katana.$activeTab.find('#editor_layout_container').attr('data-startdir')});
      console.log(dataToSend);
      var url = 'editor/getFiles';
      var dataType = 'json';
      katana.templateAPI.get.call(katana.$activeTab, url, null, dataToSend, dataType, editor.filesViewer.buildTree);
    },

    buildTree: function(data){
      katana.$activeTab.find('#editor_layout_container').jstree({
        'core': {
          'data': [data],
        },
      });
      katana.$activeTab.find('#editor_layout_container').jstree().hide_dots();
    },
  }



}
