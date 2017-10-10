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
        console.log($footerBlockRow);
        $footerBlockRow.find('.fa').removeClass('fa-times').removeClass('red');
        $footerBlockRow.find('.fa').removeClass('fa-check').removeClass('green');
        $footerBlockRow.find('.fa').removeClass('fa-exclamation-triangle').removeClass('tan')
        $footerBlockRow.find('.col-sm-8').html('');
        var url = $elem.val();
        if(url == ""){
            $footerBlockRow.find('.fa').addClass('fa-exclamation-triangle').addClass('tan')
            $footerBlockRow.find('.col-sm-8').html('No Repository Information Provided.');
            $footerBlockRow.show();
        }
        else if(!url.endsWith(".git")){
            $footerBlockRow.find('.fa').addClass('fa-times').addClass('red');
            $footerBlockRow.find('.col-sm-8').html('Repository Not Available.');
            $footerBlockRow.show();
        } else {
            $footerBlockRow.find('.fa').addClass('fa-check').addClass('green');
            $footerBlockRow.find('.col-sm-8').html('Repository Available.');
            $footerBlockRow.show();
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
    }
}