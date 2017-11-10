'use strict';

var cliData = {

    fileDisplayAPI: {
        init: function() {
            var $currentPage = katana.$activeTab;
            var $displayFilesDiv = $currentPage.find('#display-files');
            var $displayErrorMsgDiv = $currentPage.find('#display-error-message');
            var $mainDiv = $currentPage.find('#main-div');
            $mainDiv.hide();
            $.ajax({
                type: 'GET',
                url: 'read_config_file/',
            }).done(function(config_json_data) {
                if(config_json_data["testdata"] === ""){
                    $displayErrorMsgDiv.show();
                    $displayFilesDiv.hide();
                } else {
                    $displayErrorMsgDiv.hide();
                    $displayFilesDiv.show();
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
                            $displayFilesDiv.on("select_node.jstree", function (e, data) {
                                if (data["node"]["icon"] == "jstree-file") {
                                    $.ajax({
                                        url: "cli_data/get_default_file/",
                                        type: "GET",
                                        data: {"path": data["node"]["li_attr"]["data-path"]},
                                        success: function(data){
                                            console.log(data);
                                        }
                                    });
                                }
                            });
                        });
                }
            });
        },

        newFile: function() {
            $.ajax({
               type: 'GET',
               url: 'cli_data/get_default_file/',
               data: {"path": false}
            }).done(function(data) {
                var $currentPage = katana.$activeTab;
                var $displayFilesDiv = $currentPage.find('#display-files');
                $displayFilesDiv.hide();
                var $displayErrorMsgDiv = $currentPage.find('#display-error-message');
                $displayErrorMsgDiv.hide();
                var $mainDiv = $currentPage.find('#main-div');
                $mainDiv.show();
                var $toolBarDiv = $currentPage.find('.tool-bar');
                $toolBarDiv.find('.title').html(data["name"]);

                var globalCmd = new globalCommand(data.contents.data.global.command_params);
                $currentPage.find('.cli-data-left-column').html(globalCmd.htmlLeftContent);

                /*console.log(data.contents.data.global.verifications[0]);
                var globalVer = new globalVerifications(data.contents.data.global.verifications[0])
                $currentPage.find('.cli-data-left-column').html(globalVer.htmlLeftContent);

                console.log(data.contents.data.global.verifications[1]);
                var globalComb = new globalCombinations(data.contents.data.global.verifications[1])
                $currentPage.find('.cli-data-left-column').html(globalComb.htmlLeftContent);

                console.log(data.contents.data.global.keys);
                var glKey = new globalKeys(data.contents.data.global.keys)
                $currentPage.find('.cli-data-left-column').html(glKey.htmlLeftContent);

                console.log(data.contents.data.global.variable_pattern);
                var vp = new globalVariablePattern(data.contents.data.global.variable_pattern)
                $currentPage.find('.cli-data-left-column').html(vp.htmlLeftContent);*/

                /*var globalCmd = new globalCommand(data.contents.data.global.command_params);
                $currentPage.find('.cli-data-right-column').find('.cli-data-full-width').append(globalCmd.htmlRightContent);
                console.log(globalCmd.htmlRightContent);

                var globalVer = new globalVerifications(data.contents.data.global.verifications[0])
                $currentPage.find('.cli-data-right-column').find('.cli-data-full-width').append(globalVer.htmlRightContent);

                var globalComb = new globalCombinations(data.contents.data.global.verifications[1])
                $currentPage.find('.cli-data-right-column').find('.cli-data-full-width').append(globalComb.htmlRightContent)

                var glKey = new globalKeys(data.contents.data.global.keys)
                $currentPage.find('.cli-data-right-column').find('.cli-data-full-width').append(glKey.htmlRightContent);

                var vp = new globalVariablePattern(data.contents.data.global.variable_pattern)
                $currentPage.find('.cli-data-right-column').find('.cli-data-full-width').append(vp.htmlRightContent)*/

            });
        },
    }

}