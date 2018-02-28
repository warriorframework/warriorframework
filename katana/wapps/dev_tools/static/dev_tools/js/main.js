var dev_tools = {

  createApp: function(){
    var csrf = katana.$activeTab.find('.csrf-container input').val();
    katana.templateAPI.post('dev_tools/build_new_app', csrf, katana.toJSON(), function( data ){
      katana.openDialog('Your app has been built and installed', 'Success');
      setTimeout( function(){
        katana.refreshLandingPage();
      }, 3000);
    });
  }

};
