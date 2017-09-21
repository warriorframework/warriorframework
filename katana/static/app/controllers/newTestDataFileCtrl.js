/*
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

*/

app.controller('newTestDataFileCtrl', ['$scope', '$http', '$controller', '$location', '$route', 'saveNewTestDataFileFactory', 'TestDataFileFactory', 'fileFactory', 'subdirs',
    function($scope, $http, $controller, $location, $route, saveNewTestDataFileFactory, TestDataFileFactory, fileFactory, subdirs) {

        $scope.subdirs = "none";
        $scope.cp_verification_tag_names = [];
        $scope.cp_verification_tag_attributes = [];
        $scope.td_verification_tag_names = [];
        $scope.td_verification_tag_attributes = [];
        $scope.cp_combo_tag_names = [];
        $scope.cp_combo_tag_attributes = [];
        $scope.showGlobalVerificationTags = true;
        $scope.showGlobalComboTags = true;
        $scope.individualCPVerificationTag = [];
        $scope.individualCPComboTag = [];
        $scope.showTDCommandTags = [];
        $scope.individualTDCommandTag = [];
        $scope.showTDVerificationTags = [];
        $scope.individualTDVerificationTag = [];
        $scope.tdf_name = "";
        $scope.showCmdParams = true;
        $scope.retry_list = ["y", "n"];
        $scope.resp_req_list = ["", "n"];
        $scope.inorder_list = ["", "y"];
        $scope.repeat_list = ["", "y"];
        $scope.found_list = ["y", "n", "yes", "no"];
        $scope.iter_type_list = ["per_cmd", "per_td_block"];
        $scope.execute_list = ["y", "n", "yes", "no"];
        $scope.copy_global_ver_list = [];
        $scope.copy_global_combo_list = [];
        $scope.copy_entire_td_list = [];
        $scope.copy_command_list = [];
        $scope.copy_td_ver_list = [];
        $scope.global_ver_tag_editor_is_open = false;
        $scope.global_ver_being_edited = "None";
        $scope.global_combo_tag_editor_is_open = false;
        $scope.global_combo_being_edited = "None";
        $scope.td_cp_tag_editor_is_open = [];
        $scope.td_cp_being_edited = [];
        $scope.td_ver_tag_editor_is_open = [];
        $scope.td_ver_being_edited = [];

        $scope.jsonData = {
            "data": {
                "global": {
                    "command_params": {
                        "_sys": "",
                        "_session": "",
                        "_start": "",
                        "_end": "",
                        "_timeout": "60",
                        "_sleep": "0",
                        "_verify": "",
                        "_retry": "n",
                        "_retry_timer": "60",
                        "_retry_count": "5",
                        "_retry_onmatch": "",
                        "_resp_req": "",
                        "_resp_pat_req": "",
                        "_resp_ref": "",
                        "_monitor": "",
                        "_inorder": "",
                        "_repeat": ""
                    },
                    "verifications": {
                        /*"v1": {
                            "_found": "",
                            "_search": "",
                            "_verify_on": ""
                        },
                        "combo1": {
                            combo: ""
                        }*/
                    }
                },
                "testdata": [
                    /*{
                        "_title": "",
                        "_row": "",
                        "_execute": "",
                        "_monitor": "",
                        "_iter_type": "",
                        "command": [
                            {
                                "_send": "",
                                "_sys": "",
                                "_session": "",
                                "_start": "",
                                "_end": "",
                                "_timeout": "",
                                "_sleep": "",
                                "_verify": "",
                                "_retry": "",
                                "_retry_timer": "",
                                "_retry_count": "",
                                "_retry_onmatch": "",
                                "_resp_req": "",
                                "_resp_pat_req": "",
                                "_resp_ref": "",
                                "_monitor": "",
                                "_inorder": "",
                                "_repeat": ""
                            }
                        ],
                        "v1": {
                            "found": "",
                            "search": "",
                            "verify_on": ""
                        }
                    }*/
                ]
            }
        };

         $scope.cancelFile = function() {
            location.href = '/katana/#/testdatafiles';
        };
				window.cancelFile = $scope.cancelFile;
			
        function verifyInput(){
            var check = true;

            if($scope.tdf_name === "" || $scope.tdf_name.trim() === ""){
                swal({
                    title: "File name cannot be empty.",
                    text: "",
                    type: "error",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
                check = false;
            }

            if(check) {
                for (var i = 0; i < $scope.cp_verification_tag_names.length; i++) {
                    if ($scope.cp_verification_tag_names[i] === "" || $scope.cp_verification_tag_names[i].trim() === "") {
                        check = false;
                        swal({
                            title: "Tag name of the verification tag number " + (i + 1) + " in the Global section has been left empty.",
                            type: "error",
                            confirmButtonText: "Ok",
                            closeOnConfirm: true,
                            confirmButtonColor: '#3b3131'
                        });
                        break;
                    }
                }
            }

            if(check){
                for(i=0; i<$scope.cp_combo_tag_names.length; i++){
                    if($scope.cp_combo_tag_names[i] === "" || $scope.cp_combo_tag_names[i].trim() === ""){
                        check = false;
                        swal({
                            title: "Tag name of the Combination tag number " + (i+1) + " in the Global section has been left empty.",
                            type: "error",
                            confirmButtonText: "Ok",
                            closeOnConfirm: true,
                            confirmButtonColor: '#3b3131'
                        });
                        break;
                    }
                }
            }

            if(check) {
                for (i = 0; i < $scope.jsonData.data.testdata.length; i++) {
                    if(($scope.jsonData.data.testdata[i]._title == "" || $scope.jsonData.data.testdata[i]._title == "") &&
                        ($scope.jsonData.data.testdata[i]._row == "" || $scope.jsonData.data.testdata[i]._row== "")){
                        swal({
                            title: "Both title and row for testdata block " + (i+1) + " are empty. At least one of two is required.",
                            type: "error",
                            confirmButtonText: "Ok",
                            closeOnConfirm: true,
                            confirmButtonColor: '#3b3131'
                        });
                        check = false;
                        break;
                    }
                }
            }

            if(check){
                for (i = 0; i < $scope.jsonData.data.testdata.length; i++) {
                    for (j = i+1; j < $scope.jsonData.data.testdata.length; j++) {
                        if($scope.jsonData.data.testdata[i]._title === $scope.jsonData.data.testdata[j]._title &&
                            $scope.jsonData.data.testdata[i]._row === $scope.jsonData.data.testdata[j]._row){
                            check = false;
                            swal({
                                title: "Title and Row for testdata blocks " + (i+1) + " and " + (j+1) + " are the same.",
                                text: "Both title and row of any two testdata blocks cannot be the same. Please change at least one of them",
                                type: "warning",
                                confirmButtonText: "Ok",
                                closeOnConfirm: true,
                                confirmButtonColor: '#3b3131'
                            });
                            break;
                        }
                    }
                }
            }

            if(check){
                for(i=0; i<$scope.td_verification_tag_names.length; i++){
                    for(var j=0; j<$scope.td_verification_tag_names[i].length; j++){
                        if($scope.td_verification_tag_names[i][j] === "" || $scope.td_verification_tag_names[i][j].trim() === ""){
                            check = false;
                            swal({
                                title: "Tag name of the Verification tag number " + (j+1) + " in the Testdata block number " + (i+1) +" has been left empty.",
                                type: "error",
                                confirmButtonText: "Ok",
                                closeOnConfirm: true,
                                confirmButtonColor: '#3b3131'
                            });
                            break;
                        }
                    }
                }
            }

            if(check){
                if($scope.jsonData.data.global.command_params._end.trim() == ""){
                    for(i=0; i<$scope.jsonData.data.testdata.length; i++){
                        for(j=0; j<$scope.jsonData.data.testdata[i].command.length; j++){
                            if($scope.jsonData.data.testdata[i].command[j]._end === ""){
                                check = false;
                                swal({
                                    title: "The end field in testdata block " + (i+1) + " and command number " + (j+1) + " has been left empty.",
                                    text: "End prompt is a mandatory field since the end attribute in the global command params has been left empty.",
                                    type: "error",
                                    confirmButtonText: "Ok",
                                    closeOnConfirm: true,
                                    confirmButtonColor: '#3b3131'
                                });
                                break;
                            }
                        }
                    }
                }
            }

            return check;
        }
				
        $scope.saveFile = function() {

            var check = verifyInput();

            if(check){
                var filename = $scope.tdf_name + ".xml";

                for(var i=0; i<$scope.cp_verification_tag_names.length; i++){
                    $scope.jsonData.data.global.verifications[$scope.cp_verification_tag_names[i]] = $scope.cp_verification_tag_attributes[i];
                }
                for(i=0; i<$scope.cp_combo_tag_names.length; i++){
                    $scope.jsonData.data.global.verifications[$scope.cp_combo_tag_names[i]] = $scope.cp_combo_tag_attributes[i];
                }
                for(i=0; i<$scope.td_verification_tag_names.length; i++){
                    for(var j=0; j<$scope.td_verification_tag_names[i].length; j++){
                        $scope.jsonData.data.testdata[i][$scope.td_verification_tag_names[i][j]] = $scope.td_verification_tag_attributes[i][j];
                    }
                }
							  fileFactory.checkfileexistwithsubdir(filename, 'testdatafile', $scope.subdirs)
                    .then(
                        function(data) {
                            console.log(data);
                            var fileExist = data.response;
                            if (fileExist == 'y') {
                                sweetAlert({
                                    title: "File " + filename + " already exists. Do you want to overwrite it?",
                                    closeOnConfirm: false,
                                    confirmButtonColor: '#3b3131',
                                    confirmButtonText: "Yes!",
                                    showCancelButton: true,
                                    cancelButtonText: "Nope.",
                                    type: "warning"
                                },
                                function(isConfirm){
                                    if (isConfirm) {
                                       return true;
                                    }
                                    else {
                                        return false;
                                    }
                                });

                            } else {
                                return true;
                            }
                        },
                        function(data) {
                            alert(data);
                        });
            
            }
        };

        function save(filename){
            var x2js = new X2JS();
            var token = angular.toJson($scope.jsonData);
						console.log('save', $scope.jsonData, token);
            var xmlObj = x2js.json2xml_str(wizardAPI.formsToJSON());
            saveNewTestDataFileFactory.saveNew( wizardAPI.returnFileName() + '.xml', $scope.subdirs, xmlObj)
                .then(
                    function(data) {
                        console.log(data);
                    },
                    function(data) {
                        alert(data);
                    });
            sweetAlert({
                title: "File saved: " + wizardAPI.returnFileName() + '.xml',
                showConfirmButton: false,
                type: "success",
                timer: 1250
            });
            $location.path('/testDatafiles');
        }
			    window.checkExists = function(){ fileFactory.checkfileexistwithsubdir( wizardAPI.returnFileName() + '.xml', 'testdatafile', $scope.subdirs)
                    .then(
                        function(data) {
                            console.log(data);
                            var fileExist = data.response;
                            if (fileExist == 'yes') {
                                sweetAlert({
                                    title: "File " + wizardAPI.returnFileName() + '.xml' + " already exists. Do you want to overwrite it?",
                                    closeOnConfirm: false,
                                    confirmButtonColor: '#3b3131',
                                    confirmButtonText: "Yes!",
                                    showCancelButton: true,
                                    cancelButtonText: "Nope.",
                                    type: "warning"
                                },
                                function(isConfirm){
                                    if (isConfirm) {
                                       window.save();
                                    }
                                    else {
                                        return false;
                                    }
                                });

                            } else {
                                window.save();
                            }
                        },
                        function(data) {
                            alert(data);
                        });
																				 };
				window.save = save;
        $scope.spanClick = function(){
        };

        $scope.saveCmdParams = function(){
            $scope.showCmdParams = false;
        };

        $scope.editCmdParams = function(){
            $scope.showCmdParams = true;
        };

        $scope.addAnotherTDBlock = function(){
            $scope.showTDVerificationTags.push(true);
            $scope.individualTDVerificationTag.push([]);
            $scope.individualTDCommandTag.push([]);
            $scope.showTDCommandTags.push(true);
            $scope.jsonData.data.testdata.push({
                "_title": "",
                "_row": "",
                "_execute": "y",
                "_monitor": "",
                "_iter_type": "per_cmd",
                "command": [
                    /*{
                        "send": "",
                        "sys": "",
                        "session": "",
                        "start": "",
                        "end": "",
                        "timeout": "",
                        "sleep": "",
                        "verify": "",
                        "retry": "",
                        "retry_timer": "",
                        "retry_count": "",
                        "retry_onmatch": "",
                        "resp_req": "",
                        "resp_pat_req": "",
                        "resp_ref": "",
                        "monitor": "",
                        "inorder": "",
                        "repeat": ""
                    }*/
                ]
            }
            );

            $scope.td_verification_tag_names.push([]);
            $scope.td_verification_tag_attributes.push([]);
            $scope.copy_entire_td_list.push([]);
            $scope.copy_command_list.push([]);
            $scope.copy_td_ver_list.push([]);

            for(var i=0; i<$scope.jsonData.data.testdata.length; i++){
                $scope.copy_entire_td_list[i] = [];
                for(var j=0; j<$scope.jsonData.data.testdata.length; j++){
                    if(j !== i){
                        $scope.copy_entire_td_list[i].push(j+1);
                    }
                }
            }

            $scope.td_cp_tag_editor_is_open.push(false);
            $scope.td_cp_being_edited.push("None");
            $scope.td_ver_tag_editor_is_open.push(false);
            $scope.td_ver_being_edited.push("None");
        };

        $scope.deleteTDBlock = function(index) {
            if($scope.jsonData.data.testdata.length > 1){
                $scope.jsonData.data.testdata.splice(index, 1);
                $scope.showTDVerificationTags.splice(index, 1);
                $scope.individualTDVerificationTag.splice(index, 1);
                $scope.individualTDCommandTag.splice(index, 1);
                $scope.showTDCommandTags.splice(index, 1);
                $scope.td_verification_tag_names.splice(index, 1);
                $scope.td_verification_tag_attributes.splice(index, 1);
                $scope.copy_entire_td_list.splice(index, 1);
                $scope.copy_command_list.splice(index, 1);
                $scope.copy_td_ver_list.splice(index, 1);
                $scope.td_cp_being_edited.splice(index, 1);
                $scope.td_cp_tag_editor_is_open.splice(index, 1);
                $scope.td_ver_being_edited.splice(index, 1);
                $scope.td_ver_tag_editor_is_open.splice(index, 1);
            }
            else{
                $scope.jsonData.data.testdata = [];
                $scope.showTDVerificationTags = [];
                $scope.individualTDVerificationTag = [];
                $scope.individualTDCommandTag = [];
                $scope.showTDCommandTags = [];
                $scope.td_verification_tag_names = [];
                $scope.td_verification_tag_attributes = [];
                $scope.copy_entire_td_list = [];
                $scope.copy_command_list = [];
                $scope.copy_td_ver_list = [];
                $scope.td_cp_being_edited = [];
                $scope.td_cp_tag_editor_is_open = [];
                $scope.td_ver_being_edited = [];
                $scope.td_ver_tag_editor_is_open = [];
            }

            for(var i=0; i<$scope.jsonData.data.testdata.length; i++){
                $scope.copy_entire_td_list[i] = [];
                for(var j=0; j<$scope.jsonData.data.testdata.length; j++){
                    if(j !== i){
                        $scope.copy_entire_td_list[i].push(j+1);
                    }
                }
            }

        };

        $scope.addTDVerificationTag = function(index){
            if($scope.td_ver_tag_editor_is_open[index]){
                swal({
                    title: "You have a Verification already open in The Editor for Testdata Block " + (index+1) + ".",
                    text: "Please save that Verification before creating a new one.",
                    type: "warning",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
                return;
            }
            $scope.td_ver_tag_editor_is_open[index] = true;
            $scope.individualTDVerificationTag[index].push(true);
            $scope.td_verification_tag_names[index].push("");
            $scope.td_verification_tag_attributes[index].push({
                            "_found": "y",
                            "_search": "",
                            "_verify_on": ""
                        });
            $scope.td_ver_being_edited[index] = $scope.td_verification_tag_names[index].command.length-1;
            if(index < $scope.copy_td_ver_list.length){
                $scope.copy_td_ver_list.push([]);
            }
            $scope.copy_td_ver_list[index].push([]);

            for(var i=0; i<$scope.td_verification_tag_names[index].length; i++){
                $scope.copy_td_ver_list[index][i] = [];
                for(var j=0; j<$scope.td_verification_tag_names[index].length; j++){
                    if(j !== i){
                        $scope.copy_td_ver_list[index][i].push(j+1);
                    }
                }
            }

        };

        $scope.saveTDVerificationTag = function(parent_index, index){
            if($scope.td_verification_tag_names[parent_index][index] === "" ||
                $scope.td_verification_tag_names[parent_index][index].trim() === ""){
                swal({
                    title: "Tag name is empty.",
                    text: "Please add a tag name and then save.",
                    type: "error",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
            }
            else if($scope.td_verification_tag_names[parent_index][index].match(/^[0-9_]/)){
                swal({
                    title: "Tag names cannot start with a number or an underscore.",
                    type: "error",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
            }
            else if($scope.td_verification_tag_names[parent_index][index].match(/[^a-zA-Z 0-9\._\-]/i)){
                swal({
                    title: "Tag names cannot contain special characters other than an underscore, period, and hyphen.",
                    type: "error",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
            }
            else if($scope.td_verification_tag_names[parent_index][index].indexOf(" ") !== -1){
                swal({
                    title: "Tag names cannot contain spaces.",
                    type: "error",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
            }
            else{
                $scope.showTDVerificationTags[parent_index] = false;
                $scope.individualTDVerificationTag[parent_index][index] = false;
                $scope.td_ver_tag_editor_is_open[parent_index] = false;
                $scope.td_ver_being_edited[parent_index] = "None";
            }
        };

        $scope.editTDVerificationTag = function(parent_index, index){
            if($scope.td_ver_tag_editor_is_open[parent_index]){
                swal({
                    title: "You have a Verification already open in The Editor for Testdata Block " + (parent_index+1) + ".",
                    text: "Please save that Verification before editing a new one.",
                    type: "warning",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
                return;
            }
            $scope.individualTDVerificationTag[parent_index][index] = true;
            var flag = true;
            for(var i=0; i<$scope.individualTDVerificationTag[parent_index].length; i++){
                if(!$scope.individualTDVerificationTag[parent_index][i]){
                    flag = false;
                    $scope.showTDVerificationTags[parent_index] = false;
                    break;
                }
            }
            if(flag){
                $scope.showTDVerificationTags[parent_index] = true;
            }
            $scope.td_ver_tag_editor_is_open[parent_index] = true;
            $scope.td_ver_being_edited[parent_index] = index;
        };

        $scope.deleteTDVerificationTag = function(parent_index, index){
            if($scope.td_verification_tag_names[parent_index].length > 1){
                $scope.td_verification_tag_names[parent_index].splice(index, 1);
                $scope.td_verification_tag_attributes[parent_index].splice(index, 1);
                $scope.individualTDVerificationTag[parent_index].splice(index, 1);
                $scope.copy_td_ver_list[parent_index].splice(index, 1);
                if($scope.td_ver_being_edited[parent_index] == "None"){
                    $scope.td_ver_tag_editor_is_open[parent_index] = false;
                }
                else if($scope.td_ver_being_edited[parent_index] == index){
                    $scope.td_ver_being_edited[parent_index] = "None";
                    $scope.td_ver_tag_editor_is_open[parent_index] = false;
                }
                else if(index< $scope.td_ver_being_edited[parent_index]){
                    $scope.td_ver_being_edited[parent_index] = $scope.td_ver_being_edited[parent_index] - 1;
                }
            }
            else{
                $scope.td_verification_tag_names[parent_index] = [];
                $scope.td_verification_tag_attributes[parent_index] = [];
                $scope.individualTDVerificationTag[parent_index] = [];
                $scope.copy_td_ver_list[parent_index] = [];
                $scope.td_ver_tag_editor_is_open[parent_index] = false;
                $scope.td_ver_being_edited[parent_index] = "None";
            }
            var flag = true;
            for(var i=0; i<$scope.individualTDVerificationTag[parent_index].length; i++){
                if(!$scope.individualTDVerificationTag[parent_index][i]){
                    flag = false;
                    $scope.showTDVerificationTags[parent_index] = false;
                    break;
                }
            }
            if(flag){
                $scope.showTDVerificationTags[parent_index] = true;
            }
            for(i=0; i<$scope.td_verification_tag_names[parent_index].length; i++){
                $scope.copy_td_ver_list[parent_index][i] = [];
                for(var j=0; j<$scope.td_verification_tag_names[parent_index].length; j++){
                    if(j !== i){
                        $scope.copy_td_ver_list[parent_index][i].push(j+1);
                    }
                }
            }
        };

        $scope.saveCommandTag = function(parent_index, index){
            if($scope.jsonData.data.testdata[parent_index].command[index]._end !== "" || $scope.jsonData.data.global.command_params._end !== ""){
                $scope.individualTDCommandTag[parent_index][index] = false;
                $scope.showTDCommandTags[parent_index] = false;
                $scope.td_cp_tag_editor_is_open[parent_index] = false;
                $scope.td_cp_being_edited[parent_index] = "None";
            }
            else{
                swal({
                    title: "End parameter is mandatory.",
                    type: "warning",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
            }

        };

        $scope.editCommandTag = function(parent_index, index){
            if($scope.td_cp_tag_editor_is_open[parent_index]){
                swal({
                    title: "You have a Command already open in The Editor for Testdata Block " + (parent_index+1) + ".",
                    text: "Please save that Command before editing a new one.",
                    type: "warning",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
                return;
            }
            $scope.individualTDCommandTag[parent_index][index] = true;
            var flag = true;
            for(var i=0; i<$scope.individualTDCommandTag[parent_index].length; i++){
                if(!$scope.individualTDCommandTag[parent_index][i]){
                    flag = false;
                    $scope.showTDCommandTags[parent_index] = false;
                    break;
                }
            }
            if(flag){
                $scope.showTDCommandTags[parent_index] = true;
            }
            $scope.td_cp_tag_editor_is_open[parent_index] = true;
            $scope.td_cp_being_edited[parent_index] = index;
        };

        $scope.deleteCommandTag = function(parent_index, index){
            if($scope.jsonData.data.testdata[parent_index].command.length > 1){
                $scope.jsonData.data.testdata[parent_index].command.splice(index, 1);
                $scope.individualTDCommandTag[parent_index].splice(index, 1);
                $scope.copy_command_list[parent_index].splice(index, 1);
                if($scope.td_cp_being_edited[parent_index] == "None"){
                    $scope.td_cp_being_edited[parent_index] = false;
                }
                else if($scope.td_cp_being_edited[parent_index] == index){
                    $scope.td_cp_being_edited[parent_index] = "None";
                    $scope.td_cp_tag_editor_is_open[parent_index] = false;
                }
                else if(index < $scope.td_cp_being_edited[parent_index]){
                    $scope.td_cp_being_edited[parent_index] = $scope.td_cp_being_edited[parent_index] - 1;
                }
            }
            else{
                $scope.jsonData.data.testdata[parent_index].command = [];
                $scope.individualTDCommandTag[parent_index] = [];
                $scope.copy_command_list[parent_index] = [];
                $scope.td_cp_tag_editor_is_open[parent_index] = false;
                $scope.td_cp_being_edited[parent_index] = "None";
            }
            var flag = true;
            for(var i=0; i<$scope.individualTDCommandTag[parent_index].length; i++){
                if(!$scope.individualTDCommandTag[parent_index][i]){
                    flag = false;
                    $scope.showTDCommandTags[parent_index] = false;
                    break;
                }
            }
            if(flag){
                $scope.showTDCommandTags[parent_index] = true;
            }

            for(i=0; i<$scope.jsonData.data.testdata[parent_index].command.length; i++){
                $scope.copy_command_list[index][i] = [];
                for(var j=0; j<$scope.jsonData.data.testdata[parent_index].command.length; j++){
                    if(j !== i){
                        $scope.copy_command_list[index][i].push(j+1);
                    }
                }
            }
        };
				window.jsonData = $scope.jsonData.data;
        $scope.addAnotherCommandTag = function(index){
            if($scope.td_cp_tag_editor_is_open[index]){
                swal({
                    title: "You have a Command already open in The Editor for Testdata Block " + (index+1) + ".",
                    text: "Please save that Command before creating a new one.",
                    type: "warning",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
                return;
            }
            $scope.td_cp_tag_editor_is_open[index] = true;
            var len = $scope.jsonData.data.testdata[index].command.length + 1;
            $scope.individualTDCommandTag[index].push(true);
            $scope.jsonData.data.testdata[index].command.push(
                {
                    "_send": "",
                    "_sys": "",
                    "_session": "",
                    "_start": "",
                    "_end": "",
                    "_timeout": "60",
                    "_sleep": "0",
                    "_verify": "",
                    "_retry": "n",
                    "_retry_timer": "60",
                    "_retry_count": "5",
                    "_retry_onmatch": "",
                    "_resp_req": "",
                    "_resp_pat_req": "",
                    "_resp_ref": len,
                    "_monitor": "",
                    "_inorder": "",
                    "_repeat": ""
                }
            );
            $scope.td_cp_being_edited[index] = $scope.jsonData.data.testdata[index].command.length-1;

            if(index < $scope.copy_command_list.length){
                $scope.copy_command_list.push([]);
            }
            $scope.copy_command_list[index].push([]);

            for(var i=0; i<$scope.jsonData.data.testdata[index].command.length; i++){
                $scope.copy_command_list[index][i] = [];
                for(var j=0; j<$scope.jsonData.data.testdata[index].command.length; j++){
                    if(j !== i){
                        $scope.copy_command_list[index][i].push(j+1);
                    }
                }
            }
        };

        $scope.saveCPVerificationTag = function(index){
            if($scope.cp_verification_tag_names[index] === "" ||
                $scope.cp_verification_tag_names[index].trim() === ""){
                swal({
                    title: "Tag name is empty.",
                    text: "Please add a tag name and then save.",
                    type: "error",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
            }
            else if($scope.cp_verification_tag_names[index].match(/^[0-9_]/)){
                swal({
                    title: "Tag names cannot start with a number or an underscore.",
                    type: "error",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
            }
            else if($scope.cp_verification_tag_names[index].match(/[^a-zA-Z 0-9\._\-]/i)){
                swal({
                    title: "Tag names cannot contain special characters other than an underscore, period, and hyphen.",
                    type: "error",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
            }
            else if($scope.cp_verification_tag_names[index].indexOf(" ") !== -1){
                swal({
                    title: "Tag names cannot contain spaces.",
                    type: "error",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
            }
            else {
                $scope.showGlobalVerificationTags = false;
                $scope.individualCPVerificationTag[index] = false;
                $scope.global_ver_tag_editor_is_open = false;
                $scope.global_ver_being_edited = "None";
            }
        };

        $scope.addAnotherCPVerificationTag = function(){
            if($scope.global_ver_tag_editor_is_open){
                swal({
                    title: "A Global Verification Tag is currently open in the Editor. Please save that tag information before creating a new one.",
                    type: "warning",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
                return;
            }
            $scope.individualCPVerificationTag.push(true);
            $scope.cp_verification_tag_names.push("");
            $scope.cp_verification_tag_attributes.push({
                            "_found": "y",
                            "_search": "",
                            "_verify_on": ""
                        });
            $scope.copy_global_ver_list.push([]);
            for(var i=0; i<$scope.cp_verification_tag_names.length; i++){
                $scope.copy_global_ver_list[i] = [];
                for(var j=0; j<$scope.cp_verification_tag_names.length; j++){
                    if(j !== i){
                        $scope.copy_global_ver_list[i].push(j+1);
                    }
                }
            }
            $scope.global_ver_being_edited = $scope.cp_verification_tag_names.length - 1;
            $scope.global_ver_tag_editor_is_open = true;
        };

        $scope.editCPVerificationTag = function (index) {
            if($scope.global_ver_tag_editor_is_open){
                swal({
                    title: "A Global Verification Tag is currently open in the Editor. Please save that tag information before editing a new one.",
                    type: "warning",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
                return;
            }
            $scope.individualCPVerificationTag[index] = true;
            $scope.global_ver_being_edited = index;
            $scope.global_ver_tag_editor_is_open = true;
            var flag = true;
            for(var i=0; i<$scope.individualCPVerificationTag.length; i++){
                if(!$scope.individualCPVerificationTag[i]){
                    flag = false;
                    $scope.showGlobalVerificationTags = false;
                    break;
                }
            }
            if(flag){
                $scope.showGlobalVerificationTags = true;
            }
        };

        $scope.deleteCPVerificationTag = function(index){
            if($scope.cp_verification_tag_names.length > 1){
                $scope.individualCPVerificationTag.splice(index, 1);
                $scope.cp_verification_tag_names.splice(index, 1);
                $scope.cp_verification_tag_attributes.splice(index, 1);
                $scope.copy_global_ver_list.splice(index, 1);
            }
            else{
                $scope.individualCPVerificationTag = [];
                $scope.cp_verification_tag_names = [];
                $scope.cp_verification_tag_attributes = [];
                $scope.copy_global_ver_list = [];
            }
            var flag = true;
            for(var i=0; i<$scope.individualCPVerificationTag.length; i++){
                if(!$scope.individualCPVerificationTag[i]){
                    flag = false;
                    $scope.showGlobalVerificationTags = false;
                    break;
                }
            }
            if(flag){
                $scope.showGlobalVerificationTags = true;
            }

            for(i=0; i<$scope.cp_verification_tag_names.length; i++){
                $scope.copy_global_ver_list[i] = [];
                for(var j=0; j<$scope.cp_verification_tag_names.length; j++){
                    if(j !== i){
                        $scope.copy_global_ver_list[i].push(j+1);
                    }
                }
            }
            if($scope.global_ver_being_edited == index){
                $scope.global_ver_tag_editor_is_open = false;
                $scope.global_ver_being_edited = "None";
            }
            else if(index < $scope.global_ver_being_edited){
                $scope.global_ver_being_edited = $scope.global_ver_being_edited - 1;
            }

        };

        $scope.saveCPComboTag = function(index){
            if($scope.cp_combo_tag_names[index] === "" ||
                $scope.cp_combo_tag_names[index].trim() === ""){
                swal({
                    title: "Tag name is empty.",
                    text: "Please add a tag name and then save.",
                    type: "error",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
            }
            else if($scope.cp_combo_tag_names[index].match(/^[0-9_]/)){
                swal({
                    title: "Tag names cannot start with a number or an underscore.",
                    type: "error",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
            }
            else if($scope.cp_combo_tag_names[index].match(/[^a-zA-Z 0-9\._\-]/i)){
                swal({
                    title: "Tag names cannot contain special characters other than an underscore, period, and hyphen.",
                    type: "error",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
            }
            else if($scope.cp_combo_tag_names[index].indexOf(" ") !== -1){
                swal({
                    title: "Tag names cannot contain spaces.",
                    type: "error",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
            }
            else {
                $scope.showGlobalComboTags = false;
                $scope.individualCPComboTag[index] = false;
                $scope.global_combo_tag_editor_is_open = false;
                $scope.global_combo_being_edited = "None";
            }
        };

        $scope.addAnotherCPComboTag = function(){
            if($scope.global_combo_tag_editor_is_open){
                swal({
                    title: "A Global Combination Tag is currently open in the Editor. Please save that tag information before creating a new one.",
                    type: "error",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
                return;
            }
            $scope.individualCPComboTag.push(true);
            $scope.cp_combo_tag_names.push("");
            $scope.cp_combo_tag_attributes.push({"_combo": ""});
            $scope.copy_global_combo_list.push([]);

            for(var i=0; i<$scope.cp_combo_tag_names.length; i++){
                $scope.copy_global_combo_list[i] = [];
                for(var j=0; j<$scope.cp_combo_tag_names.length; j++){
                    if(j !== i){
                        $scope.copy_global_combo_list[i].push(j+1);
                    }
                }
            }
            $scope.global_combo_being_edited = $scope.cp_combo_tag_names.length - 1;
            $scope.global_combo_tag_editor_is_open = true;
        };

        $scope.editCPComboTag = function(index){
            if($scope.global_combo_tag_editor_is_open){
                swal({
                    title: "A Global Combination Tag is currently open in the Editor. Please save that tag information before editing a new one.",
                    type: "error",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
                return;
            }
            $scope.individualCPComboTag[index] = true;
            $scope.global_combo_being_edited = index;
            $scope.global_combo_tag_editor_is_open = true;
            var flag = true;
            for(var i=0; i<$scope.individualCPComboTag.length; i++){
                if(!$scope.individualCPComboTag[i]){
                    flag = false;
                    $scope.showGlobalComboTags = false;
                    break;
                }
            }
            if(flag){
                $scope.showGlobalComboTags = true;
            }
        };

        $scope.deleteCPComboTag = function(index){
            if($scope.cp_combo_tag_names.length > 1){
                $scope.individualCPComboTag.splice(index, 1);
                $scope.cp_combo_tag_names.splice(index, 1);
                $scope.cp_combo_tag_attributes.splice(index, 1);
                $scope.copy_global_combo_list.splice(index, 1);
            }
            else{
                $scope.individualCPComboTag = [];
                $scope.cp_combo_tag_names = [];
                $scope.cp_combo_tag_attributes = [];
                $scope.copy_global_combo_list = [];
            }
            var flag = true;
            for(var i=0; i<$scope.individualCPComboTag.length; i++){
                if(!$scope.individualCPComboTag[i]){
                    flag = false;
                    $scope.showGlobalComboTags = false;
                    break;
                }
            }
            if(flag){
                $scope.showGlobalComboTags = true;
            }

            for(i=0; i<$scope.cp_combo_tag_names.length; i++){
                $scope.copy_global_combo_list[i] = [];
                for(var j=0; j<$scope.cp_combo_tag_names.length; j++){
                    if(j !== i){
                        $scope.copy_global_combo_list[i].push(j+1);
                    }
                }
            }

            if($scope.global_combo_being_edited == index){
                $scope.global_combo_tag_editor_is_open = false;
                $scope.global_combo_being_edited = "None";
            }
            else if(index < $scope.global_combo_being_edited){
                $scope.global_combo_being_edited = $scope.global_combo_being_edited - 1;
            }
        };

        fileFactory.readtooltipfile('testdata')
        .then(
            function(data) {
                // console.log(data);
                $scope.testdataTooltips = data;
            },
            function(data) {
                alert(data);
            });

        if($route.current.$$route.newFile == "no"){
            $scope.subdirs = subdirs;
            readTestDataFile();
        }
				else
					wizardAPI && wizardAPI.init();

        function readTestDataFile(){
            TestDataFileFactory.fetch()
            .then(function (data) {
                    $scope.xmlData = data["xml"];
                    $scope.tdf_name = data["filename"].split(".")[0];

                    var x2js = new X2JS();
                    $scope.jsonData = x2js.xml_str2json($scope.xmlData);
										window.tdOriginalJSON = $scope.jsonData;
                    if ($scope.jsonData == null) {
                        sweetAlert({
                            title: "There was an error reading the TestData File: " + data["filename"],
                            text: "This XML file may be malformed.",
                            closeOnConfirm: true,
                            confirmButtonColor: '#3b3131',
                            confirmButtonText: "Ok",
                            type: "error"
                        });
                    }
                    else{

                        //Global Tag validation

                        if(!$scope.jsonData.data.hasOwnProperty("global")){
                            $scope.jsonData.data.global =
                                {
                                    "command_params": {
                                        "_sys": "",
                                        "_session": "",
                                        "_start": "",
                                        "_end": "",
                                        "_timeout": "60",
                                        "_sleep": "0",
                                        "_verify": "",
                                        "_retry": "n",
                                        "_retry_timer": "60",
                                        "_retry_count": "5",
                                        "_retry_onmatch": "",
                                        "_resp_req": "",
                                        "_resp_pat_req": "",
                                        "_resp_ref": "",
                                        "_monitor": "",
                                        "_inorder": "",
                                        "_repeat": ""
                                    },
                                    "verifications": {
                                        /*"v1": {
                                            "_found": "",
                                            "_search": "",
                                            "_verify_on": ""
                                        },
                                        "combo1": {
                                            combo: ""
                                        }*/
                                    }
                            }
                        }

                        // Global Command Params validation

                        if(!$scope.jsonData.data.global.hasOwnProperty("command_params")){
                            $scope.jsonData.data.global.command_params =
                            {
                                "_sys": "",
                                "_session": "",
                                "_start": "",
                                "_end": "",
                                "_timeout": "60",
                                "_sleep": "0",
                                "_verify": "",
                                "_retry": "n",
                                "_retry_timer": "60",
                                "_retry_count": "5",
                                "_retry_onmatch": "",
                                "_resp_req": "",
                                "_resp_pat_req": "",
                                "_resp_ref": "",
                                "_monitor": "",
                                "_inorder": "",
                                "_repeat": ""
                            }
                        }

                        $scope.showCmdParams = false;

                        if(!$scope.jsonData.data.global.command_params.hasOwnProperty("_sys")){
                            $scope.jsonData.data.global.command_params._sys = "";
                        }
                        if(!$scope.jsonData.data.global.command_params.hasOwnProperty("_session")){
                            $scope.jsonData.data.global.command_params._session = "";
                        }
                        if(!$scope.jsonData.data.global.command_params.hasOwnProperty("_start")){
                            $scope.jsonData.data.global.command_params._start = "";
                        }
                        if(!$scope.jsonData.data.global.command_params.hasOwnProperty("_end")){
                            $scope.jsonData.data.global.command_params._end = "";
                        }
                        if(!$scope.jsonData.data.global.command_params.hasOwnProperty("_timeout")){
                            $scope.jsonData.data.global.command_params._timeout = "60";
                        }
                        if(!$scope.jsonData.data.global.command_params.hasOwnProperty("_sleep")){
                            $scope.jsonData.data.global.command_params._sleep = "0";
                        }
                        if(!$scope.jsonData.data.global.command_params.hasOwnProperty("_verify")){
                            $scope.jsonData.data.global.command_params._verify = "";
                        }
                        if(!$scope.jsonData.data.global.command_params.hasOwnProperty("_retry")){
                            $scope.jsonData.data.global.command_params._retry = "n";
                        }

                        for(i=0; i<$scope.retry_list.length; i++){
                            if($scope.jsonData.data.global.command_params._retry.toLowerCase() == $scope.retry_list[i].toLowerCase()){
                                $scope.jsonData.data.global.command_params._retry = $scope.retry_list[i];
                                break;
                            }
                        }

                        if(!$scope.jsonData.data.global.command_params.hasOwnProperty("_retry_timer")){
                            $scope.jsonData.data.global.command_params._retry_timer = "60";
                        }
                        if(!$scope.jsonData.data.global.command_params.hasOwnProperty("_retry_count")){
                            $scope.jsonData.data.global.command_params._retry_count = "5";
                        }
                        if(!$scope.jsonData.data.global.command_params.hasOwnProperty("_retry_onmatch")){
                            $scope.jsonData.data.global.command_params._retry_onmatch = "";
                        }
                        if(!$scope.jsonData.data.global.command_params.hasOwnProperty("_resp_req")){
                            $scope.jsonData.data.global.command_params._resp_req = "";
                        }

                        for(i=0; i<$scope.resp_req_list.length; i++){
                            if($scope.jsonData.data.global.command_params._resp_req.toLowerCase() == $scope.resp_req_list[i].toLowerCase()){
                                $scope.jsonData.data.global.command_params._resp_req = $scope.resp_req_list[i];
                                break;
                            }
                        }

                        if(!$scope.jsonData.data.global.command_params.hasOwnProperty("_resp_pat_req")){
                            $scope.jsonData.data.global.command_params._resp_pat_req = "";
                        }
                        if(!$scope.jsonData.data.global.command_params.hasOwnProperty("_resp_ref")){
                            $scope.jsonData.data.global.command_params._resp_ref = "";
                        }
                        if(!$scope.jsonData.data.global.command_params.hasOwnProperty("_monitor")){
                            $scope.jsonData.data.global.command_params._monitor = "";
                        }
                        if(!$scope.jsonData.data.global.command_params.hasOwnProperty("_inorder")){
                            $scope.jsonData.data.global.command_params._inorder = "";
                        }

                        for(i=0; i<$scope.inorder_list.length; i++){
                            if($scope.jsonData.data.global.command_params._inorder.toLowerCase() == $scope.inorder_list[i].toLowerCase()){
                                $scope.jsonData.data.global.command_params._inorder = $scope.inorder_list[i];
                                break;
                            }
                        }

                        if(!$scope.jsonData.data.global.command_params.hasOwnProperty("_repeat")){
                            $scope.jsonData.data.global.command_params._repeat = "";
                        }

                        for(i=0; i<$scope.repeat_list.length; i++){
                            if($scope.jsonData.data.global.command_params._repeat.toLowerCase() == $scope.repeat_list[i].toLowerCase()){
                                $scope.jsonData.data.global.command_params._repeat = $scope.repeat_list[i];
                                break;
                            }
                        }

                        // Global Verification and Combo tags validation

                        if(!$scope.jsonData.data.global.hasOwnProperty("verifications")){
                            $scope.jsonData.data.global.verifications = {};
                        }

                        for(var key in $scope.jsonData.data.global.verifications){
                            if($scope.jsonData.data.global.verifications.hasOwnProperty(key)){
                                if($scope.jsonData.data.global.verifications[key].hasOwnProperty("_combo")){
                                    $scope.cp_combo_tag_names.push(key);
                                    if(!$scope.jsonData.data.global.verifications[key].hasOwnProperty("_combo")){
                                        $scope.jsonData.data.global.verifications[key]._combo = "";
                                    }
                                    $scope.cp_combo_tag_attributes.push($scope.jsonData.data.global.verifications[key]);
                                    $scope.showGlobalComboTags = false;
                                    $scope.individualCPComboTag.push(false);
                                }
                                else{
                                    $scope.cp_verification_tag_names.push(key);
                                    if(!$scope.jsonData.data.global.verifications[key].hasOwnProperty("_found")){
                                        $scope.jsonData.data.global.verifications[key]._found = "y";
                                    }

                                    for(i=0; i<$scope.found_list.length; i++){
                                        if($scope.jsonData.data.global.verifications[key]._found.toLowerCase() == $scope.found_list[i].toLowerCase()){
                                            $scope.jsonData.data.global.verifications[key]._found = $scope.found_list[i];
                                            break;
                                        }
                                    }

                                    if(!$scope.jsonData.data.global.verifications[key].hasOwnProperty("_search")){
                                        $scope.jsonData.data.global.verifications[key]._search = "";
                                    }
                                    if(!$scope.jsonData.data.global.verifications[key].hasOwnProperty("_verify_on")){
                                        $scope.jsonData.data.global.verifications[key]._verify_on = "";
                                    }
                                    $scope.cp_verification_tag_attributes.push($scope.jsonData.data.global.verifications[key]);
                                    $scope.showGlobalVerificationTags = false;
                                    $scope.individualCPVerificationTag.push(false);
                                }
                            }
                        }

                        //Testdata Tag validation

                        $scope.copy_entire_td_list = [];

                        if(!$scope.jsonData.data.hasOwnProperty("testdata")){
                            $scope.jsonData.data.testdata = [];
                        }
                        else if(!$scope.jsonData.data.testdata.hasOwnProperty(length)){
                            if($scope.jsonData.data.testdata !== ""){
                                $scope.jsonData.data.testdata = [$scope.jsonData.data.testdata];
                            }
                            else{
                                $scope.jsonData.data.testdata = [];
                            }
                        }

                        //Testdata blocks validation

                        for(var i=0; i<$scope.jsonData.data.testdata.length; i++){
                            $scope.copy_entire_td_list.push([]);
                            if(!$scope.jsonData.data.testdata[i].hasOwnProperty("_title")){
                                $scope.jsonData.data.testdata[i]._title = "";
                            }
                            if(!$scope.jsonData.data.testdata[i].hasOwnProperty("_row")){
                                $scope.jsonData.data.testdata[i]._row = "";
                            }
                            if(!$scope.jsonData.data.testdata[i].hasOwnProperty("_execute")){
                                $scope.jsonData.data.testdata[i]._execute = "y";
                            }

                            for(j=0; j<$scope.execute_list.length; j++){
                                if($scope.jsonData.data.testdata[i]._execute.toLowerCase() == $scope.execute_list[j].toLowerCase()){
                                    $scope.jsonData.data.testdata[i]._execute = $scope.execute_list[j];
                                    break;
                                }
                            }

                            if(!$scope.jsonData.data.testdata[i].hasOwnProperty("_monitor")){
                                $scope.jsonData.data.testdata[i]._monitor = "";
                            }
                            if(!$scope.jsonData.data.testdata[i].hasOwnProperty("_iter_type")){
                                $scope.jsonData.data.testdata[i]._iter_type = "per_cmd";
                            }

                            for(j=0; j<$scope.iter_type_list.length; j++){
                                if($scope.jsonData.data.testdata[i]._iter_type.toLowerCase() == $scope.iter_type_list[j].toLowerCase()){
                                    $scope.jsonData.data.testdata[i]._iter_type = $scope.iter_type_list[j];
                                    break;
                                }
                            }

                            if(!$scope.jsonData.data.testdata[i].hasOwnProperty("command")){
                                $scope.jsonData.data.testdata[i].command = [];
                            }
                            if(!$scope.jsonData.data.testdata[i].command.hasOwnProperty(length)){
                                $scope.jsonData.data.testdata[i].command = [$scope.jsonData.data.testdata[i].command];
                                $scope.showTDCommandTags.push(false);
                                $scope.individualTDCommandTag.push([]);
                            }
                            else{
                                $scope.showTDCommandTags.push(false);
                                $scope.individualTDCommandTag.push([]);
                            }

                            //Command Tags validation

                            for(var j=0; j<$scope.jsonData.data.testdata[i].command.length; j++){
                                $scope.individualTDCommandTag[i].push(false);
                                if(!$scope.jsonData.data.testdata[i].command[j].hasOwnProperty("_send")){
                                    $scope.jsonData.data.testdata[i].command[j]._send = "";
                                }
                                if(!$scope.jsonData.data.testdata[i].command[j].hasOwnProperty("_sys")){
                                    $scope.jsonData.data.testdata[i].command[j]._sys = "";
                                }
                                if(!$scope.jsonData.data.testdata[i].command[j].hasOwnProperty("_session")){
                                    $scope.jsonData.data.testdata[i].command[j]._session = "";
                                }
                                if(!$scope.jsonData.data.testdata[i].command[j].hasOwnProperty("_start")){
                                    $scope.jsonData.data.testdata[i].command[j]._start = "";
                                }
                                if(!$scope.jsonData.data.testdata[i].command[j].hasOwnProperty("_end")){
                                    $scope.jsonData.data.testdata[i].command[j]._end = "";
                                }
                                if(!$scope.jsonData.data.testdata[i].command[j].hasOwnProperty("_timeout")){
                                    $scope.jsonData.data.testdata[i].command[j]._timeout = "60";
                                }
                                if(!$scope.jsonData.data.testdata[i].command[j].hasOwnProperty("_sleep")){
                                    $scope.jsonData.data.testdata[i].command[j]._sleep = "0";
                                }
                                if(!$scope.jsonData.data.testdata[i].command[j].hasOwnProperty("_verify")){
                                    $scope.jsonData.data.testdata[i].command[j]._verify = "";
                                }
                                if(!$scope.jsonData.data.testdata[i].command[j].hasOwnProperty("_retry")){
                                    $scope.jsonData.data.testdata[i].command[j]._retry = "n";
                                }

                                for(var k=0; k<$scope.retry_list.length; k++){
                                    if($scope.jsonData.data.testdata[i].command[j]._retry.toLowerCase() == $scope.retry_list[k].toLowerCase()){
                                        $scope.jsonData.data.testdata[i].command[j]._retry = $scope.retry_list[k];
                                        break;
                                    }
                                }

                                if(!$scope.jsonData.data.testdata[i].command[j].hasOwnProperty("_retry_timer")){
                                    $scope.jsonData.data.testdata[i].command[j]._retry_timer = "60";
                                }
                                if(!$scope.jsonData.data.testdata[i].command[j].hasOwnProperty("_retry_count")){
                                    $scope.jsonData.data.testdata[i].command[j]._retry_count = "5";
                                }
                                if(!$scope.jsonData.data.testdata[i].command[j].hasOwnProperty("_retry_onmatch")){
                                    $scope.jsonData.data.testdata[i].command[j]._retry_onmatch = "";
                                }
                                if(!$scope.jsonData.data.testdata[i].command[j].hasOwnProperty("_resp_req")){
                                    $scope.jsonData.data.testdata[i].command[j]._resp_req = "";
                                }

                                for(k=0; k<$scope.resp_req_list.length; k++){
                                    if($scope.jsonData.data.testdata[i].command[j]._resp_req.toLowerCase() == $scope.resp_req_list[k].toLowerCase()){
                                        $scope.jsonData.data.testdata[i].command[j]._resp_req = $scope.resp_req_list[k];
                                        break;
                                    }
                                }

                                if(!$scope.jsonData.data.testdata[i].command[j].hasOwnProperty("_resp_pat_req")){
                                    $scope.jsonData.data.testdata[i].command[j]._resp_pat_req = "";
                                }
                                if(!$scope.jsonData.data.testdata[i].command[j].hasOwnProperty("_resp_ref")){
                                    $scope.jsonData.data.testdata[i].command[j]._resp_ref = j+1;
                                }
                                if(!$scope.jsonData.data.testdata[i].command[j].hasOwnProperty("_monitor")){
                                    $scope.jsonData.data.testdata[i].command[j]._monitor = "";
                                }
                                if(!$scope.jsonData.data.testdata[i].command[j].hasOwnProperty("_inorder")){
                                    $scope.jsonData.data.testdata[i].command[j]._inorder = "";
                                }

                                for(k=0; k<$scope.inorder_list.length; k++){
                                    if($scope.jsonData.data.testdata[i].command[j]._inorder.toLowerCase() == $scope.inorder_list[k].toLowerCase()){
                                        $scope.jsonData.data.testdata[i].command[j]._inorder = $scope.inorder_list[k];
                                        break;
                                    }
                                }

                                if(!$scope.jsonData.data.testdata[i].command[j].hasOwnProperty("_repeat")){
                                    $scope.jsonData.data.testdata[i].command[j]._repeat = "";
                                }

                                for(k=0; k<$scope.repeat_list.length; k++){
                                    if($scope.jsonData.data.testdata[i].command[j]._repeat.toLowerCase() == $scope.repeat_list[k].toLowerCase()){
                                        $scope.jsonData.data.testdata[i].command[j]._repeat = $scope.repeat_list[k];
                                        break;
                                    }
                                }

                            }

                            $scope.td_verification_tag_names.push([]);
                            $scope.td_verification_tag_attributes.push([]);
                            $scope.showTDVerificationTags.push(true);
                            $scope.individualTDVerificationTag.push([]);
                            for(key in $scope.jsonData.data.testdata[i]){
                                if(key !== "_title" &&
                                    key !== "_row" &&
                                    key !== "_execute" &&
                                    key !== "_monitor" &&
                                    key !== "_iter_type" &&
                                    key !== "command"){
                                    if($scope.jsonData.data.testdata[i].hasOwnProperty(key)){
                                        $scope.individualTDVerificationTag[i].push(false);
                                        $scope.showTDVerificationTags[$scope.showTDVerificationTags.length - 1] = false;
                                        $scope.td_verification_tag_names[i].push(key);
                                        if(!$scope.jsonData.data.testdata[i][key].hasOwnProperty("_found")){
                                            $scope.jsonData.data.testdata[i][key]._found = "y";
                                        }

                                        for(j=0; j<$scope.found_list.length; j++){
                                            if($scope.jsonData.data.testdata[i][key]._found.toLowerCase() == $scope.found_list[j].toLowerCase()){
                                                $scope.jsonData.data.testdata[i][key]._found = $scope.found_list[j];
                                                break;
                                            }
                                        }

                                        if(!$scope.jsonData.data.testdata[i][key].hasOwnProperty("_search")){
                                            $scope.jsonData.data.testdata[i][key]._search = "";
                                        }
                                        if(!$scope.jsonData.data.testdata[i][key].hasOwnProperty("_verify_on")){
                                            $scope.jsonData.data.testdata[i][key]._verify_on = "";
                                        }
                                        $scope.td_verification_tag_attributes[i].push($scope.jsonData.data.testdata[i][key]);
                                    }
                                }
                            }

                            if($scope.individualTDVerificationTag[i] == []){
                                //$scope.individualTDVerificationTag.pop();
                                //$scope.showTDVerificationTags.pop();
                            }

                        }

                        if($scope.jsonData.data.testdata.hasOwnProperty(length)){
                            for(i=0; i<$scope.jsonData.data.testdata.length; i++){
                                $scope.copy_entire_td_list[i] = [];
                                for(j=0; j<$scope.jsonData.data.testdata.length; j++){
                                    if(j !== i){
                                        $scope.copy_entire_td_list[i].push(j+1);
                                    }
                                }
                            }
                        }
                    }
								wizardAPI && wizardAPI.init();
                },
                    function (msg) {
                        alert(msg);
                    }
                );
        }

        $scope.copyEntireTestdata = function(index, copy_index){

            if($scope.showTDCommandTags[parseInt(copy_index)-1]){
                $scope.showTDCommandTags[index] = true;
            }
            else{
                $scope.showTDCommandTags[index] = false;
            }

            for(var i=0; i<$scope.individualTDCommandTag[parseInt(copy_index)-1].length; i++){
                if($scope.individualTDCommandTag[parseInt(copy_index)-1][i]){
                    $scope.individualTDCommandTag[index][i] = true;
                }
                else{
                    $scope.individualTDCommandTag[index][i] = false;
                }
            }

            if($scope.showTDVerificationTags[parseInt(copy_index)-1]){
                $scope.showTDVerificationTags[index] = true;
            }
            else{
                $scope.showTDVerificationTags[index] = false;
            }

            for(i=0; i<$scope.individualTDVerificationTag[parseInt(copy_index)-1].length; i++){
                if($scope.individualTDVerificationTag[parseInt(copy_index)-1][i]){
                    $scope.individualTDVerificationTag[index][i] = true;
                }
                else{
                    $scope.individualTDVerificationTag[index][i] = false;
                }
            }

            for(var key in $scope.jsonData.data.testdata[parseInt(copy_index)-1]){
                if($scope.jsonData.data.testdata[parseInt(copy_index)-1].hasOwnProperty(key)){
                    if(key === "_title" ||
                        key === "_row" ||
                        key === "_execute" ||
                        key === "_monitor" ||
                        key === "_iter_type"){
                        $scope.jsonData.data.testdata[index][key] = $scope.jsonData.data.testdata[parseInt(copy_index)-1][key]
                    }
                    else if(key === "command"){
                        $scope.jsonData.data.testdata[index].command = [];
                        for(i=0; i<$scope.jsonData.data.testdata[parseInt(copy_index)-1].command.length; i++){
                            $scope.jsonData.data.testdata[index].command.push({});
                            for(var command_key in $scope.jsonData.data.testdata[parseInt(copy_index)-1].command[i]){
                                if($scope.jsonData.data.testdata[parseInt(copy_index)-1].command[i].hasOwnProperty(command_key)){
                                    $scope.jsonData.data.testdata[index].command[i][command_key] = $scope.jsonData.data.testdata[parseInt(copy_index)-1].command[i][command_key];
                                }
                            }
                        }
                    }
                }
            }

            $scope.td_verification_tag_names[index] = [];
            $scope.td_verification_tag_attributes[index] = [];
            for(i=0; i<$scope.td_verification_tag_names[parseInt(copy_index)-1].length; i++){
                $scope.td_verification_tag_names[index].push($scope.td_verification_tag_names[parseInt(copy_index)-1][i]);
                for(key in $scope.td_verification_tag_attributes[parseInt(copy_index)-1]){
                    if($scope.td_verification_tag_attributes[parseInt(copy_index)-1].hasOwnProperty(key)){
                        $scope.td_verification_tag_attributes[index][key] = $scope.td_verification_tag_attributes[parseInt(copy_index)-1][key];
                    }
                }
            }

        };

        $scope.copyGlobalComboTags = function(index, copy_index){
            for(var key in $scope.cp_combo_tag_attributes[parseInt(copy_index)-1]){
                if($scope.cp_combo_tag_attributes[parseInt(copy_index)-1].hasOwnProperty(key)){
                    $scope.cp_combo_tag_attributes[index][key] = $scope.cp_combo_tag_attributes[parseInt(copy_index)-1][key]
                }
            }
        };

        $scope.copyGlobalVerifyTags = function(index, copy_index){
            for(var key in $scope.cp_verification_tag_attributes[parseInt(copy_index)-1]){
                if($scope.cp_verification_tag_attributes[parseInt(copy_index)-1].hasOwnProperty(key)){
                    $scope.cp_verification_tag_attributes[index][key] = $scope.cp_verification_tag_attributes[parseInt(copy_index)-1][key]
                }
            }
        };

        $scope.copyTDCommandTags = function(parent_index, index, copy_index){
            for(var key in $scope.jsonData.data.testdata[parent_index].command[parseInt(copy_index)-1]){
                if($scope.jsonData.data.testdata[parent_index].command[parseInt(copy_index)-1].hasOwnProperty(key)){
                    $scope.jsonData.data.testdata[parent_index].command[index][key] = $scope.jsonData.data.testdata[parent_index].command[parseInt(copy_index)-1][key]
                }
            }
        };

        $scope.copyTDVerifyTags = function(parent_index, index, copy_index){
            for(var key in $scope.td_verification_tag_attributes[parent_index][parseInt(copy_index)-1]){
                if($scope.td_verification_tag_attributes[parent_index][parseInt(copy_index)-1].hasOwnProperty(key)){
                    $scope.td_verification_tag_attributes[parent_index][index][key] = $scope.td_verification_tag_attributes[parent_index][parseInt(copy_index)-1][key];
                }
            }
        };

    }
]);
