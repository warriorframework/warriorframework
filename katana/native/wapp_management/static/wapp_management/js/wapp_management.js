var wapp_management = {

    uninstallAnApp: function(){
        var $elem = $(this);
        var app_path = $elem.attr('app_path');
        var app_type = $elem.attr('app_type');
        var app_name = $elem.attr('app_name');
        r = confirm("This would delete all the files associated with the App. Are you sure you want to uninstall " + app_name + "?")
        if (r){
            $.ajax({
                headers: {
                    'X-CSRFToken': wapp_management.getCookie('csrftoken')
                },
                type: 'POST',
                url: 'wapp_management/uninstall_an_app/',
                data: {"app_path": app_path, "app_type": app_type}
            }).done(function(data) {
                $('#installed_apps_div').html(data)
                alert(app_name + " has been uninstalled.")
            });
        }
        else {
            alert("Whew! Uninstall suspended.")
        }
    },

    installAnApp: function(){

        var $elements = $("input[id*='app_path_for_config']")
        var app_paths = []
        var path = "";
        for(var i=0 ; i<$elements.length; i++){
            path = $elements[i].value.trim();
            if(path == ""){
                alert("Field cannot be empty");
                return;
            }
            else {
                app_paths.push(path)
            }
        }

        var save_config = $(this).attr('save_config');

        if(save_config == "yes"){
            file_saved = wapp_management.saveConfig(app_paths);
        }
        else {
            wapp_management.setSaveConfigAttr("yes");
        }

        $.ajax({
                headers: {
                    'X-CSRFToken': wapp_management.getCookie('csrftoken')
                },
                type: 'POST',
                url: 'wapp_management/install_an_app/',
                data: {"app_paths": app_paths},
            }).done(function(data) {
                $('#installed_apps_div').html(data)
            });
    },

    saveConfig: function(app_paths){
        if(app_paths === undefined){
            var $elements = $("input[id*='app_path_for_config']")
            var app_paths = []
            var path = "";
            for(var i=0 ; i<$elements.length; i++){
                path = $elements[i].value.trim();
                if(path == ""){
                    alert("Field cannot be empty");
                    return;
                }
                else {
                    app_paths.push(path)
                }
            }
        }
        r = confirm("Do you want to save this configuration?")
        if(r){
            var filename = prompt("Please enter a name for the configuration.");
            if (filename == null ||  filename == ""){
                alert("Configuration not saved.")
                return false;
            }
            else {
                $.ajax({
                    headers: {
                        'X-CSRFToken': wapp_management.getCookie('csrftoken')
                    },
                    type: 'POST',
                    url: 'wapp_management/create_config/',
                    data: {"app_paths": app_paths, "filename":  filename},
                }).done(function(data) {
                    alert("Configuration Saved: " +  filename)
                    wapp_management.setSaveConfigAttr("no");
                    return true;
                });
            }
        }
        else {
            alert("Configuration not saved.")
            return false;
        }
    },

    setSaveConfigAttr: function(value){
        $install_btn = $('button[katana-click="wapp_management.installAnApp"]');
        $install_btn.attr('save_config', value);
    },

    loadConfig: function(){
        $.ajax({
            type: 'GET',
            url: 'wapp_management/load_configs/',
        }).done(function(data) {
            $('#pop-up-file-info').html(data);
		});
    },

    addAnotherApp: function(){
        var $current = $(this);
        var $loop_num = $current.attr('input_num');
        $current.attr("input_num", (parseInt($loop_num)+1).toString());
        var $parent = document.getElementById("form-for-paths");
        var $elem = $('<div class="row" id="row_for_' + $loop_num +
        '"><div class="col-sm-5"><input class="form-control" id="app_path_for_config_'
        + $loop_num + '"></div><div class="col-sm-1" style="padding: 0.3rem 0 0 0;"><button class="btn btn-default">&nbsp;&nbsp;Browse...&nbsp;&nbsp;</button></div><div class="col-sm-1" style="padding: 0.3rem 0 0 0;"><button class="btn btn-default" katana-click="wapp_management.deleteAppPath" app_path_index="'
        + $loop_num +'">&nbsp;&nbsp;Delete&nbsp;&nbsp;</button></div></div>');

        /* <div class="col-sm-3" id="status-div" style="padding: 0.8rem 0 0 0.5rem "></div> */
        $parent.append($elem[0]);
        console.log($parent);
        wapp_management.hideAndShowCardOne();
        wapp_management.setSaveConfigAttr("yes");
    },

    openConfig: function(){
        var $elem = $(this);
        var $checked = $elem.attr('choice');

        $.ajax({
            type: 'GET',
            url: 'wapp_management/open_config?config_name=' + $checked,
        }).done(function(data) {
            $('#new-app-info').html(data);
		});
    },

    storeValue: function(){
        var $elem = $(this);
        var $value = $elem.val()

        var $attach = $("#open_config")
        var $attach = $("#open_config")
        $attach.attr("choice", $value);
    },

    getCookie: function(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    },

    goToElement: function(){
        var $elem = $(this);
        var $elem_link = $elem.attr('elem-link');

        var $target = $('#' + $elem_link);
        console.log($target);

        /* need to scroll to $target here */

    },

    hideAndShowCardOne: function(){
        var $form_for_paths = $('#form-for-paths');
        if($form_for_paths.children().length == 0){
            $('#rest-of-the-card-1').hide()
            $('#rest-of-the-card-2').hide()
        }
        else{
            $('#rest-of-the-card-1').show()
            $('#rest-of-the-card-2').show()
        }
    },

    deleteAppPath: function(){
        var $element = $(this);
        var $loop_num_str = $element.attr('app_path_index');
        var $loop_num = parseInt($loop_num_str);

        var del_element = $('#row_for_' + $loop_num);

        var $parent = $('#form-for-paths');
        var $children = $parent.children();

        var appending_html = [];

        for(var i=0; i<$children.length; i++){
            if(($($children[i]).attr('id')) !== del_element.attr('id')){
                appending_html.push($children[i]);
            }
        }
        $parent.html(appending_html);
        wapp_management.hideAndShowCardOne();
        wapp_management.setSaveConfigAttr("yes");

    }
};


$(document).ready(function() {

    wapp_management.hideAndShowCardOne();

    /*var typingTimer;
    var doneTypingInterval = 1000;
    var $elements = $("[id*='#app_path_for_config']");

    $app_path_for_config.on('keyup', function () {
      clearTimeout(typingTimer);
      typingTimer = setTimeout(doneTyping, doneTypingInterval);
    });

    $app_path_for_config.on('keydown', function () {
          clearTimeout(typingTimer);
          $status_div = $('#status-div');
          $status_div.html('<i class="fa fa-spinner fa-pulse fa-fw yellow"></i>')
    });

    function doneTyping () {
        var $status_div = $('#status-div');
        var value = $app_path_for_config.val();
        var value_list = value.split(".");
        var ext = value_list[value_list.length-1]
        if (ext == "git"){
            $status_div.html(' <i class="fa fa-check-circle green">&nbsp;.git</i>')
        }
        else if (ext == "zip") {
            $status_div.html('<i class="fa fa-check-circle green">&nbsp;.zip</i>')
        }
        else {
            $status_div.html('<i class="fa fa-check-circle green">&nbsp;directory</i>')
        }
        //$status_div.html('<i class="fa fa-times-circle red">&nbsp; Input has to be either a .zip, .git, or a directory path</i>')
    }*/

});