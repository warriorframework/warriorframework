'use strict';

var cliData = {

    fileDisplayAPI: {

        init: function() {
            var $currentPage = katana.$activeTab;
            var $displayFilesDiv = $currentPage.find('#displayFiles');
            $.ajax({
                type: 'GET',
                url: 'read_config_file/',
            }).done(function(config_json_data) {
                if(config_json_data["testdata"] === ""){
                    katana.openAlert({"alert_type": "danger", "heading": "Configuration Not Set",
                                      "text": "Please set up the configuration to use this App",
                                      "show_cancel_btn": false})

                    $displayFilesDiv.html('Please set up the configuration to use this App');
                } else {
                    $displayFilesDiv.html('');
                     $.ajax({
                            headers: {
                                'X-CSRFToken': $currentPage.find('input[name="csrfmiddlewaretoken"]').attr('value')
                            },
                            type: 'POST',
                            url: 'get_file_explorer_data/',
                            data: {"data": {"start_dir": config_json_data["testdata"]}}
                        }).done(function(data) {
                            $displayFilesDiv.jstree({
                                "core": { "data": [data]},
                                "plugins": ["search", "sort"],
                                "sort": function (a, b) {
                                            var nodeA = this.get_node(a);
                                            var nodeB = this.get_node(b);
                                            var lengthA = nodeA.children.length;
                                            var lengthB = nodeB.children.length;
                                            if ((lengthA == 0 && lengthB == 0) || (lengthA > 0 && lengthB > 0))
                                                return this.get_text(a).toLowerCase() > this.get_text(b).toLowerCase() ? 1 : -1;
                                            else
                                                return lengthA > lengthB ? -1 : 1;
                                    }
                            });
                            $displayFilesDiv.jstree().hide_dots();
                        });
                }
            });
        },

        newFile: function() {

        }
    }

}