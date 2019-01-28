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

app.controller('newTestsuiteCtrl', ['$scope', '$http', '$location', '$route', '$controller', '$timeout', 'saveNewTestsuiteFactory', 'fileFactory', 'getConfigFactory', 'subdirs',
    function($scope, $http, $location, $route, $controller, $timeout, saveNewTestsuiteFactory, fileFactory, getConfigFactory, subdirs) {

        $scope.subdirs = subdirs;
        $scope.resultsdirSuite = '';
        $scope.IDFSuite = '';
        $scope.suitereqs = [];
        $scope.date = new Date();
        $scope.newtestsuiteTooltip = [];
        $scope.alldirinfo = "";
        $scope.table = "";
        $scope.path_array = [];
        $scope.td_df_path_array = [];
        $scope.earlier_li = [];
        $scope.td_df_earlier_li = [];
        $scope.btnValue=[];
        $scope.td_df_btnValue=[];
        $scope.idf_btnValue = "Path";
        $scope.idf_path_array = [];
        $scope.idf_earlier_li = "";
        $scope.showModal = [];
        $scope.td_df_showModal = [];
        $scope.showSavedSuite = [false];
        $scope.showTable = false;
        $scope.showReqEditor = false;
        $scope.newReq = "";
        $scope.index = false;
        $scope.testcaseToBeCopied = "None";
        $scope.testcase_numbers = [];
        $scope.testcaseEditor = true;
        $scope.testcaseBeingEdited = "None";
        $scope.newDate = '';
        $scope.newTime = '';
        $scope.newEng = '';
        $scope.btnValueJocket = "Path";
        $scope.showModalJ = {visible: false};



       function readConfig(){
          getConfigFactory.readconfig()
          .then(function (data) {
             $scope.cfg = data;
            });
      }

      readConfig();

//To Load the Case File from Suite
//Works for base Directory as well as Subdirectories
     $scope.loadFile = function(filepath) {
        var checkFlag = filepath.includes("..");
        if(checkFlag==true){                                                      //For files inside the Warrior directory
             dirCheck=filepath.split("/").reverse()[1];
             if(dirCheck=="Testcases"){                                           //Fetch Parent directory files
                splitDir = filepath.split('/Testcases')[1];
                finalUrl = "#/testcase"+splitDir+"/none";
                window.open(finalUrl);
             }
             else if(dirCheck=="testcases"){
                splitDir = filepath.split('/testcases')[1];
                finalUrl = "#/testcase"+splitDir+"/none";
                window.open(finalUrl);
             }
            else{                                                                 //Fetch subdirectory files
                splitPath = filepath.split("/").pop(-1);
                splitter = splitPath+"/";
                if(filepath.includes("Testcases")==true){
                var checkDir = filepath.split("Testcases/")[1].split(splitPath)[0];
                }
                else{var checkDir = filepath.split("testcases/")[1].split(splitPath)[0];}
                   checkDir = checkDir.slice(0, -1);
                   checkDir = checkDir.replace(/\//g,',');
                   finalUrlDir = "#/testcase/"+splitter+checkDir;
                   window.open(finalUrlDir);
            }
        }
        else{                                                                     //For files outside the Warrior directory
            testcaseDir = $scope.cfg.testsuitedir;
            var matchPath = filepath.includes(testcaseDir);
            if(matchPath == true){
              splitPath = filepath.split(testcaseDir)[1];
              fileName = splitPath.split("/").pop(-1);
              splitter = fileName+"/";
              checkDir = filepath.split(testcaseDir)[1].split(fileName)[0];
              checkDir = checkDir.slice(0, -1);
              checkDir = checkDir.replace(/\//g,',');
              finalUrlDir = "#/testcase/"+splitter+checkDir;
              window.open(finalUrlDir);
          }
            else{
            if(filepath != '')
                 {                                                                  //Mismatched Config and selected path;
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



//To Load the InputData File from Suite
//Works for base Directory as well as Subdirectories
    $scope.loadDataFile = function(filepath) {
        var checkFlag = filepath.includes("..");
        if(checkFlag==true){                                                      //For files inside the Warrior directory
             dirCheck=filepath.split("/").reverse()[1];
             if(dirCheck=="Data"){                                           //Fetch Parent directory files
                splitDir = filepath.split('/Data')[1];
                finalUrl = "#/datafile"+splitDir+"/none";
                window.open(finalUrl);
             }
             else if(dirCheck=="data"){
                splitDir = filepath.split('/data')[1];
                finalUrl = "#/datafile"+splitDir+"/none";
                window.open(finalUrl);
             }
            else{                                                                 //Fetch subdirectory files
                splitPath = filepath.split("/").pop(-1);
                splitter = splitPath+"/";
                if(filepath.includes("Data")==true){
                var checkDir = filepath.split("Data/")[1].split(splitPath)[0];
                }
                else{var checkDir = filepath.split("data/")[1].split(splitPath)[0];}
                      checkDir = checkDir.slice(0, -1);
                      checkDir = checkDir.replace(/\//g,',');
                      finalUrlDir = "#/datafile/"+splitter+checkDir;
                      window.open(finalUrlDir);
            }
        }
        else{                                                                     //For files outside the Warrior directory
            dataDir = $scope.cfg.idfdir;
            var matchPath = filepath.includes(dataDir);
            if(matchPath == true){
              splitPath = filepath.split(dataDir)[1];
              fileName = splitPath.split("/").pop(-1);
              splitter = fileName+"/";
              checkDir = filepath.split(dataDir)[1].split(fileName)[0];
              checkDir = checkDir.slice(0, -1);
              checkDir = checkDir.replace(/\//g,',');
              finalUrlDir = "#/datafile/"+splitter+checkDir;
              window.open(finalUrlDir);
          }
            else{
            if(filepath != '')
                 {                                                                  //Mismatched Config and selected path;
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

        fileFactory.readdatafile()
            .then(
                function(data) {
                    $scope.alldirinfo = data;
                    $scope.table = $scope.table + "<ul class=\"collapsibleList\" id='path_list'>";
                    get_folders_names($scope.alldirinfo);
                    $scope.table = $scope.table + "</ul>";
                    document.getElementById("idf_tree_div").innerHTML = $scope.table;
                    CollapsibleLists.applyTo(document.getElementById('idf_tree_div'));
                    document.getElementById("tree_div_j").innerHTML = $scope.table;
                    CollapsibleLists.applyTo(document.getElementById('tree_div_j'));
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
            var tc_folder_array = [];
            var suite_folder_array = [];
            var folder_index = -1;
            var final_array = [];
            $scope.testcases[index].path = "";
            if($scope.cfg.xmldir.indexOf('/') === -1) {
                tc_folder_array = $scope.cfg.xmldir.split("\\");
            }
            else{
                tc_folder_array = $scope.cfg.xmldir.split("/");
            }
            for(var i=0; i<tc_folder_array.length; i++){
                if(tc_folder_array[i] === $scope.path_array[index][$scope.path_array[index].length-1]){
                    tc_folder_array.splice(i, (tc_folder_array.length-i));
                    break;
                }
            }
            for(i=$scope.path_array[index].length-1; i>=0; i--){
                tc_folder_array.push($scope.path_array[index][i])
            }
            if($scope.cfg.testsuitedir.indexOf('/') === -1) {
                suite_folder_array = $scope.cfg.testsuitedir.split("\\");
            }
            else{
                suite_folder_array = $scope.cfg.testsuitedir.split("/");
            }
            if($scope.subdirs != "none"){
                var subdir_array = $scope.subdirs.split(",");
                for(i=0; i<subdir_array.length; i++){
                    suite_folder_array.push(subdir_array[i]);
                }
            }
            for(i=0; i<suite_folder_array.length; i++){
                if(tc_folder_array[i] !== suite_folder_array[i]){
                    folder_index = i;
                    break;
                }
            }
            if(folder_index !== -1) {
                var dots = suite_folder_array.length - folder_index;
                for (i = 0; i < dots; i++) {
                    final_array.push("..");
                }
            } else {
                folder_index = suite_folder_array.length;
            }
            for(i=folder_index; i<tc_folder_array.length; i++){
                final_array.push(tc_folder_array[i]);
            }
            for (i = 0; i < final_array.length; i++) {
                $scope.testcases[index].path = $scope.testcases[index].path + final_array[i] + "/"
            }
            if (!$scope.testcases[index].path.match(/\.\.\/$/)) {
                $scope.testcases[index].path = $scope.testcases[index].path.slice(0, -1);
            }
            $scope.btnValue[index]="Edit";
            $scope.toggleModal(index);
        };

        $scope.td_df_storePaths = function(index){
            var td_df_folder_array = [];
            var suite_folder_array = [];
            var folder_index = -1;
            var final_array = [];
            $scope.testcases[index].InputDataFile = "";
            if($scope.cfg.idfdir.indexOf('/') === -1) {
                td_df_folder_array = $scope.cfg.idfdir.split("\\");
            }
            else{
                td_df_folder_array = $scope.cfg.idfdir.split("/");
            }
            for(var i=0; i<td_df_folder_array.length; i++){
                if(td_df_folder_array[i] === $scope.td_df_path_array[index][$scope.td_df_path_array[index].length-1]){
                    td_df_folder_array.splice(i, (td_df_folder_array.length-i));
                    break;
                }
            }
            for(i=$scope.td_df_path_array[index].length-1; i>=0; i--){
                td_df_folder_array.push($scope.td_df_path_array[index][i])
            }
            if($scope.cfg.testsuitedir.indexOf('/') === -1) {
                suite_folder_array = $scope.cfg.testsuitedir.split("\\");
            }
            else{
                suite_folder_array = $scope.cfg.testsuitedir.split("/");
            }
            if($scope.subdirs != "none"){
                var subdir_array = $scope.subdirs.split(",");
                for(i=0; i<subdir_array.length; i++){
                    suite_folder_array.push(subdir_array[i]);
                }
            }
            for(i=0; i<suite_folder_array.length; i++){
                if(td_df_folder_array[i] !== suite_folder_array[i]){
                    folder_index = i;
                    break;
                }
            }
            if(folder_index !== -1) {
                var dots = suite_folder_array.length - folder_index;
                for (i = 0; i < dots; i++) {
                    final_array.push("..");
                }
            }else{
                folder_index = suite_folder_array.length;
            }
            for (i = folder_index; i < td_df_folder_array.length; i++) {
                final_array.push(td_df_folder_array[i]);
            }
            if (!$scope.testcases[index].InputDataFile.match(/\.\.\/$/)) {
                $scope.testcases[index].InputDataFile = $scope.testcases[index].InputDataFile.slice(0, -1);
            }
            $scope.td_df_btnValue[index]="Edit";
            $scope.td_df_toggleModal(index);
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

        $scope.td_df_getPaths = function(e, index){

             $scope.td_df_path_array[index] = [];
             $scope.td_df_earlier_li[index].className = "";
             if(e == undefined){
                 e = window.event;
             }
             var li = (e.target ? e.target : e.srcElement);
             var temp_name = li.innerHTML.split("<");
             $scope.td_df_path_array[index].push(temp_name[0]);
             var li_temp = li;
             while(li_temp.parentNode.id.substring(0, 14) != "td_df_tree_div"){
                 if(!li_temp.parentNode.innerHTML.match(/^</)){
                     var temp_list = li_temp.parentNode.innerHTML.split("<");
                     $scope.td_df_path_array[index].push(temp_list[0]);
                 }
                 li_temp = li_temp.parentNode
             }
             if (li.className == ""){
                 li.className = "colorChange";
                 $scope.td_df_earlier_li[index] = li;
             }
        };

        $scope.suitestates = "";
        $scope.new_state = "";
        $scope.State = "";

        var ChildCtrl=this;
        ChildCtrl.baseCtrl = $controller('baseChariotCtrl',{ $scope: $scope, $http: $http });
        ChildCtrl.baseCtrl.readConfig();

        $scope.newDate = ChildCtrl.baseCtrl.getDate();
        $scope.newTime = ChildCtrl.baseCtrl.getTime();

        $scope.toggleModal = function(index){
            document.getElementById("tree_div-" + index.toString()).innerHTML = $scope.table;
            CollapsibleLists.applyTo(document.getElementById("tree_div-" + index.toString()));
            $scope.showModal[index].visible = !$scope.showModal[index].visible;
        };

        $scope.td_df_toggleModal = function(index){
            document.getElementById("td_df_tree_div-" + index.toString()).innerHTML = $scope.table;
            CollapsibleLists.applyTo(document.getElementById("td_df_tree_div-" + index.toString()));
            $scope.td_df_showModal[index].visible = !$scope.td_df_showModal[index].visible;
        };

        $scope.idf_monitorPathBtnValue = function(){
            if($scope.IDFSuite === undefined || $scope.IDFSuite === ""){
                $scope.idf_btnValue = "Path";
            } else {
                $scope.idf_btnValue = "Edit";
            }
        };

        $scope.monitorPathBtnValue = function(index){
            if($scope.testcases[index].path === undefined || $scope.testcases[index].path === ""){
                $scope.btnValue[index] = "Path";
            } else {
                $scope.btnValue[index] = "Edit";
            }
        };

        $scope.td_df_monitorPathBtnValue = function(index){
            if($scope.testcases[index].InputDataFile === undefined || $scope.testcases[index].InputDataFile === ""){
                $scope.td_df_btnValue[index] = "Path";
            } else {
                $scope.td_df_btnValue[index] = "Edit";
            }
        };

        $scope.idf_showModal =  {visible: false};

        $scope.idf_toggleModal = function(){
            $scope.idf_showModal.visible = !$scope.idf_showModal.visible;
        };

        $scope.idf_getPaths = function(e) {
             $scope.idf_path_array = [];
             $scope.idf_earlier_li.className = "";
             if(e == undefined){
                 e = window.event;
             }
             var idf_li = (e.target ? e.target : e.srcElement);
             var temp_name = idf_li.innerHTML.split("<");
             $scope.idf_path_array.push(temp_name[0]);
             var idf_li_temp = idf_li;
             while(idf_li_temp.parentNode.id != "idf_tree_div"){
                 if(!idf_li_temp.parentNode.innerHTML.match(/^</)){
                     var temp_list = idf_li_temp.parentNode.innerHTML.split("<");
                     $scope.idf_path_array.push(temp_list[0]);
                 }
                 idf_li_temp = idf_li_temp.parentNode
             }
             if (idf_li.className == ""){
                 idf_li.className = "colorChange";
                 $scope.idf_earlier_li = idf_li;
             }
        };

        $scope.idf_storePaths = function() {
            var idf_tc_folder_array = [];
            var idf_data_folder_array = [];
            var idf_folder_index = -1;
            var idf_final_array = [];
            $scope.IDFSuite = "";
            if ($scope.cfg.idfdir.indexOf('/') === -1) {
                idf_data_folder_array = $scope.cfg.idfdir.split("\\");
            }
            else {
                idf_data_folder_array = $scope.cfg.idfdir.split("/");
            }
            for (var i = 0; i < idf_data_folder_array.length; i++) {
                if (idf_data_folder_array[i] === $scope.idf_path_array[$scope.idf_path_array.length - 1]) {
                    idf_data_folder_array.splice(i, (idf_data_folder_array.length - i));
                    break;
                }
            }
            for (i = $scope.idf_path_array.length - 1; i >= 0; i--) {
                idf_data_folder_array.push($scope.idf_path_array[i])
            }
            if ($scope.cfg.testsuitedir.indexOf('/') === -1) {
                idf_tc_folder_array = $scope.cfg.testsuitedir.split("\\");
            }
            else {
                idf_tc_folder_array = $scope.cfg.testsuitedir.split("/");
            }
            if($scope.subdirs != "none"){
                var subdir_array = $scope.subdirs.split(",");
                for(i=0; i<subdir_array.length; i++){
                    idf_tc_folder_array.push(subdir_array[i]);
                }
            }
            for (i = 0; i < idf_tc_folder_array.length; i++) {
                if (idf_data_folder_array[i] !== idf_tc_folder_array[i]) {
                    idf_folder_index = i;
                    break;
                }
            }
            if (idf_folder_index !== -1) {
                var dots = idf_tc_folder_array.length - idf_folder_index;
                for (i = 0; i < dots; i++) {
                    idf_final_array.push("..");
                }
            } else {
                idf_folder_index = idf_tc_folder_array.length;
            }
            for (i = idf_folder_index; i < idf_data_folder_array.length; i++) {
                idf_final_array.push(idf_data_folder_array[i]);
            }
            for (i = 0; i < idf_final_array.length; i++) {
                $scope.IDFSuite = $scope.IDFSuite + idf_final_array[i] + "/"
            }
            if (!$scope.IDFSuite.match(/\.\.\/$/)) {
                $scope.IDFSuite = $scope.IDFSuite.slice(0, -1);
            }
            $scope.idf_btnValue = "Edit";
            $scope.idf_toggleModal();
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
                      closeOnConfirm: false});
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
                      closeOnConfirm: false});
            }
            else{
                fileFactory.updatestatesfile("suitestate%"+$scope.new_state)
                    .then(
                        function(data) {
                            var check = data["check"];
                            if(check){
                                $scope.suitestates.pop();
                                $scope.suitestates.push($scope.new_state);
                                $scope.suitestates.push("Add Another");
                                $scope.State = $scope.new_state;
                                $scope.new_state = "";
                            }
                            else{
                                swal({
                                      title: "States file could not be updated!",
                                      text: "",
                                      type: "warning",
                                      showCancelButton: false,
                                      confirmButtonColor: '#3b3131',
                                      confirmButtonText: "Ok",
                                      closeOnConfirm: false});
                            }
                        },
                        function(data) {
                            alert(data);
                        });
            }
        };

        $scope.testcases = [{
            "path": "",
            "context": "positive",
            "InputDataFile": "",
            "runtype": "sequential_keywords",
            "onError": {
                "_action": "next",
                "_value": ""
            },
            "runmode": {
                "_type": "Standard",
                "_value": ""
            },
            "Execute": {
                "_ExecType": "Yes",
                "Rule": {
                    "_Elsevalue": "",
                    "_Else": "next",
                    "_Condvalue": "",
                    "_Condition": ""
                }
            },
            "impact": "impact"
        }];

        $scope.condition_list = [[]];
        $scope.popoverContentList = [""];

        fileFactory.readtooltipfile('testsuite')
            .then(
                function(data) {
                    $scope.newEng = $scope.cfg.engineer;
                    console.log(data);
                    $scope.newtestsuiteTooltip = data;
                },
                function(data) {
                    alert(data);
                });


        fileFactory.readstatesfile()
            .then(
                function(data) {
                    console.log(data);
                    $scope.suitestates = data["suitestate"];
                },
                function(data) {
                    alert(data);
                });

        $scope.showModal.push({"visible": false});
        $scope.td_df_showModal.push({"visible": false});
        $scope.btnValue.push("Path");
        $scope.td_df_btnValue.push("Path");
        $scope.path_array.push([]);
        $scope.td_df_path_array.push([]);
        $scope.earlier_li.push("");
        $scope.td_df_earlier_li.push("");
        $scope.defaultRuntypes = ['sequential_keywords', 'parallel_keywords']; //Options in the dropdown for the default on runtype.
        $scope.defaultRuntype = 'sequential_keywords'; //this will be the default value shown in the dropdown

        $scope.defaultContexts = ['positive', 'negative']; //Options in the dropdown for the default on context.
        $scope.defaultContext = 'positive'; //this will be the default value shown in the dropdown

        $scope.ExecuteTypes = ['Yes', 'If', 'If Not', 'No'];
        $scope.FirstExecuteTypes = ['Yes', 'No'];
        $scope.ruleElseTypes = ['next', 'abort', 'abort_as_error', 'goto'];
        $scope.ConditionValueTypes = ['PASS', 'FAIL', 'ERROR', 'SKIP'];
        $scope.impact_list = ['impact', 'noimpact'];

        $scope.defaultExectypes = ['sequential_testcases', 'parallel_testcases', 'iterative_sequential', 'iterative_parallel', 'Run_Until_Fail', 'Run_Until_Pass', 'Run_Multiple']; //Options in the dropdown for the default on exectype.
        $scope.defaultExectype = 'Functional'; //this will be the default value shown in the dropdown

        $scope.runmodes = ["Standard", "RUP", "RUF", "RMT"];

        $scope.isMaxFailAttempSelected = function() {
            if ($scope.exectype == 'Run_Until_Fail') {
                console.log("Run_Until_Fail");
                return true;
            } else {
                return false;
            }
        };
        $scope.isMaxPassAttempSelected = function() {
            if ($scope.exectype == 'Run_Until_Pass') {
                console.log("Run_Until_Pass");
                return true;
            } else {
                return false;
            }
        };
        $scope.isNumAttempSelected = function() {
            if ($scope.exectype == 'Run_Multiple') {
                console.log("Run_Multiple");
                return true;
            } else {
                return false;
            }
        };

        $scope.defaultSuiteActions = ['next', 'abort', 'abort_as_error', 'goto']; //Options in the dropdown for the default on error action for the test suite.
        $scope.defaultCaseActions = ['next', 'abort', 'abort_as_error', 'goto']; //Options in the dropdown for the default on error action for test cases.

        $scope.defaultSuiteAction = 'next'; //this will be the default value shown in the dropdown
        $scope.isGotoSelectedSuite = function() {
            if ($scope.defaultSuiteAction == 'goto') {
                console.log("goto");
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

        $scope.isGotoSelectedTestcase = function(action) {
            if (action != undefined) {
                if (action.indexOf('goto') != -1) {
                    return true;
                }
            }
            return false;
        };

        $scope.deleteTestcase = function(index) {
            swal({
                title: "Are you sure you want to delete this Case?",
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
                        $scope.$apply(deleteCase(index));
                        swal({
                            title: "Case deleted",
                            timer: 1250,
                            type: "success",
                            showConfirmButton: false
                        });
                    } else {
                        swal({
                            title: "Case not deleted",
                            timer: 1250,
                            type: "error",
                            showConfirmButton: false
                        });
                    }
                });
        };

        function deleteCase(index){
            $scope.testcases.splice(index, 1);
            $scope.condition_list.splice(index, 1);
            $scope.popoverContentList.splice(index, 1);
            $scope.showSavedSuite.splice(index, 1);
            tableIsShown();
            $scope.updateConditionList();
            if($scope.testcases.length == 0){
                $scope.testcaseBeingEdited = "None";
                $scope.testcaseEditor = false;
                $scope.testcaseBeingEdited = "None";
                $scope.testcase_numbers = [];
            }
            else if($scope.testcaseBeingEdited != "None"){
                if(index == $scope.testcaseBeingEdited){
                    $scope.testcaseEditor = false;
                    $scope.testcaseBeingEdited = "None";
                    $scope.testcase_numbers = [];
                }
            }
        }

 	$scope.insertTestcaseCap = function(index) {
        if($scope.testcaseEditor){
            swal({
                title: "You have a Case open in the case editor that should be saved before creating a new Case.",
                text: "Please save that Case.",
                type: "warning",
                confirmButtonText: "Ok",
                closeOnConfirm: true,
                confirmButtonColor: '#3b3131'
            });
        }
        else {
            $scope.testcaseToBeCopied = "None";
            $scope.testcase_numbers = [];
            for(var i=0; i<$scope.testcases.length; i++){
                $scope.testcase_numbers.push(i+1);
            }
            openTestcaseCap(index);
        }
    };

        function openTestcaseCap(index) {
            $scope.testcases.splice(index+1,0,{
                "path": "",
                "context": "positive",
                "InputDataFile": "",
                "runtype": "sequential_keywords",
                "onError": {
                    "_action": "next",
                    "_value": ""
                },
                "Execute": {
                    "_ExecType": "Yes",
                    "Rule": {
                        "_Elsevalue": "",
                        "_Else": "next",
                        "_Condvalue": "",
                        "_Condition": ""
                    }
                },
                "runmode": {
                            "_type": "Standard",
                            "_value": ""
                        },
                "impact": "impact"
            });
            //alert(JSON.stringify($scope.testcases));
            $scope.showModal.splice(index+1,0,{"visible": false});
            $scope.td_df_showModal.splice(index+1,0,{"visible": false});
            $scope.btnValue.splice(index+1,0,"Path");
            $scope.td_df_btnValue.splice(index+1,0,"Path");
            $scope.path_array.splice(index+1,0,[]);
            $scope.td_df_path_array.splice(index+1,0,[]);
            $scope.earlier_li.splice(index+1,0,"");
            $scope.td_df_earlier_li.splice(index+1,0,"");
            $scope.condition_list.splice(index+1, 0, []);
            $scope.popoverContentList.splice(index+1, 0, "");
            $scope.showSavedSuite.splice(index+1, 0, false);
            $scope.testcaseBeingEdited = index + 1;
            $scope.testcaseEditor = true;
            $scope.updateConditionList();
        }

        $scope.copyTestCase = function(){
            //alert($scope.testcaseToBeCopied - 1);
            //alert($scope.testcaseBeingEdited);
            if($scope.testcaseToBeCopied == "None"){
                swal({
                    title: "Please select a Case number from the dropdown.",
                    type: "error",
                    showConfirmButton: true,
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131',
                    confirmButtonText: "Ok"
                });
                return;
            }

            $scope.testcases[$scope.testcaseBeingEdited].path = $scope.testcases[$scope.testcaseToBeCopied - 1].path;
            $scope.testcases[$scope.testcaseBeingEdited].context = $scope.testcases[$scope.testcaseToBeCopied - 1].context;
            $scope.testcases[$scope.testcaseBeingEdited].InputDataFile = $scope.testcases[$scope.testcaseToBeCopied - 1].InputDataFile;
            $scope.testcases[$scope.testcaseBeingEdited].runtype = $scope.testcases[$scope.testcaseToBeCopied - 1].runtype;
            $scope.testcases[$scope.testcaseBeingEdited].onError._action = $scope.testcases[$scope.testcaseToBeCopied - 1].onError._action;
            $scope.testcases[$scope.testcaseBeingEdited].onError._value = $scope.testcases[$scope.testcaseToBeCopied - 1].onError._value;
            $scope.testcases[$scope.testcaseBeingEdited].runmode._action = $scope.testcases[$scope.testcaseToBeCopied - 1].runmode._action;
            $scope.testcases[$scope.testcaseBeingEdited].runmode._value = $scope.testcases[$scope.testcaseToBeCopied - 1].runmode._value;
            $scope.testcases[$scope.testcaseBeingEdited].Execute._ExecType = $scope.testcases[$scope.testcaseToBeCopied - 1].Execute._ExecType;
            $scope.testcases[$scope.testcaseBeingEdited].Execute.Rule._Condition = $scope.testcases[$scope.testcaseToBeCopied - 1].Execute.Rule._Condition;
            $scope.testcases[$scope.testcaseBeingEdited].Execute.Rule._Condvalue = $scope.testcases[$scope.testcaseToBeCopied - 1].Execute.Rule._Condvalue;
            $scope.testcases[$scope.testcaseBeingEdited].Execute.Rule._Else = $scope.testcases[$scope.testcaseToBeCopied - 1].Execute.Rule._Else;
            $scope.testcases[$scope.testcaseBeingEdited].Execute.Rule._Elsevalue = $scope.testcases[$scope.testcaseToBeCopied - 1].Execute.Rule._Elsevalue;
            $scope.testcases[$scope.testcaseBeingEdited].impact = $scope.testcases[$scope.testcaseToBeCopied - 1].impact;
        };

    $scope.addCase = function (index) {
        if($scope.testcaseEditor){
            swal({
                title: "You have a Case open in the Case editor that should be saved before editing a new Case.",
                text: "Please save that Case.",
                type: "warning",
                confirmButtonText: "Ok",
                closeOnConfirm: true,
                confirmButtonColor: '#3b3131'
            });
        }
        else {
            $scope.testcaseToBeCopied = "None";
            $scope.testcase_numbers = [];
            for(var i=0; i<$scope.testcases.length; i++){
                $scope.testcase_numbers.push(i+1);
            }
            openTestcaseCap(index);
        }
    };

        $scope.saveTestcaseCap = function(index){
            var re = /^[0-9]*$/;
            var flag = true;
            if($scope.testcases[index].path == "" || $scope.testcases[index].path == undefined){
                flag = false;
                swal({
                      title: "Case path is a mandatory field.",
                      text: "Please add in a case path for case " + (index + 1).toString(),
                      type: "error",
                      showCancelButton: false,
                      confirmButtonColor: '#3b3131',
                      confirmButtonText: "Ok",
                      closeOnConfirm: false});
            }
            if(flag) {
                if ($scope.testcases[index].runmode._type !== "" && $scope.testcases[index].runmode._type !== "Standard") {
                    if ($scope.testcases[index].runmode._value === "" || $scope.testcases[index].runmode._value === undefined) {
                        flag = false;
                        swal({
                              title: "Run Mode Value cannot be empty!",
                              text: "",
                              type: "error",
                              showCancelButton: false,
                              confirmButtonColor: '#3b3131',
                              confirmButtonText: "Ok",
                              closeOnConfirm: false});
                    }
                    if(flag) {
                        if (!re.test($scope.testcases[index].runmode._value)) {
                            flag = false;
                            swal({
                              title: "Run Mode Value can only be numerical.",
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
                if ($scope.testcases[index].onError._action == "goto") {
                    if ($scope.testcases[index].onError._value == "" || $scope.testcases[index].onError._value == undefined) {
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
                        if (!re.test($scope.testcases[index].onError._value)) {
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
                if ($scope.testcases[index].Execute._ExecType == "If" || $scope.testcases[index].Execute._ExecType == "If Not") {
                    if ($scope.testcases[index].Execute.Rule._Condition == "" || $scope.testcases[index].Execute.Rule._Condition == undefined) {
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
                    if(flag) {
                        if ($scope.testcases[index].Execute.Rule._Condvalue == "" || $scope.testcases[index].Execute.Rule._Condvalue == undefined) {
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
                        if ($scope.testcases[index].Execute.Rule._Else == "goto") {
                            if ($scope.testcases[index].Execute.Rule._Elsevalue == "" || $scope.testcases[index].Execute.Rule._Elsevalue == undefined) {
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
                                if (!re.test($scope.testcases[index].Execute.Rule._Elsevalue)) {
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
            if(flag) {
                $scope.showSavedSuite[index] = true;
                $scope.showTable = true;
                $scope.testcaseBeingEdited = "None";
                $scope.testcaseEditor = false;
                $scope.testcaseBeingEdited = "None";
                $scope.testcase_numbers = [];
            }
        };

        $scope.editTestcase = function(index){
            if($scope.testcaseEditor){
                swal({
                    title: "You have a Case open in the case editor that should be saved before editing another Case.",
                    text: "Please save that Case.",
                    type: "warning",
                    confirmButtonText: "Ok",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131'
                });
            }
            else {
                $scope.testcaseToBeCopied = "None";
                $scope.testcase_numbers = [];
                for(var i=0; i<$scope.testcases.length; i++){
                    if(i !== index){
                        $scope.testcase_numbers.push(i+1);
                    }
                }
                $scope.testcaseEditor = true;
                $scope.testcaseBeingEdited = index;
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

        //Requirements Section

        $scope.showRequirementEditor = function(){
            $scope.showReqEditor = true;
        };

        $scope.addReq = function(){
            if($scope.newReq !== ""){
                if($scope.index == false){
                    $scope.suitereqs.push($scope.newReq);
                }
                else{
                    $scope.suitereqs.splice($scope.index, 0, $scope.newReq);
                    $scope.index = false;
                }
                $scope.newReq = "";
                $scope.showReqEditor = false;
            }
            else{
                swal({
                      title: "No new Requirement Entered.",
                      text: "",
                      type: "error",
                      showCancelButton: false,
                      confirmButtonColor: '#3b3131',
                      confirmButtonText: "Ok",
                      closeOnConfirm: false});
            }
        };

        $scope.cancelReq = function(){
            if($scope.index !== false){
                $scope.suitereqs.splice($scope.index, 0, $scope.newReq);
                $scope.index = false;
            }
            $scope.newReq = "";
            $scope.showReqEditor = false;
        };

        $scope.editReq = function(index){
            $scope.newReq = $scope.suitereqs[index];
            $scope.index = index;
            $scope.suitereqs.splice(index, 1);
            $scope.showReqEditor = true;
        };

        $scope.delReq = function(index){
            swal({
                title: "Are you sure you want to delete this requirement?",
                text: "",
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
                        $scope.$apply($scope.suitereqs.splice(index, 1));
                        swal({
                            title: "Requirement deleted",
                            timer: 1250,
                            type: "success",
                            showConfirmButton: false
                        });
                    } else {
                        swal({
                            title: "Requirement not deleted",
                            timer: 1250,
                            type: "error",
                            showConfirmButton: false
                        });
                    }
                });
        };

        $scope.updateConditionList = function(param){
            for(var i=0; i<$scope.testcases.length; i++){
                $scope.condition_list[i] = [];
                $scope.popoverContentList[i] = "";
                for(var j=0; j<i; j++){
                    $scope.condition_list[i].push("testcase_"+(j+1).toString()+"_status");
                    if($scope.testcases[j].path.trim() !== "") {
                        $scope.popoverContentList[i] = $scope.popoverContentList[i] + (j + 1) + ". \"" + $scope.testcases[j].path + "\"<br />";
                    }
                    else{
                        $scope.popoverContentList[i] = $scope.popoverContentList[i] + (j + 1) + ". \No Case Path Entered<br />";
                    }
                }
            }

            if(param !== undefined){
                for(i=0; i<$scope.condition_list.length; i++){
                    if($scope.condition_list[i].length < 1){
                        if($scope.testcases[i].Execute._ExecType !== "Yes" && $scope.testcases[i].Execute._ExecType !== "No"){
                            $scope.testcases[i].Execute._ExecType = "Yes";
                        }
                    }
                }
            }
        };

        //save functionality section
        $scope.saveTestsuite = function() {

            var hasSpace = _.find($.trim($scope.testsuitename), function (c) {
                return c == ' ';
            });
            if (hasSpace != undefined) {
                swal({
                      title: "Please do not use spaces in the Suite Name field.",
                      text: "The name field value is used as the name of the XML file to store this Suite. " +
                      "We suggest that you use the underscore character (_) in lieu of the space character.",
                      type: "error",
                      showCancelButton: false,
                      confirmButtonColor: '#3b3131',
                      confirmButtonText: "Ok",
                      closeOnConfirm: false});
                return;
            }

            if ($scope.testsuitename == undefined || $scope.testsuitename === '') {
                swal({
                      title: "Suite name is mandatory!",
                      text: "",
                      type: "error",
                      showCancelButton: false,
                      confirmButtonColor: '#3b3131',
                      confirmButtonText: "Ok",
                      closeOnConfirm: false});
            } else if ($scope.testsuitetitle == undefined || $scope.testsuitetitle === '') {
                swal({
                      title: "Suite Title is mandatory!",
                      text: "",
                      type: "error",
                      showCancelButton: false,
                      confirmButtonColor: '#3b3131',
                      confirmButtonText: "Ok",
                      closeOnConfirm: false});
            } else if ($scope.exectype == undefined) {
                swal({
                      title: "Type is mandatory!",
                      text: "",
                      type: "error",
                      showCancelButton: false,
                      confirmButtonColor: '#3b3131',
                      confirmButtonText: "Ok",
                      closeOnConfirm: false});
            } else if ($scope.exectype === 'Run_Until_Fail' && $scope.maxAttempts == undefined) {
                swal({
                      title: "Max attempt should be specified for type Run Until Fail!",
                      text: "",
                      type: "error",
                      showCancelButton: false,
                      confirmButtonColor: '#3b3131',
                      confirmButtonText: "Ok",
                      closeOnConfirm: false});
            } else if ($scope.exectype === 'Run_Until_Pass' && $scope.maxAttempts == undefined) {
                swal({
                      title: "Max attempt should be specified for type Run Until Pass!",
                      text: "",
                      type: "error",
                      showCancelButton: false,
                      confirmButtonColor: '#3b3131',
                      confirmButtonText: "Ok",
                      closeOnConfirm: false});

            } else if ($scope.exectype === 'Run_Multiple' && $scope.numAttempts == undefined) {
                swal({
                      title: "Number of attempt should be specified for type Run Multiple!",
                      text: "",
                      type: "error",
                      showCancelButton: false,
                      confirmButtonColor: '#3b3131',
                      confirmButtonText: "Ok",
                      closeOnConfirm: false});
            }else if ($scope.State === 'Add Another') {

                swal({
                      title: "Please specify a new State!",
                      text: "",
                      type: "error",
                      showCancelButton: false,
                      confirmButtonColor: '#3b3131',
                      confirmButtonText: "Ok",
                      closeOnConfirm: false});
            } else if ($scope.defaultSuiteAction === 'goto' && $scope.gotovalueSuite == undefined) {
                swal({
                      title: "Step to go to should be specified for default on error action GoTo!",
                      text: "",
                      type: "error",
                      showCancelButton: false,
                      confirmButtonColor: '#3b3131',
                      confirmButtonText: "Ok",
                      closeOnConfirm: false});
            } else if($scope.testcases.length < 1 && $scope.State != "New"){

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

                $.each($scope.testcases, function(index, value) {
                    var step = parseInt(index) + 1;
                    var re = /^[0-9]*$/;
                    if (value.path == undefined || value.path === '') {
                        inValid = true;
                        msg = 'Path should be specified for the Case ' + step + '!';
                        return false;
                    } else if (value.runmode._type !== "" && value.runmode._type !== "Standard"){
                        if (!re.test(value.runmode._value)){
                            inValid = true;
                            msg = "Run Mode - Value takes in only numeric values";
                        }
                        if(value.runmode._value.trim() == ""){
                            inValid = true;
                            msg = "Run Mode - Value cannot be empty!";
                        }
                    } else if (value.onError._action === 'goto' && (value.onError._value == undefined || value.onError._value === '')) {
                        inValid = true;
                        msg = 'Case to go should be specified for default on error action GoTo for the Case ' + step + '!';
                    } else if(value.Execute._ExecType == "If" || value.Execute._ExecType == "If Not"){
                        if(value.Execute.Rule._Condition == ""){
                            inValid = true;
                            msg = "Condition must be specified for Case " + step + "!"
                        } else if(value.Execute.Rule._Condition !== "") {
                            if($scope.condition_list[step-1].indexOf(value.Execute.Rule._Condition) == -1){
                                inValid = true;
                                msg = "Condition must be specified for Case " + step + "!"
                            }
                        } else if(value.Execute.Rule._Condvalue == ""){
                            inValid = true;
                            msg = "Condition Value must be specified for Case " + step + "!"
                        } else if(value.Execute.Rule._Else == ""){
                            inValid = true;
                            msg = "Else must be specified for Case " + step + "!"
                        }
                        else if(value.Execute.Rule._Else == "goto"){
                            if(!re.test(value.Execute.Rule._Elsevalue)){
                                inValid = true;
                                msg = "Else Value can contain only numeric values! Please correct Else value in Case " + step;
                            } else if(value.Execute.Rule._Elsevalue.trim() == ""){
                                inValid = true;
                                msg = "Else Value cannot be empty! Please correct Else value in Case " + step;
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
                      closeOnConfirm: false});
                } else {
                    if($scope.exectype === 'iterative_parallel' || $scope.exectype === 'iterative_sequential'){
                        for(var i=0; i<$scope.testcases.length; i++){
                            $scope.testcases[i].InputDataFile = "";
                        }
                    }

                    var filename = $scope.testsuitename + ".xml";

                    fileFactory.checkfileexistwithsubdir(filename, 'suite', $scope.subdirs)
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
        };

        $scope.cancelSuite = function() {
            $location.path('/testsuites');
        };

        function save(filename) {
           var finalJSON = {
                "TestSuite": {
                    "Details": {
                        "Name": $scope.testsuitename,
                        "Title": $scope.testsuitetitle,
                        "Engineer": $scope.newEng,
                        "Date": $scope.newDate,
                        "Time": $scope.newTime,
                        "type": {
                            "_exectype": $scope.exectype,
                            "_Max_Attempts": $scope.maxAttempts,
                            "_Number_Attempts": $scope.numAttempts
                        },
                        "State": $scope.State,
                        "default_onError": {
                            "_action": $scope.defaultSuiteAction,
                            "_value": $scope.gotovalueSuite
                        },
                        "Resultsdir": $scope.resultsdirSuite,
                        "InputDataFile": $scope.IDFSuite,
                        "TestWrapperFile": $scope.TestWrapperFile
                    },
                    "Requirements": {
                        "Requirement": $scope.suitereqs
                    },
                    "Testcases": {
                        "Testcase": $scope.testcases
                    }
                }
            };
            var x2js = new X2JS();
            var token = angular.toJson(finalJSON);
            var xmlObj = x2js.json2xml_str(JSON.parse(token));
            saveNewTestsuiteFactory.saveNew(filename, $scope.subdirs, xmlObj)
                .then(
                    function(data) {
                        console.log(data);
                        if ($scope.savecreateTestsuite == true) {
                          //  $route.reload();
                        }  else {
                            $location.path('/testsuites');
                        }
                    },
                    function(data) {
                        alert(data);
                    });


        }

// To select a Test Wrapper File

         $scope.getPathsJocket = function(e) {
            $scope.path_array = [];
            $scope.earlier_li.className = "";
            if(e == undefined){
                e = window.event;
            }
            var li = (e.target ? e.target : e.srcElement);
            var temp_name = li.innerHTML.split("<");
            $scope.path_array.push(temp_name[0]);
            var li_temp = li;
            while(li_temp.parentNode.id != "tree_div_j"){
                if(!li_temp.parentNode.innerHTML.match(/^</)){
                    var temp_list = li_temp.parentNode.innerHTML.split("<");
                    $scope.path_array.push(temp_list[0]);
                }
                li_temp = li_temp.parentNode
            }
            if (li.className == ""){
                li.className = "colorChange";
                $scope.earlier_li = li;
            }
       };

//Submitting the selected Testwrapper file.

       $scope.storePathsJocket = function() {
            var data_folder_array = [];
            var tc_folder_array = [];
            var folder_index = -1;
            var final_array = [];
            $scope.TestWrapperFile = "";
            if ($scope.cfg.idfdir.indexOf('/') === -1) {
                data_folder_array = $scope.cfg.idfdir.split("\\");
            }
            else {
                data_folder_array = $scope.cfg.idfdir.split("/");
            }
            for (var i = 0; i < data_folder_array.length; i++) {
                if (data_folder_array[i] === $scope.path_array[$scope.path_array.length - 1]) {
                    data_folder_array.splice(i, (data_folder_array.length - i));
                    break;
                }
            }
            for (i = $scope.path_array.length - 1; i >= 0; i--) {
                data_folder_array.push($scope.path_array[i])
            }
            if ($scope.cfg.xmldir.indexOf('/') === -1) {
                tc_folder_array = $scope.cfg.xmldir.split("\\");
            }
            else {
                tc_folder_array = $scope.cfg.xmldir.split("/");
            }
            if($scope.subdirs != "none"){
                var subdir_array = $scope.subdirs.split(",");
                for(i=0; i<subdir_array.length; i++){
                    tc_folder_array.push(subdir_array[i]);
                }
            }
            for (i = 0; i < tc_folder_array.length; i++) {
                if (data_folder_array[i] !== tc_folder_array[i]) {
                    folder_index = i;
                    break;
                }
            }
            if (folder_index !== -1) {
                var dots = tc_folder_array.length - folder_index;
                for (i = 0; i < dots; i++) {
                    final_array.push("..");
                }
            } else {
                folder_index = tc_folder_array.length;
            }
            for (i = folder_index; i < data_folder_array.length; i++) {
                final_array.push(data_folder_array[i]);
            }
            for (i = 0; i < final_array.length; i++) {
                $scope.TestWrapperFile = $scope.TestWrapperFile + final_array[i] + "/"
            }
            if (!$scope.TestWrapperFile.match(/\.\.\/$/)) {
                $scope.TestWrapperFile = $scope.TestWrapperFile.slice(0, -1);
            }
            $scope.btnValueJocket = "Edit";
            $scope.toggleModalJocket();
        };

// Toggle button When the file is selected or Not.

         $scope.toggleModalJocket = function(){
            document.getElementById("tree_div_j").innerHTML = $scope.table;
            CollapsibleLists.applyTo(document.getElementById('tree_div_j'));
            $scope.showModalJ.visible = !$scope.showModalJ.visible;
        };
//Toggle the button between Path and Edit.
        $scope.monitorPathBtnValueForJocket = function(){
            if($scope.TestWrapperFile === undefined || $scope.TestWrapperFile === ""){
                $scope.btnValueJocket = "Path";
            } else {
                $scope.btnValueJocket = "Edit";
            }
        };

        // No data file check box
         $scope.noteJocketStatus = function () {

        var jval = '', // 'Jocket File Required'
            clazz = '';
        if ($scope.status.nojocketfile == '1') {
            if($scope.editStepFlag == 1){
                $scope.noDatacheck();
            }
            jval = 'No_Data';
            clazz = 'disabled';

        }
        $scope.status.jclass = clazz;
        $scope.TestWrapperFile = jval;
        if($scope.status.nojocketfile != '1') {
            $scope.changeExistingIterTypes();
        }
        $scope.monitorPathBtnValueForJocket();

        };




    }
]);