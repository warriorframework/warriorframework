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

        var $currentPage = katana.$activeTab;


        var $elements = $currentPage.find("input[id*='app_path_for_config']")
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
                alert("Apps have been installed!");
                $currentPage.find('#form-for-paths').html('');
                wapp_management.addAnotherApp(1);
                $currentPage.find('#installed_apps_div').html(data)
            });
    },

    getFileName: function(){
        var $browsedInput = $(this);
        var $filepath = $browsedInput.val().split("\\");
        var $filename = $filepath[$filepath.length - 1];

        var temp_array = $filename.split(".")
        var extension = temp_array[temp_array.length - 1]

        if(extension !== "zip"){
            alert("Please select a .zip file.");
            return;
        }

        var $browserInputId = $browsedInput.attr('id');
        var $currentPage = katana.$activeTab;
        var $fileInput = $currentPage.find('input[id="' + $browserInputId + '"]')

        var temp = $browserInputId.split("_");
        var $loop_num = temp[temp.length - 1];

        var $displayInput = $currentPage.find('input[id="app_path_for_config_' + $loop_num + '"]')

        $displayInput.val($filename);

        var selectedFile = $browsedInput[0].files[0];
        $.wapp_management_globals.app_path_details[$filename] = selectedFile;

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

    addAnotherApp: function(loop_num){
        if(loop_num == undefined){
            var $current = $(this);
            var $loop_num = $current.attr('input_num');
            $current.attr("input_num", (parseInt($loop_num)+1).toString());
        }
        else{
            $loop_num = loop_num;
        }

        var $parent = document.getElementById("form-for-paths");
        var html_content = '<div class="row" id="row_for_' + $loop_num + '">' +
                                '<div class="col-sm-5">' +
                                    '<input class="form-control" id="app_path_for_config_' + $loop_num + '">' +
                                '</div>' +
                                '<div class="col-sm-1" style="padding: 0.2rem 0.5rem 0 0.5rem;">' +
                                    '<label style="width: 100%;">' +
                                        '<span class="btn btn-info btn-block">' +
                                            '<input type="file" accept=".zip" ' +
                                                    'katana-change="wapp_management.getFileName" ' +
                                                    'id="file_path_' + $loop_num + '" hidden> ' +
                                            'Browse' +
                                        '</span>' +
                                    '</label>' +
                                '</div>' +
                                '<div class="col-sm-1" style="padding: 0.2rem 0.5rem 0 0.5rem;">' +
                                    '<button class="btn btn-danger btn-block" ' +
                                             'katana-click="wapp_management.deleteAppPath" ' +
                                             'app_path_index="' + $loop_num + '">' +
                                        'Delete' +
                                    '</button>' +
                                '</div>' +
                            '</div>'
        var $elem = $(html_content);

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

    goToElement: function(target){

        var $currentPage = katana.$activeTab;

        if(target == undefined){
            var $elem = $(this);
            var $elem_link = $elem.attr('elem-link');

            var $target = $currentPage.find("#" + $elem_link);
        }
        else{
            $target = target;
        }

        console.log($target);

        $all_links = $currentPage.find('.tool-bar-links')
        console.log($all_links);

        for(var i=0; i<$all_links.length; i++){
            var temp = $($all_links[i]).attr("elem-link")
            var $temp = $currentPage.find('#' + temp);
            $temp.hide();
        }

        $target.show();
        /* need to scroll to $target here */

    },

    hideAndShowCardOne: function(){

        var $currentPage = katana.$activeTab;

        var $form_for_paths = $currentPage.find('#form-for-paths');
        if($form_for_paths.children().length == 0){
            $currentPage.find('#rest-of-the-card-1').hide()
            $currentPage.find('#rest-of-the-card-2').hide()
        }
        else{
            $currentPage.find('#rest-of-the-card-1').show()
            $currentPage.find('#rest-of-the-card-2').show()
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

    },

    getPreferenceDetails: function(){

        var $currentPage = katana.$activeTab;

        var $parentDiv = $currentPage.find('#config-file-div');
        var $childDiv = $parentDiv.find('div .card-header');
        for(var i=0; i<$childDiv.length; i++){
            $($childDiv[i]).css("background-color", "#98afc7")
        }

        var $elem = $(this);
        $elem.css("background-color", "#C7B097")
        var $attribute = $elem.attr('id');

        if(jQuery.isEmptyObject($.wapp_management_globals.preference_details)){
            wapp_management.getPreferenceFile($attribute);
        }
        else{
            console.log($.wapp_management_globals.preference_details);
            if(!($attribute in $.wapp_management_globals.preference_details)){
                wapp_management.getPreferenceFile($attribute);
            }
            else {
                wapp_management.setPreferenceDetails($currentPage.find('#config-details-' + $attribute), $.wapp_management_globals.preference_details[$attribute]);
            }
        }
    },

    getPreferenceFile: function(attribute){
        $.ajax({
            type: 'GET',
            url: 'wapp_management/open_config?config_name=' + attribute,
        }).done(function(data) {
            $.wapp_management_globals.preference_details[attribute] = data;
            wapp_management.setPreferenceDetails( $('#config-details-' + attribute), data)
        });
    },

    setPreferenceDetails: function(target, data){
        var $elements = $("div[id^='config-details-']");
        for(var i=0; i<$elements.length; i++){
            var temp = $($elements[i]).html('');
        }
        target.html(data);
    },

    initFunction: function(){

        var $currentPage = katana.$activeTab;

        wapp_management.goToElement($currentPage.find('#installed_apps'));
        wapp_management.hideAndShowCardOne();


        $.wapp_management_globals = new Object();
        $.wapp_management_globals.preference_details = {};
        $.wapp_management_globals.app_path_details = {};

        wapp_management.addAnotherApp(1);


    },

    createNewPref: function(){
        var $currentPage = katana.$activeTab;
        wapp_management.goToElement($currentPage.find('#app_installation'));
    },

    editConfig: function() {

        var $elem = $(this);
        var config_name = $elem.attr("config_name");

        var $currentPage = katana.$activeTab;

        var $parentDiv = $currentPage.find('#config-file-div');
        var $childDiv = $parentDiv.find('#' + config_name);
        $childDiv.css("background-color", "#98afc7");
        var $siblings = $childDiv.siblings();
        $siblings.html("");

        delete $.wapp_management_globals.preference_details[config_name];

    }

};