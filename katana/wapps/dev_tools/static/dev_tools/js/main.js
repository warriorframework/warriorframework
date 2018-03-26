var dev_tools = {

  createApp: function(){
    var csrf = katana.$activeTab.find('.csrf-container input').val();
    katana.templateAPI.post('dev_tools/build_new_app', csrf, katana.toJSON(), function( data ){
      katana.openDialog('Your app has been built and installed', 'Success');
      setTimeout( function(){
        katana.refreshLandingPage();
      }, 3000);
    });
  },

  initEditMode: function(){
    var csrf = katana.$activeTab.find('.csrf-container input').val();
    katana.fileExplorerAPI.openFileExplorer(null, '', null, null, function( appURL ){
      katana.templateAPI.post( 'dev_tools/get_urls', csrf, appURL, function( data ){
        dev_tools.populateSideBar( data.data );
      } );
    });
  },

  populateSideBar: function( data ){
    var list = katana.$activeTab.find('.side-bar > ul');
    var template = list.find('li:first');
    $.each( Object.keys(data), function(){
      var temp = template.clone().appendTo(list);
      temp.find('span').prepend( this );
      var subTemplate = temp.find('li:first');
      $.each( data[this], function(){
        subTemplate.clone().insertAfter(subTemplate).text(this.replace(/^.*[\\\/]/, '')).attr('url', this);
      });
      subTemplate.remove();
    });
    template.remove();
  },

  openFile: function(){
    var csrf = katana.$activeTab.find('.csrf-container input').val();
    var $elem = this;
    var tab = dev_tools.tabs.addTab($elem);
    katana.templateAPI.post( 'dev_tools/open_file', csrf, $elem.attr('url'), function( data ){
      dev_tools.Editor.startEditor( tab.find('.tab-content'), dev_tools.convertType($elem.text()), data.data, $elem.attr('url') );
    });
  },

  saveFile: function(){
    var $elem = this;
    var csrf = katana.$activeTab.find('.csrf-container input').val();
    var tab = $elem.closest('.cmd-tab');
    var editor = tab.data();
    var data = editor.session.getValue();
    var toSend = JSON.stringify({'file': data, 'url' : tab.attr('url') });
    katana.templateAPI.post( 'dev_tools/save_file', csrf, toSend, function(){
      $elem.addClass('active');
    });
  },

  convertType: function( str ){
    str = str.split('.').pop();
    if( str == 'js')
      str = 'javascript';
    else if( str = 'py' )
      str = 'python'
    return str;
  },

  removeActive: function( saveButton ){
    saveButton.removeClass('active');
  },

  cancelFunc: function(){
    this.closest('i.active').removeClass('active');
  },

  addActive: function(){
    this.addClass('active');
  },

  Editor: {
    startEditor: function( container, type, data, url ){
      var editor = ace.edit( container.get(0) );
      var saveButton = container.closest('.cmd-tab').find('.tool-bar .save');
      saveButton.addClass('active');
      editor.session.setValue(data);
      this.configureEditor( editor, type );
      this.initEvents( editor, container, saveButton );
      container.closest('.cmd-tab').data(editor).attr('url', url);
    },

    configureEditor: function( editor, type ){
      editor.session.setMode("ace/mode/" + type );
      editor.setTheme("ace/theme/twilight");
      editor.container.style.lineHeight = 1.3;
    },

    initEvents: function( editor, container, saveButton ){
      editor.session.on('change', function(delta) {
          // if you wanted to add auto save use this event
          dev_tools.removeActive( saveButton );
      });
      editor.commands.addCommand({
          name: 'save',
          bindKey: {win: 'Ctrl-S',  mac: 'Command-S'},
          exec: function(editor) {
              dev_tools.saveFile.call( saveButton );
          },
          readOnly: false // false if this command should not apply in readOnly mode
      });
    }

  },
  tabs:{
      tabDiv: '<div class="cmd-tab"><div class="tab-content"></div></div>',
      navTabText: '<i class="fa fa-times" katana-click="dev_tools.tabs.closeTab"></i>',

    addTab: function( $elem ){
      var topLevel = $elem.closest('.dev_tools');
      var nav = topLevel.find('.page-content > .top-nav');
      var tabName =  $elem.text();
      var navTab = $( dev_tools.tabs.tabDiv ).attr('katana-click', 'dev_tools.tabs.swichTab').append( dev_tools.tabs.navTabText + tabName ).appendTo( nav );
      var contentTab = $( dev_tools.tabs.tabDiv ).appendTo( topLevel.find('.page-content > .content') );
      navTab.data( contentTab );
      dev_tools.tabs.swichTab( navTab );
      var toolBar = topLevel.find('#tool-bar');
      toolBar.length && contentTab.prepend(toolBar.html());
      return contentTab;
    },

    swichTab: function( $tab ){
      var $tab = $tab ? $tab : this;
      var tabs = $tab.closest('.page-content').find('.cmd-tab');
      tabs.removeClass('active');
      $tab.addClass('active');
      $tab.data().addClass('active');
    },

    closeTab: function( $tab ){
      var $tab = $tab ? $tab : this.parent();
      var tabContainer = $tab.parent();
      $tab.data().remove();
      $tab.remove();
      tabContainer.find('.cmd-tab').length && dev_tools.tabs.swichTab( tabContainer.find('.cmd-tab:last-child') );
    }
  }
};
