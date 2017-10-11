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
                var kw_repo_list = data.xml_contents.data.drivers.repository;
                var ws_repo_list = data.xml_contents.data.warriorspace.repository;
                var tools = data.xml_contents.data.tools;

                var dep_objs = [];
                for(var i=0; i<data.xml_contents.data.warhorn.dependency.length; i++){
                    dep_objs.push(new dependency(data.xml_contents.data.warhorn.dependency[i]))
                    $currentPage.find('#dependency-div').append(dep_objs[i].domElement);
                }

                var kw_objs = []
                for(var i=0; i<kw_repo_list.length; i++){
                    console.log(kw_repo_list[i]);
                    kw_objs.push(new kwRepository(kw_repo_list[i]))
                    $currentPage.find('#kw-div').append(kw_objs[i].domElement);
                    console.log(kw_objs[i]);
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
        var $upgradeBtn = $parentDiv.siblings('button[katana-click="assembler.upgradeDependency"]');
        $upgradeBtn.html(text + '&nbsp;<i class="fa fa-check" style="color: white" aria-hidden="true"></i>&nbsp;');
        $upgradeBtn.css("background-color", "#987150");
        $upgradeBtn.css("color", "white")
    },

    updateKwRepoDetails: function(){
        $elem = $(this);
        $parentCardBlock = $elem.closest('.card-block');
        console.log($parentCardBlock);
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
                url: 'assembler/check_repo_availability/',
                data: {"url": url}
            }).done(function(data) {
                $footerBlockRowIcon.attr('class', 'fa');
                if(data["available"]){
                    $footerBlockRowIcon.addClass('fa-check').addClass('green');
                    $footerBlockRow.find('.col-sm-8').html('Repository Available.');
                    $parentCardBlock.siblings('.card-header').find('.col-sm-7').html(data["repo_name"])

                    $driverBlock = $($parentCardBlock.find('.row')[1]);
                    for(var i=0; i<data["drivers"].length; i++){
                        var ddObj = new driverDetails({"@name": data["drivers"][i], "@clone": "yes"})
                        console.log(ddObj.domElement);
                        console.log($driverBlock.find('.row, .text-center'));
                        $driverBlock.find('.row, .text-center').append(ddObj.domElement)
                    }
                    $driverBlock.show();

                } else {
                    $footerBlockRowIcon.addClass('fa-times').addClass('red');
                    $footerBlockRow.find('.col-sm-8').html('Repository Not Available.');
                }
            });
        }
    },

    toggleKwRepoClone: function(){
        var $elem = $(this);
        if($elem.attr('aria-selected') == "true"){
            $elem.attr('aria-selected', 'false');
            $elem.removeClass('fa-toggle-on').removeClass('green');
            $elem.addClass('fa-toggle-off').addClass('grey');
        }
        else{
            $elem.attr('aria-selected', 'true');
            $elem.removeClass('fa-toggle-off').removeClass('grey');
            $elem.addClass('fa-toggle-on').addClass('green');
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
        if($elem.attr("aria-selected") == "true"){
            $elem.attr("aria-selected", "false");
            $elem.attr("class", "");
            $elem.addClass("fa").addClass("fa-toggle-off").addClass("grey");
        } else {
            $elem.attr("aria-selected", "true");
            $elem.attr("class", "");
            $elem.addClass("fa").addClass("fa-toggle-on").addClass("green");
        }
    },

    toggleAllDrivers: function(){
        var $elem = $(this);
        if($elem.attr("aria-selected") == "true"){
            $elem.attr("aria-selected", "false");
            $elem.attr("class", "");
            $elem.addClass("fa").addClass("fa-toggle-off").addClass("grey");
        } else {
            $elem.attr("aria-selected", "true");
            $elem.attr("class", "");
            $elem.addClass("fa").addClass("fa-toggle-on").addClass("green");
        }
    }
}