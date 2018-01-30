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

app.controller('projectCapCtrl', ['$scope', '$http', '$routeParams', '$controller', '$location', '$timeout', 'fileFactory', 'saveasProjectFactory', 'getProjectFactory', 'setProjectFactory', 'getConfigFactory', 'subdirs',
    function($scope, $http, $routeParams, $controller, $location, $timeout, fileFactory, saveasProjectFactory, getProjectFactory, setProjectFactory, getConfigFactory, subdirs) {

        $scope.subdirs = subdirs;
        $scope.xml = {};
        $scope.xml.projectfile = '';
        $scope.xml.projectjson = '';
        $scope.projectGotoStep = '';
        $scope.projecttooltips = {};
        $scope.alldirinfo = "";
        $scope.table = "";
        $scope.path_array = [];
        $scope.earlier_li = [];
        $scope.btnValue = [];
        $scope.projectstates = "";
        $scope.showModal = [];
        $scope.condition_list = [[]];
        $scope.popoverContentList = [""];
        $scope.showSavedSuite = [false];
        $scope.showTable = false;
        $scope.suiteToBeCopied = "None";
        $scope.suite_numbers = [];
        $scope.suiteEditor = false;
        $scope.suiteBeingEdited = "None";

   function readConfig(){
      getConfigFactory.readconfig()
      .then(function (data) {
         $scope.cfg = data;
        });
  }

  readConfig();

//To Load the InputData File from Suite 
//Works for base Directory as well as Subdirectories
    $scope.loadFile = function(filepath) { 
        var checkFlag = filepath.includes("..");                                         
        if(checkFlag==true){                                                      //For files inside the Warrior directory
           var dirCheck=filepath.split("/").reverse()[1];
             if(dirCheck=="Suites"){                                           //Fetch Parent directory files
                var splitDir = filepath.split('/Suites')[1]; 
                var finalUrl = "#/testsuite"+splitDir+"/none";
                window.open(finalUrl);    
             }
             else if(dirCheck=="suites"){
                var splitDir = filepath.split('/suites')[1]; 
                var finalUrl = "#/testsuite"+splitDir+"/none";
                window.open(finalUrl);
             }
            else{                                                                 //Fetch subdirectory files
                var splitPath = filepath.split("/").pop(-1); 
                var splitter = splitPath+"/"; 
                if(filepath.includes("Suites")==true){
                var checkDir = filepath.split("Suites/")[1].split(splitPath)[0]; 
                }
                else{var checkDir = filepath.split("suites/")[1].split(splitPath)[0];}
                checkDir = checkDir.slice(0, -1);
                checkDir = checkDir.replace(/\//g,','); 
                var finalUrlDir = "#/testsuite/"+splitter+checkDir;
                window.open(finalUrlDir);
            }
        }
        else{                                                                     //For files outside the Warrior directory
            var dataDir = $scope.cfg.testsuitedir;
            var matchPath = filepath.includes(dataDir);
            if(matchPath == true){
              splitPath = filepath.split(dataDir)[1]; 
              var fileName = splitPath.split("/").pop(-1); 
              splitter = fileName+"/";
              var checkDir = filepath.split(dataDir)[1].split(fileName)[0]; 
              checkDir = checkDir.replace(/\//g,','); 
              var finalUrlDir = "#/testsuite/"+splitter+checkDir;
              window.open(finalUrlDir);
          }
            else{    
            if(filepath != '') 
                 {                                                        //Mismatched Config and selected path;   
                sweetAlert({
                    title: "Config Path mismatch with the selected path !",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131',
                    confirmButtonText: "Ok",
                    type: "info"
                });
            }
          }
        } 
     };

        fileFactory.readstatesfile()
            .then(
                function(data) {
                    $scope.projectstates = data["projectstate"];
                },
                function(data) {
                    alert(data);
                });

        $scope.storePaths = function(index){
            var project_folder_array = [];
            var suite_folder_array = [];
            var folder_index = -1;
            var final_array = [];
            $scope.suites[index].path = "";
            if($scope.cfg.testsuitedir.indexOf('/') === -1) {
                suite_folder_array = $scope.cfg.testsuitedir.split("\\");
            }
            else{
                suite_folder_array = $scope.cfg.testsuitedir.split("/");
            }
            for(var i=0; i<suite_folder_array.length; i++){
                if(suite_folder_array[i] === $scope.path_array[index][$scope.path_array[index].length-1]){
                    suite_folder_array.splice(i, (suite_folder_array.length-i));
                    break;
                }
            }
            for(i=$scope.path_array[index].length-1; i>=0; i--){
                suite_folder_array.push($scope.path_array[index][i])
            }
            if($scope.cfg.projdir.indexOf('/') === -1) {
                project_folder_array = $scope.cfg.projdir.split("\\");
            }
            else{
                project_folder_array = $scope.cfg.projdir.split("/");
            }
            if($scope.subdirs != "none"){
                var subdir_array = $scope.subdirs.split(",");
                for(i=0; i<subdir_array.length; i++){
                    project_folder_array.push(subdir_array[i]);
                }
            }
            for(i=0; i<project_folder_array.length; i++){
                if(suite_folder_array[i] !== project_folder_array[i]){
                    folder_index = i;
                    break;
                }
            }
            if(folder_index !== -1) {
                var dots = project_folder_array.length - folder_index;
                for (i = 0; i < dots; i++) {
                    final_array.push("..");
                }
            } else {
                folder_index = project_folder_array.length;
            }
            for(i=folder_index; i<suite_folder_array.length; i++){
                final_array.push(suite_folder_array[i]);
            }
            for(i=0; i<final_array.length; i++){
                $scope.suites[index].path = $scope.suites[index].path + final_array[i] + "/"
            }
            if (!$scope.suites[index].path.match(/\.\.\/$/)){
                $scope.suites[index].path = $scope.suites[index].path.slice(0, -1);
            }
            $scope.btnValue[index] = "Edit";
            $scope.toggleModal(index);
        };

         $scope.getPaths = function(e, index){

             $scope.path_array[index] = [];
             $scope.earlier_li[index].className = "";
             if(e == undefined){
                 e = window.event;
             }
             var li = (e.target ? e.target : e.srcElement);
             var temp_name = li.innerHTML.split("<");
             $scope.path_array[index].push(temp_name[0]);
             var li_temp = li;
             while(li_temp.parentNode.id.substring(0, 8) != "tree_div"){
                 if(!li_temp.parentNode.innerHTML.match(/^</)){
                     var temp_list = li_temp.parentNode.innerHTML.split("<");
                     $scope.path_array[index].push(temp_list[0]);
                 }
                 li_temp = li_temp.parentNode
             }
             if (li.className == ""){
                 li.className = "colorChange";
                 $scope.earlier_li[index] = li;
             }
        };

        $scope.toggleModal = function(index){
            document.getElementById("tree_div-" + index.toString()).innerHTML = $scope.table;
            CollapsibleLists.applyTo(document.getElementById('tree_div-' + index.toString()));
            $scope.showModal[index].visible = !$scope.showModal[index].visible;
        };

        $scope.monitorPathBtnValue = function(index) {
            if ($scope.suites[index].path === undefined || $scope.suites[index].path === "") {
                $scope.btnValue[index] = "Path";
            } else {
                $scope.btnValue[index] = "Edit";
            }
        };

        var ChildCtrl=this;
        ChildCtrl.baseCtrl = $controller('baseChariotCtrl',{ $scope: $scope, $http: $http });
        ChildCtrl.baseCtrl.readConfig();

        function get_folders_names(json_dir_data){
            var dir = json_dir_data["dir"];
            var files = json_dir_data["file"];
            $scope.table = $scope.table + "<li>";
            $scope.table = $scope.table + dir;
            $scope.table = $scope.table + "<ul>";
            if(json_dir_data["children"].length > 0){
                for(var j=0; j<json_dir_data["children"].length; j++){
                    var children = json_dir_data["children"][j];
                     get_folders_names(children);
                }
            }
            if(files !== undefined){
                for(var i=0; i<files.length; i++){
                    $scope.table = $scope.table + "<li>" + files[i] + "</li>"
                }
            }
            $scope.table = $scope.table + "</ul></li>";
        }

        var fetchProjectDetails = function() {
            getProjectFactory.list()
                .then(
                    function(data) {

                        $scope.xml.projectfile = data.xml;
                        var x2js = new X2JS();
                        var jsonObj = x2js.xml_str2json($scope.xml.projectfile);
                        if (jsonObj == null) {
                            sweetAlert({
                                title: "There was an error reading the Project: " + data["filename"],
                                text: "This XML file may be malformed.",
                                closeOnConfirm: true,
                                confirmButtonColor: '#3b3131',
                                confirmButtonText: "Ok",
                                type: "error"
                            });
                            return;
                        }
                        console.log("Data: " + data);
                        $scope.xml.projectjson = JSON.stringify(jsonObj, null, 2);

                        console.log("Json: " + $scope.xml.projectjson );

                        $scope.projectmodel = jsonObj;
                        console.log("Model : " + $scope.projectmodel);
                    },
                    function(data) {
                        alert(data);
                    });
        };

        fetchProjectDetails();

        $scope.getNewStateValue = function(tab){
            if(tab.indexOf('%') !== -1) {
                swal({
                  title: "The symbol % is not allowed!",
                  text: "",
                  type: "warning",
                  showCancelButton: false,
                  confirmButtonColor: '#3b3131',
                  confirmButtonText: "Ok",
                  closeOnConfirm: false
                });
            }

            $scope.new_state = tab;
        };

        $scope.isAddAnotherSelectedSuite = function() {
            if ($scope.projectmodel.Project.Details.State == 'Add Another') {
                console.log("Add Another");
                return true;
            } else {
                return false;
            }
        };

        $scope.saveNewlyAddedState = function() {
            if($scope.new_state === undefined || $scope.new_state === ""){
                swal({
                  title: "New State cannot be empty!",
                  text: "",
                  type: "warning",
                  showCancelButton: false,
                  confirmButtonColor: '#3b3131',
                  confirmButtonText: "Ok",
                  closeOnConfirm: false
                });
            }
            else{
                fileFactory.updatestatesfile("suitestate%"+$scope.new_state)
                    .then(
                        function(data) {
                            var check = data["check"];
                            if(check){
                                $scope.projectstates.pop();
                                $scope.projectstates.push($scope.new_state);
                                $scope.projectstates.push("Add Another");
                                $scope.projectmodel.Project.Details.State = $scope.new_state;
                                $scope.new_state = "";
                            }
                            else{
                                swal({
                                      title: "States file could not be updated!",
                                      text: "",
                                      type: "error",
                                      showCancelButton: false,
                                      confirmButtonColor: '#3b3131',
                                      confirmButtonText: "Ok",
                                      closeOnConfirm: false
                                });
                            }
                        },
                        function(data) {
                            alert(data);
                        });
            }
        };

        fileFactory.readtooltipfile('project')
            .then(
                function(data) {
                    console.log(data);
                    $scope.projecttooltips = data;
                },
                function(data) {
                    alert(data);
                });


        $timeout(function() {

            //To Handle the default action on error Section
            $scope.defaultProjectActions = ['next', 'abort', 'abort_as_error', 'goto'];

            $scope.ExecuteTypes = ['Yes', 'If', 'If Not', 'No'];
            $scope.FirstExecuteTypes = ['Yes', 'No'];
            $scope.ruleElseTypes = ['next', 'abort', 'abort_as_error', 'goto'];
            $scope.ConditionValueTypes = ['PASS', 'FAIL', 'ERROR', 'SKIP'];
            $scope.suiteDefaultActions = ['goto', 'abort', 'abort_as_error', 'next'];
            $scope.impactOptions = ['impact', 'noimpact'];

            $scope.projectmodel.Project.Details.Date = ChildCtrl.baseCtrl.getDate();
            $scope.projectmodel.Project.Details.Time = ChildCtrl.baseCtrl.getTime();
            $scope.projectmodel.Project.Details.Engineer = $scope.cfg.engineer;

            if(!$scope.projectmodel.Project.Details.hasOwnProperty("State")){
                $scope.projectmodel.Project.Details.State = "";
            }

            for(var j=0; j<$scope.projectstates.length; j++){
                if($scope.projectmodel.Project.Details.State.toLowerCase() == $scope.projectstates[j].toLowerCase()){
                    $scope.projectmodel.Project.Details.State = $scope.projectstates[j];
                    break;
                }
            }

            if(!$scope.projectmodel.Project.Details.hasOwnProperty("default_onError")){
                $scope.projectmodel.Project.Details.default_onError = {"_action": "next", "_value": ""};
            }

            if(!$scope.projectmodel.Project.Details.default_onError.hasOwnProperty("_action")){
                $scope.projectmodel.Project.Details.default_onError._action = "next";
            }

            if(!$scope.projectmodel.Project.Details.default_onError.hasOwnProperty("_value")){
                $scope.projectmodel.Project.Details.default_onError._value = "";
            }

            for(j=0; j<$scope.defaultProjectActions.length; j++){
                if($scope.projectmodel.Project.Details.default_onError._action.toLowerCase() == $scope.defaultProjectActions[j].toLowerCase()){
                    $scope.projectmodel.Project.Details.default_onError._action = $scope.defaultProjectActions[j];
                    break;
                }
            }

            $scope.defaultProjectAction = $scope.projectmodel.Project.Details.default_onError._action;
            $scope.projectGotoStep = $scope.projectmodel.Project.Details.default_onError._value;

            $scope.isGotoSelectedProject = function() {
                if ($scope.defaultProjectAction == 'goto') {
                    return true;
                } else {
                    return false;
                }
            };

            //default actions for step section
            $scope.suiteDefaultGotoValue = [];

            if ($scope.projectmodel.Project.Testsuites == '' || $scope.projectmodel.Project.Testsuites == undefined) {
                $scope.projectmodel.Project.Testsuites = {"Testsuite": []};
            }

            if ($scope.projectmodel.Project.Testsuites.Testsuite === '') {
                $scope.projectmodel.Project.Testsuites.Testsuite = [];
            }


            //Suites Section
            if (Array.isArray($scope.projectmodel.Project.Testsuites.Testsuite)) {
                $scope.suites = $scope.projectmodel.Project.Testsuites.Testsuite;
            } else {
                $scope.suites = [];
                $scope.suites.push($scope.projectmodel.Project.Testsuites.Testsuite);
            }
            $scope.showSavedSuite = [];
            for(var i=0; i<$scope.suites.length; i++){
                $scope.path_array.push([]);
                $scope.earlier_li.push("");
                $scope.btnValue.push("Edit");
                $scope.showModal.push({"visible":false});
                $scope.showSavedSuite.push(true);
                $scope.showTable = true;
            }

            $.each($scope.suites, function(index, value) {


                if (!value.hasOwnProperty('path')) {
                    value.path = "";
                }

                if (!value.hasOwnProperty('Execute')) {
                    value.Execute = {"_ExecType": "Yes",
                        "Rule": {"_Elsevalue": "",
                            "_Else": "next",
                            "_Condvalue": "",
                            "_Condition": ""
                        }
                    }
                }

                if(!value.Execute.hasOwnProperty('_ExecType')){
                    value.Execute._ExecType = "Yes";
                }

                if(!value.Execute.hasOwnProperty('Rule')){
                    value.Execute.Rule = {
                        "_Elsevalue": "",
                        "_Else": "next",
                        "_Condvalue": "",
                        "_Condition": ""
                        }
                }

                if(!value.Execute.Rule.hasOwnProperty('_Elsevalue')){
                    value.Execute.Rule._Elsevalue = "";
                }

                if(!value.Execute.Rule.hasOwnProperty('_Else')){
                    value.Execute.Rule._Else = "next";
                }

                if(!value.Execute.Rule.hasOwnProperty('_Condition')){
                    value.Execute.Rule._Condition = "";
                }

                if(!value.Execute.Rule.hasOwnProperty('_Condvalue')){
                    value.Execute.Rule._Condvalue = "";
                }

                if (!value.hasOwnProperty('onError')) {
                    value.onError = {"_action": "next", "_value": ""}
                }

                if(!value.onError.hasOwnProperty('_action')){
                    value.onError._action = "next";
                }

                if(!value.onError.hasOwnProperty('_value')){
                    value.onError._value = "";
                }

                if(!value.hasOwnProperty('impact')){
                    value.impact = "impact";
                }

                for(var i=0; i<$scope.suiteDefaultActions.length; i++){
                    if(value.onError._action.toLowerCase() == $scope.suiteDefaultActions[i].toLowerCase()){
                        value.onError._action = $scope.suiteDefaultActions[i];
                        break;
                    }
                }

                for(i=0; i<$scope.ExecuteTypes.length; i++){
                    if(value.Execute._ExecType.toLowerCase() == $scope.ExecuteTypes[i].toLowerCase()){
                        value.Execute._ExecType = $scope.ExecuteTypes[i];
                        break;
                    }
                }

                if(value.Execute.Rule._Condvalue != ""){
                    for(i=0; i<$scope.ConditionValueTypes.length; i++){
                        if(value.Execute.Rule._Condvalue.toLowerCase() == $scope.ConditionValueTypes[i].toLowerCase()){
                            value.Execute.Rule._Condvalue = $scope.ConditionValueTypes[i];
                            break;
                        }
                    }
                }

                for(i=0; i<$scope.impactOptions.length; i++){
                    if(value.impact.toLowerCase() == $scope.impactOptions[i].toLowerCase()){
                        value.impact = $scope.impactOptions[i];
                        break;
                    }
                }
            });


            $scope.saveSuite = function(index){
            var re = /^[0-9]*$/;
            var flag = true;
            if($scope.suites[index].path == "" || $scope.suites[index].path == undefined){
                flag = false;
                swal({
                      title: "Suite path is a mandatory field.",
                      text: "Please add in a suite path for suite " + (index + 1).toString(),
                      type: "error",
                      showCancelButton: false,
                      confirmButtonColor: '#3b3131',
                      confirmButtonText: "Ok",
                      closeOnConfirm: false});
            }
            if(flag) {
                if ($scope.suites[index].onError._action == "goto") {
                    if ($scope.suites[index].onError._value == "" || $scope.suites[index].onError._value == undefined) {
                        flag = false;
                        swal({
                              title: "Go To Step # for On Error Action cannot be empty!",
                              text: "",
                              type: "error",
                              showCancelButton: false,
                              confirmButtonColor: '#3b3131',
                              confirmButtonText: "Ok",
                              closeOnConfirm: false});
                    }
                    if(flag) {
                        if (!re.test($scope.suites[index].onError._value)) {
                            flag = false;
                            swal({
                              title: "Go To Step # for On Error Action can only be numerical.",
                              text: "",
                              type: "error",
                              showCancelButton: false,
                              confirmButtonColor: '#3b3131',
                              confirmButtonText: "Ok",
                              closeOnConfirm: false});
                        }
                    }
                }
            }
            if(flag) {
                if ($scope.suites[index].Execute._ExecType == "If" || $scope.suites[index].Execute._ExecType == "If Not") {
                    if ($scope.suites[index].Execute.Rule._Condition == "" || $scope.suites[index].Execute.Rule._Condition == undefined) {
                        flag = false;
                        swal({
                              title: "Condition for Execute Type cannot be empty",
                              text: "",
                              type: "error",
                              showCancelButton: false,
                              confirmButtonColor: '#3b3131',
                              confirmButtonText: "Ok",
                              closeOnConfirm: false});
                    }
                    if(flag) {
                        if ($scope.suites[index].Execute.Rule._Condvalue == "" || $scope.suites[index].Execute.Rule._Condvalue == undefined) {
                            flag = false;
                            swal({
                              title: "Condition Value for Execute type cannot be empty",
                              text: "",
                              type: "error",
                              showCancelButton: false,
                              confirmButtonColor: '#3b3131',
                              confirmButtonText: "Ok",
                              closeOnConfirm: false});
                        }
                    }
                    if(flag) {
                        if ($scope.suites[index].Execute.Rule._Else == "goto") {
                            if ($scope.suites[index].Execute.Rule._Elsevalue == "" || $scope.suites[index].Execute.Rule._Elsevalue == undefined) {
                                flag = false;
                                swal({
                                      title: "Go To Step # for Else Value cannot be empty!",
                                      text: "",
                                      type: "error",
                                      showCancelButton: false,
                                      confirmButtonColor: '#3b3131',
                                      confirmButtonText: "Ok",
                                      closeOnConfirm: false});
                            }
                            if(flag) {
                                if (!re.test($scope.suites[index].Execute.Rule._Elsevalue)) {
                                    flag = false;
                                    swal({
                                      title: "Go To Step # for Else Value can only be numerical.",
                                      text: "",
                                      type: "error",
                                      showCancelButton: false,
                                      confirmButtonColor: '#3b3131',
                                      confirmButtonText: "Ok",
                                      closeOnConfirm: false});
                                }
                            }
                        }
                    }
                }
            }
            if(flag){
                $scope.showSavedSuite[index] = true;
                $scope.showTable = true;
                $scope.suiteEditor = false;
                $scope.suiteBeingEdited = "None";
                $scope.suite_numbers = [];
            }
        };

        $scope.editSuite = function(index){
            if($scope.suiteEditor){
                swal({
                    title: "You have a Suite open in the suite editor that should be saved before editing another Suite.",
                    text: "Please save that Suite.",
                    type: "warning",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
            }
            else {
                $scope.suiteToBeCopied = "None";
                $scope.suite_numbers = [];
                for(var i=0; i<$scope.suites.length; i++){
                    if(i !== index){
                        $scope.suite_numbers.push(i+1);
                    }
                }
                $scope.suiteEditor = true;
                $scope.suiteBeingEdited = index;
                $scope.showSavedSuite[index] = false;
                tableIsShown();
            }
        };

        function tableIsShown(){
            var flag = true;
            for(var i=0; i<$scope.showSavedSuite.length; i++){
                if($scope.showSavedSuite[i]){
                    flag = false;
                    $scope.showTable = true;
                    break;
                }
            }
            if(flag){
                $scope.showTable = false;
            }
        }

            $scope.isGotoSelectedAction = function(action) {
                if (action != undefined) {
                    if (action.indexOf('goto') != -1) {
                        return true;
                    }
                }
                return false;
            };

            $scope.updateConditionList = function(param){
            for(var i=0; i<$scope.suites.length; i++){
                $scope.condition_list[i] = [];
                $scope.popoverContentList[i] = "";
                for(var j=0; j<i; j++){
                    $scope.condition_list[i].push("testsuite_"+(j+1).toString()+"_status");
                    if($scope.suites[j].path.trim() !== "") {
                        $scope.popoverContentList[i] = $scope.popoverContentList[i] + (j + 1) + ". \"" + $scope.suites[j].path + "\"<br />";
                    }
                    else{
                        $scope.popoverContentList[i] = $scope.popoverContentList[i] + (j + 1) + ". No Suite Path Entered<br />";
                    }
                }
            }

            if(param !== undefined){
                for(i=0; i<$scope.condition_list.length; i++){
                    if($scope.condition_list[i].length < 1){
                        if($scope.suites[i].Execute._ExecType !== "Yes" && $scope.suites[i].Execute._ExecType !== "No"){
                            $scope.suites[i].Execute._ExecType = "Yes";
                        }
                    }
                }
            }
        };

            $scope.isGotoSelectedActionIndex = function(action, index) {
                if (action != undefined) {
                    if (action.indexOf('goto') != -1) {
                        return true;
                    } else {
                        $scope.suites[index].onError._value = '';
                    }
                }
                return false;
            };

            $scope.deleteTestSuite = function(index) {
                 swal({
                     title: "Are you sure you want to delete this Suite?",
                     type: "warning",
                     showCancelButton: true,
                     confirmButtonText: "Yes, delete it!",
                     cancelButtonText: "No, Keep it.",
                     confirmButtonColor: '#3b3131',
                     closeOnConfirm: false,
                     closeOnCancel: false
                 },
                    function(isConfirm){
                        if (isConfirm) {
                            $scope.$apply(deleteSuite(index));
                            swal({
                                title: "Suite deleted",
                                timer: 1250,
                                type: "success",
                                showConfirmButton: false
                            });
                        } else {
                            swal({
                                title: "Suite not deleted",
                                timer: 1250,
                                type: "error",
                                showConfirmButton: false
                            });
                        }
                    });
            };

            function deleteSuite(index){
                $scope.suites.splice(index, 1);
                $scope.suiteDefaultActions.splice(index, 1);
                $scope.suiteDefaultGotoValue.splice(index, 1);
                $scope.path_array.splice(index, 1);
                $scope.earlier_li.splice(index, 1);
                $scope.btnValue.splice(index, 1);
                $scope.showModal.splice(index, 1);
                $scope.condition_list.splice(index, 1);
                $scope.popoverContentList.splice(index, 1);
                $scope.showSavedSuite.splice(index, 1);
                tableIsShown();
                $scope.updateConditionList();
                if($scope.suites.length == 0){
                    $scope.suiteEditor = false;
                    $scope.suiteBeingEdited = "None";
                    $scope.suite_numbers = [];
                }
                else if($scope.suiteBeingEdited != "None"){
                    if(index == $scope.suiteBeingEdited){
                        $scope.suiteEditor = false;
                        $scope.suiteBeingEdited = "None";
                        $scope.suite_numbers = [];
                    }
                }
            }

	    $scope.insertSuite = function(index) {
            if($scope.suiteEditor){
                swal({
                    title: "You have a Suite open in the suite editor that should be saved before creating a new Suite.",
                    text: "Please save that Suite.",
                    type: "warning",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
            }
            else {
                $scope.suiteToBeCopied = "None";
                $scope.suite_numbers = [];
                for(var i=0; i<$scope.suites.length; i++){
                    $scope.suite_numbers.push(i+1);
                }
                openSuiteCap(index);
            }
        };

            function openSuiteCap(index){
                $scope.suites.splice(index+1,0,{
                    "path": "",
                    "Execute": {
                    "_ExecType": "Yes",
                        "Rule": {
                            "_Elsevalue": "",
                            "_Else": "next",
                            "_Condvalue": "",
                            "_Condition": ""
                        }
                    },
                    "onError": {
                       "_action": "next",
                       "_value": ""
                    },
                    "impact": "impact"
                });

                $scope.path_array.splice(index+1,0, []);
                $scope.earlier_li.splice(index+1,0, "");
                $scope.btnValue.splice(index+1,0, "Edit");
                $scope.showModal.splice(index+1,0, {"visible": false});
                $scope.condition_list.splice(index+1, 0, []);
                $scope.popoverContentList.splice(index+1, 0, "");
                $scope.showSavedSuite.splice(index+1, 0, false);
                $scope.suiteBeingEdited = index + 1;
                $scope.suiteEditor = true;
                $scope.updateConditionList();
            }

            $scope.copySuite = function(){
                //alert($scope.suiteToBeCopied - 1);
                //alert($scope.suiteBeingEdited);

                if($scope.suiteToBeCopied == "None"){
                    swal({
                        title: "Please select a Suite number from the dropdown.",
                        type: "error",
                        showConfirmButton: true,
                        closeOnConfirm: true,
                        confirmButtonColor: '#3b3131',
                        confirmButtonText: "Ok"
                    });
                    return;
                }

                $scope.suites[$scope.suiteBeingEdited].path = $scope.suites[$scope.suiteToBeCopied - 1].path;
                $scope.suites[$scope.suiteBeingEdited].onError._action = $scope.suites[$scope.suiteToBeCopied - 1].onError._action;
                $scope.suites[$scope.suiteBeingEdited].onError._value = $scope.suites[$scope.suiteToBeCopied - 1].onError._value;
                $scope.suites[$scope.suiteBeingEdited].Execute._ExecType = $scope.suites[$scope.suiteToBeCopied - 1].Execute._ExecType;
                $scope.suites[$scope.suiteBeingEdited].Execute.Rule._Condition = $scope.suites[$scope.suiteToBeCopied - 1].Execute.Rule._Condition;
                $scope.suites[$scope.suiteBeingEdited].Execute.Rule._Condvalue = $scope.suites[$scope.suiteToBeCopied - 1].Execute.Rule._Condvalue;
                $scope.suites[$scope.suiteBeingEdited].Execute.Rule._Else = $scope.suites[$scope.suiteToBeCopied - 1].Execute.Rule._Else;
                $scope.suites[$scope.suiteBeingEdited].Execute.Rule._Elsevalue = $scope.suites[$scope.suiteToBeCopied - 1].Execute.Rule._Elsevalue;
                $scope.suites[$scope.suiteBeingEdited].impact = $scope.suites[$scope.suiteToBeCopied - 1].impact;
            };

            $scope.changeSuiteCapImpact = function(impact, index) {
                if (impact == true) {
                    $scope.suites[index].impact = 'impact';
                } else {
                    $scope.suites[index].impact = 'noimpact';
                }
            };

            //Impact Section
            $scope.isSuiteCapImpacted = function(index) {
                if ($scope.suites[index].impact == 'noimpact') {
                    $scope.changeSuiteCapImpact(false, index);
                    return false;
                } else {
                    $scope.changeSuiteCapImpact(true, index);
                    return true;
                }

            }

            $scope.saveProjectCap = function() {

                var hasSpace = _.find($.trim($scope.projectmodel.Project.Details.Name), function (c) {
                    return c == ' ';
                });
                if (hasSpace != undefined) {
                    swal({
                          title: "Please do not use spaces in the Name field of the Project.",
                          text: "The name field value is used as the name of the XML file to store this Project.\n\n" +
                          "We suggest that you use the underscore character (_) in lieu of the space character.",
                          type: "error",
                          showCancelButton: false,
                          confirmButtonColor: '#3b3131',
                          confirmButtonText: "Ok",
                          closeOnConfirm: false});
                    return;
                }

                if ($scope.projectmodel.Project.Details.Name == undefined || $scope.projectmodel.Project.Details.Name.trim().length == 0) {
                    swal({
                          title: "Project name is mandatory!",
                          text: "",
                          type: "error",
                          showCancelButton: false,
                          confirmButtonColor: '#3b3131',
                          confirmButtonText: "Ok",
                          closeOnConfirm: false
                    });
                } else if ($scope.projectmodel.Project.Details.Title == undefined || $scope.projectmodel.Project.Details.Title.trim().length == 0) {
                    swal({
                          title: "Project Title is mandatory!",
                          text: "",
                          type: "error",
                          showCancelButton: false,
                          confirmButtonColor: '#3b3131',
                          confirmButtonText: "Ok",
                          closeOnConfirm: false
                    });
                } else if ($scope.defaultProjectAction === 'goto' && $scope.projectGotoStep == undefined) {
                    swal({
                          title: "Step to go should be specified for default on error action GoTo!",
                          text: "",
                          type: "error",
                          showCancelButton: false,
                          confirmButtonColor: '#3b3131',
                          confirmButtonText: "Ok",
                          closeOnConfirm: false
                    });
                } else if ($scope.projectmodel.Project.Details.State === 'Add Another') {
                    swal({
                          title: "Please specify a new State to be added!",
                          text: "",
                          type: "error",
                          showCancelButton: false,
                          confirmButtonColor: '#3b3131',
                          confirmButtonText: "Ok",
                          closeOnConfirm: false
                    });
                } else if($scope.suites.length < 1 && $scope.projectmodel.Project.Details.State != "New"){
                    swal({
                          title: "A Suite should contain at least one Case!",
                          text: "Setting the Suite State to 'New' would let you create a Suite without any Cases",
                          type: "error",
                          showCancelButton: false,
                          confirmButtonColor: '#3b3131',
                          confirmButtonText: "Ok",
                          closeOnConfirm: false});
                }
                else {

                    var inValid = false;
                    var msg = '';

                    var re = /^[0-9]*$/;
                    $.each($scope.suites, function(index, value) {
                        var step = parseInt(index) + 1;
                        if (value.path == undefined || value.path === '') {
                            inValid = true;
                            msg = 'Path should be specified for the Suite ' + step + '!';
                            return false;
                        } else if (value.onError._action === 'goto' && (value.onError._value == undefined || value.onError._value === '')) {
                            inValid = true;
                            msg = 'Suite to go should be specified for default on error action GoTo for the Suite ' + step + '!';
                        } else if(value.Execute._ExecType == "If" || value.Execute._ExecType == "If Not"){
                            if(value.Execute.Rule._Condition == ""){
                                inValid = true;
                                msg = "Condition must be specified for Suite " + step + "!"
                            } else if(value.Execute.Rule._Condition !== "") {
                                if($scope.condition_list[step-1].indexOf(value.Execute.Rule._Condition) == -1){
                                    inValid = true;
                                    msg = "Condition must be specified for Suite " + step + "!"
                                }
                            } else if(value.Execute.Rule._Condvalue == ""){
                                inValid = true;
                                msg = "Condition Value must be specified for Suite " + step + "!"
                            } else if(value.Execute.Rule._Else == ""){
                                inValid = true;
                                msg = "Else must be specified for Suite " + step + "!"
                            }
                            else if(value.Execute.Rule._Else == "goto"){
                                if(!re.test(value.Execute.Rule._Elsevalue)){
                                    inValid = true;
                                    msg = "Else Value can contain only numeric values! Please correct Else value in Suite " + step;
                                } else if(value.Execute.Rule._Elsevalue.trim() == ""){
                                    inValid = true;
                                    msg = "Else Value cannot be empty! Please correct Else value in Suite " + step;
                                }
                            }
                        }
                    });

                    if (inValid) {
                        swal({
                          title: msg,
                          text: "",
                          type: "error",
                          showCancelButton: false,
                          confirmButtonColor: '#3b3131',
                          confirmButtonText: "Ok",
                          closeOnConfirm: false
                        });
                    } else {

                        var filename = $scope.projectmodel.Project.Details.Name + '.xml';

                        fileFactory.checkfileexistwithsubdir(filename, 'project', $scope.subdirs)
                            .then(
                                function(data) {
                                    console.log(data);
                                    var fileExist = data.response;

                                    if (fileExist == 'yes') {
                                        swal({
                                            title: "A file with this name already exists. Do you want to overwite it?",
                                            text: "",
                                            type: "warning",
                                            showCancelButton: true,
                                            confirmButtonText: "Yes!",
                                            cancelButtonText: "No, don't overwrite.",
                                            confirmButtonColor: '#3b3131',
                                            closeOnConfirm: false,
                                            closeOnCancel: false
                                        },
                                            function(isConfirm){
                                                if (isConfirm) {
                                                    swal({
                                                        title: "Overwriting File",
                                                        timer: 1250,
                                                        type: "success",
                                                        showConfirmButton: false
                                                    });
                                                    save(filename);
                                                } else {
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
                }
            }

           $scope.cancelProjectCap = function() {
                $location.path('/projects');
            }

            function save(filename) {
                var finalJSON = {
                    "Project": {
                        "Details": {
                            "Name": $scope.projectmodel.Project.Details.Name,
                            "Title": $scope.projectmodel.Project.Details.Title,
                            "Engineer": $scope.projectmodel.Project.Details.Engineer,
                            "State":$scope.projectmodel.Project.Details.State,
                            "Date": $scope.projectmodel.Project.Details.Date,
                            "Time": $scope.projectmodel.Project.Details.Time,
                            "default_onError": {
                                "_action": $scope.defaultProjectAction,
                                "_value": $scope.projectGotoStep
                            }
                        },
                        "Testsuites": {
                            "Testsuite": $scope.suites
                        }
                    }
                }

                var x2js = new X2JS();
                var token = angular.toJson(finalJSON);
                var xmlObj = x2js.json2xml_str(JSON.parse(token));
                setProjectFactory.projectsave(filename, $scope.subdirs, xmlObj)
                    .then(
                        function(data) {
                            console.log(data);
                            if ($scope.savecreateProjectCap == true) {
                                // $location.path('/newproject');
                            }  else {
                                $location.path('/projects');
                            }
                        },
                        function(data) {
                            alert(data);
                        });


            }

            $scope.projectSaveCreate = function() {

                if ($scope.projectmodel.Project.Details.Name == undefined || $scope.projectmodel.Project.Details.Name.trim().length == 0) {
                    swal({
                          title: "Project name is mandatory!",
                          text: "",
                          type: "error",
                          showCancelButton: false,
                          confirmButtonColor: '#3b3131',
                          confirmButtonText: "Ok",
                          closeOnConfirm: false
                    });
                } else if ($scope.defaultProjectAction === 'goto' && $scope.projectGotoStep == undefined) {
                    swal({
                          title: "Step to go should be specified for default on error action GoTo!",
                          text: "",
                          type: "error",
                          showCancelButton: false,
                          confirmButtonColor: '#3b3131',
                          confirmButtonText: "Ok",
                          closeOnConfirm: false
                    });
                }  else {
                    var inValid = false;
                    var msg = '';

                    $.each($scope.suites, function(index, value) {
                        var step = parseInt(index) + 1;
                        if (value.path == undefined || value.path === '') {
                            inValid = true;
                            msg = 'Path should be specified for the Suite ' + step + '!';
                            return false;
                        } else if (value.onError._action === 'goto' && (value.onError._value == undefined || value.onError._value === '')) {
                            inValid = true;
                            msg = 'Suite to go should be specified for default on error action GoTo for the Suite ' + step + '!';
                        }
                    });

                    if (inValid) {
                        swal({
                              title: msg,
                              text: "",
                              type: "error",
                              showCancelButton: false,
                              confirmButtonColor: '#3b3131',
                              confirmButtonText: "Ok",
                              closeOnConfirm: false
                        });
                    } else {

                        var finalJSON = {
                            "Project": {
                                "Details": {
                                    "Name": $scope.projectmodel.Project.Details.Name,
                                    "Title": $scope.projectmodel.Project.Details.Title,
                                    "default_onError": {
                                        "_action": $scope.defaultProjectAction,
                                        "_value": $scope.projectGotoStep
                                    }
                                },
                                "Testsuites": {
                                    "Testsuite": $scope.suites
                                }
                            }
                        }

                        var x2js = new X2JS();
                        var token = angular.toJson(finalJSON);
                        var xmlObj = x2js.json2xml_str(JSON.parse(token));
                        setProjectFactory.projectsave(xmlObj)
                            .then(
                                function(data) {
                                    console.log(data);
                                },
                                function(data) {
                                    alert(data);
                                });
                        $location.path('/newproject');
                    }
                }
            }

            $scope.projectSaveas = function() {

                if ($scope.projectmodel.Project.Details.Name == undefined || $scope.projectmodel.Project.Details.Name.trim().length == 0) {
                    swal({
                          title: "Project name is mandatory!",
                          text: "",
                          type: "error",
                          showCancelButton: false,
                          confirmButtonColor: '#3b3131',
                          confirmButtonText: "Ok",
                          closeOnConfirm: false
                    });
                } else if ($scope.defaultProjectAction === 'goto' && $scope.projectGotoStep == undefined) {
                    swal({
                          title: "Step to go should be specified for default on error action GoTo!",
                          text: "",
                          type: "error",
                          showCancelButton: false,
                          confirmButtonColor: '#3b3131',
                          confirmButtonText: "Ok",
                          closeOnConfirm: false
                    });
                }  else {

                    var inValid = false;
                    var msg = '';

                    $.each($scope.suites, function(index, value) {
                        var step = parseInt(index) + 1;
                        if (value.path == undefined || value.path === '') {
                            inValid = true;
                            msg = 'Path should be specified for the Suite ' + step + '!';
                            return false;
                        } else if (value.onError._action === 'goto' && (value.onError._value == undefined || value.onError._value === '')) {
                            inValid = true;
                            msg = 'Suite to go should be specified for default on error action GoTo for the Suite ' + step + '!';
                        }
                    })

                    if (inValid) {
                        swal({
                              title: msg,
                              text: "",
                              type: "error",
                              showCancelButton: false,
                              confirmButtonColor: '#3b3131',
                              confirmButtonText: "Ok",
                              closeOnConfirm: false
                        });
                    } else {

                        var filename = prompt("Enter the filename :", $scope.projectFilename);

                        if (filename == undefined || filename.trim().length == 0) {
                            swal({
                                  title: "Filename should be provided!",
                                  text: "",
                                  type: "error",
                                  showCancelButton: false,
                                  confirmButtonColor: '#3b3131',
                                  confirmButtonText: "Ok",
                                  closeOnConfirm: false
                            });
                            return false;
                        } else {
                            filename = filename + ".xml";
                            var finalJSON = {
                                "Project": {
                                    "Details": {
                                        "Name": $scope.projectmodel.Project.Details.Name,
                                        "Title": $scope.projectmodel.Project.Details.Title,
                                        "default_onError": {
                                            "_action": $scope.defaultProjectAction,
                                            "_value": $scope.projectGotoStep
                                        }
                                    },
                                    "Testsuites": {
                                        "Testsuite": $scope.suites
                                    }
                                }
                            }
                            var x2js = new X2JS();
                            var token = angular.toJson(finalJSON);
                            var xmlObj = x2js.json2xml_str(JSON.parse(token));
                            saveasProjectFactory.projectsaveas(filename, xmlObj)
                                .then(
                                    function(data) {
                                        console.log(data);
                                    },
                                    function(data) {
                                        alert(data);
                                    });
                            $location.path('/projects');
                        }
                    }
                }
            };
            fileFactory.readdatafile()
            .then(
                function(data) {
                    $scope.alldirinfo = data;
                    $scope.table = $scope.table + "<ul class=\"collapsibleList\" id='path_list'>";
                    get_folders_names($scope.alldirinfo);
                    $scope.table = $scope.table + "</ul>";
                },
                function(data) {
                    alert(data);
                });
        }, 500);
    }
]);
