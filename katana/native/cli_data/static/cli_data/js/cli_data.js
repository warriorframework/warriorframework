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
                //console.log(data);
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
                var $content = globalCmd.htmlLeftContent;
                $currentPage.find('.cli-data-left-column').html($content);

                setTimeout(function(){cliData.fileDisplayAPI.displayRightContents(data.contents.data)}, 1);

            });
        },

        displayRightContents: function(data){
            var $currentPage = katana.$activeTab;
            var $rightColumn = $currentPage.find('.cli-data-right-column').find('.cli-data-full-width');

            var globalCmd = new globalCommand(data.global.command_params);
            var $content = globalCmd.htmlRightContent;
            $rightColumn.append($content);

            var globalVerHtmlContent = false;
            for(var i=0; i<data.global.verifications.length; i++){
                for(var key in data.global.verifications[i]){
                    if(data.global.verifications[i][key]["type"] == "verification"){
                        var globalVer = new globalVerifications(data.global.verifications[i])
                        if(!globalVerHtmlContent){
                            globalVerHtmlContent = globalVer.htmlRightContent;
                        } else {
                            globalVerHtmlContent = globalVer.addAnother(globalVerHtmlContent);
                        }
                    }
                    break;
                }
            }
            $rightColumn.append(globalVerHtmlContent);

            var globalCombHtmlContent = false;
            for(var i=0; i<data.global.verifications.length; i++){
                for(var key in data.global.verifications[i]){
                    if(data.global.verifications[i][key]["type"] == "combination"){
                        var globalComb = new globalCombinations(data.global.verifications[i])
                        if(!globalCombHtmlContent){
                            globalCombHtmlContent = globalComb.htmlRightContent;
                        } else {
                            globalCombHtmlContent = globalComb.addAnother(globalCombHtmlContent);
                        }
                    }
                    break;
                }
            }
            $rightColumn.append(globalCombHtmlContent);

            var globalKeysHtmlContent = false;
            for(var key in data.global.keys){
                var jsonVar = {};
                jsonVar[key] = data.global.keys[key]
                var globalRespKeys = new globalKeys(jsonVar);
                if(!globalKeysHtmlContent){
                    globalKeysHtmlContent = globalRespKeys.htmlRightContent;
                } else {
                    globalKeysHtmlContent = globalRespKeys.addAnother(globalKeysHtmlContent);
                }
            }
            $rightColumn.append(globalKeysHtmlContent);

            var globalVarPat = new globalVariablePattern(data.global.variable_pattern);
            $rightColumn.append(globalVarPat.htmlRightContent);


            for(i=0; i<data.testdata.length; i++){
                var tdCmdHtmlContent = false;
                for(var j=0; j<data.testdata[i].command.length; j++){
                    var tdCmd = new testdataCommand(data.testdata[i].command[j]);
                    if(!tdCmdHtmlContent){
                        tdCmdHtmlContent = tdCmd.htmlRightContent;
                    } else {
                        tdCmdHtmlContent = tdCmd.addAnother(tdCmdHtmlContent);
                    }
                }
                $rightColumn.append(tdCmdHtmlContent);


                var tdVerHtmlContent = false;
                for(key in data.testdata[i]){
                    if(key !== "command" && key !== "variable_pattern"){
                        if(data.testdata[i][key]["type"] == "verification"){
                            var jsonVar = {};
                            jsonVar[key] = data.testdata[i][key]
                            var tdVer = new testdataVerifications(jsonVar)
                            if(!tdVerHtmlContent){
                                tdVerHtmlContent = tdVer.htmlRightContent;
                            } else {
                                tdVerHtmlContent = tdVer.addAnother(tdVerHtmlContent);
                            }
                        }
                    }
                }
                $rightColumn.append(tdVerHtmlContent)

                var tdKeysHtmlContent = false;
                for(key in data.testdata[i]){
                    if(key !== "command" && key !== "variable_pattern"){
                        if(data.testdata[i][key]["type"] == "key"){
                            var jsonVar = {};
                            jsonVar[key] = data.testdata[i][key]
                            var tdKey = new testdataKeys(jsonVar)
                            if(!tdKeysHtmlContent){
                                tdKeysHtmlContent = tdKey.htmlRightContent;
                            } else {
                                tdKeysHtmlContent = tdKey.addAnother(tdKeysHtmlContent)
                            }
                        }
                    }
                }
                $rightColumn.append(tdKeysHtmlContent)

                var tdVarPat = new testdataVariablePattern(data.testdata[i].variable_pattern)
                $rightColumn.append(tdVarPat.htmlRightContent)
            }
        },
    },

    leftColumn: {
        nextBlock: function() {
            var $elem = $(this);
        },

        previousBlock: function(){
            var $elem = $(this);
        },

        deleteBlock: function(){
            var $elem = $(this);
        },

        duplicateBlock: function(){
            var $elem = $(this);
        },

        addAnotherBlock: function(){
            var $elem = $(this);
        },
    },

    rightColumn: {

        pinTable: function(){
            var $elem = $(this);
            var pinned = $elem.attr('pinned');

            var $rightColumn = $elem.closest('.cli-data-right-column');
            var $fullWidth = $elem.closest('.cli-data-full-width');
            var $rightTopBar = $elem.closest('.cli-data-right-column-topbar');

            if(pinned == "false"){
                $fullWidth.hide();
                $rightColumn.addClass('cli-data-no-padding');
                var $content = $rightTopBar.data().dataObject.htmlRightContent;
                $($content[0]).find('i').addClass('fa-rotate-270 blue');
                $($content[0]).find('i').attr('pinned', 'true');
                $rightColumn.append($content[0]);
                $rightColumn.append($content[1]);
            } else {
                $rightColumn.removeClass('cli-data-no-padding');
                var $children = $rightColumn.children();
                console.log($children);
                for(var i=0; i<$children.length; i++){
                    $($children[i]).hide();
                }
                $fullWidth.show();
            }

        },

    },

}