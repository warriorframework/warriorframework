'use strict';

var cliData = {

    Editor: {

        closeFile: function(){
            var $currentPage = katana.$activeTab;
            var callbackOnAccept = function(){
                $currentPage.find('[katana-click="cliData.fileDisplayAPI.newFile"]').show();
                $currentPage.find('[katana-click="cliData.Editor.closeFile"]').hide();
                $currentPage.find('[katana-click="cliData.Editor.saveFile"]').hide();
                $currentPage.find('#main-div').find('.cli-data-left-column').html('');
                $currentPage.find('#main-div').find('.cli-data-full-width').html('');
                $currentPage.find('#main-div').hide();
                $currentPage.find('#display-files').show();
            }
            katana.openAlert({"alert_type": "warning",
                               "heading": "Do You Want To Continue?",
                               "text": "All changes made would be discarded.",
                               "accept_btn_text": "Yes", "cancel_btn_text": "No"},
                             callbackOnAccept)

        },

        saveFile: function() {
            var $currentPage = katana.$activeTab;
            $.ajax({
                headers: {
                    'X-CSRFToken': $currentPage.find('input[name="csrfmiddlewaretoken"]').attr('value')
                },
                type: 'GET',
                url: 'read_config_file/',
            }).done(function(config_file_data){
                var callBack_on_accept = function(inputValue){
                    var finalJson = cliData.Editor.getJson();
                    $.ajax({
                        headers: {
                            'X-CSRFToken': $currentPage.find('input[name="csrfmiddlewaretoken"]').attr('value')
                        },
                        type: 'POST',
                        url: 'cli_data/save_testdata_file/',
                        data: {"json_data": JSON.stringify(finalJson), "filename": inputValue, "directory": config_file_data.testdata}
                    }).done(function(data) {
                        if(data.saved){
                            cliData.fileDisplayAPI.init();
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
                };
                katana.openAlert({
                    "alert_type": "light",
                    "heading": "Name for the file",
                    "text": "",
                    "prompt": "true",
                    "prompt_default": $currentPage.find('.tool-bar').find('.title').text()
                    },
                    function(inputValue){
                         $.ajax({
                            headers: {
                                'X-CSRFToken': $currentPage.find('input[name="csrfmiddlewaretoken"]').attr('value')
                            },
                            type: 'POST',
                            url: 'check_if_file_exists/',
                            data: {"filename": inputValue, "directory": config_file_data.testdata, "extension": ".xml"}
                        }).done(function(data){
                             if(data.exists){
                                katana.openAlert({
                                    "alert_type": "warning",
                                    "heading": "File Exists",
                                    "text": "A file with the name " + inputValue + " already exists; do you want to overwrite it?",
                                    "accept_btn_text": "Yes",
                                    "cancel_btn_text": "No"
                                    }, function() {callBack_on_accept(inputValue)})
                             } else {
                                callBack_on_accept(inputValue);
                             }
                        });
                    })
            });
        },

        getJson: function(){
            var $currentPage = katana.$activeTab;
            var finalJson = {
                "data": {
                    "global": {},
                    "testdata": []
                    }
                }

            var $rightFullWidth = $currentPage.find('.cli-data-right-column').find('.cli-data-full-width');
            var $dataCarriers = $rightFullWidth.children('div .cli-data-right-column-topbar');

            var globalEnd = false;

           finalJson.data.global.command_params = $($dataCarriers[0]).data().dataObject[0].jsonObj;
           finalJson.data.global.verifications = {};

           for(var i=0; i<$($dataCarriers[1]).data().dataObject.length; i++){
               var key_name = $($dataCarriers[1]).data().dataObject[i].name;
               var obj_data = $($dataCarriers[1]).data().dataObject[i].jsonObj
               finalJson.data.global.verifications[key_name] = obj_data[key_name];
           }

           for(i=0; i<$($dataCarriers[2]).data().dataObject.length; i++){
               var key_name = $($dataCarriers[2]).data().dataObject[i].name;
               var obj_data = $($dataCarriers[2]).data().dataObject[i].jsonObj
               finalJson.data.global.verifications[key_name] = obj_data[key_name];
           }

           finalJson.data.global.keys = {};

           for(i=0; i<$($dataCarriers[3]).data().dataObject.length; i++){
               var key_name = $($dataCarriers[3]).data().dataObject[i].name;
               var obj_data = $($dataCarriers[3]).data().dataObject[i].jsonObj
               finalJson.data.global.keys[key_name] = obj_data[key_name];
           }

           finalJson.data.global.variable_pattern = $($dataCarriers[4]).data().dataObject[0].jsonObj;


            for(i=5; i<$dataCarriers.length; i+=5){
                var temp_data = {}
                for(var j=0; j<5; j++){
                    if(j ==0){
                        for(var k=0; k<$($dataCarriers[i+j]).data().dataObject.length; k++){
                            var tempJsonVar = $($dataCarriers[i+j]).data().dataObject[k].jsonObj;
                            for(var key in tempJsonVar){
                                var jsonVar = {};
                                temp_data[key] = tempJsonVar[key];
                            }
                        }
                    } else if(j == 1){
                        temp_data.command = [];
                        for(var k=0; k<$($dataCarriers[i+j]).data().dataObject.length; k++){
                            temp_data.command.push($($dataCarriers[i+j]).data().dataObject[k].jsonObj);
                        }
                    } else if(j == 2){
                        for(var k=0; k<$($dataCarriers[i+j]).data().dataObject.length; k++){
                            var tempJsonVar = $($dataCarriers[i+j]).data().dataObject[k].jsonObj;
                            for(var key in tempJsonVar){
                                var jsonVar = {};
                                temp_data[key] = tempJsonVar[key];
                                break;
                            }

                        }
                    } else if(j == 3){
                        for(var k=0; k<$($dataCarriers[i+j]).data().dataObject.length; k++){
                            var tempJsonVar = $($dataCarriers[i+j]).data().dataObject[k].jsonObj;
                            for(var key in tempJsonVar){
                                var jsonVar = {};
                                temp_data[key] = tempJsonVar[key];
                                break;
                            }

                        }
                    } else if(j == 4){
                        for(var k=0; k<$($dataCarriers[i+j]).data().dataObject.length; k++){
                            temp_data.variable_pattern = $($dataCarriers[i+j]).data().dataObject[k].jsonObj;
                        }
                    }
                }
                finalJson.data.testdata.push(jQuery.extend({}, temp_data));
            }

            console.log(finalJson);
            return finalJson
        },
    },

    fileDisplayAPI: {
        init: function() {
            var $currentPage = katana.$activeTab;
            var $newBtn = $currentPage.find('[katana-click="cliData.fileDisplayAPI.newFile"]');
            var $closeBtn = $currentPage.find('[katana-click="cliData.Editor.closeFile"]');
            var $saveBtn = $currentPage.find('[katana-click="cliData.Editor.saveFile"]');
            var $displayFilesDiv = $currentPage.find('#display-files');
            var $displayErrorMsgDiv = $currentPage.find('#display-error-message');
            var $mainDiv = $currentPage.find('#main-div');
            $newBtn.hide();
            $closeBtn.hide();
            $saveBtn.hide();
            $mainDiv.hide();
            $.ajax({
                type: 'GET',
                url: 'read_config_file/',
            }).done(function(config_json_data) {
                if(config_json_data["testdata"] === ""){
                    $displayErrorMsgDiv.show();
                    $displayFilesDiv.hide();
                } else {
                    $newBtn.show();
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
                                            var $currentPage = katana.$activeTab;
                                            var $newBtn = $currentPage.find('[katana-click="cliData.fileDisplayAPI.newFile"]');
                                            var $closeBtn = $currentPage.find('[katana-click="cliData.Editor.closeFile"]');
                                            var $saveBtn = $currentPage.find('[katana-click="cliData.Editor.saveFile"]');
                                            var $displayFilesDiv = $currentPage.find('#display-files');
                                            $displayFilesDiv.hide();
                                            var $displayErrorMsgDiv = $currentPage.find('#display-error-message');
                                            $displayErrorMsgDiv.hide();
                                            var $mainDiv = $currentPage.find('#main-div');
                                            $mainDiv.show();
                                            var $toolBarDiv = $currentPage.find('.tool-bar');
                                            $toolBarDiv.find('.title').html(data["name"]);

                                            $newBtn.hide();
                                            $closeBtn.show();
                                            $saveBtn.show();

                                            $currentPage.find('.page-content-inner').append('<div class="overlay"><div class="cli-data-loading"></div></div>');

                                            var globalCmd = new globalCommand(data.contents.data.global.command_params);
                                            var $content = globalCmd.htmlLeftContent;
                                            $($content[0]).attr("objectIndex", "0");
                                            $currentPage.find('.cli-data-left-column').html($content);

                                            setTimeout(function(){cliData.fileDisplayAPI.displayRightContents(data.contents.data)}, 1);
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
                var $newBtn = $currentPage.find('[katana-click="cliData.fileDisplayAPI.newFile"]');
                var $closeBtn = $currentPage.find('[katana-click="cliData.Editor.closeFile"]');
                var $saveBtn = $currentPage.find('[katana-click="cliData.Editor.saveFile"]');
                var $displayFilesDiv = $currentPage.find('#display-files');
                $displayFilesDiv.hide();
                var $displayErrorMsgDiv = $currentPage.find('#display-error-message');
                $displayErrorMsgDiv.hide();
                var $mainDiv = $currentPage.find('#main-div');
                $mainDiv.show();
                var $toolBarDiv = $currentPage.find('.tool-bar');
                $toolBarDiv.find('.title').html(data["name"]);

                $newBtn.hide();
                $closeBtn.show();
                $saveBtn.show();

                $currentPage.find('.page-content-inner').append('<div class="overlay"><div class="cli-data-loading"></div></div>');

                var globalCmd = new globalCommand(data.contents.data.global.command_params);
                var $content = globalCmd.htmlLeftContent;
                $($content[0]).attr("objectIndex", "0");
                $currentPage.find('.cli-data-left-column').html($content);

                setTimeout(function(){cliData.fileDisplayAPI.displayRightContents(data.contents.data)}, 1);

            });
        },

        displayRightContents: function(data){
            var $currentPage = katana.$activeTab;
            var $rightColumn = $currentPage.find('.cli-data-right-column').find('.cli-data-full-width');

            var globalCmd = new globalCommand(data.global.command_params);
            var $content = globalCmd.htmlRightContent;
            $($content[0]).attr("active", "true");
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

                var td = new testdata(data.testdata[i]);
                $rightColumn.append(td.htmlRightContent);

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

            $currentPage.find('.overlay').remove();
        },
    },

    leftColumn: {
        nextBlock: function() {
            var $elem = $(this);
            var objectIndex = parseInt($elem.closest('.cli-data-left-column-topbar').attr('objectIndex')) + 1;
            var $currentPage = katana.$activeTab;
            var $activeElement = $currentPage.find('[active="true"]');
            var dataObj = $activeElement.data().dataObject;
            var nextElemIndex = 0;
            var lastChildIndex = 1;
            if(dataObj.length > objectIndex){
                var actualObj = dataObj[objectIndex];
                $activeElement.get(0).scrollIntoView(true);
            } else {
                objectIndex = 0;
                var $nextElem = $activeElement.next().next().next();
                nextElemIndex = $nextElem.index() + 1;
                lastChildIndex = $currentPage.find('.cli-data-right-column').find('.cli-data-full-width').children().length - 2;
                $nextElem.attr('active', 'true');
                $activeElement.attr('active', 'false');
                var dataObj = $nextElem.data().dataObject;
                var actualObj = dataObj[objectIndex];
                $nextElem.get(0).scrollIntoView(true);
            }
            var $leftColumn = $currentPage.find('.cli-data-left-column');
            var $leftData = actualObj.htmlLeftContent;
            if(lastChildIndex == nextElemIndex){
                $leftData.find('.fa-chevron-right').addClass('cli-data-disabled-icon');
            }
            $leftData.hide();
            $leftColumn.html($leftData.fadeIn(500));
            $leftColumn.find('.cli-data-left-column-topbar').attr("objectIndex", objectIndex);
        },

        previousBlock: function(){
            var $elem = $(this);
            var objectIndex = parseInt($elem.closest('.cli-data-left-column-topbar').attr('objectIndex')) - 1;
            var $currentPage = katana.$activeTab;
            var $activeElement = $currentPage.find('[active="true"]');
            var dataObj = $activeElement.data().dataObject;
            if(objectIndex >= 0){
                var actualObj = dataObj[objectIndex];
                $activeElement.get(0).scrollIntoView(true);
            } else {
                var $prevElem = $activeElement.prev().prev().prev();
                $prevElem.attr('active', 'true');
                $activeElement.attr('active', 'false');
                var dataObj = $prevElem.data().dataObject;
                objectIndex = dataObj.length - 1;
                var actualObj = dataObj[objectIndex];
                $prevElem.get(0).scrollIntoView(true);
            }
            var $leftColumn = $currentPage.find('.cli-data-left-column');
            var $leftData = actualObj.htmlLeftContent;
            $leftData.hide();
            $leftColumn.html($leftData.fadeIn(500));
            $leftColumn.find('.cli-data-left-column-topbar').attr("objectIndex", objectIndex);
        },

        deleteBlock: function(){
            var $elem = $(this);
            var objectIndex = parseInt($elem.closest('.cli-data-left-column-topbar').attr('objectIndex'));
            var $currentPage = katana.$activeTab;
            var $leftColumn = $currentPage.find('.cli-data-left-column');
            var $activeElement = $currentPage.find('[active="true"]');
            var $content = $activeElement;
            $content.push($activeElement.next()[0]);
            $content.push($activeElement.next().next()[0]);
            var dataObj = $activeElement.data().dataObject;
            var className = dataObj[objectIndex].constructor.name;
            if (className == "testdata") {
                var $rightFullWidthColumn = $currentPage.find('.cli-data-right-column').find('.cli-data-full-width');
                var $rightChildren = $rightFullWidthColumn.children();
                var currIndex = $activeElement.index();
                var nextIndex = currIndex + 15;
                if(nextIndex >= $rightChildren.length && nextIndex == 30) {
                    var $newTdBlock = dataObj[objectIndex].addAnother();
                    $rightFullWidthColumn.append($newTdBlock);
                }
                for(var i=currIndex; i<nextIndex; i++){
                    $($rightChildren[i]).remove();
                }
                $rightChildren = $currentPage.find('.cli-data-right-column').find('.cli-data-full-width').children();
                if (currIndex >= $rightChildren.length){
                    currIndex = currIndex - 1;
                }
                $($rightChildren[currIndex]).attr("active", "true");
                $activeElement = $currentPage.find('[active="true"]');
                $activeElement.get(0).scrollIntoView(true);
                dataObj = $activeElement.data().dataObject;
                objectIndex = dataObj.length - 1;
                var $leftData = dataObj[objectIndex].htmlLeftContent;
                $leftData.hide();
                $leftColumn.html($leftData.fadeIn(500));
                $leftColumn.find('.cli-data-left-column-topbar').attr("objectIndex", objectIndex);
            } else {
                dataObj[objectIndex].deleteBlockElement($content, objectIndex);
                if(objectIndex < dataObj.length){
                    var $leftData = dataObj[objectIndex].htmlLeftContent;
                    $leftData.hide();
                    $leftColumn.html($leftData.fadeIn(500));
                    $leftColumn.find('.cli-data-left-column-topbar').attr("objectIndex", objectIndex);
                } else if (objectIndex-1 <= dataObj.length) {
                    var $leftData = dataObj[objectIndex-1].htmlLeftContent;
                    $leftData.hide();
                    $leftColumn.html($leftData.fadeIn(500));
                    $leftColumn.find('.cli-data-left-column-topbar').attr("objectIndex", objectIndex-1);
                }
            }
        },

        duplicateBlock: function(){
            var $elem = $(this);
            var $currentPage = katana.$activeTab;
            var $activeElement = $currentPage.find('[active="true"]');
            var objectIndex = parseInt($elem.closest('.cli-data-left-column-topbar').attr('objectIndex'));
            var dataObj = $activeElement.data().dataObject;
            var $currentObject = dataObj[objectIndex];
            var className = $currentObject.constructor.name;
            if (className == "testdata") {
                var activeIndex = $activeElement.index();
                var $rightFullWidthColumn = $currentPage.find('.cli-data-right-column').find('.cli-data-full-width');
                var $rightChildren = $rightFullWidthColumn.children();
                var cmdJsons = [];
                var temp = $($rightChildren[activeIndex + 3]).data().dataObject;
                for(var i=0; i<temp.length; i++){
                    cmdJsons.push(temp[i].jsonObj);
                }
                var verJsons = [];
                temp = $($rightChildren[activeIndex + 6]).data().dataObject;
                for(var i=0; i<temp.length; i++){
                    verJsons.push(temp[i].jsonObj);
                }
                var keyJsons = [];
                temp = $($rightChildren[activeIndex + 9]).data().dataObject;
                for(var i=0; i<temp.length; i++){
                    keyJsons.push(temp[i].jsonObj);
                }
                var varPatJsons = [];
                temp = $($rightChildren[activeIndex + 12]).data().dataObject;
                for(var i=0; i<temp.length; i++){
                    varPatJsons.push(temp[i].jsonObj);
                }
                cliData.leftColumn.addAnotherBlock($elem, $currentObject.jsonObj, cmdJsons, verJsons, keyJsons, varPatJsons)
            } else {
                cliData.leftColumn.addAnotherBlock($elem, $currentObject.jsonObj)
            }
        },

        addAnotherBlock: function(elem, data, tdCmd, tdVer, tdKey, tdVarPat){
            if(elem !== undefined){
                var $elem = elem;
            } else {
                var $elem = $(this);
            }
            var objectIndex = parseInt($elem.closest('.cli-data-left-column-topbar').attr('objectIndex'));
            var $currentPage = katana.$activeTab;
            var $activeElement = $currentPage.find('[active="true"]');
            var $content = $activeElement;
            $content.push($activeElement.next()[0]);
            $content.push($activeElement.next().next()[0]);
            var dataObj = $activeElement.data().dataObject;
            var $currentObject = dataObj[objectIndex];
            var className = $currentObject.constructor.name;
            var newObj = false;
            if (className == "testdataCommand") {
                newObj = new testdataCommand(data);
            } else if (className == "testdata") {
                newObj = new testdata(data);
            } else if(className == "globalVerifications"){
                newObj = new globalVerifications(data);
            } else if (className == "testdataVerifications") {
                newObj = new testdataVerifications(data);
            } else if (className == "globalCombinations") {
                newObj = new globalCombinations(data);
            } else if (className == "testdataCombinations") {
                newObj = new testdataCombinations(data);
            } else if (className == "globalKeys") {
                newObj = new globalKeys(data);
            } else if (className == "testdataKeys") {
                newObj = new testdataKeys(data);
            } else {
                alert("You cannot add another block.");
            }

            if(newObj) {
                var $leftColumn = $currentPage.find('.cli-data-left-column');
                if(className == "testdata"){
                    $content = newObj.addAnother(data, tdCmd, tdVer, tdKey, tdVarPat);
                    $activeElement.attr("active", "false");
                    $($content[0]).attr("active", "true")
                    var $rightFullWidthColumn = $currentPage.find('.cli-data-full-width');
                    $rightFullWidthColumn.append($content);
                    $($content[0]).get(0).scrollIntoView(true);
                    var $leftData = newObj.htmlLeftContent;
                    $leftData.hide();
                    $leftColumn.html($leftData.fadeIn(500));
                    $leftColumn.find('.cli-data-left-column-topbar').attr("objectIndex", 0);
                } else {
                    $content = newObj.addAnother($content);
                    var $leftData = newObj.htmlLeftContent;
                    $leftData.hide();
                    $leftColumn.html($leftData.fadeIn(500));
                    $leftColumn.find('.cli-data-left-column-topbar').attr("objectIndex", dataObj.length - 1);
                }
            }
        },

        inputChange: function(event, elem){
            var $currentPage = katana.$activeTab;
            var elemRowIndex = $(elem).closest('.row').index();
            var objectIndex = $currentPage.find('.cli-data-left-column').find('.cli-data-left-column-topbar').attr('objectindex');
            var $activeRightTable = $currentPage.find('.cli-data-right-column').find('.cli-data-full-width').find('[active="true"]');
            var $divBeingModified = $($($activeRightTable.next().find('ul').children()[elemRowIndex]).find('.cli-data-columns').children()[objectIndex])
            var objectData = $activeRightTable.data().dataObject[objectIndex];
            for (var key in objectData.orderedVariables[elemRowIndex]){
                var varKey = objectData.orderedVariables[elemRowIndex][key]["variable"];
            }
            var newValue = $(elem).val();
            objectData[varKey] = newValue;
            $divBeingModified.text(newValue);
        },

        selectChange: function(){
            var $elem = $(this);
            var $currentPage = katana.$activeTab;
            var elemRowIndex = $elem.closest('.row').index();
            var objectIndex = $currentPage.find('.cli-data-left-column').find('.cli-data-left-column-topbar').attr('objectindex');
            var $activeRightTable = $currentPage.find('.cli-data-right-column').find('.cli-data-full-width').find('[active="true"]');
            var $divBeingModified = $($($activeRightTable.next().find('ul').children()[elemRowIndex]).find('.cli-data-columns').children()[objectIndex])
            var objectData = $activeRightTable.data().dataObject[objectIndex];
            for (var key in objectData.orderedVariables[elemRowIndex]){
                var varKey = objectData.orderedVariables[elemRowIndex][key]["variable"];
            }
            var newValue = $elem.val();
            objectData[varKey] = newValue;
            $divBeingModified.text(newValue);
        },
    },

    rightColumn: {

        pinTable: function(){
            var $elem = $(this);
            var pinned = $elem.attr('pinned');
            var $currentPage = katana.$activeTab;
            var $rightColumn = $elem.closest('.cli-data-right-column');
            var $fullWidth = $rightColumn.find('.cli-data-full-width');
            var $rightTopBar = $elem.closest('.cli-data-right-column-topbar');

            if(pinned == "false"){
                $rightTopBar.find('i').addClass('fa-rotate-270 blue');
                $rightTopBar.find('i').attr('pinned', 'true');
                var $children = $fullWidth.children('.cli-data-right-column-topbar');
                for(var i=0; i<$children.length; i++){
                    $($children[i]).next().next().hide();
                    if($($children[i]).find('i').attr('pinned') == "false"){
                        $($children[i]).next().hide();
                        $($children[i]).hide();
                    }
                }

            } else {
                var $children = $fullWidth.children();
                for(var i=0; i<$children.length; i++){
                    $($children[i]).show();
                }
                $rightTopBar.get(0).scrollIntoView(true);
                $rightTopBar.find('i').removeClass('fa-rotate-270 blue');
                $rightTopBar.find('i').attr('pinned', 'false');
            }

        },

        makeActive: function(){
            var $currentPage = katana.$activeTab;
            $currentPage.find('[active="true"]').attr('active', 'false');
            var $elem = $(this);
            $elem.css("border-color", "1px solid red");
            var objectIndex = $elem.index();
            var $parentLi = $elem.closest('li');
            var fieldIndex = $parentLi.index();
            var $contentParent = $elem.closest('.cli-data-right-content');
            var $headerParent = $contentParent.prev();
            var lastChildIndex = $contentParent.closest('.cli-data-full-width').children().length - 2;
            var indexOfCurrent = $contentParent.index();
            var dataObj = $headerParent.data().dataObject;
            var actualObj = dataObj[objectIndex];
            var $leftColumn = $currentPage.find('.cli-data-left-column');
            var $leftData = actualObj.htmlLeftContent;
            if(lastChildIndex == indexOfCurrent){
                $leftData.find('.fa-chevron-right').addClass('cli-data-disabled-icon');
            }
            $leftData.hide();
            $leftColumn.html($leftData.fadeIn(500));
            $($leftColumn.find('#left-content').children().get(fieldIndex)).find('.cli-data-left-content-value-input').focus();
            $leftColumn.find('.cli-data-left-column-topbar').attr("objectIndex", objectIndex);
            $headerParent.attr('active', 'true');
            setTimeout(function(){$elem.css("border-color", "none");}, 3000);
        }

    },

}