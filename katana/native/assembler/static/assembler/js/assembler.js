var assembler = {
    init: function(){
        $currentPage = katana.$activeTab;
        $.ajax({
                headers: {
                    'X-CSRFToken': $currentPage.find('input[name="csrfmiddlewaretoken"]').attr('value')
                },
                type: 'POST',
                url: 'assembler/get_config_file/',
                data: {"filepath": false}
            }).done(function(data) {
                var dep_objs = [];
                var dependencyDom= "";
                for(var i=0; i<data.xml_contents.data.warhorn.dependency.length; i++){
                    dep_objs.push(new dependency(data.xml_contents.data.warhorn.dependency[i]));
                    dependencyDom = dep_objs[i].domElement;
                    dependencyDom.data("data-object", dep_objs[i]);
                    $currentPage.find('#dependency-div').append(dependencyDom);
                }

                var tools_obj = new toolsRepository(data.xml_contents.data.tools);
                var toolsDom = "";
                toolsDom = tools_obj.domElement;
                toolsDom.data("data-object", tools_obj);
                $currentPage.find('#tools-div').append(toolsDom);

                var kw_objs = []
                var kwDom = "";
                for(var i=0; i<data.xml_contents.data.drivers.repository.length; i++){
                    kw_objs.push(new kwRepository(data.xml_contents.data.drivers.repository[i]));
                    kwDom = kw_objs[i].domElement;
                    kwDom.data("data-object", kw_objs[i]);
                    $currentPage.find('#kw-div').append(kwDom);
                }

                var ws_objs = [];
                var wsDom ="";
                for(var i=0; i<data.xml_contents.data.warriorspace.repository.length; i++){
                    ws_objs.push(new wsRepository(data.xml_contents.data.warriorspace.repository[i]));
                    wsDom = ws_objs[i].domElement;
                    wsDom.data("data-object", ws_objs[i]);
                    $currentPage.find('#ws-div').append(wsDom);
                }
            });
    },

    installDependency: function(){
        var $elem = $(this);
        if($elem.attr('aria-selected') == 'false'){
            $elem.attr('aria-selected', 'true');
            $parent = $elem.parent();
            $elem.hide();
            $parent.find('br').hide();
            $parent.find('hr').hide();
            $parent.append('<div class="card" style="padding: 0.5rem 1rem;"></div>')
            var $subClass = $parent.find('.card')

            $subClass.append('<div class="row">' +
                                '<div class="col-sm-10">Install As:&nbsp;</div>' +
                                '<div class="col-sm-1" style="padding-bottom: 0.4rem;">' +
                                    '<i class="fa fa-times" aria-hidden="true" katana-click="assembler.cancelDependencyInstallation"></i>' +
                                '</div>' +
                             '</div>')
            $subClass.append('<div class="row">' +
                                 '<div class="col-sm-2"></div>' +
                                 '<div class="col-sm-8">' +
                                     '<button class="btn btn-info" katana-click="assembler.installDependencyAsAdmin">Admin</button>' +
                                     '&nbsp;&nbsp;' +
                                     '<button class="btn btn-info" katana-click="assembler.installDependencyAsUser">User</button>' +
                                 '</div>' +
                             '</div>')
        }
        else{
            $elem.attr('aria-selected', 'false');
            $elem.html('Install');
            $elem.css("background-color", "white");
            $elem.css("color", "black")

        }
    },

    cancelDependencyInstallation: function(elem, ariaValue){
        if(elem){
            var $elem = elem;
        }
        else{
            $elem = $(this);
        }
        if(ariaValue == undefined){
            ariaValue = "false";
        }
        var $parentDiv = $elem.closest('.card');
        var $installBtn = $parentDiv.siblings('button[katana-click="assembler.installDependency"]');
        $installBtn.attr('aria-selected', ariaValue);
        $parentDiv.remove();
        $installBtn.siblings('br').show();
        $installBtn.siblings('hr').show();
        $installBtn.show();
    },

    installDependencyAsAdmin: function(){
        var $elem = $(this);
        $.when(assembler.setInstallBtn($elem, "Install As Admin")).then(assembler.cancelDependencyInstallation($elem, "true"));
    },

    installDependencyAsUser: function(){
        $.when(assembler.setInstallBtn($elem, "Install As User")).then(assembler.cancelDependencyInstallation($elem, "true"));
    },

    setInstallBtn: function(elem, text){
        var $elem = elem;
        var $parentDiv = $elem.closest('.card');
        var $topLevelDiv = $parentDiv.closest('.card-block').closest('.card').parent();
        if(text == "Install As Admin"){
            $topLevelDiv.data().dataObject.install = "yes";
            $topLevelDiv.data().dataObject.user = "no";
        } else {
            $topLevelDiv.data().dataObject.install = "yes";
            $topLevelDiv.data().dataObject.user = "yes";
        }
        var $installBtn = $parentDiv.siblings('button[katana-click="assembler.installDependency"]');
        $installBtn.html(text + '&nbsp;<i class="fa fa-check" style="color: white" aria-hidden="true"></i>&nbsp;');
        $installBtn.css("background-color", "#3b7a4c");
        $installBtn.css("color", "white")
    },

    upgradeDependency: function(){
        var $elem = $(this);
        if($elem.attr('aria-selected') == 'false'){
            $elem.attr('aria-selected', 'true');
            $parent = $elem.parent();
            $elem.hide();
            $parent.find('br').hide();
            $parent.find('hr').hide();
            $parent.append('<div class="card" style="padding: 0.5rem 1rem;"></div>')
            var $subClass = $parent.find('.card')

            $subClass.append('<div class="row">' +
                                '<div class="col-sm-10">Upgrade As:&nbsp;</div>' +
                                '<div class="col-sm-1" style="padding-bottom: 0.4rem;">' +
                                    '<i class="fa fa-times" aria-hidden="true" katana-click="assembler.cancelDependencyUpgrade"></i>' +
                                '</div>' +
                             '</div>')
            $subClass.append('<div class="row">' +
                                 '<div class="col-sm-2"></div>' +
                                 '<div class="col-sm-8">' +
                                     '<button class="btn btn-info" katana-click="assembler.upgradeDependencyAsAdmin">Admin</button>' +
                                     '&nbsp;&nbsp;' +
                                     '<button class="btn btn-info" katana-click="assembler.upgradeDependencyAsUser">User</button>' +
                                 '</div>' +
                             '</div>')
        }
        else{
            $elem.attr('aria-selected', 'false');
            $elem.html('Upgrade&nbsp;<i class="fa fa-exclamation-triangle tan" aria-hidden="true">');
            $elem.css("background-color", "white");
            $elem.css("color", "black")

        }
    },

    cancelDependencyUpgrade: function(elem, ariaValue){
        if(elem){
            var $elem = elem;
        }
        else{
            $elem = $(this);
        }
        if(ariaValue == undefined){
            ariaValue = "false";
        }
        var $parentDiv = $elem.closest('.card');
        var $upgradeBtn = $parentDiv.siblings('button[katana-click="assembler.upgradeDependency"]');
        $upgradeBtn.attr('aria-selected', ariaValue);
        $parentDiv.remove();
        $upgradeBtn.siblings('br').show();
        $upgradeBtn.siblings('hr').show();
        $upgradeBtn.show();
    },

    upgradeDependencyAsAdmin: function(){
        var $elem = $(this);
        $.when(assembler.setUpgradeBtn($elem, "Upgrade As Admin")).then(assembler.cancelDependencyUpgrade($elem, "true"));
    },

    upgradeDependencyAsUser: function(){
        $.when(assembler.setUpgradeBtn($elem, "Upgrade As User")).then(assembler.cancelDependencyUpgrade($elem, "true"));
    },

    setUpgradeBtn: function(elem, text){
        var $elem = elem;
        var $parentDiv = $elem.closest('.card');
        var topLevelDiv = $parentDiv.closest('.card-block').closest('.card').parent();
        if(text == "Upgrade As Admin"){
            topLevelDiv.data().dataObject.install = "yes";
            topLevelDiv.data().dataObject.user = "no";
        } else {
            topLevelDiv.data().dataObject.install = "yes";
            topLevelDiv.data().dataObject.user = "yes";
        }
        var $upgradeBtn = $parentDiv.siblings('button[katana-click="assembler.upgradeDependency"]');
        $upgradeBtn.html(text + '&nbsp;<i class="fa fa-check" style="color: white" aria-hidden="true"></i>&nbsp;');
        $upgradeBtn.css("background-color", "#987150");
        $upgradeBtn.css("color", "white")
    },

    updateKwRepoDetails: function(){
        $elem = $(this);
        var $topLevelDiv = $elem.closest('.card');
        var $parentCardBlock = $elem.closest('.card-block');
        var $footerBlockRow = $parentCardBlock.siblings('.card-footer').find('.row');
        var $footerBlockRowIcon = $footerBlockRow.find('.fa');
        $footerBlockRowIcon.attr('class', 'fa')
        $footerBlockRow.find('.col-sm-8').html('');
        var url = $elem.val();
        if(url == ""){
            $footerBlockRowIcon.addClass('fa-exclamation-triangle').addClass('tan')
            $footerBlockRow.find('.col-sm-8').html('No Repository Information Provided.');
            $footerBlockRow.show();
        }
        else if(!url.endsWith(".git")){
            $footerBlockRowIcon.addClass('fa-times').addClass('red');
            $footerBlockRow.find('.col-sm-8').html('Repository Not Available.');
            $footerBlockRow.show();
        } else {
            $footerBlockRowIcon.addClass('fa-spinner').addClass('fa-spin').addClass('tan');
            $footerBlockRow.find('.col-sm-8').html('Checking Availability.');
            $footerBlockRow.show();
            $.ajax({
                headers: {
                    'X-CSRFToken': $currentPage.find('input[name="csrfmiddlewaretoken"]').attr('value')
                },
                type: 'POST',
                url: 'assembler/check_repo_availability/',
                data: {"url": url}
            }).done(function(data) {
                $footerBlockRowIcon.attr('class', 'fa');
                if(data["available"]){
                    $topLevelDiv.data().dataObject.url = url;
                    $topLevelDiv.data().dataObject.available = true;
                    $footerBlockRowIcon.addClass('fa-check').addClass('green');
                    $footerBlockRow.find('.col-sm-8').html('Repository Available.');
                    $parentCardBlock.siblings('.card-header').find('.col-sm-7').html(data["repo_name"])

                    $driverBlock = $($parentCardBlock.find('.row')[1]);
                    $driverBlock.find('.row, .text-center').html('')
                    $topLevelDiv.data().dataObject.drivers = [];
                    for(var i=0; i<data["drivers"].length; i++){
                        var ddObj = new driverDetails({"@name": data["drivers"][i], "@clone": "yes"})
                        $driverBlock.find('.row, .text-center').append(ddObj.domElement)
                        $topLevelDiv.data().dataObject.drivers.push(ddObj)
                    }
                    $driverBlock.show();

                } else {
                    $topLevelDiv.data().dataObject.url = url;
                    $topLevelDiv.data().dataObject.available = false;
                    $footerBlockRowIcon.addClass('fa-times').addClass('red');
                    $footerBlockRow.find('.col-sm-8').html('Repository Not Available.');
                }
            });
        }
    },

    toggleKwRepoClone: function(){
        var $elem = $(this);
        var $topLevelDiv = $elem.closest('.card');
        if($elem.attr('aria-selected') == "true"){
            $elem.attr('aria-selected', 'false');
            $elem.removeClass('fa-toggle-on').removeClass('green');
            $elem.addClass('fa-toggle-off').addClass('grey');
            $topLevelDiv.data().dataObject.clone = "no";
        }
        else{
            $elem.attr('aria-selected', 'true');
            $elem.removeClass('fa-toggle-off').removeClass('grey');
            $elem.addClass('fa-toggle-on').addClass('green');
            $topLevelDiv.data().dataObject.clone = "no";
        }
    },

    openFileExplorer: function(){
        $.ajax({
                headers: {
                    'X-CSRFToken': $currentPage.find('input[name="csrfmiddlewaretoken"]').attr('value')
                },
                type: 'GET',
                url: 'read_config_file/',
            }).done(function(data) {
                console.log(data);
                callBack_on_accept = function(inputValue){
                    console.log(inputValue)
                };
                callBack_on_dismiss = function(){
                    console.log("Dismissed");
                }
                katana.fileExplorerAPI.openFileExplorer(false, data["warhorn_config"],
                                                        $currentPage.find('input[name="csrfmiddlewaretoken"]').attr('value'),
                                                        false, callBack_on_accept, callBack_on_dismiss)
            });
    },

    addKwRepository: function(){
        $currentPage = katana.$activeTab;
        kw_repo_obj = new kwRepository()
        $currentPage.find('#kw-div').append(kw_repo_obj.domElement);
    },

    deleteKwRepo: function(){
        var $elem = $(this);
        var callBack_on_accept = function(){
            $elem.closest('.card').remove();
            katana.openAlert({
                "alert_type": "success",
                "text": "Repository Deleted.",
                "timer": 1250,
                "show_accept_btn": false,
                "show_cancel_btn": false,
            })
        };
        var callBack_on_dismiss = function(){
            katana.openAlert({
                "heading": "Whew!",
                "text": "Repository not deleted",
                "timer": 1250,
                "show_accept_btn": false,
                "show_cancel_btn": false,
            })
        };
        katana.openAlert({
            "alert_type": "danger",
	        "heading": "This will delete the Keyword Repository.",
	        "text": "Are you sure you want to delete it?",
	        "accept_btn_text": "Yes",
	        "cancel_btn_text": "No",
        }, callBack_on_accept, callBack_on_dismiss);
    },

    toggleDriverClone: function(){
        var $elem = $(this);
        var $topLevelDiv = $elem.closest('.card').closest('.row').closest('.card');
        if($elem.attr("aria-selected") == "true"){
            $elem.attr("aria-selected", "false");
            $elem.attr("class", "");
            $elem.addClass("fa").addClass("fa-toggle-off").addClass("grey");
            for(var i=0; i<$topLevelDiv.data().dataObject.drivers.length; i++){
                if($topLevelDiv.data().dataObject.drivers[i]["name"] == $elem.siblings('label').text()){
                    $topLevelDiv.data().dataObject.drivers[i]["clone"] = "no";
                    break;
                }
            }

        } else {
            $elem.attr("aria-selected", "true");
            $elem.attr("class", "");
            $elem.addClass("fa").addClass("fa-toggle-on").addClass("green");
            for(var i=0; i<$topLevelDiv.data().dataObject.drivers.length; i++){
                if($topLevelDiv.data().dataObject.drivers[i]["name"] == $elem.siblings('label').text()){
                    $topLevelDiv.data().dataObject.drivers[i]["clone"] = "yes";
                    break;
                }
            }
        }
    },

    toggleAllDrivers: function(){
        var $elem = $(this);
        var $topLevelDiv = $elem.closest('.card');
        if($elem.attr("aria-selected") == "true"){
            $elem.attr("aria-selected", "false");
            $elem.attr("class", "");
            $elem.addClass("fa").addClass("fa-toggle-off").addClass("grey");
            $topLevelDiv.data().dataObject.all_drivers = "no";
        } else {
            $elem.attr("aria-selected", "true");
            $elem.attr("class", "");
            $elem.addClass("fa").addClass("fa-toggle-on").addClass("green");
            $topLevelDiv.data().dataObject.all_drivers = "yes";
        }
    },

    toggleWsOverwriteButton: function(){
        var $elem = $(this);
        var $topLevelDiv = $elem.closest('.card');
        if($elem.attr("aria-selected") == "true"){
            $elem.attr("aria-selected", "false");
            $elem.attr("class", "");
            $elem.addClass("fa").addClass("fa-toggle-off").addClass("grey");
            $topLevelDiv.data().dataObject.overwrite = "no";
        } else {
            $elem.attr("aria-selected", "true");
            $elem.attr("class", "");
            $elem.addClass("fa").addClass("fa-toggle-on").addClass("green");
            $topLevelDiv.data().dataObject.overwrite = "yes";
        }
    },

    toggleWsRepoClone: function(){
        var $elem = $(this);
        var $topLevelDiv = $elem.closest('.card');
        if($elem.attr("aria-selected") == "true"){
            $elem.attr("aria-selected", "false");
            $elem.attr("class", "");
            $elem.addClass("fa").addClass("fa-toggle-off").addClass("grey");
            $topLevelDiv.data().dataObject.clone = "no";
        } else {
            $elem.attr("aria-selected", "true");
            $elem.attr("class", "");
            $elem.addClass("fa").addClass("fa-toggle-on").addClass("green");
            $topLevelDiv.data().dataObject.clone = "yes";
        }
    },

    checkWsRepository: function(){
        $elem = $(this);
        $topLevelDiv = $elem.closest('.card');
        $parentCardBlock = $elem.closest('.card-block');
        $footerBlockRow = $parentCardBlock.siblings('.card-footer').find('.row');
        var $footerBlockRowIcon = $footerBlockRow.find('.fa');
        $footerBlockRowIcon.attr('class', 'fa')
        $footerBlockRow.find('.col-sm-8').html('');
        var url = $elem.val();
        if(url == ""){
            $footerBlockRowIcon.addClass('fa-exclamation-triangle').addClass('tan')
            $footerBlockRow.find('.col-sm-8').html('No Repository Information Provided.');
            $footerBlockRow.show();
        }
        else if(!url.endsWith(".git")){
            $footerBlockRowIcon.addClass('fa-times').addClass('red');
            $footerBlockRow.find('.col-sm-8').html('Repository Not Available.');
            $footerBlockRow.show();
        } else {
            $footerBlockRowIcon.addClass('fa-spinner').addClass('fa-spin').addClass('tan');
            $footerBlockRow.find('.col-sm-8').html('Checking Availability.');
            $footerBlockRow.show();
            $.ajax({
                headers: {
                    'X-CSRFToken': $currentPage.find('input[name="csrfmiddlewaretoken"]').attr('value')
                },
                type: 'POST',
                url: 'assembler/check_ws_repo_availability/',
                data: {"url": url}
            }).done(function(data) {
                $footerBlockRowIcon.attr('class', 'fa');
                if(data["available"]){
                    $topLevelDiv.data().dataObject.url = url;
                    $topLevelDiv.data().dataObject.available = true;
                    $footerBlockRowIcon.addClass('fa-check').addClass('green');
                    $footerBlockRow.find('.col-sm-8').html('Repository Available.');
                    $parentCardBlock.siblings('.card-header').find('.col-sm-4').html(data["repo_name"]);
                } else {
                    $footerBlockRowIcon.addClass('fa-times').addClass('red');
                    $footerBlockRow.find('.col-sm-8').html('Repository Not Available.');
                    $topLevelDiv.data().dataObject.available = false;
                }
            });
        }
    },

    checkWsLabel: function(){
        var $elem = $(this);
        var $topLevelDiv = $elem.closest('.card');
        $topLevelDiv.data().dataObject.label = $elem.val();
    },

    deleteWsRepo: function(){
        var $elem = $(this);
        var callBack_on_accept = function(){
            $elem.closest('.card').remove();
            katana.openAlert({
                "alert_type": "success",
                "text": "Repository Deleted.",
                "timer": 1250,
                "show_accept_btn": false,
                "show_cancel_btn": false,
            })
        };
        var callBack_on_dismiss = function(){
            katana.openAlert({
                "heading": "Whew!",
                "text": "Repository not deleted",
                "timer": 1250,
                "show_accept_btn": false,
                "show_cancel_btn": false,
            })
        };
        katana.openAlert({
            "alert_type": "danger",
	        "heading": "This will delete the Warriorspace Repository.",
	        "text": "Are you sure you want to delete it?",
	        "accept_btn_text": "Yes",
	        "cancel_btn_text": "No",
        }, callBack_on_accept, callBack_on_dismiss);

    },

    addWsRepository: function(){
        $currentPage = katana.$activeTab;
        ws_repo_obj = new wsRepository();
        $currentPage.find('#ws-div').append(ws_repo_obj.domElement);
    },

    toggleToolsClone: function(){
        var $elem = $(this);
        var $topLevelDiv = $elem.closest('.card');
        if($elem.attr("aria-selected") == "true"){
            $elem.attr("aria-selected", "false");
            $elem.attr("class", "");
            $elem.addClass("fa").addClass("fa-toggle-off").addClass("grey");
            $topLevelDiv.data().dataObject.clone = "no";
        } else {
            $elem.attr("aria-selected", "true");
            $elem.attr("class", "");
            $elem.addClass("fa").addClass("fa-toggle-on").addClass("green");
            $topLevelDiv.data().dataObject.clone = "yes";
        }
    },

    onchangeToolsUrl: function(){
        var $elem = $(this);
        var $parentCardBlock = $elem.closest('.card-block');
        var $topLevelDiv = $elem.closest('.card')
        var $footerBlockRow = $parentCardBlock.siblings('.card-footer').find('.row');
        var $footerBlockRowIcon = $footerBlockRow.find('.fa');
        $footerBlockRowIcon.attr('class', 'fa')
        $footerBlockRow.find('.col-sm-8').html('');
        var url = $elem.val();
        if(url == ""){
            $footerBlockRowIcon.addClass('fa-exclamation-triangle').addClass('tan')
            $footerBlockRow.find('.col-sm-8').html('No Repository Information Provided.');
            $footerBlockRow.show();
        }
        else if(!url.endsWith(".git")){
            $footerBlockRowIcon.addClass('fa-times').addClass('red');
            $footerBlockRow.find('.col-sm-8').html('Repository Not Available.');
            $footerBlockRow.show();
        } else {
            $footerBlockRowIcon.addClass('fa-spinner').addClass('fa-spin').addClass('tan');
            $footerBlockRow.find('.col-sm-8').html('Checking Availability.');
            $footerBlockRow.show();
            $.ajax({
                headers: {
                    'X-CSRFToken': $currentPage.find('input[name="csrfmiddlewaretoken"]').attr('value')
                },
                type: 'POST',
                url: 'assembler/check_tools_repo_availability/',
                data: {"url": url}
            }).done(function(data) {
                $footerBlockRowIcon.attr('class', 'fa');
                if(data["available"]){
                    $topLevelDiv.data().dataObject.available = false;
                    $topLevelDiv.data().dataObject.url = url;
                    $topLevelDiv.data().dataObject.available = true;
                    $footerBlockRowIcon.addClass('fa-check').addClass('green');
                    $footerBlockRow.find('.col-sm-8').html('Repository Available.');
                    $parentCardBlock.siblings('.card-header').find('.col-sm-8').html(data["repo_name"]);
                } else {
                    $topLevelDiv.data().dataObject.available = false;
                    $footerBlockRowIcon.addClass('fa-times').addClass('red');
                    $footerBlockRow.find('.col-sm-8').html('Repository Not Available.');
                }
            });
        }
    },

    onchangeToolsLabel: function(){
        var $elem = $(this);
        var $topLevelDiv = $elem.closest('.card');
        $topLevelDiv.data().dataObject.label = $elem.val();
    },

    saveFile: function(){
        $.ajax({
                headers: {
                    'X-CSRFToken': $currentPage.find('input[name="csrfmiddlewaretoken"]').attr('value')
                },
                type: 'GET',
                url: 'read_config_file/'
            }).done(function(config_file_data) {
                var callBack_on_accept = function(inputValue){
                var $currentPage = katana.$activeTab;
                var finalJson = {
                                    "data": {
                                        "warhorn": {
                                            "dependency": []
                                        },
                                        "tools": "",
                                        "drivers": {
                                            "repository": []
                                        },
                                        "warriorspace": {
                                            "repository": []
                                        }
                                    }
                                }
                var dependencyDivChildren = $currentPage.find('#dependency-div').children('div');
                for(var i=0; i<dependencyDivChildren.length; i++){
                    finalJson.data.warhorn.dependency.push(JSON.parse(JSON.stringify($(dependencyDivChildren[i]).data().dataObject.jsonObj)));
                }

                var toolsDivChild = $currentPage.find('#tools-div').children('div');
                finalJson.data.tools = JSON.parse(JSON.stringify($(toolsDivChild[0]).data().dataObject.jsonObj));

                var kwDivChildren = $currentPage.find('#kw-div').children('div');
                for(i=0; i<kwDivChildren.length; i++){
                    finalJson.data.drivers.repository.push(JSON.parse(JSON.stringify($(kwDivChildren[i]).data().dataObject.jsonObj)));
                }

                var wsDivChildren = $currentPage.find('#ws-div').children('div');
                for(i=0; i<wsDivChildren.length; i++){
                    finalJson.data.warriorspace.repository.push(JSON.parse(JSON.stringify($(wsDivChildren[i]).data().dataObject.jsonObj)));
                }

                $.ajax({
                    headers: {
                        'X-CSRFToken': $currentPage.find('input[name="csrfmiddlewaretoken"]').attr('value')
                    },
                    type: 'POST',
                    url: 'assembler/save_warhorn_config_file/',
                    data: {"json_data": JSON.stringify(finalJson), "filename": inputValue, "directory": config_file_data["warhorn_config"]}
                }).done(function(data) {
                    if(data.saved){
                        $currentPage.find('#dependency-div').html('');
                        $currentPage.find('#tools-div').html('');
                        $currentPage.find('#kw-div').html('');
                        $currentPage.find('#ws-div').html('');
                        assembler.init();
                        katana.openAlert({"alert_type": "success",
                            "heading": "Saved",
                            "text": "Saved as: " + inputValue,
                            "timer": 1250, "show_cancel_btn": false, "show_accept_btn": false})
                    } else {
                        katana.openAlert({"alert_type": "danger",
                            "heading": "Not Saved!",
                            "text": "Some error occurred: " + data.message,
                            "show_cancel_btn": false})
                    }

                });
            }
            katana.openAlert({"alert_type": "light",
                "heading": "Name for the file",
                "text": "",
                "prompt": "true"}, callBack_on_accept)
            });
    },
}