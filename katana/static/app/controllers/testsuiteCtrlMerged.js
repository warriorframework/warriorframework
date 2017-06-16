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

app.controller('testsuiteCtrlMerged', ['$scope', '$http', '$routeParams', '$controller',
    '$timeout', '$location', 'fileFactory', 'getTestsuiteFactory', 'setTestsuiteFactory',
    'saveasTestsuiteFactory', 'subdirs', '$route', 'saveNewTestsuiteFactory',
    function($scope, $http, $routeParams, $controller, $timeout, $location, fileFactory,
             getTestsuiteFactory, setTestsuiteFactory, saveasTestsuiteFactory, subdirs, $route, saveNewTestsuiteFactory) {

        $scope.subdirs = subdirs;
        $scope.xml = {};
        $scope.xml.suitefile = '';
        $scope.xml.suitejson = '';
        $scope.resultsdirSuite = '';
        $scope.IDFSuite = '';
        $scope.suitereqs = [];
        $scope.date = new Date();
        $scope.newtestsuiteTooltip = [];
        $scope.testsuiteTooltip = [];
        $scope.alldirinfo = "";
        $scope.table = "";
        $scope.path_array = [];
        $scope.temp_path_array = [];
        $scope.td_df_path_array = [];
        $scope.earlier_li = [];
        $scope.td_df_earlier_li = [];
        $scope.btnValue=[];
        $scope.td_df_btnValue=[];
        $scope.idf_btnValue = "Path";
        $scope.idf_path_array = [];
        $scope.idf_earlier_li = "";
        $scope.condition_list = [];
        $scope.popoverContentList = [];
        $scope.showModal = [];
        $scope.td_df_showModal = [];
        $scope.showSavedSuite = [false];
        $scope.showTable = false;
        $scope.showReqEditor = false;
        $scope.newReq = "";
        $scope.index = false;
        $scope.testcaseToBeCopied = "None";
        $scope.testcase_numbers = [];
        $scope.fetchFlag = 0;
        $scope.testcaseEditor = false;
        $scope.testcaseBeingEdited = "None";
        $scope.showModal.push({"visible": false});
        $scope.td_df_showModal.push({"visible": false});

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

        function firstLaunch(index){

            if($routeParams.testsuite == undefined){
                $scope.testcaseEditor = false;
                $scope.fetchFlag = 1;


            }

            else{
                $scope.testcaseEditor = false;
            }

        }

        firstLaunch();

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
            for (i = 0; i < final_array.length; i++) {
                $scope.testcases[index].InputDataFile = $scope.testcases[index].InputDataFile + final_array[i] + "/"
            }
            if (!$scope.testcases[index].InputDataFile.match(/\.\.\/$/)) {
                $scope.testcases[index].InputDataFile = $scope.testcases[index].InputDataFile.slice(0, -1);
            }
            $scope.td_df_btnValue[index]="Edit";
            $scope.td_df_toggleModal(index);
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



        $scope.suitemodel = {

            "TestSuite": {
                "Details": {
                    "Name": $scope.Name,
                    "Title": $scope.Title,
                    "State": $scope.State,
                    "Engineer": $scope.Engineer,
                    "Date": $scope.Date,
                    "Time": $scope.Time,
                    "default_onError": {
                        "_action": $scope.defaultSuiteAction,
                        "_value": $scope.gotovalueSuite
                    }
                },
                "Requirements": {
                    "Requirement": $scope.suitereqs

                }

            }
        };


        fileFactory.readstatesfile()
            .then(
                function(data) {
                    console.log(data);
                    $scope.suitestates = data["suitestate"];
                },
                function(data) {
                    alert(data);
                });

        $scope.isAddAnotherSelectedSuite = function() {
            if ($scope.State == 'Add Another') {
                console.log("Add Another");
                return true;
            } else {
                return false;
            }
        };

        $scope.isAddAnotherSelectedSuiteEx = function() {
            if ($scope.suitemodel.TestSuite.Details.State == 'Add Another') {
                console.log("Add Another");
                return true;
            } else {
                return false;
            }
        };
        var ChildCtrl=this;
        ChildCtrl.baseCtrl = $controller('baseChariotCtrl',{ $scope: $scope, $http: $http });
        ChildCtrl.baseCtrl.readConfig();

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

        $scope.idf_showModal =  {visible: false};

        $scope.idf_toggleModal = function(){
            $scope.idf_showModal.visible = !$scope.idf_showModal.visible;
        };

        $scope.idf_monitorPathBtnValue = function(){
            if($scope.IDFSuite === undefined || $scope.IDFSuite === ""){
                $scope.idf_btnValue = "Path";
            } else {
                $scope.idf_btnValue = "Edit";
            }
        };

        $scope.idf_monitorPathBtnValueNew = function(){
            if($scope.IDFSuite === undefined || $scope.IDFSuite === ""){
                $scope.idf_btnValue = "Path";
            } else {
                $scope.idf_btnValue = "Edit";
            }
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
            $scope.suitemodel.TestSuite.Details.IDF = "";
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
                                $scope.suitemodel.TestSuite.Details.State = $scope.new_state;
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
        if($scope.fetchFlag != 1) {

            getTestsuiteFactory.list()
                .then(
                    function (data) {
                        $scope.xml.suitefile = data.xml;
                        var x2js = new X2JS();
                        var jsonObj = x2js.xml_str2json($scope.xml.suitefile);

                        if (jsonObj == null) {
                            sweetAlert({
                                title: "There was an error reading the Suite: " + data["filename"],
                                text: "This XML file may be malformed.",
                                closeOnConfirm: true,
                                confirmButtonColor: '#3b3131',
                                confirmButtonText: "Ok",
                                type: "error"
                            });
                            return;
                        }

                        $scope.xml.suitejson = JSON.stringify(jsonObj, null, 2);
                        $scope.suitemodel = jsonObj;
                        console.log(JSON.stringify(jsonObj));
                    },
                    function (data) {
                        alert(data);
                    });

        }
        fileFactory.readtooltipfile('testsuite')
            .then(
                function(data) {
                    console.log(data);
                    $scope.testsuiteTooltip = data;
                    $scope.newtestsuiteTooltip = data;
                },
                function(data) {
                    alert(data);
                });


        $timeout(function() {

            $scope.defaultRuntypes = ['sequential_keywords', 'parallel_keywords']; //Options in the dropdown for the default on runtype.
            $scope.defaultExectypes = ['sequential_testcases', 'parallel_testcases', 'iterative_sequential', 'iterative_parallel','Run_Until_Fail', 'Run_Until_Pass', 'Run_Multiple']; //Options in the dropdown for the default on exectype.

            $scope.ExecuteTypes = ['If', 'If Not', 'Yes', 'No'];
            $scope.FirstExecuteTypes = ['Yes', 'No'];
            $scope.ruleElseTypes = ['next', 'abort', 'abort_as_error', 'goto'];
            $scope.ConditionalValueTypes = ['PASS', 'FAIL', 'ERROR', 'SKIP'];
            $scope.ConditionValueTypes = ['PASS', 'FAIL', 'ERROR', 'SKIP']
            $scope.defaultSuiteActions = ['next', 'abort', 'abort_as_error', 'goto'];
            $scope.defaultCaseActions = ['next', 'abort', 'abort_as_error', 'goto'];
            $scope.impact_list = ["impact", "noimpact"];

            $scope.defaultContexts = ['positive', 'negative']; //Options in the dropdown for the default on context.
            $scope.defaultContext = 'positive'; //this will be the default value shown in the dropdown

            $scope.runmodes = ["Standard", "RUP", "RUF", "RMT"];

            if($scope.fetchFlag != 0) {
                $scope.suitemodel.TestSuite.Details.default_onError._action = "next";
            }

            if(!$scope.suitemodel.TestSuite.Details.hasOwnProperty("type")){
                $scope.suitemodel.TestSuite.Details.type = {"_exectype": "sequential_testcases",
                    "_Max_Attempts": "", "_Number_Attempts": ""}
            }

            if(!$scope.suitemodel.TestSuite.Details.type.hasOwnProperty("_exectype")){
                $scope.suitemodel.TestSuite.Details.type._exectype = "sequential_testcases";
            }

            if(!$scope.suitemodel.TestSuite.Details.type.hasOwnProperty("_Max_Attempts")){
                $scope.suitemodel.TestSuite.Details.type._Max_Attempts = "";
            }

            if(!$scope.suitemodel.TestSuite.Details.type.hasOwnProperty("_Number_Attempts")){
                $scope.suitemodel.TestSuite.Details.type._Number_Attempts = "";
            }

            for(var k=0; k<$scope.defaultExectypes.length; k++){
                if($scope.suitemodel.TestSuite.Details.type._exectype.toLowerCase() == $scope.defaultExectypes[k].toLowerCase()){
                    $scope.suitemodel.TestSuite.Details.type._exectype = $scope.defaultExectypes[k];
                    break;
                }
            }

            if(!$scope.suitemodel.TestSuite.Details.hasOwnProperty("State")){
                $scope.suitemodel.TestSuite.Details.State = "";
            }

            for(k=0; k<$scope.suitestates.length; k++){
                if($scope.suitemodel.TestSuite.Details.State.toLowerCase() == $scope.suitestates[k].toLowerCase()){
                    $scope.suitemodel.TestSuite.Details.State = $scope.suitestates[k];
                    break;
                }
            }

            if(!$scope.suitemodel.TestSuite.Details.hasOwnProperty("default_onError")){
                $scope.suitemodel.TestSuite.Details.default_onError = {"_action": "next", "_value": ""}
            }

            if(!$scope.suitemodel.TestSuite.Details.default_onError.hasOwnProperty("_action")){
                $scope.suitemodel.TestSuite.Details.default_onError._action = "next";
            }

            if(!$scope.suitemodel.TestSuite.Details.default_onError.hasOwnProperty("_value")){
                $scope.suitemodel.TestSuite.Details.default_onError._value = "";
            }

            for(k=0; k<$scope.defaultSuiteActions.length; k++){
              //  $scope.suitemodel.TestSuite.Details.default_onError._action = "next";
                if($scope.suitemodel.TestSuite.Details.default_onError._action.toLowerCase() == $scope.defaultSuiteActions[k].toLowerCase()){
                    $scope.suitemodel.TestSuite.Details.default_onError._action = $scope.defaultSuiteActions[k];
                    break;
                }
            }

            $scope.exectypeCap = $scope.suitemodel.TestSuite.Details.type._exectype;
            $scope.maxAttemptsCap = $scope.suitemodel.TestSuite.Details.type._Max_Attempts;
            $scope.numAttemptsCap = $scope.suitemodel.TestSuite.Details.type._Number_Attempts;

            $scope.suitemodel.TestSuite.Details.Date = ChildCtrl.baseCtrl.getDate();
            $scope.suitemodel.TestSuite.Details.Time = ChildCtrl.baseCtrl.getTime();
            $scope.suitemodel.TestSuite.Details.Engineer = $scope.cfg.engineer;

            $scope.isMaxFailAttempSelected = function() {
                if ($scope.exectype == 'Run_Until_Fail'  || $scope.exectypeCap == 'Run_Until_Fail') {
                    console.log("Run_Until_Fail");
                    $scope.numAttemptsCap = '';
                    return true;
                } else {
                    return false;
                }
            };

            $scope.isMaxPassAttempSelected = function() {
                if ($scope.exectype == 'Run_Until_Pass'  || $scope.exectypeCap == 'Run_Until_Pass') {
                    console.log("Run_Until_Pass");
                    $scope.numAttemptsCap = '';
                    return true;
                } else {
                    return false;
                }
            };

            $scope.isNumAttempSelected = function() {
                if ($scope.exectype == 'Run_Multiple' || $scope.exectypeCap == 'Run_Multiple') {
                    console.log("Run_Multiple");
                    return true;
                } else {
                    return false;
                }
            };

            //To Handle the default action on error Section
            $scope.defaultSuiteAction = $scope.suitemodel.TestSuite.Details.default_onError._action;
            $scope.suiteGotoStep = $scope.suitemodel.TestSuite.Details.default_onError._value;
            $scope.isGotoSelectedSuite = function() {
                if ($scope.defaultSuiteAction == 'goto') {
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
            //default actions for testcase section
            $scope.testcaseDefaultGotoValue = [];
            $scope.testcaseDefaultActions = [];

            if ($scope.suitemodel.TestSuite.Testcases == "" || $scope.suitemodel.TestSuite.Testcases == undefined) {
                $scope.suitemodel.TestSuite.Testcases = {"Testcase": []};
            }

            if($scope.suitemodel.TestSuite.Testcases.Testcase == undefined){
                $scope.suitemodel.TestSuite.Testcases.Testcase = [];
            }

            $.each($scope.suitemodel.TestSuite.Testcases.Testcase, function(index, value) {
                if (value.hasOwnProperty('onError')) {
                    $scope.testcaseDefaultActions[index] = value.onError._action;
                    $scope.testcaseDefaultGotoValue[index] = value.onError._value;
                }
            });
            $scope.testcaseDefaultActionsUnion = _.union($scope.testcaseDefaultActions, ['goto', 'abort', 'abort_as_error', 'next']);
            $scope.isGotoSelectedAction = function(action) {
                if (action != undefined) {
                    if (action.indexOf('goto') != -1) {
                        return true;
                    }
                }
                return false;
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

            //Requirements Section
            if ($scope.suitemodel.TestSuite.Requirements.Requirement === '') {
                $scope.suitemodel.TestSuite.Requirements.Requirement = [];
            }

            if (Array.isArray($scope.suitemodel.TestSuite.Requirements.Requirement)) {
                $scope.suitereqs = $scope.suitemodel.TestSuite.Requirements.Requirement;
            } else {
                $scope.suitereqs = [];
                if($scope.suitemodel.TestSuite.Requirements.Requirement != "" && $scope.suitemodel.TestSuite.Requirements.Requirement != undefined){
                    $scope.suitereqs.push($scope.suitemodel.TestSuite.Requirements.Requirement);
                }
            }

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
                $scope.newReq = ""
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
                        confirmButtonColor: '#3b3131',
                        confirmButtonText: "Yes, delete it!",
                        cancelButtonText: "No, Keep it.",
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

            //Test cases Section
            if (Array.isArray($scope.suitemodel.TestSuite.Testcases.Testcase)) {
                $scope.testcases = $scope.suitemodel.TestSuite.Testcases.Testcase;
            } else {
                $scope.testcases = [];
                $scope.testcases.push($scope.suitemodel.TestSuite.Testcases.Testcase);
            }
            $scope.showSavedSuite = [];
            for(var i=0; i<$scope.testcases.length; i++){
                $scope.showSavedSuite.push(true);
                $scope.showTable = true;
                $scope.btnValue.push("Edit");
                $scope.td_df_btnValue.push("Edit");
                $scope.showModal.push({visible: false});
                $scope.td_df_showModal.push({visible: false});
                $scope.earlier_li.push("");
                $scope.td_df_earlier_li.push("");
                $scope.path_array.push([]);
                $scope.td_df_path_array.push([]);
                if($scope.testcases[i].hasOwnProperty("rmt")){
                    if(!$scope.testcases[i].hasOwnProperty("runmode")){
                        $scope.testcases[i].runmode = {
                            "_type": "Standard",
                            "_value": ""
                        }
                    }
                    $scope.testcases[i].runmode._type = "RMT";
                    $scope.testcases[i].runmode._value = $scope.testcases[i].rmt;
                    delete $scope.testcases[i].rmt
                }

                $scope.condition_list.push([]);
                $scope.popoverContentList.push("");

                if(!$scope.testcases[i].hasOwnProperty("path")){
                    $scope.testcases[i].path = "";
                }
                if(!$scope.testcases[i].hasOwnProperty("context")){
                    $scope.testcases[i].context = "positive";
                }
                if(!$scope.testcases[i].hasOwnProperty("InputDataFile")){
                    $scope.testcases[i].InputDataFile = "";
                }
                if(!$scope.testcases[i].hasOwnProperty("runtype")){
                    $scope.testcases[i].runtype = "sequential_keywords";
                }


                if(!$scope.testcases[i].hasOwnProperty("impact")){
                    $scope.testcases[i].impact = "impact";
                }
                if(!$scope.testcases[i].hasOwnProperty("Execute")){
                    $scope.testcases[i].Execute = {
                        "_ExecType": "Yes",
                        "Rule": {
                            "_Elsevalue": "",
                            "_Else": "next",
                            "_Condvalue": "",
                            "_Condition": ""
                        }
                    };
                }
                else{
                    if(!$scope.testcases[i].Execute.hasOwnProperty("_ExecType")){
                        $scope.testcases[i].Execute._ExecType = "Yes";
                    }
                    if(!$scope.testcases[i].Execute.hasOwnProperty("Rule")){
                        $scope.testcases[i].Execute.Rule = {
                            "_Elsevalue": "",
                            "_Else": "next",
                            "_Condvalue": "",
                            "_Condition": ""
                        };
                    }
                    else{
                        if(!$scope.testcases[i].Execute.Rule.hasOwnProperty("_Elsevalue")){
                            $scope.testcases[i].Execute.Rule._Elsevalue = "";
                        }
                        if(!$scope.testcases[i].Execute.Rule.hasOwnProperty("_Else")){
                            $scope.testcases[i].Execute.Rule._Else = "next";
                        }
                        if(!$scope.testcases[i].Execute.Rule.hasOwnProperty("_Condvalue")){
                            $scope.testcases[i].Execute.Rule._Condvalue = "";
                        }
                        if(!$scope.testcases[i].Execute.Rule.hasOwnProperty("_Condition")){
                            $scope.testcases[i].Execute.Rule._Condition = "";
                        }
                    }
                }

                if(!$scope.testcases[i].hasOwnProperty("runmode")){
                    $scope.testcases[i].runmode = {"_type": "Standard", "_value": ""}
                } else {
                    if(!$scope.testcases[i].runmode.hasOwnProperty("_type")){
                        $scope.testcases[i].runmode._type = "Standard";
                    }
                    if(!$scope.testcases[i].runmode.hasOwnProperty("_value")){
                        $scope.testcases[i].runmode._value = "";
                    }
                }

                if(!$scope.testcases[i].hasOwnProperty("onError")){
                    $scope.testcases[i].onError = {"_action": "next", "_value": ""}
                } else {
                    if(!$scope.testcases[i].onError.hasOwnProperty("_action")){
                        $scope.testcases[i].onError._action = "next";
                    }
                    if(!$scope.testcases[i].onError.hasOwnProperty("_value")){
                        $scope.testcases[i].onError._value = "";
                    }
                }

                for(var j=0; j<$scope.defaultContexts.length; j++){
                    if($scope.testcases[i].context.toLowerCase() == $scope.defaultContexts[j].toLowerCase()){
                        $scope.testcases[i].context = $scope.defaultContexts[j];
                    }
                }

                for(j=0; j<$scope.ExecuteTypes.length; j++){
                    if($scope.testcases[i].Execute._ExecType.toLowerCase() == $scope.ExecuteTypes[j].toLowerCase()){
                        $scope.testcases[i].Execute._ExecType = $scope.ExecuteTypes[j];
                    }
                }

                for(j=0; j<$scope.ruleElseTypes.length; j++){
                    if($scope.testcases[i].Execute.Rule._Else.toLowerCase() == $scope.ruleElseTypes[j].toLowerCase()){
                        $scope.testcases[i].Execute.Rule._Else = $scope.ruleElseTypes[j];
                    }
                }

                for(j=0; j<$scope.defaultRuntypes.length; j++){
                    if($scope.testcases[i].runtype.toLowerCase() == $scope.defaultRuntypes[j].toLowerCase()){
                        $scope.testcases[i].runtype = $scope.defaultRuntypes[j];
                    }
                }

                for(j=0; j<$scope.runmodes.length; j++){
                    if($scope.testcases[i].runmode._type == ""){
                        $scope.testcases[i].runmode._type = "Standard";
                    }
                    if($scope.testcases[i].runmode._type.toLowerCase() == $scope.runmodes[j].toLowerCase()){
                        $scope.testcases[i].runmode._type = $scope.runmodes[j];
                    }
                }

                for(j=0; j<$scope.defaultCaseActions.length; j++){
                    if($scope.testcases[i].onError._action.toLowerCase() == $scope.defaultCaseActions[j].toLowerCase()){
                        $scope.testcases[i].onError._action = $scope.defaultCaseActions[j];
                    }
                }

            }
            $scope.updateConditionList();
            $scope.deleteTestcaseCap = function(index) {
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
                $scope.path_array.splice(index, 1);
                $scope.td_df_path_array.splice(index, 1);
                $scope.earlier_li.splice(index, 1);
                $scope.td_df_earlier_li.splice(index, 1);
                $scope.btnValue.splice(index, 1);
                $scope.td_df_btnValue.splice(index, 1);
                $scope.showModal.splice(index, 1);
                $scope.td_df_showModal.splice(index, 1);
                $scope.condition_list.splice(index+1, 0, []);
                $scope.popoverContentList.splice(index+1, 0, "");
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
                });
                if($scope.fetchFlag != 1) {
                    $scope.btnValue.splice(index + 1, 0, "Edit");
                    $scope.td_df_btnValue.splice(index+1,0,"Edit");
                }
                else
                {
                    $scope.btnValue.splice(index + 1, 0, "Path");
                    $scope.td_df_btnValue.splice(index+1,0,"Path");
                }

                $scope.showModal.splice(index+1,0,{visible: false});
                $scope.td_df_showModal.splice(index+1,0,{visible: false});
                $scope.earlier_li.splice(index+1,0,"");
                $scope.td_df_earlier_li.splice(index+1,0,"");
                $scope.path_array.splice(index+1,0,[]);
                $scope.td_df_path_array.splice(index+1,0,[]);
                $scope.condition_list.splice(index+1, 0, []);
                $scope.popoverContentList.splice(index+1, 0, "");
                $scope.showSavedSuite.splice(index+1, 0, false);
                $scope.testcaseBeingEdited = index + 1;


                $scope.testcaseEditor = true;

                $scope.updateConditionList();
            }
            $scope.copyTestCase = function(){


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

            $scope.saveTestcase = function(index){
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
                    if($scope.testcases[index].onError._action == "goto"){
                        if($scope.testcases[index].onError._value == "" || $scope.testcases[index].onError._value == undefined){
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
                        if(flag){
                            if(!re.test($scope.testcases[index].onError._value)){
                                flag = false;
                                swal({
                                    title: "Go To Step # for On Error Action can only be numerical..",
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
                    if($scope.testcases[index].Execute._ExecType == "If" || $scope.testcases[index].Execute._ExecType == "If Not"){
                        if($scope.testcases[index].Execute.Rule._Condition == "" || $scope.testcases[index].Execute.Rule._Condition == undefined){
                            flag = false;
                            swal({
                                title: "Condition for Execute type cannot be empty",
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
                            }
                        }
                        if(flag){
                            if(!re.test($scope.testcases[index].Execute.Rule._Elsevalue)){
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
                if(flag){
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
                                                        title: "File saved as " + filename +"!",
                                                        timer: 1250,
                                                        type: "success",
                                                        showConfirmButton: false
                                                    });
                                                    saveEx(filename);
                                                } else {
                                                    swal({
                                                        title: "File not saved",
                                                        timer: 1250,
                                                        type: "error",
                                                        showConfirmButton: false
                                                    });
                                                }
                                            });
                                    } else {
                                        saveNew(filename);
                                    }
                                },
                                function(data) {
                                    alert(data);
                                });
                    }
                }
            };
            $scope.saveTestsuiteCap = function() {


                var hasSpace = _.find($.trim($scope.suitemodel.TestSuite.Details.Name), function (c) {
                    return c == ' ';
                });
                if (hasSpace != undefined) {
                    swal({
                        title: "Please do not use spaces in the Name field of the Suite.",
                        text: "The name field value is used as the name of the XML file to store this Suite. " +
                        "We suggest that you use the underscore character (_) in lieu of the space character.",
                        type: "error",
                        showCancelButton: false,
                        confirmButtonColor: '#3b3131',
                        confirmButtonText: "Ok",
                        closeOnConfirm: false});
                    return;
                }

                if ($scope.suitemodel.TestSuite.Details.Name == undefined || $scope.suitemodel.TestSuite.Details.Name.trim().length == 0) {
                    swal({
                        title: "Suite name is mandatory!",
                        text: "",
                        type: "error",
                        showCancelButton: false,
                        confirmButtonColor: '#3b3131',
                        confirmButtonText: "Ok",
                        closeOnConfirm: false});
                } else if ($scope.suitemodel.TestSuite.Details.Title == undefined || $scope.suitemodel.TestSuite.Details.Title.trim().length == 0){
                    swal({
                        title: "Suite Title is mandatory!",
                        text: "",
                        type: "error",
                        showCancelButton: false,
                        confirmButtonColor: '#3b3131',
                        confirmButtonText: "Ok",
                        closeOnConfirm: false});
                } else if ($scope.exectypeCap == undefined) {
                    swal({
                        title: "Type is mandatory!",
                        text: "",
                        type: "error",
                        showCancelButton: false,
                        confirmButtonColor: '#3b3131',
                        confirmButtonText: "Ok",
                        closeOnConfirm: false});
                } else if ($scope.exectypeCap === 'Run_Until_Fail' && $scope.maxAttemptsCap == undefined) {
                    swal({
                        title: "Max attempt should be specified for type Run Until Fail!",
                        text: "",
                        type: "error",
                        showCancelButton: false,
                        confirmButtonColor: '#3b3131',
                        confirmButtonText: "Ok",
                        closeOnConfirm: false});
                } else if ($scope.exectypeCap === 'Run_Until_Pass' && $scope.maxAttemptsCap == undefined) {
                    swal({
                        title: "Max attempt should be specified for type Run Until Pass!",
                        text: "",
                        type: "error",
                        showCancelButton: false,
                        confirmButtonColor: '#3b3131',
                        confirmButtonText: "Ok",
                        closeOnConfirm: false});
                } else if ($scope.exectypeCap === 'Run_Multiple' && $scope.numAttemptsCap== undefined) {
                    swal({
                        title: "Number of attempt should be specified for type Run Multiple!",
                        text: "",
                        type: "error",
                        showCancelButton: false,
                        confirmButtonColor: '#3b3131',
                        confirmButtonText: "Ok",
                        closeOnConfirm: false});
                } else if ($scope.defaultSuiteAction === 'goto' && $scope.suiteGotoStep == undefined) {
                    swal({
                        title: "Step to go should be specified for default on error action GoTo!",
                        text: "",
                        type: "error",
                        showCancelButton: false,
                        confirmButtonColor: '#3b3131',
                        confirmButtonText: "Ok",
                        closeOnConfirm: false});
                } else if ($scope.suitemodel.TestSuite.Details.State === 'Add Another') {
                    swal({
                        title: "Please specify a new State to be added!",
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
                        }  else if(value.runmode._type !== "" && value.runmode._type !== "Standard"){
                            if (!re.test(value.runmode._value)) {
                                inValid = true;
                                msg = "Run Mode - Value takes in only numeric values";
                            }
                            if (value.runmode._value.trim() == "") {
                                inValid = true;
                                msg = "Run Mode - Value cannot be empty";
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

                        if($scope.exectypeCap === 'iterative_parallel' || $scope.exectypeCap === 'iterative_sequential'){
                            for(var i=0; i<$scope.testcases.length; i++){
                                $scope.testcases[i].InputDataFile = "";
                            }
                        }

                        //var filename = $routeParams.testsuite
                        var filename = $scope.suitemodel.TestSuite.Details.Name + ".xml";
                        console.log(filename);
                        fileFactory.checkfileexistwithsubdir(filename, 'suite', $scope.subdirs)
                            .then(
                                function(data) {
                                    console.log(JSON.stringify(data));
                                    var fileExist = data.response;

                                    if (fileExist == 'yes') {
                                        var emsg = "File: " + filename + " already exists.\n\nDo you want to overwrite it?";
                                        swal({
                                                title: emsg,
                                                text: "",
                                                type: "warning",
                                                showCancelButton: true,
                                                confirmButtonColor: '#3b3131',
                                                confirmButtonText: "Yes!",
                                                cancelButtonText: "No, don't overwrite.",
                                                closeOnConfirm: false,
                                                closeOnCancel: false
                                            },
                                            function(isConfirm){
                                                if (isConfirm) {
                                                    swal({
                                                        title: "File saved as " + filename +"!",
                                                        timer: 1250,
                                                        type: "success",
                                                        showConfirmButton: false
                                                    });
                                                    saveEx(filename);
                                                } else {
                                                    swal({
                                                        title: "File not saved",
                                                        timer: 1250,
                                                        type: "error",
                                                        showConfirmButton: false
                                                    });
                                                }
                                            });
                                    } else {
                                        console.log('not exist:');
                                        console.log(filename);
                                        saveEx(filename);
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
            function saveNew(filename) {

                var finalJSON = {
                    "TestSuite": {
                        "Details": {
                            "Name": $scope.testsuitename,
                            "Title": $scope.testsuitetitle,
                            "Engineer": $scope.cfg.engineer,
                            "Date": ChildCtrl.baseCtrl.getDate(),
                            "Time": ChildCtrl.baseCtrl.getTime(),
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
                            "IDF": $scope.IDFSuite
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
                        },
                        function(data) {
                            alert(data);
                        });

                if ($scope.savecreateTestsuite == true || $scope.savecreateTestsuiteCap == false) {
                    $route.reload();
                }  else if ($scope.savecreateTestsuite == false || $scope.savecreateTestsuiteCap == true) {
                    $location.path('/newtestsuite');
                }  else {
                    $location.path('/testsuites');
                }
            }
            function saveEx(filename) {

                var finalJSON = {
                    "TestSuite": {
                        "Details": {
                            "Name": $scope.suitemodel.TestSuite.Details.Name,
                            "Title": $scope.suitemodel.TestSuite.Details.Title,
                            "Engineer": $scope.suitemodel.TestSuite.Details.Engineer,
                            "Date": $scope.suitemodel.TestSuite.Details.Date,
                            "Time": $scope.suitemodel.TestSuite.Details.Time,
                            "type": {
                                "_exectype": $scope.exectypeCap,
                                "_Max_Attempts": $scope.maxAttemptsCap,
                                "_Number_Attempts": $scope.numAttemptsCap
                            },
                            "State":$scope.suitemodel.TestSuite.Details.State,
                            "default_onError": {
                                "_action": $scope.defaultSuiteAction,
                                "_value": $scope.suiteGotoStep
                            },
                            "Resultsdir": $scope.suitemodel.TestSuite.Details.Resultsdir,
                            "IDF": $scope.suitemodel.TestSuite.Details.IDF
                        },
                        "Requirements": {
                            "Requirement": $scope.suitereqs
                        },
                        "Testcases": {
                            "Testcase": $scope.testcases
                        }
                    }
                }
                var x2js = new X2JS();
                var token = angular.toJson(finalJSON);
                var xmlObj = x2js.json2xml_str(JSON.parse(token));
                setTestsuiteFactory.testsuitesave(filename, $scope.subdirs, xmlObj)
                    .then(
                        function(data) {
                            console.log(data);
                        },
                        function(data) {
                            alert(data);
                        });

                if ($scope.savecreateTestsuite == true || $scope.savecreateTestsuiteCap == false) {
                    $route.reload();
                }  else if ($scope.savecreateTestsuite == false || $scope.savecreateTestsuiteCap == true) {
                    $location.path('/newtestsuite');
                }  else {
                    $location.path('/testsuites');
                }
            }


            fileFactory.readdatafile()
                .then(
                    function(data) {
                        $scope.alldirinfo = data;
                        $scope.table = $scope.table + "<ul class=\"collapsibleList\" id='path_list'>";
                        get_folders_names($scope.alldirinfo);
                        $scope.table = $scope.table + "</ul>";
                        document.getElementById("idf_tree_div").innerHTML = $scope.table;
                        CollapsibleLists.applyTo(document.getElementById('idf_tree_div'));
                    },
                    function(data) {
                        alert(data);
                    });


        }, 500);


    }


]);


