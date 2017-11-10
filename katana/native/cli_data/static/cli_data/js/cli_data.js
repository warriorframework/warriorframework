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

                cliData.fileDisplayAPI.displayRightContents(data.contents.data);

            });
        },

        displayRightContents: function(data){
            var $currentPage = katana.$activeTab;
            var $rightColumn = $currentPage.find('.cli-data-right-column').find('.cli-data-full-width');

            var globalCmd = new globalCommand(data.global.command_params);
            $rightColumn.append(globalCmd.htmlRightContent);

            for(var i=0; i<data.global.verifications.length; i++){
                for(var key in data.global.verifications[i]){
                    if(data.global.verifications[i][key]["type"] == "verification"){
                        var globalVer = new globalVerifications(data.global.verifications[i])
                        $rightColumn.append(globalVer.htmlRightContent);
                    }
                    break;
                }
            }

            for(var i=0; i<data.global.verifications.length; i++){
                for(var key in data.global.verifications[i]){
                    if(data.global.verifications[i][key]["type"] == "combination"){
                        var globalComb = new globalCombinations(data.global.verifications[i])
                        $rightColumn.append(globalComb.htmlRightContent);
                    }
                    break;
                }
            }

            for(var i=0; i<data.global.keys.length; i++){
                console.log(data.global.keys[i]);
                var globalRespKeys = new globalKeys(data.global.keys[i]);
                $rightColumn.append(globalRespKeys.htmlRightContent);
            }

            var globalVarPat = new globalVariablePattern(data.global.variable_pattern);
            $rightColumn.append(globalVarPat.htmlRightContent);

            for(i=0; i<data.testdata.length; i++){
                for(var j=0; j<data.testdata[i].command.length; j++){
                    var tdCmd = new testdataCommand(data.testdata[i].command[i]);
                    $rightColumn.append(tdCmd.htmlRightContent)
                }

                for(key in data.testdata[i]){
                    if(key !== "command" && key !== "variable_pattern"){
                        if(data.testdata[i][key]["type"] == "verification"){
                            var tdVer = new testdataVerifications({ key: data.testdata[i][key] })
                            $rightColumn.append(tdVer.htmlRightContent)
                        }
                    }
                }

                for(key in data.testdata[i]){
                    if(key !== "command" && key !== "variable_pattern"){
                        if(data.testdata[i][key]["type"] == "key"){
                            var tdKey = new testdataKeys({ key: data.testdata[i][key] })
                            $rightColumn.append(tdKey.htmlRightContent)
                        }
                    }
                }

                var tdVarPat = new testdataVariablePattern(data.testdata[i].variable_pattern)
                $rightColumn.append(tdVarPat.htmlRightContent)
            }
        },
    }

}