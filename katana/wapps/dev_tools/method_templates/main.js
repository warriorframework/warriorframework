MethodName: function(){
  var csrf = katana.$activeTab.find('.csrf-container input').val();
  katana.templateAPI.post( 'AppName/MethodName', csrf, {'data': "Your Data"}, function( data ){
    console.log(data);
  });
},
