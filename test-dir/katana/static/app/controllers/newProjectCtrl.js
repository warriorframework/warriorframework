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

app.controller('newProjectCtrl', ['$scope', '$http', '$controller', '$location', '$route', 'saveasProjectFactory', 'fileFactory', 'getConfigFactory', 'subdirs',
    function($scope, $http, $controller, $location, $route, saveasProjectFactory, fileFactory, getConfigFactory, subdirs) {

        $scope.subdirs = subdirs;
        $scope.defaultProjectActions = ['next', 'abort', 'abort_as_error', 'goto'];
        $scope.newProjecttooltips = {};
        $scope.alldirinfo = "";
        $scope.table = "";
        $scope.path_array = [];
        $scope.earlier_li = [];
        $scope.btnValue = [];
        $scope.projectstates = "";
        $scope.new_state = "";
        $scope.State = "";
        $scope.showModal =  [];
        $scope.condition_list = [[]];
        $scope.popoverContentList = [""];
        $scope.showSavedSuite = [false];
        $scope.showTable = false;
        $scope.suiteToBeCopied = "None";
        $scope.suite_numbers = [];
        $scope.suiteEditor = true;
        $scope.suiteBeingEdited = "None";
        $scope.newDate = '';
        $scope.newTime = '';
        $scope.newEng = '';

        $scope.ExecuteTypes = ['Yes', 'If', 'If Not', 'No'];
        $scope.FirstExecuteTypes = ['Yes', 'No'];
        $scope.ruleElseTypes = ['next', 'abort', 'abort_as_error', 'goto'];
        $scope.ConditionValueTypes = ['PASS', 'FAIL', 'ERROR', 'SKIP'];
        $scope.impactOptions = ['impact', 'noimpact'];

        var ChildCtrl=this;
        ChildCtrl.baseCtrl = $controller('baseChariotCtrl',{ $scope: $scope, $http: $http });
        ChildCtrl.baseCtrl.readConfig();

        $scope.newDate = ChildCtrl.baseCtrl.getDate();
        $scope.newTime = ChildCtrl.baseCtrl.getTime();

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
                var checkDir = filepath.split("Suites/")[1].split(splitPath)[0]; 
                checkDir = checkDir.slice(0, -1);
                checkDir = checkDir.replace(/\//g,','); 
                var finalUrlDir = "#/testsuite/"+splitter+checkDir;
                window.open(finalUrlDir);
            }
        }
        else{                                                                     //For files outside the Warrior directory
            var dataDir = $scope.cfg.idfdir;
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
                 {                                                                  //Mismatched Config and selected path;   
                sweetAlert({
                    title: "Config Path mismatch witn the selected path !",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131',
                    confirmButtonText: "Ok",
                    type: "info"
                });
              }
          }
        } 
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
                fileFactory.updatestatesfile("projectstate%"+$scope.new_state)
                    .then(
                        function(data) {
                            var check = data["check"];
                            if(check){
                                $scope.projectstates.pop();
                                $scope.projectstates.push($scope.new_state);
                                $scope.projectstates.push("Add Another");
                                $scope.State = $scope.new_state;
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
                    $scope.newEng = $scope.cfg.engineer;
                    console.log(data);
                    $scope.newProjecttooltips = data;
                },
                function(data) {
                    alert(data);
                });

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
        fileFactory.readstatesfile()
            .then(
                function(data) {
                    console.log(data);
                    $scope.projectstates = data["projectstate"];
                },
                function(data) {
                    alert(data);
                });

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

        $scope.storePaths = function(index){
            var suite_folder_array = [];
            var project_folder_array = [];
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

        $scope.monitorPathBtnValue = function(index){
            if($scope.suites[index].path === undefined || $scope.suites[index].path === ""){
                $scope.btnValue[index] = "Path";
            } else {
                $scope.btnValue[index] = "Edit";
            }
        };


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

        $scope.isGotoSelectedProject = function() {
            if ($scope.defaultProjectAction == 'goto') {
                return true;
            } else {
                return false;
            }
        };

        $scope.isAddAnotherSelectedSuite = function() {
            if ($scope.State == 'Add Another') {
                console.log("Add Another");
                return true;
            } else {
                return false;
            }
        };

        $scope.isGotoSelectedSuite = function(action) {
            if (action != undefined) {
                if (action.indexOf('goto') != -1) {
                    return true;
                }
            }
            return false;
        };

        $scope.suites = [{
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
        }];
        $scope.showModal.push({"visible":false});
        $scope.btnValue.push("Path");
        $scope.path_array.push([]);
        $scope.earlier_li.push("");

        $scope.deleteSuite = function(index) {
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

            $scope.showModal.splice(index+1,0,{"visible":false});
            $scope.btnValue.splice(index+1,0,"Path");
            $scope.path_array.splice(index+1,0,[]);
            $scope.earlier_li.splice(index+1,0,"");

            $scope.condition_list.splice(index+1, 0, []);
            $scope.popoverContentList.splice(index+1, 0, "");

            $scope.showSavedSuite.splice(index+1, 0, false);
            $scope.suiteBeingEdited = index + 1;
            $scope.suiteEditor = true;

            $scope.updateConditionList();
        }

        $scope.copySuite = function(){
            //alert($scope.suiteToBeCopied - 1)
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

        $scope.saveProject = function() {

            var hasSpace = _.find($.trim($scope.projectName), function (c) {
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
                      closeOnConfirm: false
                });
                return;
            }

            if ($scope.projectName == undefined || $scope.projectName.trim().length == 0) {
                swal({
                      title: "Project name is mandatory!",
                      text: "",
                      type: "error",
                      showCancelButton: false,
                      confirmButtonColor: '#3b3131',
                      confirmButtonText: "Ok",
                      closeOnConfirm: false
                });
            } else if ($scope.projectTitle == undefined || $scope.projectTitle.trim().length == 0) {
                swal({
                      title: "Project Title is mandatory!",
                      text: "",
                      type: "error",
                      showCancelButton: false,
                      confirmButtonColor: '#3b3131',
                      confirmButtonText: "Ok",
                      closeOnConfirm: false
                });
            } else if ($scope.defaultProjectAction === 'goto' && $scope.gotoStep == undefined) {
                swal({
                      title: "Step to go should be specified for default on error action GoTo!",
                      text: "",
                      type: "error",
                      showCancelButton: false,
                      confirmButtonColor: '#3b3131',
                      confirmButtonText: "Ok",
                      closeOnConfirm: false
                });
            } else if ($scope.State === 'Add Another') {
                swal({
                      title: "Please specify a new State to be added!",
                      text: "",
                      type: "error",
                      showCancelButton: false,
                      confirmButtonColor: '#3b3131',
                      confirmButtonText: "Ok",
                      closeOnConfirm: false
                });
            } else if($scope.suites.length < 1 && $scope.State != "New"){
                swal({
                      title: "A Project should contain at least one Suite!",
                      text: "Setting the Project State to 'New' would let you create a Project without any Suites",
                      type: "error",
                      showCancelButton: false,
                      confirmButtonColor: '#3b3131',
                      confirmButtonText: "Ok",
                      closeOnConfirm: false
                });
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

                    var filename = $scope.projectName + ".xml";

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
                                        confirmButtonColor: '#3b3131',
                                        cancelButtonText: "No, don't overwrite.",
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

        $scope.cancelProject = function() {
            $location.path('/projects');
        }

        function save(filename) {
            var finalJSON = {
                "Project": {
                    "Details": {
                        "Name": $scope.projectName,
                        "Title": $scope.projectTitle,
                        "Engineer": $scope.newEng,
                        "State": $scope.State,
                        "Date": $scope.newDate,
                        "Time": $scope.newTime,
                        "default_onError": {
                            "_action": $scope.defaultProjectAction,
                            "_value": $scope.gotoStep
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
            saveasProjectFactory.projectsaveas(filename, subdirs, xmlObj)
                .then(
                    function(data) {
                        console.log(data);
                        if ($scope.savecreateProject == true) {
                            // $route.reload();
                        }  else {
                            $location.path('/projects');
                        }
                    },
                    function(data) {
                        alert(data);
                    });


        }
    }
]);
