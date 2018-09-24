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

app.controller('newWarhornConfigFileCtrl', ['$scope', '$http', '$controller', '$location', '$route', 'saveNewWarhornConfigFileFactory', 'WarhornConfigFileFactory', 'fileFactory', 'subdirs',
    function($scope, $http, $controller, $location, $route, saveNewWarhornConfigFileFactory, WarhornConfigFileFactory, fileFactory, subdirs) {

        $scope.subdirs = "none";

        $scope.dependencies = [
            ["jira", false, "1.0.3"], ["lxml", true, "3.5"],
            ["ncclient", false, "0.4.6"], ["paramiko", true, "2.4.1"],
            ["pexpect", true, "3.1"], ["pysnmp", true, "4.3.2"],
            ["requests", true, "2.9.1"], ["selenium", true, "2.48.0"]
        ];

        $scope.choices = ["yes", "no"];

        $scope.showKWRepoTable = false;
        $scope.showKWRepoEditor = [];
        $scope.kwRepoEditorIsOpen = false;
        $scope.kwRepoBeingEdited = "None";

        $scope.showWariosTable = false;
        $scope.showWariosEditor = [];
        $scope.wariosEditorIsOpen = false;
        $scope.wariosBeingEdited = "None";

        $scope.jsonData =
        {
            "data": {
                "warhorn":{
                    "dependency": [
                        /*{
                            "_name": "",
                            "_install": ""
                        }*/
                    ]
                },
                "warrior": {
                    "_url": "",
                    "_destination": "",
                    "_label": "",
                    "_clean_install": "no"
                },
                "katana": {
                    "_url": "",
                    "_destination": "",
                    "_label": "",
                    "_clean_install": "no",
                    "_clone": "no"
                },
                "drivers": {
                    "repository": [
                        /*{
                            "_url": "",
                            "_clone": "yes",
                            "_label": "",
                            "_overwrite": "yes",
                            "_all_drivers": "yes",
                            "driver": [
                                {
                                    "_name": "",
                                    "_clone": ""
                                }
                            ]
                        }*/
                    ]
                },
                "warriorspace": {
                    "repository": [
                        /*{
                            "_url": "",
                            "_clone": "yes",
                            "_label": "",
                            "_overwrite": "yes"
                        }*/
                    ]
                }
            }
        };

        fileFactory.readtooltipfile('warhornconfig')
        .then(
            function(data) {
                // console.log(data);
                $scope.wcfTooltips = data;
            },
            function(data) {
                alert(data);
            });

        $scope.saveFile = function() {
            var filename = $scope.wcf_name + ".xml";
            fileFactory.checkfileexistwithsubdir(filename, 'warhornconfigfile', $scope.subdirs)
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
        };

        function save(filename){
            var x2js = new X2JS();
            var token = angular.toJson($scope.jsonData);
            var xmlObj = x2js.json2xml_str(JSON.parse(token));
            saveNewWarhornConfigFileFactory.saveNew(filename, $scope.subdirs, xmlObj)
                .then(
                    function(data) {
                        $location.path('/warhornconfigfiles');
                        console.log(data);
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

        $scope.cancel = function() {
            $location.path('/warhornconfigfiles');
        };

        $scope.addOrRemoveDriverNames = function(index){
            if($scope.jsonData.data.drivers.repository[index]._all_drivers == "no" &&
                $scope.jsonData.data.drivers.repository[index].driver.length == 0){
                $scope.jsonData.data.drivers.repository[index].driver.push({"_name": "", "_clone": "yes"});
            }
            else if($scope.jsonData.data.drivers.repository[index]._all_drivers == "no" &&
                $scope.jsonData.data.drivers.repository[index].driver.length == 1){
                $scope.jsonData.data.drivers.repository[index].driver = [{"_name": "", "_clone": "yes"}];
            }
            else{
                $scope.jsonData.data.drivers.repository[index].driver = [];
            }
        };

        $scope.doNotCloneKWDriver = function(parent_index, index){
            if($scope.jsonData.data.drivers.repository[parent_index].driver[index]._clone == "no"){
                $scope.jsonData.data.drivers.repository[parent_index].driver[index]._clone = "yes"
            }
            else{
                $scope.jsonData.data.drivers.repository[parent_index].driver[index]._clone = "no";
            }
        };

        $scope.deleteDriver = function(parent_index, index){
            if(index == 0){
                if($scope.jsonData.data.drivers.repository[parent_index].driver.length > 1){
                    $scope.jsonData.data.drivers.repository[parent_index].driver.splice(0, 1)
                }
                else{
                    $scope.jsonData.data.drivers.repository[parent_index].driver = [];
                    $scope.jsonData.data.drivers.repository[parent_index]._all_drivers = "yes";
                }
            }
            else{
                $scope.jsonData.data.drivers.repository[parent_index].driver.splice(index, 1)
            }
        };

        $scope.addAnotherDriver = function(index){
            $scope.jsonData.data.drivers.repository[index].driver.push({"_name": "", "_clone": "yes"});
        };

        $scope.addKeywordRepo = function(){
            if($scope.kwRepoEditorIsOpen){
                swal({
                    title: "You have a Keyword Repository open in the Keyword Repository Editor that should be saved before creating a new Keyword Repository.",
                    text: "Please save that Keyword Repository.",
                    type: "warning",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
                return;
            }
            $scope.kwRepoEditorIsOpen = true;
            $scope.showKWRepoEditor.push(true);
            $scope.jsonData.data.drivers.repository.push({"_url": "", "_clone": "yes", "_label": "", "_overwrite": "yes", "_all_drivers": "yes", "driver": [] });
            $scope.kwRepoBeingEdited = $scope.jsonData.data.drivers.repository.length - 1;
        };

        $scope.DeleteKeywordRepo = function(index){
            sweetAlert({
                title: "Are you sure you want to delete this Keyword Repository?",
                closeOnConfirm: false,
                closeOnCancel: false,
                confirmButtonColor: '#3b3131',
                confirmButtonText: "Yes, I am sure.",
                showCancelButton: true,
                cancelButtonText: "Nope.",
                type: "warning"
            },
            function(isConfirm){
                if (isConfirm) {
                    $scope.$apply(deleteKWRepo(index));
                    swal({
                        title: "Keyword Repository deleted.",
                        timer: 1250,
                        type: "success",
                        showConfirmButton: false
                    });
                }
                else{
                    swal({
                        title: "Keyword Repository not deleted.",
                        timer: 1250,
                        type: "error",
                        showConfirmButton: false
                    });
                }
            });
        };

        function deleteKWRepo(index){
            $scope.jsonData.data.drivers.repository.splice(index, 1);
            $scope.showKWRepoEditor.splice(index, 1);
            $scope.showKWRepoTable = false;
            if($scope.kwRepoBeingEdited == index){
                $scope.kwRepoEditorIsOpen = false;
                $scope.kwRepoBeingEdited = "None";
            }
            else{
                $scope.kwRepoBeingEdited = $scope.kwRepoBeingEdited - 1;
            }
            for(var i=0; i<$scope.showKWRepoEditor.length; i++){
                if(!$scope.showKWRepoEditor[i]){
                    $scope.showKWRepoTable = true;
                    break;
                }
            }
        }

        $scope.SaveKeywordRepo = function(index){
            if($scope.jsonData.data.drivers.repository[index]._url == ""){
                sweetAlert({
                    title: "The URL for a Keyword Repository is a mandatory field and cannot be left empty.",
                    text: "Please add the URL.",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131',
                    confirmButtonText: "Ok.",
                    showCancelButton: false,
                    type: "error"
                });
                return;
            }
            $scope.kwRepoEditorIsOpen = false;
            $scope.showKWRepoEditor[index] = false;
            $scope.showKWRepoTable = false;
            $scope.kwRepoBeingEdited = "None";
            for(var i=0; i<$scope.showKWRepoEditor.length; i++){
                if(!$scope.showKWRepoEditor[i]){
                    $scope.showKWRepoTable = true;
                    break;
                }
            }
        };

        $scope.EditKeywordRepo = function(index){
            if($scope.kwRepoEditorIsOpen){
                swal({
                    title: "You have a Keyword Repository open in the Keyword Repository Editor that should be saved before editing a new Keyword Repository.",
                    text: "Please save that Keyword Repository.",
                    type: "warning",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
                return;
            }
            $scope.kwRepoEditorIsOpen = true;
            $scope.showKWRepoEditor[index] = true;
            $scope.showKWRepoTable = false;
            $scope.kwRepoBeingEdited = index;
            for(var i=0; i<$scope.showKWRepoEditor.length; i++){
                if(!$scope.showKWRepoEditor[i]){
                    $scope.showKWRepoTable = true;
                    break;
                }
            }
        };

        $scope.addWarriorSpaceRepo = function(){
            if($scope.wariosEditorIsOpen){
                swal({
                    title: "You have a Warriorspace Repository open in the Warios Editor that should be saved before creating a new Warriorspace Repository.",
                    text: "Please save that Warriorspace Repository.",
                    type: "warning",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
                return;
            }
            $scope.wariosEditorIsOpen = true;
            $scope.showWariosEditor.push(true);
            $scope.jsonData.data.warriorspace.repository.push({"_url": "", "_clone": "yes", "_label": "", "_overwrite": "yes"});
            $scope.wariosBeingEdited = $scope.jsonData.data.warriorspace.repository.length - 1;
        };

        $scope.SaveWarriorSpaceRepo = function(index){
            if($scope.jsonData.data.warriorspace.repository[index]._url == ""){
                sweetAlert({
                    title: "The URL for a Warriorspace Repository is a mandatory field and cannot be left empty.",
                    text: "Please add the URL.",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131',
                    confirmButtonText: "Ok.",
                    showCancelButton: false,
                    type: "error"
                });
                return;
            }
            $scope.wariosEditorIsOpen = false;
            $scope.showWariosEditor[index] = false;
            $scope.showWariosTable = false;
            $scope.wariosBeingEdited = "None";
            for(var i=0; i<$scope.showWariosEditor.length; i++){
                if(!$scope.showWariosEditor[i]){
                    $scope.showWariosTable = true;
                    break;
                }
            }
        };

        $scope.DeleteWarriorSpaceRepo = function(index){
            sweetAlert({
                title: "Are you sure you want to delete this Warriorspace Repository?",
                closeOnConfirm: false,
                confirmButtonColor: '#3b3131',
                confirmButtonText: "Yes, I am sure.",
                showCancelButton: true,
                cancelButtonText: "Nope.",
                type: "warning"
            },
            function(isConfirm){
                if (isConfirm) {
                    $scope.$apply(deleteWariosRepo(index));
                    swal({
                        title: "Warriorspace Repository deleted.",
                        timer: 1250,
                        type: "success",
                        showConfirmButton: false
                    });
                }
                else{
                    swal({
                        title: "Warriorspace Repository not deleted.",
                        timer: 1250,
                        type: "error",
                        showConfirmButton: false
                    });
                }
            });
        };

        function deleteWariosRepo(index){
            $scope.jsonData.data.warriorspace.repository.splice(index, 1);
            $scope.showWariosEditor.splice(index, 1);
            $scope.showWariosTable = false;
            if($scope.wariosBeingEdited == index){
                $scope.wariosEditorIsOpen = false;
                $scope.wariosBeingEdited = "None";
            }
            else if(index < $scope.wariosBeingEdited){
                $scope.wariosBeingEdited = $scope.wariosBeingEdited - 1;
            }
            for(var i=0; i<$scope.showWariosEditor.length; i++){
                if(!$scope.showWariosEditor[i]){
                    $scope.showWariosTable = true;
                    break;
                }
            }
        }

        $scope.EditWarriorSpaceRepo = function(index){
            if($scope.wariosEditorIsOpen){
                swal({
                    title: "You have a Warriorspace Repository open in the Warios Editor that should be saved before editing a new Warriorspace Repository.",
                    text: "Please save that Warriorspace Repository.",
                    type: "warning",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
                return;
            }
            $scope.wariosEditorIsOpen = true;
            $scope.showWariosEditor[index] = true;
            $scope.wariosBeingEdited = index;
            $scope.showWariosTable = false;
            for(var i=0; i<$scope.showWariosEditor.length; i++){
                if(!$scope.showWariosEditor[i]){
                    $scope.showWariosTable = true;
                    break;
                }
            }
        };

        function getDependencyList(){
            var temp_list = [];
            var temp = {};
            for(var i=0; i<$scope.dependencies.length; i++){
                if($scope.dependencies[i][1]){
                    temp = {"_name": $scope.dependencies[i][0], "_install": "yes"}
                }
                else{
                    temp = {"_name": $scope.dependencies[i][0], "_install": "no"}
                }
                temp_list.push(temp)
            }
            $scope.jsonData.data.warhorn.dependency = temp_list
        }

        $scope.updateDependency = function(index){
            $scope.dependencies[index][1] = !$scope.dependencies[index][1];
            if($scope.dependencies[index][1]){
                $scope.jsonData.data.warhorn.dependency[index]._install = "yes";
            }
            else{
                $scope.jsonData.data.warhorn.dependency[index]._install = "no";
            }
        };

        if($route.current.$$route.newFile == "no"){
            $scope.subdirs = subdirs;
            readWarhornConfigFile();
        }
        else{
            getDependencyList();
        }

        function readWarhornConfigFile(){
            WarhornConfigFileFactory.fetch()
                .then(function (data) {
                    $scope.xmlData = data["xml"];
                    $scope.wcf_name = data["filename"].split(".")[0];

                    var x2js = new X2JS();
                    $scope.jsonData = x2js.xml_str2json($scope.xmlData);
                    if ($scope.jsonData == null) {
                        sweetAlert({
                            title: "There was an error reading the Warhorn Config File: " + data["filename"],
                            text: "This XML file may be malformed.",
                            closeOnConfirm: true,
                            confirmButtonColor: '#3b3131',
                            confirmButtonText: "Ok",
                            type: "error"
                        });
                    }
                    else{
                        for(var i=0; i<$scope.jsonData.data.warhorn.dependency.length; i++){
                            for(var j=0; j<$scope.dependencies.length; j++){
                                if($scope.jsonData.data.warhorn.dependency[i]._name === $scope.dependencies[j][0]){
                                    if($scope.jsonData.data.warhorn.dependency[i]._install.toLowerCase() === "yes"){
                                        $scope.dependencies[j][1] = true;
                                    }
                                    else{
                                        $scope.dependencies[j][1] = false;
                                    }
                                    break;
                                }
                            }
                        }

                        if(!$scope.jsonData.data.drivers.repository.hasOwnProperty(length)){
                            $scope.jsonData.data.drivers.repository = [$scope.jsonData.data.drivers.repository];
                        }

                        if(!$scope.jsonData.data.warriorspace.repository.hasOwnProperty(length)){
                            $scope.jsonData.data.warriorspace.repository = [$scope.jsonData.data.warriorspace.repository];
                        }

                        //Warrior details JSON validation
                        if(!$scope.jsonData.data.warrior.hasOwnProperty("_url")){
                            $scope.jsonData.data.warrior._url = "";
                        }
                        if(!$scope.jsonData.data.warrior.hasOwnProperty("_label")){
                            $scope.jsonData.data.warrior._label = "";
                        }
                        if(!$scope.jsonData.data.warrior.hasOwnProperty("_destination")){
                            $scope.jsonData.data.warrior._destination = "";
                        }
                        if($scope.jsonData.data.warrior.hasOwnProperty("_clean_install_warrior")){
                            $scope.jsonData.data.warrior._clean_install = $scope.jsonData.data.warrior["_clean_install_warrior"];
                            delete $scope.jsonData.data.warrior["_clean_install_warrior"];
                        }
                        if(!$scope.jsonData.data.warrior.hasOwnProperty("_clean_install")){
                            $scope.jsonData.data.warrior._clean_install = "no";
                        }

                        for(j=0; j<$scope.choices.length; j++){
                            if($scope.jsonData.data.warrior._clean_install.toLowerCase() == $scope.choices[j].toLowerCase()){
                                $scope.jsonData.data.warrior._clean_install = $scope.choices[j];
                                break;
                            }
                        }

                        //Katana details JSON validation
                        if(!$scope.jsonData.data.katana.hasOwnProperty("_url")){
                            $scope.jsonData.data.katana._url = "";
                        }
                        if(!$scope.jsonData.data.katana.hasOwnProperty("_label")){
                            $scope.jsonData.data.katana._label = "";
                        }
                        if(!$scope.jsonData.data.katana.hasOwnProperty("_destination")){
                            $scope.jsonData.data.katana._destination = "";
                        }
                        if(!$scope.jsonData.data.katana.hasOwnProperty("_clean_install")){
                            $scope.jsonData.data.katana._clean_install = "no";
                        }

                        for(j=0; j<$scope.choices.length; j++){
                            if($scope.jsonData.data.katana._clean_install.toLowerCase() == $scope.choices[j].toLowerCase()){
                                $scope.jsonData.data.katana._clean_install = $scope.choices[j];
                                break;
                            }
                        }

                        if(!$scope.jsonData.data.katana.hasOwnProperty("_clone")){
                            $scope.jsonData.data.katana._clone = "no";
                        }

                        for(j=0; j<$scope.choices.length; j++){
                            if($scope.jsonData.data.katana._clone.toLowerCase() == $scope.choices[j].toLowerCase()){
                                $scope.jsonData.data.katana._clone = $scope.choices[j];
                                break;
                            }
                        }

                        //KW repository details JSON validation
                        for(i=0; i<$scope.jsonData.data.drivers.repository.length; i++){
                            if(!$scope.jsonData.data.drivers.repository[i].hasOwnProperty("_url")){
                                $scope.jsonData.data.drivers.repository[i]._url = "";
                            }
                            if(!$scope.jsonData.data.drivers.repository[i].hasOwnProperty("_label")){
                                $scope.jsonData.data.drivers.repository[i]._label = "";
                            }
                            if(!$scope.jsonData.data.drivers.repository[i].hasOwnProperty("_all_drivers")){
                                $scope.jsonData.data.drivers.repository[i]._all_drivers = "yes";
                            }
                            if($scope.jsonData.data.drivers.repository[i].hasOwnProperty("driver")){
                                if(!$scope.jsonData.data.drivers.repository[i].driver.hasOwnProperty(length)){
                                    $scope.jsonData.data.drivers.repository[i].driver = [$scope.jsonData.data.drivers.repository[i].driver];
                                }
                                for(j=0; j<$scope.jsonData.data.drivers.repository[i].driver.length; j++){
                                    if(!$scope.jsonData.data.drivers.repository[i].driver[j].hasOwnProperty("_name")){
                                        $scope.jsonData.data.drivers.repository[i].driver[j]._name = ""
                                    }
                                    if(!$scope.jsonData.data.drivers.repository[i].driver[j].hasOwnProperty("_clone")){
                                        $scope.jsonData.data.drivers.repository[i].driver[j]._clone = "yes";
                                    }
                                    else{
                                        if($scope.jsonData.data.drivers.repository[i].driver[j]._clone !== "no"){
                                            $scope.jsonData.data.drivers.repository[i].driver[j]._clone = "yes";
                                        }
                                    }
                                }
                            }
                            else{
                                $scope.jsonData.data.drivers.repository[i].driver = [];
                            }
                            if(!$scope.jsonData.data.drivers.repository[i].hasOwnProperty("_clone")){
                                $scope.jsonData.data.drivers.repository[i]._clone = "yes";
                            }

                            for(j=0; j<$scope.choices.length; j++){
                                if($scope.jsonData.data.drivers.repository[i]._clone.toLowerCase() == $scope.choices[j].toLowerCase()){
                                    $scope.jsonData.data.drivers.repository[i]._clone = $scope.choices[j];
                                }
                            }

                            if(!$scope.jsonData.data.drivers.repository[i].hasOwnProperty("_overwrite")){
                                $scope.jsonData.data.drivers.repository[i]._overwrite = "yes";
                                break;
                            }

                            for(j=0; j<$scope.choices.length; j++){
                                if($scope.jsonData.data.drivers.repository[i]._overwrite.toLowerCase() == $scope.choices[j].toLowerCase()){
                                    $scope.jsonData.data.drivers.repository[i]._overwrite = $scope.choices[j];
                                    break;
                                }
                            }
                            $scope.showKWRepoEditor.push(false);
                        }

                        if($scope.showKWRepoEditor.length > 0){
                            $scope.showKWRepoTable = true;
                        }

                        //Warriorspace repository details JSON validation
                        for(i=0; i<$scope.jsonData.data.warriorspace.repository.length; i++){
                            if(!$scope.jsonData.data.warriorspace.repository[i].hasOwnProperty("_url")){
                                $scope.jsonData.data.warriorspace.repository[i]._url = "";
                            }
                            if(!$scope.jsonData.data.warriorspace.repository[i].hasOwnProperty("_label")){
                                $scope.jsonData.data.warriorspace.repository[i]._label = "";
                            }
                            if(!$scope.jsonData.data.warriorspace.repository[i].hasOwnProperty("_clone")){
                                $scope.jsonData.data.warriorspace.repository[i]._clone = "yes";
                            }

                            for(j=0; j<$scope.choices.length; j++){
                                if($scope.jsonData.data.warriorspace.repository[i]._clone.toLowerCase() == $scope.choices[j].toLowerCase()){
                                    $scope.jsonData.data.warriorspace.repository[i]._clone = $scope.choices[j];
                                    break;
                                }
                            }

                            if(!$scope.jsonData.data.warriorspace.repository[i].hasOwnProperty("_overwrite")){
                                $scope.jsonData.data.warriorspace.repository[i]._overwrite = "yes";
                            }

                            for(j=0; j<$scope.choices.length; j++){
                                if($scope.jsonData.data.warriorspace.repository[i]._overwrite.toLowerCase() == $scope.choices[j].toLowerCase()){
                                    $scope.jsonData.data.warriorspace.repository[i]._overwrite = $scope.choices[j];
                                    break;
                                }
                            }
                            $scope.showWariosEditor.push(false);
                        }
                        if($scope.showWariosEditor.length > 0){
                            $scope.showWariosTable = true;
                        }

                    }
                },
                    function (msg) {
                        alert(msg);
                    }
                );
        }
      }
]);
