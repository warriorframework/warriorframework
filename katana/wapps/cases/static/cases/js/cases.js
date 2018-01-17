var cases = {

    invert: function(){
        var toolbarButtons = katana.$activeTab.find('.tool-bar').find('button');
        for(var i=0; i<toolbarButtons.length; i++){
            if($(toolbarButtons[i]).is(":hidden")){
                $(toolbarButtons[i]).show();
            } else {
                $(toolbarButtons[i]).hide();
            }
        }
        var divs = katana.$activeTab.find('#body-div').children();
        for(i=0; i<divs.length; i++){
            if($(divs[i]).is(":hidden")){
                $(divs[i]).show();
            } else {
                $(divs[i]).hide();
            }
        }
    },

    landing: {
        init: function(){
            $.ajax({
                type: 'GET',
                url: 'cases/get_list_of_cases/'
            }).done(function(data){
                katana.jsTreeAPI.createJstree(katana.$activeTab.find('#tree-div'), data.data);
                katana.$activeTab.find('#tree-div').on("select_node.jstree", function (e, data){
                    if (data["node"]["icon"] === "jstree-file") {
                        $.ajax({
                            headers: {
                                'X-CSRFToken': katana.$activeTab.find('.csrf-container').html()
                            },
                            type: 'GET',
                            url: 'cases/get_file/',
                            data: {"path": data["node"]["li_attr"]["data-path"]}
                        }).done(function(data){
                            cases.invert();
                            katana.$activeTab.find('#main-div').html(data);
                        });
                    }
                });
            });
        },

        openNewFile: function(){
            $.ajax({
                headers: {
                    'X-CSRFToken': katana.$activeTab.find('.csrf-container').html()
                },
                type: 'GET',
                url: 'cases/get_file/',
                data: {"path": false}
            }).done(function(data){
                cases.invert();
                katana.$activeTab.find('#main-div').html(data);
            });
        },
    },

    caseViewer:  {
        close: function () {
            cases.invert();
        }
    },
};