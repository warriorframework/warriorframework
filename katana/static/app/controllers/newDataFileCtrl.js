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

/**
 * Created by SKULKARN on 6/23/2016.
 */

/**
 * Reference JSON
 * [{
 *      "system":[{
 *              "_name": "",
 *              "tag1": {
 *                      "child_tag_1": "value"
 *                      },
 *              "tag2": "a",
 *              "tag3": "n"},
 *          {
 *              "_name": "yoyo",
 *              "subsystem":[{
 *                      "_name": "ssys1",
 *                      "tag1": "ff",
 *                      "tag2": "gg"
 *                  },
 *                  {
 *                      "_name": "ssys2",
 *                      "tag1": "ff",
 *                      "tag2": "gg"
 *                  }]
 *          }]
 *  }]
 *
 * **/


app.controller('newDataFileCtrl', ['$scope', '$http', '$controller', '$location', '$route', 'saveNewDataFileFactory', 'DataFileFactory', 'fileFactory', 'subdirs',
    function($scope, $http, $controller, $location, $route, saveNewDataFileFactory, DataFileFactory, fileFactory, subdirs) {

        $scope.subdirs = "none";
        $scope.idfTooltips = {};
        $scope.xmlData = "";
        $scope.df_name = "";
        $scope.final_json = [];
        $scope.system_info = [""];
        $scope.tag_info = [[[undefined, undefined]]];
        $scope.buffer_tag_info = [[[undefined, undefined]]];
        $scope.subsys_info = [[[[undefined, undefined]]]];
        $scope.buffer_subsys_info = [[[[undefined, undefined]]]];
        $scope.subsys_name_list = [[undefined]];
        $scope.buffer_subsys_name_list = [[undefined]];
        $scope.defSystem = -1;
        $scope.description = "";
        $scope.tag_name_list = [];
        $scope.showCopyTags = false;
        $scope.showCopySubsysTags = false;
        $scope.sysListForTagCopying = [];
        $scope.subsysListForTagCopying = [];
        $scope.selectedSystem = [];
        $scope.selectedSubsystem = [];
        $scope.temp_model = [];
        $scope.selectedSystemForTagsList = [];
        $scope.saveSystemList = [false];
        $scope.saveSubsysList = [[false]];
        $scope.buffer_saveSubsysList = [[false]];
        $scope.savedSystemTable = false;
        $scope.savedSystemList = [false];
        $scope.showSavedSubsystem = [false];
        $scope.showSpecificSubsys = [[false]];
        $scope.defSystemList = [false];
        $scope.defSubsystemList = [[false]];
        $scope.showTagChildren = [[false]];
        $scope.childTagsList = [[[[undefined, undefined]]]];
        $scope.subsysEditorIsOpen = false;
        $scope.subsysBeingEdited = "None";

        $scope.editSubsystem = function(parent_index, index){
            if($scope.subsysEditorIsOpen){
                swal({
                    title: "A Subsystem is already open in the Editor. Please save that subsystem before editing a new one.",
                    type: "warning",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
                return
            }
            var flag = false;
            $scope.showSpecificSubsys[parent_index][index] = false;
            $scope.subsysEditorIsOpen = true;
            $scope.subsysBeingEdited = index;
            for(var i=0; i<$scope.showSpecificSubsys[parent_index].length; i++){
                if($scope.showSpecificSubsys[parent_index][i] == true){
                    flag = true;
                    break;
                }
            }
            if(!flag){
                $scope.showSavedSubsystem[parent_index] = false;
            }
        };

        $scope.editSystem = function(index){
            if($scope.systemEditorIsOpen){
                swal({
                    title: "There is a System currently open in the Editor. Please save that System before editing a new one.",
                    type: "warning",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
                return;
            }
            $scope.systemEditorIsOpen = true;
            $scope.systemBeingEdited = index;
            var flag = false;
            $scope.savedSystemList[index] = false;
            for(var i=0; i<$scope.savedSystemList.length; i++){
                if($scope.savedSystemList[i] == true){
                    flag = true;
                    break;
                }
            }
            if(!flag){
                $scope.savedSystemTable = false;
            }
        };

        $scope.updateSelectedSystemForTags = function(selectedSysForTags, index){
            $scope.selectedSystemForTagsList[index] = selectedSysForTags;
        };

        $scope.copyOverTagsFromSystem = function(current_index){
            if($scope.selectedSystemForTagsList[current_index] !== ""){
                var previous_index = parseInt($scope.selectedSystemForTagsList[current_index])-1;
                $scope.tag_info[current_index] = [];
                $scope.buffer_tag_info[current_index] = [];
                for (var i = 0; i < $scope.tag_info[previous_index].length; i++) {
                    $scope.tag_info[current_index].push([]);
                    $scope.buffer_tag_info[current_index].push([]);
                    for (var j = 0; j < $scope.tag_info[previous_index][i].length; j++) {
                        $scope.tag_info[current_index][i].push($scope.tag_info[previous_index][i][j]);
                        $scope.buffer_tag_info[current_index][i].push($scope.tag_info[previous_index][i][j]);
                    }
                }

                $scope.childTagsList[current_index] = [];
                $scope.showTagChildren[current_index] = [];
                for (i = 0; i < $scope.childTagsList[previous_index].length; i++) {
                    $scope.showTagChildren[current_index].push($scope.showTagChildren[previous_index][i]);
                    $scope.childTagsList[current_index].push([]);
                    for (j = 0; j < $scope.childTagsList[previous_index][i].length; j++) {
                        $scope.childTagsList[current_index][i].push([]);
                        for(var k = 0; k < $scope.childTagsList[previous_index][i][j].length; k++){
                            $scope.childTagsList[current_index][i][j].push($scope.childTagsList[previous_index][i][j][k])
                        }
                    }
                }

                initializeCopyLists();
            }
            disableTagTab(current_index);
        };

        $scope.copyOverTagsFromSubSystem = function(current_parent_index, current_index){
            if($scope.selectedSubsystem[current_parent_index][current_index] !== ""){
                var previous_parent_index = $scope.selectedSystem[current_parent_index][current_index];
                var previous_index = $scope.selectedSubsystem[current_parent_index][current_index];

                $scope.subsys_info[current_parent_index][current_index] = [];
                $scope.buffer_subsys_info[current_parent_index][current_index] = [];
                for (var i = 0; i < $scope.subsys_info[previous_parent_index][previous_index].length; i++) {
                    $scope.subsys_info[current_parent_index][current_index].push([]);
                    $scope.buffer_subsys_info[current_parent_index][current_index].push([]);
                    for (var j = 0; j < $scope.subsys_info[previous_parent_index][previous_index][i].length; j++) {
                        $scope.subsys_info[current_parent_index][current_index][i].push($scope.subsys_info[previous_parent_index][previous_index][i][j]);
                        $scope.buffer_subsys_info[current_parent_index][current_index][i].push($scope.subsys_info[previous_parent_index][previous_index][i][j])
                    }
                }
                initializeCopyLists();
            }
            disableSubsysTab(current_parent_index);
        };

        $scope.updateSelectedSystem = function(selectedSystem, parent_index, index){
            $scope.selectedSystem[parent_index][index] = parseInt(selectedSystem)-1;
            if(parseInt(selectedSystem) === parseInt(parent_index)+1){
                $scope.temp_model[parent_index][index] = [];
                for(var i=0; i<$scope.subsysListForTagCopying[$scope.selectedSystem[parent_index][index]].length; i++){
                    if($scope.subsysListForTagCopying[$scope.selectedSystem[parent_index][index]][i] !== (parseInt(index)+1).toString()){
                        $scope.temp_model[parent_index][index].push($scope.subsysListForTagCopying[$scope.selectedSystem[parent_index][index]][i]);
                    }
                }
            }
            else{
                $scope.temp_model[parent_index][index] = [];
                for(i=0; i<$scope.subsysListForTagCopying[$scope.selectedSystem[parent_index][index]].length; i++){
                    $scope.temp_model[parent_index][index].push($scope.subsysListForTagCopying[$scope.selectedSystem[parent_index][index]][i]);
                }
            }
        };

        $scope.updateSelectedSubsystem = function(selectedSubsystem, parent_index, index){
            $scope.selectedSubsystem[parent_index][index] = parseInt(selectedSubsystem)-1;
        };

        function initializeCopyLists(check, switched_tab_index, event){
            if(check === undefined){
                check = false;
            }
            if(switched_tab_index === undefined){
                switched_tab_index = false;
            }
            $scope.sysListForTagCopying = [];
            $scope.subsysListForTagCopying = [];
            $scope.selectedSystem = [];
            $scope.selectedSubsystem = [];
            $scope.temp_model = [];
            $scope.selectedSystemForTagsList = [];
            var temp_tag_list = [];
            var flag = false;
            var temp_buffer = [""];
            if($scope.system_info.length === 1 && event === undefined){
                $scope.showCopyTags = false;
            }
            else{
                if(event !== undefined){
                    var counter = 0;
                    for(var i=0; i<$scope.system_info.length; i++){
                        if(document.getElementById("a_subsys_tab" + i) !== null &&
                            document.getElementById("a_subsys_tab" + i).getAttribute("aria-expanded") == "true"){
                            counter += 1;
                            if(event == true){
                                counter += 1;
                            }
                        }
                        else if(event.target.id === ("a_subsys_tab" + i)){
                            counter += 1;
                        }
                        else if(event !== true && event.target.id === ("a_tag_tab" + i)){
                            counter -= 1;
                        }
                        if(counter > 1){
                            $scope.showCopySubsysTags = true;
                            break;
                        }
                    }
                    counter = 0;
                    for(i=0; i<$scope.system_info.length; i++) {
                        if (event.target.id === ("a_tag_tab" + i)) {
                            counter += 1;
                        }
                        else if(event.target.id === ("a_subsys_tab" + i)){
                            counter -= 1;
                        }
                        else if (document.getElementById("a_tag_tab" + i) !== null &&
                            document.getElementById("a_tag_tab" + i).getAttribute("aria-expanded") == "true") {
                            counter += 1;
                        }
                        if (counter > 1) {
                            $scope.showCopyTags = true;
                            break;
                        }
                    }
                }
                for(i=0; i<$scope.tag_info.length; i++){
                    for(var j=0; j<$scope.tag_info[i].length; j++){
                        if($scope.tag_info[i][j][0] !== undefined || $scope.tag_info[i][j][1] !== undefined){
                            temp_tag_list.push((i+1).toString());
                            flag =true;
                            break;
                        }
                        else if(switched_tab_index == i){
                            if(check){
                                if(document.getElementById("a_subsys_tab" + switched_tab_index) !== null &&
                                    document.getElementById("a_subsys_tab" + switched_tab_index).getAttribute("aria-expanded") == "true") {
                                    temp_tag_list.push((i+1).toString());
                                    flag =true;
                                    break;
                                }
                            }
                        }
                        else{
                            if(document.getElementById("a_tag_tab" + i) !== null &&
                                document.getElementById("a_tag_tab" + i).getAttribute("aria-expanded") == "true") {
                                temp_tag_list.push((i+1).toString());
                                flag =true;
                                break;
                            }
                        }
                    }
                    if(!flag){
                        temp_tag_list.push(undefined);
                    }
                    else{
                        flag = false;
                    }
                }
                for(i=0; i<$scope.system_info.length; i++){
                    for(j=0; j<$scope.system_info.length; j++){
                        if(temp_tag_list[j] !== undefined && temp_tag_list[j] !== (i+1).toString()){
                            temp_buffer.push(temp_tag_list[j])
                        }
                    }
                    $scope.sysListForTagCopying.push([]);
                    for(j=0; j<temp_buffer.length; j++){
                        $scope.sysListForTagCopying[i].push(temp_buffer[j]);
                    }
                    temp_buffer = [""];
                }

                temp_tag_list = [];
                flag = false;
                temp_buffer = [""];
                for(i=0; i<$scope.subsys_name_list.length; i++){
                    for(j=0; j<$scope.subsys_name_list[i].length; j++){
                        if($scope.subsys_name_list[i][j] !== undefined) {
                            temp_tag_list.push((i + 1).toString());
                            flag = true;
                            break;
                        }
                        else if(switched_tab_index == i){
                            if(check){
                                if(document.getElementById("a_tag_tab" + switched_tab_index) !== null &&
                                    document.getElementById("a_tag_tab" + switched_tab_index).getAttribute("aria-expanded") == "true") {
                                    temp_tag_list.push((i + 1).toString());
                                    flag = true;
                                    break;
                                }
                            }
                        }
                        else{
                            if(document.getElementById("a_subsys_tab" + i) !== null &&
                                document.getElementById("a_subsys_tab" + i).getAttribute("aria-expanded") == "true"){
                                temp_tag_list.push((i + 1).toString());
                                flag = true;
                                break;
                            }
                        }
                    }
                    if(!flag){
                        temp_tag_list.push(undefined);
                    }
                    else{
                        flag = false;
                    }
                }
                for(i=0; i<$scope.system_info.length; i++){
                    for(j=0; j<$scope.system_info.length; j++){
                        if(temp_tag_list[j] !== undefined){
                            temp_buffer.push(temp_tag_list[j]);
                        }
                    }
                        if(temp_tag_list[i] !== undefined){
                            $scope.sysListForTagCopying[temp_tag_list[i]-1] = [];
                            for(var k=0; k<temp_buffer.length; k++){
                                $scope.sysListForTagCopying[temp_tag_list[i]-1].push(temp_buffer[k]);
                            }
                        }
                    temp_buffer = [""];
                }
            }

            for(i=0; i<$scope.sysListForTagCopying.length; i++){
                $scope.selectedSystem.push([]);
                $scope.selectedSubsystem.push([]);
                $scope.temp_model.push([]);
                $scope.subsysListForTagCopying.push([]);
                $scope.selectedSystemForTagsList.push("");
                for(j=0; j<$scope.subsys_name_list[i].length; j++){
                    $scope.selectedSystem[i].push("");
                    $scope.selectedSubsystem[i].push("");
                    $scope.temp_model[i].push([]);
                }
                if($scope.subsys_name_list[i][0] === undefined && $scope.subsys_name_list[i].length == 1){
                    $scope.subsysListForTagCopying[i].push(undefined);
                }
                    else if($scope.subsys_name_list[i] === [undefined]){
                    $scope.subsysListForTagCopying[i].push(undefined);
                }
                else{
                    $scope.subsysListForTagCopying[i].push("");
                    for(j=0; j<$scope.subsys_name_list[i].length; j++){
                        $scope.subsysListForTagCopying[i].push((j+1).toString());
                    }
                }
            }
        }

        $scope.toggleChildren = function(parent_index, index) {
            $scope.showTagChildren[parent_index][index] = !$scope.showTagChildren[parent_index][index];
            disableTagTab(parent_index)
        };

        $scope.deleteChildTag = function(grandpa_index, parent_index, index){
            sweetAlert({
                title: "Are you sure you want to delete this tag?",
                closeOnConfirm: false,
                closeOnCancel: false,
                confirmButtonColor: '#3b3131',
                confirmButtonText: "Yes!",
                showCancelButton: true,
                cancelButtonText: "Nope.",
                type: "warning"
            },
                function(isConfirm){
                    if (isConfirm) {
                        $scope.$apply(deleteThisChildTag(grandpa_index, parent_index, index));
                    }
                    else {
                        sweetAlert({
                            title: "Child Tag not deleted.",
                            showConfirmButton: false,
                            type: "error",
                            timer: 1250
                        });
                        return false;
                    }
                });
        };

        function deleteThisChildTag(grandpa_index, parent_index, index){
            if($scope.childTagsList[grandpa_index][parent_index].length == 1){
                $scope.childTagsList[grandpa_index][parent_index][index] = [undefined, undefined];
                $scope.toggleChildren(grandpa_index, parent_index)
            }
            else{
                $scope.childTagsList[grandpa_index][parent_index].splice(index, 1);
            }
            sweetAlert({
                title: "Child Tag deleted.",
                showConfirmButton: false,
                type: "success",
                timer: 1250
            });
        }

        $scope.addAnotherChild = function(parent_index, index){
            $scope.childTagsList[parent_index][index].push([undefined, undefined]);
        };

        $scope.deleteAllChildTags = function(parent_index, index){
            $scope.childTagsList[parent_index][index] = [[undefined, undefined]];
            $scope.toggleChildren(parent_index, index);
        };

        fileFactory.readdeftagsfile()
                    .then(
                        function(data) {
                            $scope.default_tags_list = new Bloodhound({
                                datumTokenizer: Bloodhound.tokenizers.obj.whitespace('tag'),
                                queryTokenizer: Bloodhound.tokenizers.whitespace,
                                identify: function(obj) { return obj.tag; },
                                local: data["defaults"]
                            });

                            for(var i=0; i<$scope.default_tags_list.local.length; i++){
                                $scope.tag_name_list.push($scope.default_tags_list.local[i]["tag"]);
                            }
                        },
                        function(data) {
                            alert(data);
                        });

        function verify_mandatory_fields() {
            var check = true;
            if($scope.df_name == ""){
                swal({
                    title: "DataFile name cannot be empty!",
                    type: "error",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
                check = false;
            } else if($scope.system_info != []){
                for(var i=0; i<$scope.system_info.length; i++){
                    if($scope.system_info[i] == ""){
                        swal({
                            title: "System names cannot be left unfilled!",
                            text: "System name for system number " + (i+1) + " has been left empty.",
                            type: "error",
                            confirmButtonText: "Ok",
                            closeOnConfirm: true,
                            confirmButtonColor: '#3b3131'
                        });
                        check = false;
                        break
                    }
                }
                if(check){
                    for(i=0; i<$scope.system_info.length; i++){
                        for(var j=(i+1); j<$scope.system_info.length; j++){
                            if($scope.system_info[i] == $scope.system_info[j]){
                                swal({
                                    title: "System names haves to be unique!",
                                    text: "System " + (i+1) + " and System " + (j+1) + " have the same names!",
                                    type: "error",
                                    confirmButtonText: "Ok",
                                    closeOnConfirm: true,
                                    confirmButtonColor: '#3b3131'
                                });
                                check = false;
                                break
                            }
                            if(!check){
                                break
                            }
                        }
                    }
                }
            }
            return check
        }

        $scope.setAsDefault = function(index){
            for(var i=0; i<$scope.defSystemList.length; i++){
                if(i == index){
                    $scope.defSystemList[i] = true;
                    $scope.defSystem = i;
                }
                else{
                    $scope.defSystemList[i] = false;
                }
            }
        };

        $scope.setSubsysAsDefault = function(parent_index, index){
            for(var i=0; i<$scope.defSubsystemList[parent_index].length; i++){
                if(i == index){
                    $scope.defSubsystemList[parent_index][i] = true;
                }
                else{
                    $scope.defSubsystemList[parent_index][i] = false;
                }
            }
        };

        function updateBloodhound(x){
            if($scope.tag_name_list.indexOf(x) == -1){
                $scope.tag_name_list.push(x);
                $scope.tag_name_list.sort(); //quicksort in chrome, merge sort in firefox
                var temp_list = {"defaults": []};
                for(var i=0;i<$scope.tag_name_list.length; i++){
                    temp_list["defaults"].push({"tag": $scope.tag_name_list[i]})
                }
                var temp_str = JSON.stringify(temp_list);
                fileFactory.updatedeftagsfile(temp_str)
                    .then(
                        function(data) {
                            console.log(data);
                        },
                        function(data) {
                            alert(data);
                        });
                fileFactory.readdeftagsfile();
            }
        }

        function disableTagTab(parent_index){
            var flag = false;

            if($scope.tag_info[parent_index].length > 1){
                flag = true;
            }
            for(var i=0; i<$scope.tag_info[parent_index].length; i++){
                if($scope.showTagChildren[parent_index][i]){
                    flag = true;
                }
                for(var j=0; j<$scope.tag_info[parent_index][i].length; j++){
                    if($scope.tag_info[parent_index][i][j] !== undefined && $scope.tag_info[parent_index][i][j] !== ""){
                        flag = true;
                        break;
                    }
                }
                if(flag){
                    break;
                }
            }
            if(flag){
                var d = document.getElementById("li_subsys_tab"+parent_index);
                d.className = "thisclass";
            }
            else{
                d = document.getElementById("li_subsys_tab"+parent_index);
                d.className = "";
            }
        }

        function disableSubsysTab(parent_index){
            var flag = false;

            if($scope.subsys_name_list[parent_index].length > 1){
                flag = true;
            }

            if(!flag){
                if($scope.subsys_info[parent_index].length > 1){
                    flag = true;
                }
                else{
                    for(i=0; i<$scope.subsys_info[parent_index].length; i++){
                        if($scope.subsys_info[parent_index][i].length > 1){
                            flag = true;
                            break;
                        }
                    }
                }
            }

            if(!flag){
                for(var i=0; i<$scope.subsys_name_list[parent_index].length; i++){
                    if($scope.subsys_name_list[parent_index][i] !== undefined && $scope.subsys_name_list[parent_index][i] !== ""){
                        flag = true;
                        break;
                    }
                }
            }

            if(!flag){
                for(i=0; i<$scope.subsys_info[parent_index].length; i++){
                    for(var j=0; j<$scope.subsys_info[parent_index][i].length; j++){
                        for(var k=0; k<$scope.subsys_info[parent_index][i][j].length; k++){
                            if($scope.subsys_info[parent_index][i][j][k] !== undefined && $scope.subsys_info[parent_index][i][j][k] !== ""){
                                flag = true;
                                break;
                            }
                        }
                        if(flag){
                            break;
                        }
                    }
                    if(flag){
                        break;
                    }
                }
            }

            if(flag){
                var d = document.getElementById("li_tag_tab"+parent_index);
                d.className = "thisclass";
            }
            else{
                d = document.getElementById("li_tag_tab"+parent_index);
                d.className = "";
            }
        }

        $scope.updateModel = function(grandpa_index, parent_index, index, identifier){
            if(identifier === 'tag'){
                var x = document.getElementById("tag_name"+ parent_index + index).value;
                $scope.$apply($scope.tag_info[parent_index][index][0] = x);
                $scope.$apply($scope.buffer_tag_info[parent_index][index][0] = x);
                updateBloodhound(x);
                disableTagTab(parent_index);
            }
            else if(identifier === 'tagvalue'){
                x = document.getElementById("tag_value"+ parent_index + index).value;
                $scope.$apply($scope.tag_info[parent_index][index][1] = x);
                $scope.$apply($scope.buffer_tag_info[parent_index][index][1] = x);
                disableTagTab(parent_index);
            }
            initializeCopyLists()
        };

        $scope.updateSubsysTagValueModel = function(grandpa_index, parent_index, index){
            var x = document.getElementById("subsys_tag_value"+ grandpa_index + parent_index + index).value;
            $scope.$apply($scope.subsys_info[grandpa_index][parent_index][index][1] = x);
            $scope.$apply($scope.buffer_subsys_info[grandpa_index][parent_index][index][1] = x);
            disableSubsysTab(grandpa_index);
            initializeCopyLists()
        };

        $scope.updateSubsysTagNameModel = function(grandpa_index, parent_index, index){
            var x = document.getElementById("subsys_tag_name"+ grandpa_index + parent_index + index).value;
            $scope.$apply($scope.subsys_info[grandpa_index][parent_index][index][0] = x);
            $scope.$apply($scope.buffer_subsys_info[grandpa_index][parent_index][index][0] = x);
            updateBloodhound(x);
            disableSubsysTab(grandpa_index);
            initializeCopyLists()
        };

        $scope.updateSubsysNameModel = function(parent_index, index){
            var x = document.getElementById("ss_name"+ parent_index + index).value;
            $scope.$apply($scope.subsys_name_list[parent_index][index] = x);
            $scope.$apply($scope.buffer_subsys_name_list[parent_index][index] = x);
            disableSubsysTab(parent_index);
            initializeCopyLists()
        };

        $scope.updateChildTags = function(grandpa_index, parent_index, index, name_or_value){
            if(name_or_value == "child_tag_name"){
                var last_index = 0;
            }
            else {
                last_index = 1;
            }
            $scope.childTagsList[grandpa_index][parent_index][index][last_index] = document.getElementById(name_or_value + grandpa_index + parent_index + index).value;;
        };

        function save(filename){
            var finalJSON = {
                "systems": {
                    "description": $scope.description,
                    "system": $scope.final_json
                }
            };
            var x2js = new X2JS();
            var token = angular.toJson(finalJSON);
            var xmlObj = x2js.json2xml_str(JSON.parse(token));
            saveNewDataFileFactory.saveNew(filename, $scope.subdirs, xmlObj)
                .then(
                    function(data) {
                        console.log(data);
                        $location.path('/datafiles');
                    },
                    function(data) {
                        alert(data);
                    });
            sweetAlert({
                title: "File saved: " + filename,
                showConfirmButton: false,
                type: "success",
                timer: 1250
            });

        }

        $scope.setSystemInfo = function(identifier, index, event){
            if(identifier == "subsys"){
                $scope.resetTag(undefined, index, 'tag', "no", event);
            } else if (identifier == "tag") {
                $scope.resetTag(undefined, index, 'subsys', "no", event);
            }
        };

        $scope.insertAnotherSystem = function() {
            if($scope.systemEditorIsOpen){
                swal({
                    title: "There is a system currently open in the system Editor. Please save that System before creating a new system.",
                    type: "warning",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
                return;
            }
            $scope.systemEditorIsOpen = true;
            $scope.system_info.push("");
            $scope.savedSystemList.push(false);
            $scope.tag_info.push([[undefined, undefined]]);
            $scope.buffer_tag_info.push([[undefined, undefined]]);
            $scope.subsys_info.push([[[undefined, undefined]]]);
            $scope.showSpecificSubsys.push([false]);
            $scope.buffer_subsys_info.push([[[undefined, undefined]]]);
            $scope.subsys_name_list.push([undefined]);
            $scope.buffer_subsys_name_list.push([undefined]);
            $scope.showSavedSubsystem.push(false);
            $scope.saveSystemList.push(false);
            $scope.defSystemList.push(false);
            $scope.defSubsystemList.push([false]);
            $scope.childTagsList.push([[[undefined, undefined]]]);
            $scope.showTagChildren.push([false]);
            $scope.systemBeingEdited = $scope.system_info.length - 1;

            initializeCopyLists()
        };

        function readyJson(){
            var level1_list = [];

            for(var level1=0; level1<$scope.system_info.length; level1++){
                var flag = false;
                if($scope.defSystem === -1 && level1 === 0){
                    level1_list.push({"_name": $scope.system_info[level1], "_default": "yes"});
                } else if($scope.defSystem === -1 && level1 !== 0){
                    level1_list.push({"_name": $scope.system_info[level1]});
                } else if ($scope.defSystem !== -1 && $scope.defSystem === level1){
                    level1_list.push({"_name": $scope.system_info[level1], "_default": "yes"});
                } else if ($scope.defSystem !== -1 && $scope.defSystem !== level1){
                    level1_list.push({"_name": $scope.system_info[level1]});
                }

                for(var level2=0; level2<$scope.tag_info[level1].length; level2++){
                    for(var level3=0; level3<$scope.tag_info[level1][level2].length; level3++) {
                        if ($scope.tag_info[level1][level2][level3] !== undefined) {
                            flag = true;
                            break;
                        }
                    }
                }

                if(flag){
                    for(level2=0; level2<$scope.tag_info[level1].length; level2++){
                        for(level3=0; level3<$scope.tag_info[level1][level2].length; level3++){
                            if(level3 === 0){
                                if($scope.tag_info[level1][level2][level3] === undefined || $scope.tag_info[level1][level2][level3] === ""){
                                    swal({
                                        title: "Tag names cannot be empty.",
                                        text: "Tag number " + (level2+1) + " of system " + (level1+1) + " is emtpy.",
                                        type: "error",
                                        confirmButtonText: "Ok",
                                        closeOnConfirm: true,
                                        confirmButtonColor: '#3b3131'
                                    });
                                    return false;
                                }
                                    else {
                                    $scope.tag_info[level1][level2][level3] = $scope.tag_info[level1][level2][level3].trim();
                                    if($scope.tag_info[level1][level2][level3] === ""){
                                        swal({
                                            title: "Tag names cannot be empty.",
                                            text: "Tag number " + (level2+1) + " of system " + (level1+1) + " is emtpy.",
                                            type: "error",
                                            confirmButtonText: "Ok",
                                            closeOnConfirm: true,
                                            confirmButtonColor: '#3b3131'
                                        });
                                        return false;
                                    }
                                }

                                if($scope.tag_info[level1][level2][level3].indexOf(' ') >= 0){
                                    swal({
                                        title: "Tag names cannot have white spaces.",
                                        text: "Tag number " + (level2+1) + " of system " + (level1+1) + " has white spaces.",
                                        type: "error",
                                        confirmButtonText: "Ok",
                                        closeOnConfirm: true,
                                        confirmButtonColor: '#3b3131'
                                    });
                                    return false;
                                }
                                else if(!isNaN($scope.tag_info[level1][level2][level3][0])){
                                    swal({
                                        title: "Tag names cannot start with numbers.",
                                        text: "Tag number " + (level2+1) + " of system " + (level1+1) + " starts with a number.",
                                        type: "error",
                                        confirmButtonText: "Ok",
                                        closeOnConfirm: true,
                                        confirmButtonColor: '#3b3131'
                                    });
                                    return false;
                                }
                                else if($scope.tag_info[level1][level2][level3].match(/[^a-zA-Z 0-9\._\-]/i)){
                                    swal({
                                        title: "Tag names cannot contain special characters other than an underscore, period, and hyphen.",
                                        text: "Tag number " + (level2+1) + " of system " + (level1+1) + " contains special characters.",
                                        type: "error",
                                        confirmButtonText: "Ok",
                                        closeOnConfirm: true,
                                        confirmButtonColor: '#3b3131'
                                    });
                                    return false;
                                }
                            }
                            else {
                                if($scope.tag_info[level1][level2][level3] === undefined){
                                    $scope.tag_info[level1][level2][level3] = "";
                                    $scope.buffer_tag_info[level1][level2][level3] = "";
                                }
                            }
                        }
                        level1_list[level1][$scope.tag_info[level1][level2][0]] = $scope.tag_info[level1][level2][1]
                    }
                }
                else{
                    for(level2=0; level2<$scope.subsys_info[level1].length; level2++){
                        if($scope.subsys_name_list[level1][level2] === undefined){
                            for(level3=0; level3<$scope.subsys_info[level1][level2].length; level3++){
                                for(var level4=0; level4<$scope.subsys_info[level1][level2][level3].length; level4++){
                                    if ($scope.subsys_info[level1][level2][level3][level4] !== undefined){
                                        flag = true;
                                    }
                                }
                            }
                        }
                        else{
                            flag = true;
                            break;
                        }
                        if(flag){
                            break;
                        }
                    }
                    if(flag){
                        level1_list[level1]["subsystem"] = [];
                        for(level2=0; level2<$scope.subsys_info[level1].length; level2++){
                            if($scope.subsys_name_list[level1][level2] === undefined || $scope.subsys_name_list[level1][level2] === ""){
                                swal({
                                    title: "Subsystem names cannot be empty.",
                                    text: "Name for subsystem number " + (level2+1) + " of system " + (level1+1) + " is empty.",
                                    type: "error",
                                    confirmButtonText: "Ok",
                                    closeOnConfirm: true,
                                    confirmButtonColor: '#3b3131'
                                });
                                return false;
                            }
                            else {
                                //$scope.subsys_name_list[level1][level2] = $scope.subsys_name_list[level1][level2].trim();
                                if($scope.subsys_name_list[level1][level2] === ""){
                                    swal({
                                        title: "Subsystem names cannot be empty.",
                                        text: "Name for subsystem number " + (level2+1) + " of system " + (level1+1) + " is empty.",
                                        type: "error",
                                        confirmButtonText: "Ok",
                                        closeOnConfirm: true,
                                        confirmButtonColor: '#3b3131'
                                    });
                                    return false;
                                }
                            }
                            if($scope.defSubsystemList[level1][level2] == true){
                                level1_list[level1]["subsystem"].push({"_name": $scope.subsys_name_list[level1][level2], "_default": "yes"});
                            }
                            else{
                                level1_list[level1]["subsystem"].push({"_name": $scope.subsys_name_list[level1][level2]});
                            }
                            for(level3=0; level3<$scope.subsys_info[level1][level2].length; level3++){
                                for(level4=0; level4<$scope.subsys_info[level1][level2][level3].length; level4++){
                                    if(level4 === 0) {
                                        if ($scope.subsys_info[level1][level2][level3][level4] === undefined || $scope.subsys_info[level1][level2][level3][level4] === "") {
                                            swal({
                                                title: "Tag names cannot be empty.",
                                                text: "Tag number " + (level3 + 1) + " of subsystem " + (level2 + 1) + " in system " + (level1 + 1) + " is emtpy.",
                                                type: "error",
                                                confirmButtonText: "Ok",
                                                closeOnConfirm: true,
                                                confirmButtonColor: '#3b3131'
                                            });
                                            return false;
                                        }
                                        else {
                                            $scope.subsys_info[level1][level2][level3][level4] = $scope.subsys_info[level1][level2][level3][level4].trim();
                                            if ($scope.subsys_info[level1][level2][level3][level4] === "") {
                                                swal({
                                                    title: "Tag names cannot be empty.",
                                                    text: "Tag number " + (level3 + 1) + " of subsystem " + (level2 + 1) + " in system " + (level1 + 1) + " is emtpy.",
                                                    type: "error",
                                                    confirmButtonText: "Ok",
                                                    closeOnConfirm: true,
                                                    confirmButtonColor: '#3b3131'
                                                });
                                                return false;
                                            }
                                        }

                                        if ($scope.subsys_info[level1][level2][level3][level4].indexOf(' ') >= 0) {
                                            swal({
                                                title: "Tag names cannot have white spaces.",
                                                text: "Tag number " + (level3 + 1) + " of subsystem " + (level2 + 1) + " in system " + (level1 + 1) + " has white spaces.",
                                                type: "error",
                                                confirmButtonText: "Ok",
                                                closeOnConfirm: true,
                                                confirmButtonColor: '#3b3131'
                                            });
                                            return false;
                                        }
                                        else if (!isNaN($scope.subsys_info[level1][level2][level3][level4][0])) {
                                            swal({
                                                title: "Tag names cannot start with numbers.",
                                                text: "Tag number " + (level3 + 1) + " of subsystem " + (level2 + 1) + " in system " + (level1 + 1) + " starts with a number.",
                                                type: "error",
                                                confirmButtonText: "Ok",
                                                closeOnConfirm: true,
                                                confirmButtonColor: '#3b3131'
                                            });
                                            return false;
                                        }
                                        else if($scope.subsys_info[level1][level2][level3][level4].match(/[^a-zA-Z 0-9\._\-]/i)){
                                            swal({
                                                title: "Tag names cannot contain special characters other than an underscore, period, and hyphen.",
                                                text: "Tag number " + (level3 + 1) + " of subsystem " + (level2 + 1) + " in system " + (level1 + 1) + " contains special characters.",
                                                type: "error",
                                                confirmButtonText: "Ok",
                                                closeOnConfirm: true,
                                                confirmButtonColor: '#3b3131'
                                            });
                                            return false;
                                        }
                                    }
                                    else {
                                        if($scope.subsys_info[level1][level2][level3][level4] === undefined){
                                            $scope.subsys_info[level1][level2][level3][level4] = "";
                                             $scope.buffer_subsys_info[level1][level2][level3][level4] = "";
                                        }
                                    }
                                }
                                level1_list[level1]["subsystem"][level2][$scope.subsys_info[level1][level2][level3][0]] = $scope.subsys_info[level1][level2][level3][1]
                            }
                        }
                    }
                }
            }

            for(var index=0; index<$scope.showTagChildren.length; index++){
                for(var i=0; i<$scope.showTagChildren[index].length; i++){
                    if($scope.showTagChildren[index][i]){
                        for(var j=0; j<$scope.childTagsList[index][i].length; j++){
                            if($scope.childTagsList[index][i][j][0] === undefined ||
                                $scope.childTagsList[index][i][j][0] === "" ||
                                $scope.childTagsList[index][i][j][0].trim() === ""){
                                swal({
                                    title: "Child tag names cannot be empty.",
                                    text: "Child tag " + (j+1) + " of Tag " + (i+1) + " in System " + (index+1) + " is empty.",
                                    type: "error",
                                    confirmButtonText: "Ok",
                                    closeOnConfirm: true,
                                    confirmButtonColor: '#3b3131'
                                });
                                return false;
                            }
                            else if($scope.childTagsList[index][i][j][0].match(/^[0-9_]/)){
                                swal({
                                    title: "Tag names cannot start with a number.",
                                    text: "Child tag " + (j+1) + " of Tag " + (i+1) + " in System " + (index+1) + " starts with a number.",
                                    type: "error",
                                    confirmButtonText: "Ok",
                                    closeOnConfirm: true,
                                    confirmButtonColor: '#3b3131'
                                });
                                return false;
                            }
                            else if($scope.childTagsList[index][i][j][0].match(/[^a-zA-Z 0-9\._\-]/i)){
                                swal({
                                    title: "Tag names cannot contain special characters other than an underscore, period, and hyphen.",
                                    text: "Child tag " + (j+1) + " of Tag " + (i+1) + " in System " + (index+1) + " contains special characters.",
                                    type: "error",
                                    confirmButtonText: "Ok",
                                    closeOnConfirm: true,
                                    confirmButtonColor: '#3b3131'
                                });
                                return false;
                            }
                            else if($scope.childTagsList[index][i][j][0].indexOf(" ") !== -1){
                                swal({
                                    title: "Tag names cannot contain spaces.",
                                    text: "Child tag " + (j+1) + " of Tag " + (i+1) + " in System " + (index+1) + " contains spaces.",
                                    type: "error",
                                    confirmButtonText: "Ok",
                                    closeOnConfirm: true,
                                    confirmButtonColor: '#3b3131'
                                });
                                return false;
                            }
                        }
                    }
                }
            }

            for(var system_number=0; system_number<$scope.showTagChildren.length; system_number++){
                var temp_json = {};
                flag = false;
                for(var system_tag_number=0; system_tag_number<$scope.showTagChildren[system_number].length; system_tag_number++){
                    var another_temp_json = {};
                    if($scope.showTagChildren[system_number][system_tag_number]){
                        for(var child_tag_number=0; child_tag_number<$scope.childTagsList[system_number][system_tag_number].length; child_tag_number++){
                            flag = true;
                            another_temp_json[$scope.childTagsList[system_number][system_tag_number][child_tag_number][0]] = $scope.childTagsList[system_number][system_tag_number][child_tag_number][1]
                        }
                    }
                    if(flag){
                        if(temp_json.hasOwnProperty($scope.tag_info[system_number][system_tag_number][0])){
                            if(temp_json[$scope.tag_info[system_number][system_tag_number][0]] instanceof Array){

                            }
                            else{
                                temp_json[$scope.tag_info[system_number][system_tag_number][0]] = [temp_json[$scope.tag_info[system_number][system_tag_number][0]]]
                            }
                            temp_json[$scope.tag_info[system_number][system_tag_number][0]].push({});
                            for(var key in another_temp_json){
                                if(another_temp_json.hasOwnProperty(key)){
                                    temp_json[$scope.tag_info[system_number][system_tag_number][0]][temp_json[$scope.tag_info[system_number][system_tag_number][0]].length-1][key] = another_temp_json[key];
                                }
                            }
                        }
                        else{
                            temp_json[$scope.tag_info[system_number][system_tag_number][0]] = {};
                            for(key in another_temp_json){
                                if(another_temp_json.hasOwnProperty(key)){
                                    temp_json[$scope.tag_info[system_number][system_tag_number][0]][key] = another_temp_json[key]
                                }
                            }
                        }
                        flag = false;
                        for(key in temp_json){
                        if(temp_json.hasOwnProperty(key)){
                            var temp_str = JSON.stringify(temp_json[key]);
                            var temp_json_value = JSON.parse(temp_str);
                            level1_list[system_number][key] = temp_json_value;
                        }
                    }
                    }
                }
            }

            $scope.final_json = level1_list;
            return true;
        }

        $scope.saveDataFile = function() {
            var verification = verify_mandatory_fields();
            var check = false;
            if (verification) {
                check = readyJson();
            }
            if(check){
                var filename = $scope.df_name + ".xml";
                fileFactory.checkfileexistwithsubdir(filename, 'datafile', $scope.subdirs)
                    .then(
                        function(data) {
                            console.log(data);
                            var fileExist = data.response;
                            if (fileExist == 'yes') {
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
                                        save(filename);
                                    }
                                    else {
                                        return false;
                                    }
                                });

                            } else {
                                save(filename);
                            }
                        },
                        function(data) {
                            alert(data);
                        });
            }
        };

        $scope.cancelDataFile = function() {
            $location.path('/datafiles');
        };

        $scope.saveSubsys = function(parent_index, index){
            var check = true;
            if($scope.subsys_name_list[parent_index][index] === undefined ||
                $scope.subsys_name_list[parent_index][index] === "" ||
                $scope.subsys_name_list[parent_index][index].trim() === ""){
                check = false;
                swal({
                    title: "Subsystem name cannot be empty.",
                    type: "error",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
            }
            if(check){
                for(var i=0; i<$scope.subsys_info[parent_index][index].length; i++){
                    if($scope.subsys_info[parent_index][index][i][0] === undefined ||
                        $scope.subsys_info[parent_index][index][i][0] === "" ||
                        $scope.subsys_info[parent_index][index][i][0].trim() === ""){
                        check = false;
                        swal({
                            title: "Tag names cannot be empty.",
                            text: "Tag " + (i+1) + " name is empty.",
                            type: "error",
                            confirmButtonText: "Ok",
                            closeOnConfirm: true,
                            confirmButtonColor: '#3b3131'
                        });
                    }
                }
            }
            if(check){
                $scope.showSavedSubsystem[parent_index] = true;
                $scope.showSpecificSubsys[parent_index][index] = true;
                $scope.subsysEditorIsOpen = false;
                $scope.subsysBeingEdited = "None";
            }
        };

        $scope.addAnotherTag = function(parent_index, index, identifier){
            if(identifier === "tag"){
                $scope.tag_info[index].push(["", ""]);
                $scope.buffer_tag_info[index].push(["", ""]);
                $scope.showTagChildren[index].push(false);
                $scope.childTagsList[index].push([[undefined, undefined]]);

                var flag = $scope.subsys_name_list.length === $scope.buffer_subsys_name_list.length;
                if(flag){
                    for(var i=0; i<$scope.subsys_name_list.length; i++){
                        if($scope.subsys_name_list[i].length !== $scope.buffer_subsys_name_list[i].length){
                            flag = false;
                            break;
                        }
                        if(flag){
                            for(var j=0; j<$scope.subsys_name_list[i].length; j++){
                                if($scope.subsys_name_list[i][j] !== $scope.buffer_subsys_name_list[i][j]){
                                    flag = false;
                                    break;
                                }
                            }
                            if(!flag){
                                break;
                            }
                        }
                    }
                }
                if(flag){
                    $scope.buffer_subsys_name_list[index].push(undefined);
                }
                $scope.subsys_name_list[index].push(undefined);

                flag = $scope.subsys_info.length === $scope.buffer_subsys_info.length;
                if(flag){
                    for(i=0; i<$scope.subsys_info.length; i++){
                        if($scope.subsys_info[i].length !== $scope.buffer_subsys_info[i].length){
                            flag = false;
                            break;
                        }
                        if(flag){
                            for(j=0; j<$scope.subsys_info[i].length; j++){
                                if($scope.subsys_info[i][j].length !== $scope.buffer_subsys_info[i][j].length){
                                    flag = false;
                                    break;
                                }
                                if(flag){
                                    for(var k=0; k<$scope.subsys_info[i][j].length; k++){
                                        if($scope.subsys_info[i][j][k] !== $scope.buffer_subsys_info[i][j][k]){
                                            flag = false;
                                            break;
                                        }
                                    }
                                }
                            }
                            if(!flag){
                                break;
                            }
                        }
                    }
                }
                if(flag){
                    $scope.buffer_subsys_info[index].push([[undefined, undefined]]);
                }

                $scope.subsys_info[index].push([[undefined, undefined]]);
                $scope.showSpecificSubsys[index]= [false];
                disableTagTab(index);
            }
            else if(identifier === "subsys"){
                $scope.subsys_info[parent_index][index].push(["", ""]);
                $scope.buffer_subsys_info[parent_index][index].push(["", ""]);
                disableSubsysTab(parent_index);
            }
        };

        $scope.resetTag = function(parent_index, index, identifier, check, event){
            var r = true;
            if(check === "yes") {
                if (identifier === "tag") {
                    if($scope.tag_info[index].length != 1 ||
                        $scope.tag_info[index][0].length != 2 ||
                        $scope.tag_info[index][0][0] != undefined ||
                        $scope.tag_info[index][0][1] != undefined) {
                        sweetAlert({
                            title: "Do you wish to continue?",
                            text: "This would delete all the tags that you have added to this System.",
                            closeOnConfirm: false,
                            confirmButtonColor: '#3b3131',
                            closeOnCancel: false,
                            confirmButtonText: "Yes!",
                            showCancelButton: true,
                            cancelButtonText: "Nope.",
                            type: "warning"
                        },
                            function(isConfirm){
                                if (isConfirm) {
                                    $scope.$apply(deleteChosenTags(parent_index, index, identifier, check, event));
                                }
                                else {
                                    sweetAlert({
                                        title: "Tags not deleted.",
                                        showConfirmButton: false,
                                        type: "error",
                                        timer: 1250
                                    });
                                    return false;
                                }
                            });
                    }
                }
                else if (identifier === "subsys-tag") {
                    if($scope.subsys_info[parent_index][index].length != 1 ||
                        $scope.subsys_info[parent_index][index][0].length != 2 ||
                        $scope.subsys_info[parent_index][index][0][0] != undefined ||
                        $scope.subsys_info[parent_index][index][0][1] != undefined) {
                        sweetAlert({
                            title: "Do you wish to continue?",
                            text: "This would delete the entire Subsystem.",
                            closeOnConfirm: false,
                            confirmButtonColor: '#3b3131',
                            closeOnCancel: false,
                            confirmButtonText: "Yes!",
                            showCancelButton: true,
                            cancelButtonText: "Nope.",
                            type: "warning"
                        },
                            function(isConfirm){
                                if (isConfirm) {
                                    $scope.$apply(deleteChosenTags(parent_index, index, identifier, check, event));
                                }
                                else {
                                    sweetAlert({
                                        title: "Subsystem not deleted.",
                                        showConfirmButton: false,
                                        type: "error",
                                        timer: 1250
                                    });
                                    return false;
                                }
                            });
                    }
                }
                else if (identifier === "subsys") {
                    if($scope.subsys_info[index].length != 1 ||
                        $scope.subsys_info[index][0].length != 1 ||
                        $scope.subsys_info[index][0][0].length != 2 ||
                        $scope.subsys_info[index][0][0][0] != undefined ||
                        $scope.subsys_info[index][0][0][1] != undefined ||
                        $scope.subsys_name_list[index][0] != undefined) {
                        sweetAlert({
                            title: "Do you wish to continue?",
                            text: "This would delete all the subsystems that you have added to this System.",
                            closeOnConfirm: false,
                            closeOnCancel: false,
                            confirmButtonColor: '#3b3131',
                            confirmButtonText: "Yes!",
                            showCancelButton: true,
                            cancelButtonText: "Nope.",
                            type: "warning"
                        },
                            function(isConfirm){
                                if (isConfirm) {
                                    $scope.$apply(deleteChosenTags(parent_index, index, identifier, check, event));
                                }
                                else {
                                    sweetAlert({
                                        title: "Subsystems not deleted.",
                                        showConfirmButton: false,
                                        type: "error",
                                        timer: 1250
                                    });
                                    return false;
                                }
                            });
                    }
                }
            }
        };

        function deleteChosenTags(parent_index, index, identifier, check, event){

            if (identifier === "tag") {
                $scope.tag_info[index] = [[undefined, undefined]];
                $scope.buffer_tag_info[index] = [[undefined, undefined]];
                if(check == "no"){
                    $scope.subsys_info[index] = [];
                    $scope.subsys_name_list[index] = [];
                    for(var i= 0; i<$scope.buffer_subsys_info[index].length; i++){
                        $scope.showSpecificSubsys[index][i] = false;
                        $scope.subsys_info[index].push([]);
                        $scope.subsys_name_list[index].push($scope.buffer_subsys_name_list[index][i]);
                        for(var j= 0; j<$scope.buffer_subsys_info[index][i].length; j++){
                            $scope.subsys_info[index][i].push([]);
                            for(var k= 0; k<$scope.buffer_subsys_info[index][i][j].length; k++){
                                $scope.subsys_info[index][i][j].push($scope.buffer_subsys_info[index][i][j][k]);
                            }
                        }
                    }
                }
                else{
                    $scope.subsys_info[index] = [[[undefined, undefined]]];
                    $scope.subsys_name_list[index] = [undefined];
                    $scope.buffer_subsys_info[index] = [[[undefined, undefined]]];
                    $scope.buffer_subsys_name_list[index] = [undefined];
                    $scope.saveSubsysList[index] = [false];
                    $scope.buffer_saveSubsysList[index] = [false];
                }
                disableTagTab(index);
            }
            else if (identifier === "subsys-tag") {
                if($scope.subsys_info[parent_index].length == 1) {
                    $scope.subsys_info[parent_index][index] = [[undefined, undefined]];
                    $scope.buffer_subsys_info[parent_index][index] = [[undefined, undefined]];
                    $scope.subsys_name_list[parent_index][index] = undefined;
                    $scope.buffer_subsys_name_list[parent_index][index] = undefined;
                    $scope.showSpecificSubsys[parent_index][index] = false;
                    $scope.showSavedSubsystem[parent_index] = false;
                }
                else{
                    if($scope.subsysBeingEdited == index){
                        $scope.subsysEditorIsOpen = false;
                        $scope.subsysBeingEdited = "None";
                    }
                    else if(index < $scope.subsysBeingEdited){
                        $scope.subsysBeingEdited = $scope.subsysBeingEdited - 1;
                    }
                    $scope.subsys_info[parent_index].splice(index, 1);
                    $scope.subsys_name_list[parent_index].splice(index, 1);
                    $scope.buffer_subsys_info[parent_index].splice(index, 1);
                    $scope.buffer_subsys_name_list[parent_index].splice(index, 1);
                    $scope.showSpecificSubsys[parent_index].splice(index, 1);
                }
                disableSubsysTab(parent_index)
            }
            else if (identifier === "subsys") {
                if(check == "no"){
                    $scope.tag_info[index] = [];
                    for(i=0; i<$scope.buffer_tag_info[index].length; i++){
                        $scope.tag_info[index].push([]);
                        for(j=0; j<$scope.buffer_tag_info[index][i].length; j++){
                            $scope.tag_info[index][i].push($scope.buffer_tag_info[index][i][j]);
                        }
                    }
                    if(!($scope.tag_info[index].length > 0)){
                        $scope.tag_info[index] = [[undefined, undefined]];
                        $scope.buffer_tag_info[index] = [[undefined, undefined]];
                    }
                }
                else{
                    $scope.tag_info[index] = [[undefined, undefined]];
                    $scope.buffer_tag_info[index] = [[undefined, undefined]];
                }
                $scope.subsys_info[index] = [[[undefined, undefined]]];
                $scope.subsys_name_list[index] = [undefined];
                $scope.saveSubsysList[index] = [false];
                disableSubsysTab(index)
            }
            if(check==="no"){
                initializeCopyLists(true, index, event);
            }
            else{
                initializeCopyLists(event);
            }

            sweetAlert({
                title: "Deleted",
                showConfirmButton: false,
                type: "success",
                timer: 1250
            });

        }

        $scope.addAnotherSubsys = function(index){
            if($scope.subsysEditorIsOpen){
                swal({
                    title: "A subsystem is currently being edited in the subsystem Editor. Please save that subsystem before creating a new one",
                    type: "warning",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
                return
            }
            $scope.subsysEditorIsOpen = false;
            $scope.subsys_info[index].push([["", ""]]);
            $scope.buffer_subsys_info[index].push([["", ""]]);
            $scope.subsys_name_list[index].push(undefined);
            $scope.buffer_subsys_name_list[index].push(undefined);
            $scope.saveSubsysList[index].push(false);
            $scope.buffer_saveSubsysList[index].push(false);
            $scope.showSpecificSubsys[index].push(false);
            $scope.defSubsystemList[index].push(false);
            $scope.subsysBeingEdited = $scope.subsys_info[index].length - 1;

            var flag = $scope.tag_info.length === $scope.buffer_tag_info.length;
            if(flag){
                for(var i=0; i<$scope.tag_info.length; i++){
                    if($scope.tag_info.length !== $scope.buffer_tag_info.length){
                        flag = false;
                        break;
                    }
                    if(flag){
                        for(var j=0; j<$scope.tag_info[i].length; j++){
                            if($scope.tag_info[i][j] !== $scope.buffer_tag_info[i][j]){
                                flag = false;
                                break;
                            }
                        }
                        if(!flag){
                            break;
                        }
                    }
                }
            }
            if(flag){
                $scope.buffer_tag_info[index].push([undefined, undefined]);
            }
            $scope.tag_info[index].push([undefined, undefined]);

            disableSubsysTab(index);

            initializeCopyLists(undefined, undefined, true)
        };

        $scope.deleteTag = function(grandpa_index, parent_index, index, identifier){
            sweetAlert({
                title: "Are you sure you want to delete this tag?",
                closeOnConfirm: false,
                closeOnCancel: false,
                confirmButtonColor: '#3b3131',
                confirmButtonText: "Yes!",
                showCancelButton: true,
                cancelButtonText: "Nope.",
                type: "warning"
            },
                function(isConfirm){
                    if (isConfirm) {
                        $scope.$apply(deleteThisTag(grandpa_index, parent_index, index, identifier));
                    }
                    else {
                        sweetAlert({
                            title: "Tag not deleted.",
                            showConfirmButton: false,
                            type: "error",
                            timer: 1250
                        });
                        return false;
                    }
                });
        };

        function deleteThisTag(grandpa_index, parent_index, index, identifier){
            if(identifier == "tag"){
              if($scope.tag_info[parent_index].length == 1){
                  $scope.tag_info[parent_index][index] = ["", ""];
                  $scope.buffer_tag_info[parent_index][index] = ["", ""];
                  $scope.showTagChildren[parent_index][index] = false;
                  $scope.childTagsList[parent_index][index] = [[undefined, undefined]];
              }
              else{
                  $scope.tag_info[parent_index].splice(index, 1);
                  $scope.buffer_tag_info[parent_index].splice(index, 1);
                  $scope.childTagsList[parent_index].splice(index, 1);
                  $scope.showTagChildren[parent_index].splice(index, 1);
              }
              disableTagTab(parent_index)
          }
            else if(identifier == "subsys-tag"){
              if($scope.subsys_info[grandpa_index][parent_index].length == 1){
                  $scope.subsys_info[grandpa_index][parent_index][index] = ["", ""];
                  $scope.buffer_subsys_info[grandpa_index][parent_index][index] = ["", ""]
              }
              else {
                  $scope.subsys_info[grandpa_index][parent_index].splice(index, 1);
                  $scope.buffer_subsys_info[grandpa_index][parent_index].splice(index, 1);
              }
              disableSubsysTab(grandpa_index);
          }
            sweetAlert({
                title: "Tag deleted.",
                showConfirmButton: false,
                type: "success",
                timer: 1250
            });
        }

        $scope.closeSystemEditor = function(index) {
            sweetAlert({
                title: "Do you wish to continue?",
                text: "This would delete the entire System.",
                closeOnConfirm: false,
                closeOnCancel: false,
                confirmButtonColor: '#3b3131',
                confirmButtonText: "Yes!",
                showCancelButton: true,
                cancelButtonText: "Nope.",
                type: "warning"
            },
                function(isConfirm){
                    if (isConfirm) {
                        $scope.$apply(deleteSystem(index));
                    }
                    else {
                        sweetAlert({
                            title: "System not deleted.",
                            showConfirmButton: false,
                            type: "error",
                            timer: 1250
                        });
                        return false;
                    }
                });
        };

        function deleteSystem(index){
            if(index === 0 && $scope.system_info.length === 1){
                $scope.system_info[index] = "";
                $scope.savedSystemList[index] = false;
                $scope.subsys_name_list[index] = [""];
                $scope.buffer_subsys_name_list[index] = [""];
                $scope.tag_info[index] = [["", ""]];
                $scope.buffer_tag_info[index] = [["", ""]];
                $scope.subsys_info[index] = [[["", ""]]];
                $scope.buffer_subsys_info[index] = [[["", ""]]];
                $scope.saveSystemList = [false];
                $scope.saveSubsysList = [[false]];
                $scope.buffer_saveSubsysList = [[false]];
                $scope.showSpecificSubsys[index] = [false];
                $scope.showSavedSubsystem[index] = false;
                $scope.defSystemList[index] = false;
                $scope.defSubsystemList[index] = [false];
                $scope.showTagChildren[index] = [false];
                $scope.childTagsList[index] = [[[undefined, undefined]]];
                $scope.systemBeingEdited = 0;
                $scope.savedSystemTable = false;
                $scope.systemEditorIsOpen = true;
                if($scope.defSystem === index){
                    $scope.defSystem = -1;
                }
                else{
                    $scope.defSystem = $scope.defSystem -1
                }
            }
            else {
                $scope.system_info.splice(index, 1);
                $scope.savedSystemList.splice(index, 1);
                $scope.subsys_name_list.splice(index, 1);
                $scope.buffer_subsys_name_list.splice(index, 1);
                $scope.tag_info.splice(index, 1);
                $scope.buffer_tag_info.splice(index, 1);
                $scope.subsys_info.splice(index, 1);
                $scope.buffer_subsys_info.splice(index, 1);
                $scope.saveSystemList.splice(index, 1);
                $scope.saveSubsysList.splice(index, 1);
                $scope.buffer_saveSubsysList.splice(index, 1);
                $scope.showSpecificSubsys.splice(index, 1);
                $scope.showSavedSubsystem.splice(index, 1);
                $scope.defSystemList.splice(index, 1);
                $scope.defSubsystemList.splice(index, 1);
                $scope.showTagChildren.splice(index, 1);
                $scope.childTagsList.splice(index, 1);
                if($scope.systemBeingEdited == index){
                    $scope.systemEditorIsOpen = false;
                    $scope.systemBeingEdited = "None";
                }
                else{
                    $scope.systemBeingEdited = $scope.systemBeingEdited - 1;
                }
                if($scope.defSystem === index){
                    $scope.defSystem = -1;
                }
                else {
                    $scope.defSystem = $scope.defSystem -1
                }
            }
            initializeCopyLists();
            sweetAlert({
                title: "System deleted.",
                showConfirmButton: false,
                type: "success",
                timer: 1250
            });
        }

        $scope.saveSystemInfo = function(index){
            var check = true;
            if($scope.system_info[index] === undefined || $scope.system_info[index] === "" || $scope.system_info[index].trim() === ""){
                check = false;
                swal({
                    title: "System name cannot be empty.",
                    type: "error",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
            }
            if(check){
                if(document.getElementById("a_subsys_tab" + index).getAttribute("aria-expanded")== "true")
                {
                    for(var i=0; i<$scope.subsys_name_list[index].length; i++){
                        if($scope.subsys_name_list[index][i] === undefined ||
                            $scope.subsys_name_list[index][i] === "" ||
                            $scope.subsys_name_list[index][i].trim() === ""){
                            check = false;
                            swal({
                                title: "Subsystem name cannot be empty.",
                                text: "The name field for Subsystem " + (i+1) + " has been left empty.",
                                type: "error",
                                confirmButtonText: "Ok",
                                closeOnConfirm: true,
                                confirmButtonColor: '#3b3131'
                            });
                        }
                    }
                    if(check){
                        for(i=0; i<$scope.subsys_info[index].length; i++){
                            for(var j=0; j<$scope.subsys_info[index][i].length; j++){
                                if($scope.subsys_info[index][i][j][0] === undefined ||
                                    $scope.subsys_info[index][i][j][0] === "" ||
                                    $scope.subsys_info[index][i][j][0].trim() === ""){
                                    check = false;
                                    swal({
                                        title: "Tag names cannot be empty.",
                                        text: "Tag " + (j+1) + " name of Subsystem " + (i+1) + " has been left empty.",
                                        type: "error",
                                        confirmButtonText: "Ok",
                                        closeOnConfirm: true,
                                        confirmButtonColor: '#3b3131'
                                    });
                                }
                                else if($scope.subsys_info[index][i][j][0].match(/^[0-9_]/)){
                                    check = false;
                                    swal({
                                        title: "Tag names cannot start with a number.",
                                        text: "Tag " + (j+1) + " name of Subsystem " + (i+1) + " starts with a number.",
                                        type: "error",
                                        confirmButtonText: "Ok",
                                        closeOnConfirm: true,
                                        confirmButtonColor: '#3b3131'
                                    });
                                }
                                else if($scope.subsys_info[index][i][j][0].match(/[^a-zA-Z 0-9\._\-]/i)){
                                    check = false;
                                    swal({
                                        title: "Tag names cannot contain special characters other than an underscore, period, and hyphen.",
                                        text: "Tag " + (j+1) + " name of Subsystem " + (i+1) + " contains a special character.",
                                        type: "error",
                                        confirmButtonText: "Ok",
                                        closeOnConfirm: true,
                                        confirmButtonColor: '#3b3131'
                                    });
                                }
                                else if($scope.subsys_info[index][i][j][0].indexOf(" ") !== -1){
                                    check = false;
                                    swal({
                                        title: "Tag names cannot contain spaces.",
                                        text: "Tag " + (j+1) + " name of Subsystem " + (i+1) + " contains spaces.",
                                        type: "error",
                                        confirmButtonText: "Ok",
                                        closeOnConfirm: true,
                                        confirmButtonColor: '#3b3131'
                                    });
                                }
                            }
                        }

                    }
                }
                else{
                    for(i=0; i<$scope.tag_info[index].length; i++){
                        if($scope.tag_info[index][i][0] === undefined ||
                            $scope.tag_info[index][i][0] === "" ||
                            $scope.tag_info[index][i][0].trim() === ""){
                            check = false;
                            swal({
                                title: "Tag names cannot be empty.",
                                text: "Tag " + (i+1) + " has been left empty.",
                                type: "error",
                                confirmButtonText: "Ok",
                                closeOnConfirm: true,
                                confirmButtonColor: '#3b3131'
                            });
                        }
                        else if($scope.tag_info[index][i][0].match(/^[0-9_]/)){
                            check = false;
                            swal({
                                title: "Tag names cannot start with a number.",
                                text: "Tag " + (i+1) + " starts with a number.",
                                type: "error",
                                confirmButtonText: "Ok",
                                closeOnConfirm: true,
                                confirmButtonColor: '#3b3131'
                            });
                        }
                        else if($scope.tag_info[index][i][0].match(/[^a-zA-Z 0-9\._\-]/i)){
                            check = false;
                            swal({
                                title: "Tag names cannot contain special characters other than an underscore, period, and hyphen.",
                                text: "Tag " + (i+1) + " contains a special character.",
                                type: "error",
                                confirmButtonText: "Ok",
                                closeOnConfirm: true,
                                confirmButtonColor: '#3b3131'
                            });
                        }
                        else if($scope.tag_info[index][i][0].indexOf(" ") !== -1){
                            check = false;
                            swal({
                                title: "Tag names cannot contain spaces.",
                                text: "Tag " + (i+1) + " contains spaces.",
                                type: "error",
                                confirmButtonText: "Ok",
                                closeOnConfirm: true,
                                confirmButtonColor: '#3b3131'
                            });
                        }
                    }
                    if(check){
                        for(i=0; i<$scope.showTagChildren[index].length; i++){
                            if($scope.showTagChildren[index][i]){
                                for(j=0; j<$scope.childTagsList[index][i].length; j++){
                                    if($scope.childTagsList[index][i][j][0] === undefined ||
                                        $scope.childTagsList[index][i][j][0] === "" ||
                                        $scope.childTagsList[index][i][j][0].trim() === ""){
                                        check = false;
                                        swal({
                                            title: "Child tag names cannot be empty.",
                                            text: "Child tag " + (j+1) + " of Tag " + (i+1) + " is empty.",
                                            type: "error",
                                            confirmButtonText: "Ok",
                                            closeOnConfirm: true,
                                            confirmButtonColor: '#3b3131'
                                        });
                                    }
                                    else if($scope.childTagsList[index][i][j][0].match(/^[0-9_]/)){
                                        check = false;
                                        swal({
                                            title: "Tag names cannot start with a number.",
                                            text: "Child tag " + (j+1) + " of Tag " + (i+1) + " starts with a number.",
                                            type: "error",
                                            confirmButtonText: "Ok",
                                            closeOnConfirm: true,
                                            confirmButtonColor: '#3b3131'
                                        });
                                    }
                                    else if($scope.childTagsList[index][i][j][0].match(/[^a-zA-Z 0-9\._\-]/i)){
                                        check = false;
                                        swal({
                                            title: "Tag names cannot contain special characters other than an underscore, period, and hyphen.",
                                            text: "Child tag " + (j+1) + " of Tag " + (i+1) + " contains a special character.",
                                            type: "error",
                                            confirmButtonText: "Ok",
                                            closeOnConfirm: true,
                                            confirmButtonColor: '#3b3131'
                                        });
                                    }
                                    else if($scope.childTagsList[index][i][j][0].indexOf(" ") !== -1){
                                        check = false;
                                        swal({
                                            title: "Tag names cannot contain spaces.",
                                            text: "Child tag " + (j+1) + " of Tag " + (i+1) + " contains spaces.",
                                            type: "error",
                                            confirmButtonText: "Ok",
                                            closeOnConfirm: true,
                                            confirmButtonColor: '#3b3131'
                                        });
                                    }
                                }
                            }
                        }
                    }
                }
            }
            if(check){
                $scope.savedSystemTable = true;
                $scope.savedSystemList[index] = true;
                $scope.systemEditorIsOpen = false;
                $scope.systemBeingEdited = "None";
            }
        };

        function readInputDataFile() {
        DataFileFactory.fetch()
            .then(function (data) {
                $scope.xmlData = data["xml"];
                $scope.df_name = data["filename"].split(".")[0];

                var x2js = new X2JS();
                var jsonObj = x2js.xml_str2json($scope.xmlData);
                if (jsonObj == null) {
                    sweetAlert({
                        title: "There was an error reading the Data File: " + data["filename"],
                        text: "This XML file may be malformed.",
                        closeOnConfirm: true,
                        confirmButtonColor: '#3b3131',
                        confirmButtonText: "Ok",
                        type: "error"
                    });
                    return;
                }
                $scope.system_info = [];
                $scope.savedSystemList = [];

                var jsonObj_root = "";

                if(jsonObj.hasOwnProperty("systems")){
                    jsonObj_root = jsonObj.systems
                }
                else if(jsonObj.hasOwnProperty("credentials")){
                     jsonObj_root = jsonObj.credentials
                }

                if(jsonObj_root.hasOwnProperty('description')){
                    $scope.description = jsonObj_root.description;
                }
                if(jsonObj_root.hasOwnProperty('system')){
                    $scope.savedSystemTable = true;
                    if(jsonObj_root.system.length == undefined){
                        jsonObj_root.system = [jsonObj_root.system];
                    }
                    $scope.savedSystemList = [];
                    $scope.defSystemList = [];
                    for(var i=0; i<jsonObj_root.system.length; i++){
                        if(jsonObj_root.system[i].hasOwnProperty('_name')){
                            $scope.defSystemList.push(false);
                            $scope.system_info.push(jsonObj_root.system[i]._name);
                            $scope.savedSystemList.push(true);
                        } else if(jsonObj_root.system[i].hasOwnProperty('name')){
                            $scope.defSystemList.push(false);
                            $scope.system_info.push(jsonObj_root.system[i].name);
                            $scope.savedSystemList.push(true);
                        }
                    }

                    for(i=0; i<jsonObj_root.system.length; i++){
                        if(jsonObj_root.system[i].hasOwnProperty('_default') || jsonObj_root.system[i].hasOwnProperty('default')){
                            if(jsonObj_root.system[i]._default == "yes" || jsonObj_root.system[i].default == "yes"){
                                $scope.defSystem = i;
                                $scope.defSystemList[i] = true;
                                break;
                            }
                        }
                    }

                    $scope.subsys_name_list = [];
                    $scope.buffer_subsys_name_list = [];
                    $scope.subsys_info = [];
                    $scope.buffer_subsys_info = [];
                    $scope.showSpecificSubsys = [];
                    $scope.tag_info = [];
                    $scope.buffer_tag_info = [];
                    $scope.showSavedSubsystem = [];
                    $scope.defSubsystemList = [];
                    $scope.childTagsList = [];
                    $scope.showTagChildren = [];
                    for(i=0; i<jsonObj_root.system.length; i++){
                        $scope.defSubsystemList.push([]);
                        $scope.subsys_info.push([]);
                        $scope.buffer_subsys_info.push([]);
                        $scope.tag_info.push([]);
                        $scope.buffer_tag_info.push([]);
                        $scope.showSpecificSubsys.push([]);
                        $scope.showTagChildren.push([]);
                        $scope.childTagsList.push([]);
                        if(jsonObj_root.system[i].hasOwnProperty('subsystem')){
                            $scope.showTagChildren[i].push(false);
                            $scope.childTagsList[i].push([[undefined, undefined]]);
                            $scope.showSavedSubsystem.push(true);
                            $scope.defSubsystemList.push([]);
                            document.getElementById('a_subsys_tab'+i).click();
                            $scope.subsys_info[i].pop();
                            $scope.buffer_subsys_info[i].pop();
                            $scope.tag_info[i].pop();
                            $scope.buffer_tag_info[i].pop();
                            $scope.subsys_name_list.push([]);
                            $scope.buffer_subsys_name_list.push([]);
                            if(i !== 0){
                                document.getElementById('addAnotherSubsys'+(i)).click();
                                $scope.subsys_name_list[i].pop();
                                $scope.buffer_subsys_name_list[i].pop();
                                $scope.subsys_info[i].pop();
                                $scope.buffer_subsys_info[i].pop();
                            }
                            else{
                                $scope.tag_info[i].push([undefined, undefined]);
                                $scope.buffer_tag_info[i].push([undefined, undefined]);
                            }
                            if(jsonObj_root.system[i].subsystem.length == undefined){
                                jsonObj_root.system[i].subsystem = [jsonObj_root.system[i].subsystem]
                            }
                            var defSubsysFlag = false;
                            for(var j=0; j<jsonObj_root.system[i].subsystem.length; j++){
                                if(jsonObj_root.system[i].subsystem[j].hasOwnProperty('default') && defSubsysFlag == false){
                                    if(jsonObj_root.system[i].subsystem[j].default === "yes"){
                                        $scope.defSubsystemList[i].push(true);
                                        defSubsysFlag = true;
                                    }
                                    else{
                                        $scope.defSubsystemList[i].push(false);
                                    }
                                }
                                    else if(jsonObj_root.system[i].subsystem[j].hasOwnProperty('_default') && defSubsysFlag == false){
                                    if(jsonObj_root.system[i].subsystem[j]._default === "yes"){
                                        $scope.defSubsystemList[i].push(true);
                                        defSubsysFlag = true;
                                    }
                                    else{
                                        $scope.defSubsystemList[i].push(false);
                                    }
                                }
                                else{
                                    $scope.defSubsystemList[i].push(false);
                                }
                                $scope.showSpecificSubsys[i].push(true);
                                $scope.subsys_info[i].push([]);
                                $scope.buffer_subsys_info[i].push([]);
                                if(jsonObj_root.system[i].subsystem[j].hasOwnProperty('_name') || jsonObj_root.system[i].subsystem[j].hasOwnProperty('name')){
                                    $scope.subsys_name_list[i].push(jsonObj_root.system[i].subsystem[j]._name);
                                    $scope.buffer_subsys_name_list[i].push(jsonObj_root.system[i].subsystem[j]._name);
                                }
                                else{
                                    $scope.subsys_name_list[i].push(undefined);
                                    $scope.buffer_subsys_name_list[i].push(undefined);
                                }

                                for(var key in jsonObj_root.system[i].subsystem[j]){
                                    if(key !== "_name" && key !== "name" && key !== "_default" && key !== "default"){
                                        $scope.subsys_info[i][j].push([key, jsonObj_root.system[i].subsystem[j][key]]);
                                        $scope.buffer_subsys_info[i][j].push([key, jsonObj_root.system[i].subsystem[j][key]]);
                                    }
                                }

                            }
                            disableSubsysTab(i);
                        }
                        else{
                            $scope.defSubsystemList[i].push(false);
                            $scope.showSavedSubsystem.push(false);
                            $scope.showSpecificSubsys[i].push([false]);
                            $scope.subsys_name_list.push([]);
                            $scope.buffer_subsys_name_list.push([]);
                            document.getElementById('a_tag_tab'+i).click();
                            $scope.subsys_info[i].pop();
                            $scope.buffer_subsys_info[i].pop();
                            $scope.tag_info[i].pop();
                            $scope.buffer_tag_info[i].pop();
                            $scope.subsys_name_list[i].pop();
                            $scope.buffer_subsys_name_list[i].pop();
                            $scope.subsys_name_list[i].push(undefined);
                            $scope.buffer_subsys_name_list[i].push(undefined);
                            $scope.subsys_info[i].push([[undefined, undefined]]);
                            $scope.buffer_subsys_info[i].push([[undefined, undefined]]);
                                for(key in jsonObj_root.system[i]){
                                    if(key !== "_name" && key !== "name" && key !== "default" && key !== "_default" && key !== "subsystem"){
                                        //alert(key);
                                        if(jsonObj_root.system[i].hasOwnProperty(key)){
                                            $scope.childTagsList[i].push([]);
                                            var flag = false;
                                            $scope.tag_info[i].push([key, jsonObj_root.system[i][key]]);
                                            //alert(jsonObj_root.system[i][key]);
                                            $scope.buffer_tag_info[i].push([key, jsonObj_root.system[i][key]]);
                                            if(jsonObj_root.system[i][key] instanceof Array){
                                                for(var x=0; x<jsonObj_root.system[i][key].length; x++){
                                                    if(x>0){
                                                        $scope.childTagsList[i].push([]);
                                                        $scope.tag_info[i].push([key, undefined]);
                                                        $scope.buffer_tag_info[i].push([key, undefined]);
                                                    }
                                                    for(var child in jsonObj_root.system[i][key][x]){
                                                        if(jsonObj_root.system[i][key][x].hasOwnProperty(child) && isNaN(child[0])){
                                                            flag = true;
                                                            $scope.childTagsList[i][($scope.childTagsList[i].length - 1)].push([child, jsonObj_root.system[i][key][x][child]])
                                                        }
                                                    }
                                                    if(flag){
                                                        $scope.showTagChildren[i].push(true);
                                                    }
                                                    else{
                                                        $scope.showTagChildren[i].push(false);
                                                        $scope.childTagsList[i][($scope.childTagsList[i].length - 1)].push([undefined, undefined])
                                                    }
                                                }
                                            }
                                            else{
                                                for(var child in jsonObj_root.system[i][key]){
                                                    if(jsonObj_root.system[i][key].hasOwnProperty(child) && isNaN(child[0])){
                                                        flag = true;
                                                        $scope.childTagsList[i][($scope.childTagsList[i].length - 1)].push([child, jsonObj_root.system[i][key][child]])
                                                    }
                                                }
                                                if(flag){
                                                    $scope.showTagChildren[i].push(true);
                                                }
                                                else{
                                                    $scope.showTagChildren[i].push(false);
                                                    $scope.childTagsList[i][($scope.childTagsList[i].length - 1)].push([undefined, undefined])
                                                }
                                            }
                                        }
                                    }
                                }
                            disableTagTab(i);
                            }
                        }
                    }
                initializeCopyLists()
                },
                function (msg) {
                alert(msg);
            });
    }

        fileFactory.readtooltipfile('idf')
        .then(
            function(data) {
                // console.log(data);
                $scope.idfTooltips = data;
            },
            function(data) {
                alert(data);
            });

        if($route.current.$$route.newFile == "no"){
            $scope.subdirs = subdirs;
            readInputDataFile();
            $scope.systemEditorIsOpen = false;
            $scope.systemBeingEdited = "None";
        }
        else{
            initializeCopyLists();
            $scope.systemEditorIsOpen = true;
            $scope.systemBeingEdited = 0;
        }

        //setInterval(function(){$scope.$apply(initializeCopyLists())}, 5000);

    }]);