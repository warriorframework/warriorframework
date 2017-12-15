var wapp_management = {

    uninstallAnApp: function(){
        var $elem = $(this);
        var app_path = $elem.attr('app_path');
        var app_type = $elem.attr('app_type');
        var app_name = $elem.attr('app_name');
        var $currentPage = katana.$activeTab;

        katana.openAlert({
            "alert_type": "warning",
            "sub_heading": "This would delete all the files associated with the App.",
            "text": "Are you sure you want to uninstall " + app_name + "?",
            "show_accept_btn": true,
            "accept_btn_text": "Yes",
            "show_cancel_btn": true,
            "cancel_btn_text": "No"
        },

        function(){
            $.ajax({
                headers: {
                    'X-CSRFToken': wapp_management.getCookie('csrftoken')
                },
                type: 'POST',
                url: 'wapp_management/uninstall_an_app/',
                data: {"app_path": app_path, "app_type": app_type}
            }).done(function(data) {
                $('#installed_apps_div').html(data)
                setTimeout(function(){
                    katana.refreshLandingPage();
                    $.ajax({
                        type: 'GET',
                        url: 'wapp_management/update_installed_apps_section/',
                    }).done(function(installed_apps_data){
                        $currentPage.find('#installed_apps_div').html(installed_apps_data);
                        katana.openAlert({
                            "alert_type": "success",
                            "text": app_name + " has been uninstalled.",
                            "timer": 1250,
                            "show_accept_btn": false,
                            "show_cancel_btn": false
                        });
                    });
                }, 2000);
            });
        },

        function(){
            katana.openAlert({
                "alert_type": "info",
                "heading": "Whew!",
                "text": "Uninstall Suspended",
                "timer": 1250,
                "show_accept_btn": false,
                "show_cancel_btn": false
            });
        });
    },

    installAnApp: function(){
        var $currentPage = katana.$activeTab;
        var $elements = $currentPage.find("input[id*='app_path_for_config']")
        var app_paths = []
        var path = "";
        for(var i=0 ; i<$elements.length; i++){
            path = $elements[i].value.trim();
            if(path == ""){
                katana.openAlert({
                    "alert_type": "danger",
                    "heading": "App Information Field Is Empty.",
                    "text": "Field Cannot Be Empty",
                    "show_accept_btn": true,
                    "show_cancel_btn": false
                 });
                return;
            }
            else {
                if($($elements[i]).attr('valid-data') == "false"){
                    katana.openAlert({
                        "alert_type": "danger",
                        "heading": "Invalid Information.",
                        "text": "One or more paths/urls to App is invalid.",
                        "show_accept_btn": true,
                        "show_cancel_btn": false
                     });
                     return
                }
                else {
                    app_paths.push(path);
                }
            }
        }

        var save_config = $(this).attr('save_config');

        if(save_config == "yes"){
            wapp_management.saveConfig(app_paths);
        }
        else {
            wapp_management.setSaveConfigAttr("yes");
        }
    },

    sendInstallInfo: function(message){
        if (message === undefined){
            message = {
                "installed": [],
                "not_installed": []
            }
        }
        var $currentPage = katana.$activeTab
        var $formDiv = $currentPage.find('#form-for-paths');
        var $formDivChildren = $formDiv.children();
        var app_path = "";
        if($formDivChildren.length > 0){
            app_path = $($formDivChildren[0]).find('input[id^="app_path_for_config"]').val();
            $.ajax({
                headers: {
                    'X-CSRFToken': wapp_management.getCookie('csrftoken')
                },
                type: 'POST',
                url: 'wapp_management/install_an_app/',
                data: {"app_paths": app_path},
            }).done(function(data){
                $($formDivChildren[0]).remove();
                if(data.status){
                    var temp = {"name": app_path, "message": data.message, "status": true};
                    message["installed"].push(temp);
                } else {
                    var temp = {"name": app_path, "message": data.message, "status": false};
                    message["not_installed"].push(temp);
                }
                setTimeout(function(){
                    katana.refreshLandingPage();
                    $.ajax({
                        type: 'GET',
                        url: 'wapp_management/update_installed_apps_section/',
                    }).done(function(installed_apps_data){
                        $currentPage.find('#installed_apps_div').html(installed_apps_data);
                        wapp_management.sendInstallInfo(message);
                    });
                }, 2000);
            });
        } else {
            var alertType = "success";
            var heading = "Apps have been installed.";
            var text = "";
            if(message["installed"].length > 0){
                for(var i=0; i<message["installed"].length; i++){
                    text += message["installed"][i]["name"] + ", ";
                }
                text = text.slice(0, -2);
                text += " have been installed successfully.<br><br>";
            }
            if(message["not_installed"].length > 0){
                alertType = "danger";
                heading = "Some apps could not be installed.";
                for(var i=0; i<message["not_installed"].length; i++){
                    text += message["not_installed"][i]["name"] + " could not be installed. Errors: " + message["not_installed"][i]["message"] + "<br><br>";
                }
            }
            wapp_management.addAnotherApp(1);
            katana.openAlert({
                "alert_type": alertType,
                "heading": heading,
                "text": text,
                "show_accept_btn": true,
                "show_cancel_btn": false
            });
        }
    },

    saveConfig: function(app_paths, callback){
        var $currentPage = katana.$activeTab;
        if(app_paths === undefined){
            var $elements = $currentPage.find("input[id*='app_path_for_config']");
            var app_paths = []
            var path = "";
            for(var i=0 ; i<$elements.length; i++){
                path = $elements[i].value.trim();
                if(path == ""){
                    katana.openAlert({
                        "alert_type": "danger",
                        "heading": "App Information Field is Empty.",
                        "text": "Field cannot be empty.",
                        "show_accept_btn": true,
                        "show_cancel_btn": false
                    });
                    return;
                }
                else {
                    app_paths.push(path)
                }
            }
        }
        katana.openAlert({
            "alert_type": "info",
            "text": "Do you want to save this configuration?",
            "show_accept_btn": true,
            "accept_btn_text": "Yes",
            "show_cancel_btn": true,
            "cancel_btn_text": "No"
        },

        function(){

            katana.openAlert({
                "alert_type": "light",
                "heading": "Configuration Name",
                "text": "Please enter a name for the configuration.",
                "show_accept_btn": true,
                "show_cancel_btn": true,
                "prompt": true
            },

            function(inputValue){
                $.ajax({
                    headers: {
                        'X-CSRFToken': wapp_management.getCookie('csrftoken')
                    },
                    type: 'POST',
                    url: 'wapp_management/create_config/',
                    data: {"app_paths": app_paths, "filename":  inputValue},
                }).done(function(data) {
                    katana.openAlert({
                        "alert_type": "success",
                        "text": "Configuration Saved: " +  inputValue,
                        "show_accept_btn": true,
                        "show_cancel_btn": false
                    },
                    function(){
                        wapp_management.setSaveConfigAttr("no");
                        var $saved_preferences = $currentPage.find('#saved-preferences');
                        $saved_preferences.html(data);
                        wapp_management.sendInstallInfo();
                    });
                });
            },
            function(){
                katana.openAlert({
                    "text": "Configuration not saved.",
                    "show_accept_btn": true,
                    "show_cancel_btn": false
                }, function(){
                    wapp_management.sendInstallInfo();
                });
            })

        },
        function(){
            katana.openAlert({
                "text": "Configuration not saved.",
                "show_accept_btn": true,
                "show_cancel_btn": false
            }, function(){
                wapp_management.sendInstallInfo();
            });
        });
    },

    setSaveConfigAttr: function(value){
        $install_btn = $('button[katana-click="wapp_management.installAnApp"]');
        $install_btn.attr('save_config', value);
    },

    addAnotherApp: function(loop_num, input_value){

        var $currentPage = katana.$activeTab;
        if(loop_num == undefined){
            var $current = $(this);
            var $loop_num = $current.attr('input_num');
            $current.attr("input_num", (parseInt($loop_num)+1).toString());
        }
        else{
            $loop_num = loop_num;
        }

        var $parent = $currentPage.find("#form-for-paths");

        if(input_value == undefined){
            input_value = "";
        }

        var html_content = '<div class="row" id="row_for_' + $loop_num + '">' +
                                '<div class="col-sm-5">' +
                                    '<input class="form-control" id="app_path_for_config_' +
                                    $loop_num + '" value="' + input_value + '" katana-change="wapp_management.validateInput" style="border-color: #dcdcdc">' +
                                '</div>' +
                                '<div class="col-sm-1" style="padding: 0.2rem 0.5rem 0 0.5rem;">' +
                                        '<button class="btn btn-info btn-block"' +
                                               'katana-click="wapp_management.openFileExplorer" ' +
                                               'id="fe_browser_' + $loop_num + '">' +
                                            'Browse' +
                                        '</button>' +
                                '</div>' +
                                '<div class="col-sm-1" style="padding: 0.2rem 0.5rem 0 0.5rem;">' +
                                    '<button class="btn btn-danger btn-block" ' +
                                             'katana-click="wapp_management.deleteAppPath" ' +
                                             'app_path_index="' + $loop_num + '">' +
                                        'Delete' +
                                    '</button>' +
                                '</div>' +
                            '</div>'

        /* <div class="col-sm-3" id="status-div" style="padding: 0.8rem 0 0 0.5rem "></div> */
        $parent.append(html_content);
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

        $all_links = $currentPage.find('.tool-bar-links')

        for(var i=0; i<$all_links.length; i++){
            var temp = $($all_links[i]).attr("elem-link")
            var $temp = $currentPage.find('#' + temp);
            $temp.hide();
        }

        $target.show();

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
            if(!($attribute in $.wapp_management_globals.preference_details)){
                wapp_management.getPreferenceFile($attribute);
            }
            else {
                wapp_management.setPreferenceDetails($currentPage.find('#config-details-' + $attribute),
                                                     $.wapp_management_globals.preference_details[$attribute]);
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

    editConfig: function(config_name, callback) {
        if(config_name == undefined){
            var $elem = $(this);
            config_name = $elem.attr("config_name");
        }

        var $currentPage = katana.$activeTab;

        var $parentDiv = $currentPage.find('#config-file-div');
        var $childDiv = $parentDiv.find('#' + config_name);
        $childDiv.css("background-color", "#98afc7");
        var $siblings = $childDiv.siblings();
        var $disabledInputs = $siblings.find('input:disabled')


        var $parent = $currentPage.find("#form-for-paths");
        $parent.html('');

        var elem_value = false;

        for(var i=0; i<$disabledInputs.length; i++){
            elem_value = $($disabledInputs[i]).val()
            wapp_management.addAnotherApp((i+1), elem_value);
            var $parentChildren = $parent.children();
            var $parentLastChild = $($parentChildren[$parentChildren.length - 1])
            wapp_management.validateInput(elem_value, $parentLastChild.find('input'), config_name);
        }

        $siblings.html('');

        setTimeout(function(){
            $currentPage.find('.page-content-inner').scrollTop(0);
        }, 100);

        delete $.wapp_management_globals.preference_details[config_name];

    },

    installAppsFromConfig: function() {
        var $currentPage = katana.$activeTab;
        var $elem = $(this);
        var config_name = $elem.attr("config_name");
        var $parentDiv = $currentPage.find('#config-file-div');
        var $childDiv = $parentDiv.find('#' + config_name);
        $childDiv.css("background-color", "#98afc7");
        var $siblings = $childDiv.siblings();
        var $disabledInputs = $siblings.find('input:disabled')


        var $parent = $currentPage.find("#form-for-paths");
        $parent.html('');

        var elem_value = false;

        for(var i=0; i<$disabledInputs.length; i++){
            elem_value = $($disabledInputs[i]).val()
            wapp_management.addAnotherApp((i+1), elem_value)
        }

        $siblings.html('');

        setTimeout(function(){
            $currentPage.find('.page-content-inner').scrollTop(0);
        }, 100);

        delete $.wapp_management_globals.preference_details[config_name];

        wapp_management.sendInstallInfo();
    },

    validateInput: function(elem_value, elem, config_name){
        if(elem_value == undefined){
            var $elem = $(this);
            elem_value = $elem.val();
            dir_name = false;
        }
        else {
            $elem = elem
        }

        if(elem_value.match(".git$")){
            wapp_management.validateData({"type": "repository", "value": elem_value}, $elem)
        }
        else if(elem_value.match(".zip$")){
            wapp_management.validateData({"type": "zip", "value": elem_value}, $elem)
        }
        else{
            wapp_management.validateData({"type": "filepath", "value": elem_value}, $elem)
        }

    },

    validateData: function(data, $elem){
        var $currentPage = katana.$activeTab;
        $.ajax({
            headers: {
                'X-CSRFToken': wapp_management.getCookie('csrftoken')
            },
            type: 'POST',
            url: 'wapp_management/validate_app_path/',
            data: data
        }).done(function(data) {
            if(!data["status"]){
                $elem.css("border-color", "red");
                $elem.attr("valid-data", false);
                if($elem.next() !== undefined){
                    $elem.next().remove();
                }
                $elem.after('<i class="fa fa-exclamation-triangle yellow" aria-hidden="true">&nbsp;' + data.message + '</i>');
            }
            else{
                $elem.css("border-color", "#dcdcdc");
                $elem.attr("valid-data", true);
                if($elem.next() !== undefined){
                    $elem.next().remove();
                }
            }
            var $displayInputs = $currentPage.find('[id^="app_path_for_config_"]')

            $currentPage.find('#rest-of-the-card-1').show()
            $currentPage.find('#rest-of-the-card-2').show()

            for(var i=0; i<$displayInputs.length; i++){
                if($($displayInputs[i]).attr("valid-data") == "false"){
                    $currentPage.find('#rest-of-the-card-1').hide()
                    $currentPage.find('#rest-of-the-card-2').hide()
                    break;
                }
            }

        });

    },

    openFileExplorer: function(){
        var $currentPage = katana.$activeTab;

        var $elemClicked = $(this);
        var elemId = $elemClicked.attr("id");
        var temp = elemId.split("_");
        var loop_num = temp[temp.length-1]

        var $displayInput = $currentPage.find("#app_path_for_config_" + loop_num)
        katana.fileExplorerAPI.openFileExplorer("Select a directory or a .zip file", false, wapp_management.getCookie('csrftoken'), false,
            function(selectedValue){
                $displayInput.attr("value", selectedValue);
                $displayInput.val(selectedValue);
                wapp_management.validateInput(selectedValue, $displayInput)
             });
    }

};