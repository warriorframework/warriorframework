var editor = {


  filesEditor:{



    loadSelectFile: function(){
      var selected = katana.$activeTab.find('#editor_layout_container').jstree('get_selected', true);
      var data = JSON.stringify(selected);
      var obj = JSON.parse(data);
      var filePath = obj[0]['li_attr']['data-path']
    //  console.log(filePath);
      var url = 'editor/getFileContent';
      var dataType = 'string';
      katana.templateAPI.post(url,katana.$activeTab.find(".csrf-container input").val(),filePath, function(data){
        console.log(data);
       /*var buildCodeEditor = CodeMirror.fromTextArea(document.getElementById("code"), {
                lineNumbers : true,
                mode: "text/html"
        });*/
     katana.$activeTab.find("#code").show();
     katana.$activeTab.find('#code').html(data);
      editor.codeEditor = CodeMirror.fromTextArea(katana.$activeTab.find('#code')[0], {
        lineNumbers: true,
        mode: "text/html",
        theme: 'mbo'

     });

        /*setTimeout(function(){
          buildCodeEditor.refresh();

        },1);*/
        console.log("Running");

      });

    },

    buildEditor: function(data){

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
