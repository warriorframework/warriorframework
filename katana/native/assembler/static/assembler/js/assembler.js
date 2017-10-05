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
                var dep_list = data.xml_contents.data.warhorn.dependency;
                var kw_repo_list = data.xml_contents.data.drivers;
                var ws_repo_list = data.xml_contents.data.warriorspace;
                var tools = data.xml_contents.data.tools;

                var dep_objs = [];

                for(var i=0; i<dep_list.length; i++){
                    dep_objs.push(new dependency(dep_list[i]))
                    //$currentPage.find('#dependency-div').append(dep_objs[i].domElement);
                }
            });
    }
}