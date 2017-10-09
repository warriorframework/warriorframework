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
        if($elem.attr("aria-selected") == "true"){
            $elem.attr("aria-selected", "false");
            $elem.css("background-color", "white");
            $elem.css("color", "black");
            $elem.html('Install');
        }
        else{
            $parent = $elem.parent();
            $elem.remove();
            $parent.find('br').remove();
            $parent.append('<div class="card" style="padding: 0.3rem 1rem;"></div>')
            var $subClass = $parent.find('.card')

            $subClass.append('<div class="row"><div class="col-sm-10">Install As:&nbsp;</div><div class="col-sm-1" style="padding-bottom: 0.4rem;"><i class="fa fa-times" aria-hidden="true"></i></div></div>')
            $subClass.append('<div class="row"><div class="col"><button class="btn btn-info btn-block">Admin</button></div><div class="col"><button class="btn btn-info btn-block">User</button></div></div>')
            /*$elem.attr("aria-selected", "true");
            $elem.css("background-color", "#3b7a4c");
            $elem.css("color", "white");
            $elem.html('Install&nbsp;<i class="fa fa-check" style="color: white;" aria-hidden="true"></i>&nbsp;');*/
        }
    },

    upgradeDependency: function(){
        var $elem = $(this);
        if($elem.attr("aria-selected") == "true"){
            $elem.attr("aria-selected", "false");
            $elem.css("background-color", "white");
            $elem.css("color", "black");
            $elem.html('Upgrade&nbsp;<i class="fa fa-exclamation-triangle tan" aria-hidden="true">');
        }
        else{
            $elem.attr("aria-selected", "true");
            $elem.css("background-color", "#987150");
            $elem.css("color", "white");
            $elem.html('Upgrade&nbsp;<i class="fa fa-check" style="color: white;" aria-hidden="true"></i>&nbsp;');
        }
    },

    installDepAsUser: function(){

    }
}