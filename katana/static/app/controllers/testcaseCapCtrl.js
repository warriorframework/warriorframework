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

app.controller('TestcaseCapCtrl', ['$scope','$routeParams','$http', '$location', '$anchorScroll', 'TestcaseFactory', 'fileFactory', 'getConfigFactory', 'subdirs',
    function ($scope, $routeParams, $http, $location, $anchorScroll, TestcaseFactory, fileFactory, getConfigFactory, subdirs) {

    'use strict';

    $scope.step_numbers = [];
        $scope.stepToBeCopied = "None";
        $scope.stepBeingEdited = "None";
        $scope.subdirs = subdirs;
        $scope.xml = {};
    $scope.xml.file = '';
    $scope.xml.json = '';
    $scope.xml.pycs = {};
    $scope.xml.args = {};
        $scope.original_iter_types = [];
    // $scope.xml.capargs = [];        // where the arguments are captured in the form.
        $scope.step_onerror = "next";
        $scope.step_onerror_value = "";
        $scope.arg_list = [{"_name": "", "_value": ""}];
        $scope.showStepEdit = false;
        $scope.insertStep = false;
        $scope.alldirinfo = "";
        $scope.table = "";
        $scope.path_array = [];
        $scope.temp_path_array = [];
        $scope.earlier_li = [];
        $scope.btnValue = "Path";
        $scope.showModal = {visible: false};

        function readConfig(){
            getConfigFactory.readconfig()
            .then(function (data) {
               $scope.cfg = data;
            });
        }

        readConfig();

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

        $scope.getPaths = function(e) {
             $scope.path_array = [];
             $scope.earlier_li.className = "";
             if(e == undefined){
                 e = window.event;
             }
             var li = (e.target ? e.target : e.srcElement);
             var temp_name = li.innerHTML.split("<");
             $scope.path_array.push(temp_name[0]);
             var li_temp = li;
             while(li_temp.parentNode.id != "tree_div"){
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

        $scope.storePaths = function() {
            var data_folder_array = [];
            var tc_folder_array = [];
            var folder_index = -1;
            var final_array = [];
            $scope.model.Testcase.Details.InputDataFile = "";
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
                $scope.model.Testcase.Details.InputDataFile = $scope.model.Testcase.Details.InputDataFile + final_array[i] + "/"
            }
            if (!$scope.model.Testcase.Details.InputDataFile.match(/\.\.\/$/)) {
                $scope.model.Testcase.Details.InputDataFile = $scope.model.Testcase.Details.InputDataFile.slice(0, -1);
            }
            $scope.btnValue = "Edit";
            $scope.toggleModal();
        };

        fileFactory.readdatafile()
            .then(
                function(data) {
                    $scope.alldirinfo = data;
                    $scope.table = $scope.table + "<ul class=\"collapsibleList\" id='path_list'>";
                    get_folders_names($scope.alldirinfo);
                    $scope.table = $scope.table + "</ul>";
                    document.getElementById("tree_div").innerHTML = $scope.table;
                    CollapsibleLists.applyTo(document.getElementById('tree_div'));
                },
                function(data) {
                    alert(data);
                });

        $scope.toggleModal = function(){
            document.getElementById("tree_div").innerHTML = $scope.table;
            CollapsibleLists.applyTo(document.getElementById('tree_div'));
            $scope.showModal.visible = !$scope.showModal.visible;
        };

        $scope.monitorPathBtnValue = function(){
            if($scope.model.Testcase.Details.InputDataFile === undefined || $scope.model.Testcase.Details.InputDataFile === ""){
                $scope.btnValue = "Path";
            } else {
                $scope.btnValue = "Edit";
            }
        };

        $scope.addAnotherArgumentToList = function (){
            $scope.arg_list.push({"_name": "", "_value": ""});
        };

        $scope.deleteArgFromList = function(index){
            if($scope.arg_list.length > 1){
                $scope.arg_list.splice(index, 1);
            }
            else{
                $scope.arg_list = [{"_name": "", "_value": ""}];
            }
        };

            $scope.syncStepOnError = function(){
                $scope.step_onerror = $scope.status.default_onError._action;
            };

        $scope.syncStepOnError_value = function(){
            if($scope.status.default_onError._action == "goto"){
                $scope.step_onerror_value = $scope.status.default_onError._value
            }
            else{
                $scope.step_onerror_value = ""
            }
        };

    $scope.xml.mapargs = {};
    $scope.xml.arglist = [];
        $scope.changedIndex = -1;

        $scope.savecreateTestcaseCap = false;
        $scope.new_state = "";

        $scope.updateNewStateValue = function(tab){
            if(tab.indexOf('%') === -1) {
              $scope.new_state = tab;
            }
            else {
                sweetAlert({
                        title: "No percentage characte (%) allowed!",
                        closeOnConfirm: true,
                        confirmButtonColor: '#3b3131',
                        confirmButtonText: "Ok",
                        type: "error"
                    });
            }
        };

        $scope.emptyKWName = function(){
            if(!$scope.status.kwCheckbox){
                $scope.status.driverCheckbox = false;
            }
            $scope.model.Testcase.Details.State = "Draft";
            $scope.status.keyword = "";
            selectKeyword($scope.status.keyword)
        };

        $scope.emptyDriverName = function(){
            $scope.model.Testcase.Details.State = "Draft";
            $scope.status.kwCheckbox = $scope.status.driverCheckbox;
            $scope.status.drivername = "";
            $scope.driverSelected($scope.status.drivername);
        };

        $scope.addNewTcstate = function(){
            if ($scope.new_state === undefined || $scope.new_state === ""){
                sweetAlert({
                    title: "New State cannot be blank!",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131',
                    confirmButtonText: "Ok",
                    type: "error"
                })
            }
            else {
                fileFactory.updatestatesfile("tcstate%" + $scope.new_state)
                .then(
                function(data) {
                    var check = data["check"];
                    if(check) {
                        $scope.tcstates.pop();
                        $scope.tcstates.push($scope.new_state);
                        $scope.tcstates.push("Add Another");
                        $scope.model.Testcase.Details.State = $scope.new_state;
                        $scope.new_state = "";
                    }
                    else {
                        sweetAlert({
                            title: "States could not be updated!",
                            closeOnConfirm: true,
                            confirmButtonColor: '#3b3131',
                            confirmButtonText: "Ok",
                            type: "error"
                        })
                    }
                });
            }
        };

        $scope.copyStep = function(){

            if($scope.stepToBeCopied == "None"){
                swal({
                    title: "Please select a step number from the dropdown.",
                    type: "error",
                    showConfirmButton: true,
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131',
                    confirmButtonText: "Ok"
                });
                return;
            }

            $scope.status.driverCheckbox = false;
            $scope.status.kwCheckbox = false;

            $scope.status.drivername = $scope.model.Testcase.Steps.step[$scope.stepToBeCopied - 1]._Driver;
            $scope.status.keyword = $scope.model.Testcase.Steps.step[$scope.stepToBeCopied - 1]._Keyword;

            var drivers = $scope.xml.pycs[$scope.status.drivername];
            if(drivers == undefined){
                $scope.status.driverCheckbox = true;
                $scope.status.kwCheckbox = true;
            }
            else{
                var ads = [];
                _.each(drivers, function (driver) {
                    ads.push(_.filter(driver, function(d) {
                        return d.type === 'fn' && d.fn !== '__init__';
                    }));
                });
                var kwds = _.flatten(ads);
                kwds = _.sortBy(kwds, function(r) {return r.fn});
                if(!kwds.hasOwnProperty(length)){
                    kwds = [kwds];
                }
                var kw_list = [];
                for(i=0; i<kwds.length; i++){
                    kw_list.push(kwds[i].fn);
                }
                var index_of_kw = kw_list.indexOf($scope.status.keyword);
                if(index_of_kw == -1){
                    $scope.status.kwCheckbox = true;
                }
                else{
                    $scope.xml.keywords = kwds;
                    $scope.status.description = kwds[index_of_kw].wdesc;
                    $scope.xml.args.def = kwds[index_of_kw].def;
                    $scope.xml.args.comment = kwds[index_of_kw].comment;
                }
            }

            if($scope.model.Testcase.Steps.step[$scope.stepToBeCopied - 1].hasOwnProperty("_draft")){
                if($scope.stepBeingEdited < $scope.model.Testcase.Steps.step.length){
                    $scope.model.Testcase.Steps.step[$scope.stepBeingEdited]["_draft"] = $scope.model.Testcase.Steps.step[$scope.stepToBeCopied - 1]["_draft"];
                }
            }
            else if($scope.status.kwCheckbox){
                if($scope.stepBeingEdited < $scope.model.Testcase.Steps.step.length) {
                    $scope.model.Testcase.Steps.step[$scope.stepBeingEdited]["_draft"] = "yes";
                }
                $scope.model.Testcase.Steps.step[$scope.stepToBeCopied - 1]["_draft"] = "yes";
            }
            else{
                if($scope.stepBeingEdited < $scope.model.Testcase.Steps.step.length) {
                    $scope.model.Testcase.Steps.step[$scope.stepBeingEdited]["_draft"] = "no";
                }
            }
            $scope.status.step.Description = $scope.model.Testcase.Steps.step[$scope.stepToBeCopied - 1].Description;
            if(!$scope.model.Testcase.Steps.step[$scope.stepToBeCopied - 1].Arguments.argument.hasOwnProperty(length)){
                $scope.model.Testcase.Steps.step[$scope.stepToBeCopied - 1].Arguments.argument = [$scope.model.Testcase.Steps.step[$scope.stepToBeCopied - 1].Arguments.argument];
            }
            if($scope.status.kwCheckbox){
                $scope.arg_list = $scope.model.Testcase.Steps.step[$scope.stepToBeCopied - 1].Arguments.argument;
            }
            else{
                var mapped_arg_obj = {};
                for(var i=0; i<$scope.model.Testcase.Steps.step[$scope.stepToBeCopied - 1].Arguments.argument.length; i++){
                    mapped_arg_obj[$scope.model.Testcase.Steps.step[$scope.stepToBeCopied - 1].Arguments.argument[i]._name] = $scope.model.Testcase.Steps.step[$scope.stepToBeCopied - 1].Arguments.argument[i]._value;
                }
                $scope.xml.mapargs = mapped_arg_obj;
                $scope.xml.args = _.where($scope.xml.keywords, { fn: $scope.status.keyword })[0];
                $scope.xml.arglist = _.map($scope.xml.args.args, function (a) {
                    return a.split('=')[0];
                });
            }
            $scope.status.step.Execute._ExecType = $scope.model.Testcase.Steps.step[$scope.stepToBeCopied - 1].Execute._ExecType;
            $scope.status.step.Execute.Rule._Condition = $scope.model.Testcase.Steps.step[$scope.stepToBeCopied - 1].Execute.Rule._Condition;
            $scope.status.step.Execute.Rule._Condvalue = $scope.model.Testcase.Steps.step[$scope.stepToBeCopied - 1].Execute.Rule._Condvalue;
            $scope.status.step.Execute.Rule._Else = $scope.model.Testcase.Steps.step[$scope.stepToBeCopied - 1].Execute.Rule._Else;
            $scope.status.step.Execute.Rule._Elsevalue = $scope.model.Testcase.Steps.step[$scope.stepToBeCopied - 1].Execute.Rule._Elsevalue;
            $scope.status.step.iteration_type._type = $scope.model.Testcase.Steps.step[$scope.stepToBeCopied - 1].iteration_type._type;
            $scope.status.step.runmode._type = $scope.model.Testcase.Steps.step[$scope.stepToBeCopied - 1].runmode._type;
            $scope.status.step.runmode._value = $scope.model.Testcase.Steps.step[$scope.stepToBeCopied - 1].runmode._value;
            $scope.status.step.impact = $scope.model.Testcase.Steps.step[$scope.stepToBeCopied - 1].impact;
            $scope.status.step.context = $scope.model.Testcase.Steps.step[$scope.stepToBeCopied - 1].context;
            $scope.status.step.onError._action = $scope.model.Testcase.Steps.step[$scope.stepToBeCopied - 1].onError._action;
            $scope.status.step.onError._value = $scope.model.Testcase.Steps.step[$scope.stepToBeCopied - 1].onError._value;
        };

    $scope.model = {
          "Testcase": {
            "Details": {
              "Name": "",
              "Title": "",
              "Category": "",
                "State": "",
              "Engineer": "",
              "Date": "",
              "Time": "",
              "default_onError": {
                "_action": "next",
                "_value": "2"
              },
              "InputDataFile": "",
              "Datatype": "",
              "Logsdir": "",
              "Resultsdir": ""
            },
            "Requirements": {
              "Requirement": []
            },
            "Steps": {
              "step": [/*
                {
                  "Arguments": {
                    "argument": {
                      "_name": "count",
                      "_value": "1"
                    }
                  },
                  "onError": {
                    "_action": "goto",
                    "_value": "2"
                  },
                  "impact": "noimpact",
                  "context": "positive",
                  "_Driver": "DriverName",
                  "_Keyword": "KeywordName"
                }*/
              ]
            }
          }
        };

        $scope.changeExistingIterTypes = function(){
            for (var i = 0; i < $scope.model.Testcase.Steps.step.length; i++){
                if ($scope.model.Testcase.Details.Datatype == "Hybrid") {
                    if ($scope.original_iter_types[i] == undefined) {
                        $scope.model.Testcase.Steps.step[i].iteration_type._type = "Standard";
                    } else {
                        if ($scope.original_iter_types[i] == ""){
                            $scope.model.Testcase.Steps.step[i].iteration_type._type = "Standard";
                        }
                        else{
                            $scope.model.Testcase.Steps.step[i].iteration_type._type = $scope.original_iter_types[i];
                        }
                    }
                } else {
                    if ($scope.original_iter_types[i] === undefined || $scope.original_iter_types[i] == ""){
                        $scope.original_iter_types[i] = $scope.model.Testcase.Steps.step[i].iteration_type._type;
                    }
                    $scope.model.Testcase.Steps.step[i].iteration_type._type = "";
                }
            }
        };
        fileFactory.readstatesfile()
        .then(
            function(data) {
                // console.log(data);
                $scope.tcstates = data.tcstate;
            },
            function(data) {
                alert(data);
            });

    function readTestCaseFile() {
        TestcaseFactory.fetch()
            .then(function (data) {
                $scope.xml.file = data.xml;
                $scope.xml.pycs = data.pycmts;
                $scope.xml.drivers = _.sortBy(_.keys(data.pycmts), function (d) { return d; });
                $scope.xml.keywords = {}; // mkKeywordMap($scope.xml.drivers, data.pycmts);

                var x2js = new X2JS();
                var jsonObj = x2js.xml_str2json($scope.xml.file);
                if (jsonObj == null) {
                    sweetAlert({
                        title: "There was an error reading the Case: " + data["filename"],
                        text: "This XML file may be malformed.",
                        closeOnConfirm: true,
                        confirmButtonColor: '#3b3131',
                        confirmButtonText: "Ok",
                        type: "error"
                    });
                    return;
                }
                $scope.model = jsonObj;

                $scope.model.Testcase.Details.Date = moment().format('YYYY-MM-DD');
                $scope.model.Testcase.Details.Time = moment().format('HH:mm');
                $scope.model.Testcase.Details.Engineer = data.engineer;

                if ($scope.model.Testcase.Requirements === undefined) {
                    $scope.model.Testcase.Requirements = {};
                    $scope.model.Testcase.Requirements.Requirement = [];
                }
                if (_.isEmpty($scope.model.Testcase.Requirements)) {
                    var ok = delete $scope.model.Testcase.Requirements;
                    $scope.model.Testcase.Requirements = {};
                    $scope.model.Testcase.Requirements.Requirement = [];
                    // console.log('Req', JSON.stringify($scope.model.Testcase.Requirements, null, 2));
                }
                if ($scope.model.Testcase.Requirements == '' ||
                    _.size($scope.model.Testcase.Requirements) == 0) {
                    $scope.model.Testcase.Requirements["Requirement"] = [];
                }
                if (_.isString($scope.model.Testcase.Requirements['Requirement'])) {
                    var req = $scope.model.Testcase.Requirements['Requirement'];
                    $scope.model.Testcase.Requirements['Requirement'] = [req];
                }
                if ($scope.model.Testcase.Requirements.Requirement === undefined) {
                    $scope.model.Testcase.Requirements.Requirement = [];
                }

                for (var i = 0; i < $scope.model.Testcase.Requirements.Requirement.length; i++) {
                    if ($scope.model.Testcase.Requirements.Requirement[i] == '') {
                        $scope.model.Testcase.Requirements.Requirement.splice(i, 1);
                    }
                }

                //---- Steps normalization.

                if ($scope.model.Testcase.Steps === undefined) {
                    $scope.model.Testcase.Steps = {};
                    $scope.model.Testcase.Steps.step = [];
                }
                if (_.isEmpty($scope.model.Testcase.Steps)) {
                    var ok = delete $scope.model.Testcase.Steps;
                    $scope.model.Testcase.Steps = {};
                    $scope.model.Testcase.Steps.step = [];
                }
                if ($scope.model.Testcase.Steps == '' || _.size($scope.model.Testcase.Steps) == 0) {
                    $scope.model.Testcase.Steps["step"] = [];
                }

                if(!$scope.model.Testcase.Steps.step.hasOwnProperty(length)){
                    if($scope.model.Testcase.Steps.step.length === 0){

                    }
                    else{
                        $scope.model.Testcase.Steps.step = [$scope.model.Testcase.Steps.step];
                    }
                }

                var flag = true;
                for(i=0; i<$scope.status.datatypes.length; i++){
                    if($scope.model.Testcase.Details.Datatype.toLowerCase() == $scope.status.datatypes[i].toLowerCase()){
                        $scope.model.Testcase.Details.Datatype = $scope.status.datatypes[i];
                        flag = false;
                        break;
                    }
                }
                if(flag){
                    $scope.model.Testcase.Details.Datatype = "Custom"
                }
                else{
                    flag = true;
                }

                for(i=0; i<$scope.status.caseerrors.length; i++){
                    if($scope.model.Testcase.Details.default_onError._action.toLowerCase() == $scope.status.caseerrors[i].toLowerCase()){
                        $scope.model.Testcase.Details.default_onError._action = $scope.status.caseerrors[i];
                        flag = false;
                        break;
                    }
                }
                if(flag){
                    $scope.model.Testcase.Details.default_onError._action = "next"
                }
                else{
                    flag = true;
                }

                for (i = 0; i < $scope.model.Testcase.Steps.step.length; i++) {
                    if(!$scope.model.Testcase.Steps.step[i].hasOwnProperty("Execute")){
                        $scope.model.Testcase.Steps.step[i]["Execute"] = {"_ExecType": "Yes", "Rule": {"_Elsevalue": "", "_Else": "", "_Condvalue": "", "_Condition": ""}}
                    }

                    if(!$scope.model.Testcase.Steps.step[i].Execute.hasOwnProperty("Rule")){
                        $scope.model.Testcase.Steps.step[i].Execute["Rule"] = {"_Elsevalue": "", "_Else": "", "_Condvalue": "", "_Condition": ""}
                    }

                    if(!$scope.model.Testcase.Steps.step[i].hasOwnProperty("onError")){
                        $scope.model.Testcase.Steps.step[i]["onError"] = {"_action": "next", "_value": ""};
                    }

                    if(!$scope.model.Testcase.Steps.step[i].hasOwnProperty("Description")){
                        $scope.model.Testcase.Steps.step[i]["Description"] = "";
                    }

                    if(!$scope.model.Testcase.Steps.step[i].hasOwnProperty("Iteration_type")){
                        $scope.model.Testcase.Steps.step[i]["Iteration_type"] = {"_type": "standard"};
                    }

                    if(!$scope.model.Testcase.Steps.step[i].hasOwnProperty("context")){
                        $scope.model.Testcase.Steps.step[i]["context"] = "positive";
                    }

                    if(!$scope.model.Testcase.Steps.step[i].hasOwnProperty("impact")){
                        $scope.model.Testcase.Steps.step[i]["impact"] = "impact";
                    }

                    if($scope.model.Testcase.Steps.step[i].hasOwnProperty("rmt")){
                        if(!$scope.model.Testcase.Steps.step[i].hasOwnProperty("runmode")) {
                            $scope.model.Testcase.Steps.step[i].runmode = {
                                "_type": "Standard",
                                "_value": ""
                            }
                        }
                        $scope.model.Testcase.Steps.step[i].runmode._type = "RMT";
                        $scope.model.Testcase.Steps.step[i].runmode._value = $scope.model.Testcase.Steps.step[i].rmt;
                        delete $scope.model.Testcase.Steps.step[i].rmt
                    }

                    if(!$scope.model.Testcase.Steps.step[i].hasOwnProperty("runmode")){
                        $scope.model.Testcase.Steps.step[i].runmode = {
                                "_type": "Standard",
                                "_value": ""
                            }
                    }

                    if(!$scope.model.Testcase.Steps.step[i].hasOwnProperty("Description")){
                        $scope.model.Testcase.Steps.step[i].Description = "";
                    }

                    for(var j=0; j<$scope.status.stepsimpacts.length; j++){
                        if($scope.model.Testcase.Steps.step[i].impact.toLowerCase() == $scope.status.stepsimpacts[j].toLowerCase()){
                            $scope.model.Testcase.Steps.step[i].impact = $scope.status.stepsimpacts[j];
                            break;
                        }
                    }

                     for(j=0; j<$scope.status.stepsexecutes.length; j++){
                        if($scope.model.Testcase.Steps.step[i].Execute._ExecType.toLowerCase() == $scope.status.stepsexecutes[j].toLowerCase()){
                            $scope.model.Testcase.Steps.step[i].Execute._ExecType = $scope.status.stepsexecutes[j];
                            break;
                        }
                    }

                    for(j=0; j<$scope.status.steperrors.length; j++){
                        if($scope.model.Testcase.Steps.step[i].Execute.Rule._Else.toLowerCase() == $scope.status.steperrors[j].toLowerCase()){
                            $scope.model.Testcase.Steps.step[i].Execute.Rule._Else = $scope.status.steperrors[j];
                            break;
                        }
                    }

                    for(j=0; j<$scope.status.runmodes.length; j++){
                        if($scope.model.Testcase.Steps.step[i].runmode._type == ""){
                            $scope.model.Testcase.Steps.step[i].runmode._type = "Standard";
                        }
                        if($scope.model.Testcase.Steps.step[i].runmode._type.toLowerCase() == $scope.status.runmodes[j].toLowerCase()){
                            $scope.model.Testcase.Steps.step[i].runmode._type = $scope.status.runmodes[j];
                            break;
                        }
                    }

                    for(j=0; j<$scope.status.stepscontexts.length; j++){
                        if($scope.model.Testcase.Steps.step[i].context.toLowerCase() == $scope.status.stepscontexts[j].toLowerCase()){
                            $scope.model.Testcase.Steps.step[i].context = $scope.status.stepscontexts[j];
                            break;
                        }
                    }

                    for(j=0; j<$scope.status.iterationtypes.length; j++){
                        if($scope.model.Testcase.Steps.step[i].Iteration_type._type.toLowerCase() == $scope.status.iterationtypes[j].toLowerCase()){
                            $scope.model.Testcase.Steps.step[i].Iteration_type._type = $scope.status.iterationtypes[j];
                            break;
                        }
                    }

                    for(j=0; j<$scope.status.steperrors.length; j++){
                        if($scope.model.Testcase.Steps.step[i].onError._action.toLowerCase() == $scope.status.steperrors[j].toLowerCase()){
                            $scope.model.Testcase.Steps.step[i].onError._action = $scope.status.steperrors[j];
                            break;
                        }
                    }

                    if($scope.model.Testcase.Steps.step[i].hasOwnProperty("_draft")){
                        if($scope.model.Testcase.Steps.step[i]["_draft"].toLowerCase() == "yes"){
                            $scope.model.Testcase.Steps.step[i]["_draft"] = "yes";
                        }
                        else{
                            $scope.model.Testcase.Steps.step[i]["_draft"] = "no";
                        }
                    }


                }

                if($scope.model.Testcase.Details.Datatype === "Hybrid"){
                    for (i = 0; i < $scope.model.Testcase.Steps.step.length; i++) {
                        if ($scope.model.Testcase.Steps.step[i].iteration_type === undefined) {
                            $scope.model.Testcase.Steps.step[i].iteration_type = {_type: "Standard"}
                        }
                        $scope.original_iter_types.push($scope.model.Testcase.Steps.step[i].iteration_type._type);
                    }
                } else {
                    for (i = 0; i < $scope.model.Testcase.Steps.step.length; i++) {
                        $scope.model.Testcase.Steps.step[i].iteration_type = {_type: ""};
                        $scope.original_iter_types.push($scope.model.Testcase.Steps.step[i].iteration_type._type);
                    }
                }

                if (  ! _.isArray($scope.model.Testcase.Steps['step'])) {
                    var xstep = $scope.model.Testcase.Steps['step'];
                    delete $scope.model.Testcase.Steps['step'];
                    $scope.model.Testcase.Steps['step'] = [xstep];
                }
                if (_.isString($scope.model.Testcase.Steps['step'])) {
                    var xstep = $scope.model.Testcase.Steps['step'];
                    $scope.model.Testcase.Steps['step'] = [xstep];
                }

                $scope.xml.json = JSON.stringify(jsonObj, null, 2);
                console.log('$scope.model.Testcase', JSON.stringify($scope.model.Testcase, null, 2));

                // Set up some $scope values that are not directly referring into the test case itself.
                $scope.status.default_onError = { _action: 'next', _value: '' };
                $scope.status.default_onError._action = $scope.model.Testcase.Details.default_onError._action;
                $scope.status.default_onError._value = $scope.model.Testcase.Details.default_onError._value || '';

                $scope.status.nodatafile =
                    ($scope.model.Testcase.Details.InputDataFile == 'No_Data') ? '1' : '0';
                $scope.status.datatype =
                    ($scope.status.nodatafile == '0') ? '' : $scope.model.Testcase.Details.Datatype;

            }, function (msg) {
                alert(msg);
            });

    }

    readTestCaseFile();

    $scope.status = {

        nodatafile: '0',
        idfclass: '',               // allows edit when zero length, else is set to 'disabled'.

        datatype: 'Iterative',      // Custom
        datatypes: ['Iterative', 'Custom', 'Hybrid'],

        reqedtype: 'None',          // Requirement editor type: 'New'/'Edit'/'None'; when None, the form is not showing.
        requirement: '',            // User makes a new req or edits existing req here.

        index: 0,

        step_edit_mode: 'None',     // Step editor type: 'New'/'Edit'/'None'; when None, the form is not showing.

        stepindex: 0,               // which'th step were we editing.
        steps: [],
        step: {},

        drivername: '',             // currently selected driver - in the select control.
        keyword: '',                // currently selected keyword - in the select box.
        runmode: {
            _type: 'Standard',                    // currently entered value.
            _value: ''
        },


        default_onError: {          // This is the default_onError as it appears in the Details section.
            _action: 'next',
            _value: ""
        },

        stepsimpacts: ['impact', 'noimpact'],

        caseerrors: ['next', 'abort', 'abort_as_error', 'goto'],

        steperrors: ['next', 'abort', 'abort_as_error', 'goto'],

        iterationtypes: ['Standard', 'once_per_tc', 'end_of_tc'],

        stepsexecutes: ['If', 'If Not', 'Yes', 'No'],

        stepexecuteerrors: ['next', 'abort', 'abort_as_error', 'goto'],

        stepscontexts: ['positive', 'negative'],

        runmodes: ['Standard', 'RMT', 'RUP', 'RUF'],

        kwCheckbox: false,

        driverCheckbox: false
    };

    $scope.grabDefaultStepNum = function () {

    };

    $scope.noteInputDataStatus = function () {
        var idfval = '', // 'Data File Required'
            clazz = '';
        if ($scope.status.nodatafile == '1') {
            idfval = 'No_Data';
            clazz = 'disabled';
            for(var i=0; i<$scope.model.Testcase.Steps.step.length; i++){
                $scope.original_iter_types[i] = $scope.model.Testcase.Steps.step[i].iteration_type._type;
                $scope.model.Testcase.Steps.step[i].iteration_type._type = "";
            }
        }
        $scope.status.idfclass = clazz;
        $scope.model.Testcase.Details.InputDataFile = idfval;
        if($scope.status.nodatafile != '1') {
            $scope.changeExistingIterTypes();
        }
        $scope.monitorPathBtnValue();
    };

    //-- Requirements Editor -----------------------------------------------

    $scope.putReqEditorOutOfSight = function () {
        if ($scope.status.reqedtype != 'None') {
            $scope.status.reqedtype = 'None';
        }
    };

    $scope.hasNoReqs = function () {
        return ($scope.model.Testcase.Requirements.Requirement.length == 0)
                || ($scope.model.Testcase.Requirements.Requirement.length == 1 &&
                                   $scope.model.Testcase.Requirements.Requirement[0] == '');
    };

    $scope.newReq = function () {
        return $scope.status.reqedtype == 'New'
    };

    $scope.reqEdTypeAsString = function () {
        if ($scope.status.reqedtype == 'None') {
            return 'New';
        }
        return $scope.status.reqedtype;
    };

    $scope.editReq = function () {
        return $scope.status.reqedtype == 'Edit'
    };

    $scope.startReqEdit = function (edtype, val, index) {
        $scope.status.reqedtype = edtype;
        $scope.status.index = index;
        $scope.status.requirement = val;
    };

    $scope.saveReq = function () {
        if ($.trim($scope.status.requirement) == '') {
            sweetAlert({
                title: "Requirement field cannot be blank.",
                closeOnConfirm: true,
                confirmButtonColor: '#3b3131',
                confirmButtonText: "Ok",
                type: "error"
            });
            return;
        }
        if (_.size($scope.model.Testcase.Requirements) == 0) {
            $scope.model.Testcase.Requirements['Requirement'] = [];
        }
        var sa = $scope.model.Testcase.Requirements['Requirement'],
            ix = sa.indexOf($scope.status.requirement); // The value edited by our user.
        if (ix < 0) {
            if ($scope.status.reqedtype == 'New') {
                $scope.model.Testcase.Requirements['Requirement'].push($scope.status.requirement);
            } else {
                $scope.model.Testcase.Requirements['Requirement'][$scope.status.index] = $scope.status.requirement;
            }
            $scope.status.requirement = '';     // Clear to capture next requirement.
            $scope.putReqEditorOutOfSight();
        } else {
            sweetAlert({
                title: "This item already exists in the list.",
                closeOnConfirm: true,
                confirmButtonColor: '#3b3131',
                confirmButtonText: "Ok",
                type: "error"
            });
        }
    };

    $scope.delReq = function (index) {
        sweetAlert({
            title: "Are you sure you wish to delete this Requirement?",
            closeOnConfirm: false,
            confirmButtonColor: '#3b3131',
            confirmButtonText: "Ok",
            showCancelButton: true,
            cancelButtonText: "Nope. I want to keep this requirement.",
            type: "warning"
        },
        function(isConfirm){
            if (isConfirm) {
                $scope.$apply($scope.model.Testcase.Requirements['Requirement'].splice(index, 1));
                swal({
                    title: "Requirement deleted.",
                    timer: 1250,
                    type: "success",
                    showConfirmButton: false});
            }
        });
    };

    /**
     * Show the Req editor if the reqedtype is New or Edit.
     * @return bool should show Req editor or not.
     */
    $scope.showReqEditor = function () {
        var ed = $scope.status.reqedtype;
        $('#reqeditor').focus();
        return ed === 'New' || ed === 'Edit';
    };

    $scope.cancelReq = function () {
        $scope.status.reqedtype = 'None';
    };

    //---------------------------------------------------------------
    //- STEPS -------------------------------------------------------
    //---------------------------------------------------------------

    $scope.delStep = function (index) {

        sweetAlert({
            title: "Are you sure you want to delete Step #" + (index+1) + "?",
            closeOnConfirm: false,
            confirmButtonColor: '#3b3131',
            confirmButtonText: "Ok",
            showCancelButton: true,
            cancelButtonText: "Nope. I want to keep this step.",
            type: "warning"
        },
        function(isConfirm){
            if (isConfirm) {
                $scope.$apply($scope.model.Testcase.Steps.step.splice(index, 1));
                swal({
                    title: "Requirement deleted.",
                    timer: 1250,
                    type: "success",
                    showConfirmButton: false});
            }
        });
    };

    $scope.hasNoSteps = function () {
        var output = false;
        if($scope.model.Testcase.Steps.step.length == 0){
            output = true;
        }
        else if($scope.model.Testcase.Steps.step.length == 1){
            if($scope.showStepEdit && $scope.stepBeingEdited !== "None"){
                output = true;
            }
        }
        return output
    };

    $scope.startStepEdit = function (edtype, val, index) {
        if($scope.showStepEdit){
            swal({
                title: "You have a Step open in the step editor that should be saved before creating a new Step.",
                text: "Please save that Step.",
                type: "warning",
                confirmButtonText: "Ok",
                closeOnConfirm: true,
                confirmButtonColor: '#3b3131'
            });
        }
        else {
            startStepCap(edtype, val, index);
        }
    };

        function startStepCap(edtype, val, index){
            $scope.step_numbers = [];
            $scope.stepToBeCopied = "None";
            for(var i=0; i<$scope.model.Testcase.Steps.step.length; i++){
                $scope.step_numbers.push(i+1);
            }
            $scope.showStepEdit = true;
            $scope.cancelReq();
            $scope.status.step_edit_mode = edtype;
            $scope.status.stepindex = index;
            $scope.status.step = mkNewStep();
            if (edtype == 'New') {
                $scope.driverSelected('');
            }
            $scope.status.driverCheckbox = false;
            $scope.status.kwCheckbox = false;
            if($scope.insertStep){
                $scope.insertStep = false;
            }
        }

        $scope.showTopTable = function(index){
            if($scope.insertStep){
                return index > $scope.stepBeingEdited
            }
            else{
                return index >= $scope.stepBeingEdited
            }

        };

    $scope.addStep = function (index) {
        if($scope.showStepEdit){
            swal({
                title: "You have a Step open in the step editor that should be saved before editing a new Step.",
                text: "Please save that Step.",
                type: "warning",
                confirmButtonText: "Ok",
                closeOnConfirm: true,
                confirmButtonColor: '#3b3131'
            });
        }
        else {
            $scope.cancelReq();
            $scope.status.step_edit_mode = 'New';
            $scope.status.stepindex = index;
            $scope.status.step = mkNewStep();
            $scope.driverSelected('');
            $scope.stepBeingEdited = index;
            $scope.showStepEdit = true;
            $scope.step_numbers = [];
            $scope.stepToBeCopied = "None";
            for(var i=0; i<$scope.model.Testcase.Steps.step.length; i++){
                $scope.step_numbers.push(i+1);
            }
            $scope.insertStep = true;
        }
    };

    $scope.reqStepEdTypeAsString = function () {
        return ($scope.status.step_edit_mode == 'Edit') ? 'Edit' : 'New';
    };

    // Allow Edit op for the Step at the given index within the Steps array.
    // Event handler when the driver name is selected in the Step Grid.
    $scope.editStep = function (drivername, index) {

        if($scope.showStepEdit){
            swal({
                title: "You have a Step open in the step editor that should be saved before editing a new Step.",
                text: "Please save that Step.",
                type: "warning",
                confirmButtonText: "Ok",
                closeOnConfirm: true,
                confirmButtonColor: '#3b3131'
            });
        }
        else {
            openStepCap(drivername, index);
        }
    };

        function openStepCap(drivername, index){
            $scope.stepBeingEdited = index;
            $scope.step_numbers = [];
            $scope.stepToBeCopied = "None";
            for(var i=0; i<$scope.model.Testcase.Steps.step.length; i++){
                if(i !== index){
                    $scope.step_numbers.push(i+1);
                }
            }
            $scope.showStepEdit = true;
            $scope.status.driverCheckbox = false;
            $scope.status.kwCheckbox = false;
            $scope.putReqEditorOutOfSight();
            $scope.status.stepindex = index;
            console.log("Editing step: " + drivername + ' @ ' + index);
            console.log('$scope.model: ' + JSON.stringify($scope.model));
            $scope.status.step = $scope.model.Testcase.Steps.step[index];
            console.log('Step to edit: ' + JSON.stringify($scope.status.step));
            $scope.changedIndex = index;
            $scope.driverSelected(drivername);
            var flag_kwd_length = true;
            if($scope.xml.keywords.length > 0){
                var kwd = _.find ($scope.xml.keywords, function (kw) {
                    return kw.fn == $scope.status.step._Keyword;
                });
                if(kwd == undefined){
                    flag_kwd_length = false;
                    kwd = get_unavailable_kwd_data(index);
                }
            }
            else{
                flag_kwd_length = false;
                kwd = get_unavailable_kwd_data(index);
            }
            console.log('kwd: ', JSON.stringify(kwd));

            $scope.status.keyword = kwd.fn;
            if(flag_kwd_length){
                $scope.selectKeyword(kwd.fn);  // Do this before setting the values of args.
            }


            var args = _.map(kwd.args, function (a) {
                return $.trim(a.split('=')[0]);
            });

            //-- mapargs management.
            if (kwd.args[0] == 'self') {
                $scope.xml.mapargs['self'] = '';
            }
            else{
                $scope.status.driverCheckbox = true;
                $scope.status.kwCheckbox = true;
            }

            if(!$scope.status.step.Arguments.argument.hasOwnProperty(length)){
                $scope.status.step.Arguments.argument = [$scope.status.step.Arguments.argument];
            }

            var vals = _.pluck($scope.status.step.Arguments.argument, '_name');

            console.log('vals ', JSON.stringify(vals));
            console.log('kwd-arg-a ', JSON.stringify(kwd, null, 2));

            // Clear the map, so that if another item is selected in the UI, the args look good.

            $scope.xml.mapargs = {};
            _.each(kwd.argsmap, function (v, k) {
                $scope.xml.mapargs[k] = '';
            });

            _.each($scope.status.step.Arguments.argument, function (a, i) {
                $scope.xml.mapargs[a._name] = a._value;
            });

            console.log('MAPARGS: ', JSON.stringify($scope.xml.mapargs, null, 2));
            $scope.status.step_edit_mode = 'Edit';
            if($scope.insertStep){
                $scope.insertStep = false;
            }

            }

    $scope.showStepEditor = function () {
        return $scope.status.step_edit_mode != 'None';
    };

        function get_unavailable_kwd_data(index){
            var kwd = {};
            kwd["fn"] = $scope.model.Testcase.Steps.step[index]._Keyword;
            kwd["type"] = "fn";
            kwd["wdesc"] = "No WDescription available as this Keyword has not been defined yet.";
            kwd["def"] = "A signature for this Keyword has not been defined yet.";
            var var_argsmap = {};
            var var_args = [];
            if($scope.model.Testcase.Steps.step[index].Arguments.argument.hasOwnProperty(length)){
                $scope.arg_list = $scope.model.Testcase.Steps.step[index].Arguments.argument;
            }
            else{
                $scope.arg_list = [$scope.model.Testcase.Steps.step[index].Arguments.argument];
            }
            for(var i=0; i<$scope.arg_list.length; i++){
                var_argsmap[$scope.arg_list[i]._name] = $scope.arg_list[i]._value;
                if($scope.arg_list[i]._value != ""){
                    var_args.push($scope.arg_list[i]._name + "=" + $scope.arg_list[i]._value + "");
                }
                else{
                    var_args.push($scope.arg_list[i]._name);
                }
            }
            kwd["argsmap"] = var_argsmap;
            kwd["line"] = 0;
            kwd["args"] = var_args;
            kwd["comment"] = ["No Comments available."];
            return kwd;
        }

    $scope.cancelArguments = function () {
        $scope.status.step = mkNewStep();
        $scope.showStepEdit = false;
        $scope.stepBeingEdited = "None";
        $scope.stepToBeCopied = "None";
        if($scope.insertStep){
            $scope.insertStep = false;
        }
        return $scope.status.step_edit_mode = 'None';
    };

    // On change of the Driver name select control.
    // Gather function names for the selected driver.
    $scope.driverSelected = function (drivername) {

        $scope.putReqEditorOutOfSight();

        $scope.status.drivername = drivername;
        $scope.status.keyword = '';                     // When driver is selected, clear the keyword.
        $scope.status.stepdescription = '';            // And, the description field.

        var drivers = $scope.xml.pycs[drivername];
        var ads = [];
        _.each(drivers, function (driver) {
            ads.push(_.filter(driver, function(d) {
                return d.type === 'fn' && d.fn !== '__init__';
            }));
        });
        var kwds = _.flatten(ads);
        kwds = _.sortBy(kwds, function(r) {return r.fn});
        $scope.xml.keywords = kwds;         // Function's details (comments, params, &c) of selected driver.

        return kwds;
    };

    // Gather arguments for currently selected keyword/fun.
    // keyword is the fun name.
    $scope.selectKeyword = function (keyword) {
        $scope.putReqEditorOutOfSight();
        console.log('In selectKeyword(' + keyword + ')');
        var k = _.findWhere ($scope.xml.keywords, { fn: keyword });
        if (k['wdesc'] != '') {
            $scope.status.stepdescription = k['wdesc'];
        } else {
            $scope.status.stepdescription = k['fn'];
        }
        $scope.xml.args = _.where($scope.xml.keywords, { fn: keyword })[0];
        $scope.xml.arglist = _.map($scope.xml.args.args, function (a) {
            return a.split('=')[0];
        });
        $scope.xml.mapargs = {};
        _.each($scope.xml.arglist, function (v) {
            $scope.xml.mapargs[v] = '';
        });
        console.log('xml.args', JSON.stringify($scope.xml.args));
        return $scope.xml.args;
    };



    function mkNewStep() {
        var rec = {
          "Arguments": {
            "argument": []
          },
          "onError": {
            "_action": $scope.step_onerror, // Inherits from default_onError value in the TC
            "_value": $scope.step_onerror_value
          },
          "Description": "",
            "iteration_type": {
                "_type":"Standard"
            },
          "Execute": {
            "_ExecType": "Yes",
            "Rule": {
                "_Condition":"",
                "_Condvalue":"",
                "_Else":"next",
                "_Elsevalue":""
            }
          },
          "context": "positive",    // negative, positive
          "impact": "impact",     // impact, noimpact
          "_TS": "1",
            "runmode": {
                "_type": "Standard",
                "_value": ""
            },
          "_Driver": '',
          "_Keyword": ''
        };
        $scope.xml.mapargs = {};
        return rec;
    }


    function populate_step(driver, funname) {
        var rec = {
          "Arguments": {
            "argument": []
          },
          "onError": {
            "_action": "", // next, abort, goto
            "_value": ""
          },
          "Description": "",
            "iteration_type": {
                "_type":"Standard"
            },
          "Execute": {
            "_ExecType": "Yes",
            "Rule": {
                "_Condition":"",
                "_Condvalue":"",
                "_Else":"next",
                "_Elsevalue":""
            }
          },
            "context": "positive",    // negative, positive
            "impact": "impact",     // impact, noimpact
            "runmode": {
                "_type": "Standard",
                "_value": ""
            },
            "_TS": "1",
            "_Driver": '',
            "_Keyword": ''
        };
        console.log('mapargs', JSON.stringify($scope.xml.mapargs, null, 2));
        rec._Driver = driver;
        rec._Keyword = funname;
        console.log('$scope.xml.mapargs: ', JSON.stringify($scope.xml.mapargs));
        _.each($scope.xml.mapargs, function (v, k) {
            if (k != 'self' && $.trim(v) != '') {
                rec.Arguments.argument.push({'_name': k, '_value': v });
            }
        });
        rec.Description = $scope.status.step.Description;
        if($scope.status.step.onError == undefined){
            $scope.status.step.onError = {};
            $scope.status.step.onError['_action'] = $scope.status.default_onError['_action'];
        }
        if($scope.status.step.onError['_action'] == undefined || $scope.status.step.onError['_action'] == "" || $scope.status.step.onError['_action'] == {}){
            $scope.status.step.onError['_action'] = $scope.status.default_onError['_action'];
        }
        rec.onError['_action'] = $scope.status.step.onError['_action'];
        if (rec.onError['_action'] == 'goto') {
            if ($.trim($scope.status.step.onError._value) == '') {
                sweetAlert({
                    title: "A Step # is required when 'On Error' is goto.",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131',
                    confirmButtonText: "Ok",
                    type: "error"
                });
                return null;
            } else {
                rec.onError['_value'] = $scope.status.step.onError['_value'];
            }
        } else {
            delete rec.onError['_value'];
        }
       if($scope.status.step.context == undefined){
           $scope.status.step.context = "positive"
       }
        rec.context = $scope.status.step.context;
        if($scope.status.step.impact == undefined){
           $scope.status.step.impact = "impact"
       }
        rec.impact = $scope.status.step.impact;
        rec.runmode._type = $scope.status.step.runmode._type;
        rec.runmode._value = $scope.status.step.runmode._value;

        if($scope.model.Testcase.Details.Datatype == "Hybrid"){
            if($scope.status.step.iteration_type['_type'] === ""){
                $scope.status.step.iteration_type['_type'] = "Standard";
            }
        }
        else{
            $scope.status.step.iteration_type['_type'] = "";
        }
        rec.iteration_type['_type'] = $scope.status.step.iteration_type['_type'];
        if($scope.status.step.Execute == undefined){
            $scope.status.step.Execute = {};
        }
        if($scope.status.step.Execute['_ExecType'] == undefined){
            $scope.status.step.Execute['_ExecType'] = "Yes";
        }
        rec.Execute['_ExecType'] = $scope.status.step.Execute['_ExecType'];

        if (rec.Execute['_ExecType'] == 'If' || rec.Execute['_ExecType'] == 'If Not') {
            rec.Execute['Rule']['_Condition'] = $scope.status.step.Execute['Rule']['_Condition'];
            rec.Execute['Rule']['_Condvalue'] = $scope.status.step.Execute['Rule']['_Condvalue'];
            rec.Execute['Rule']['_Else'] = $scope.status.step.Execute['Rule']['_Else'];

            if (rec.Execute['Rule']['_Else'] == 'goto') {
                if ($.trim($scope.status.step.Execute['Rule']['_Elsevalue']) == '') {
                    sweetAlert({
                        title: "A Step # is required when 'On Error' is goto.",
                        closeOnConfirm: true,
                        confirmButtonColor: '#3b3131',
                        confirmButtonText: "Ok",
                        type: "error"
                    });
                    return null;
                } else {
                    rec.Execute['Rule']['_Elsevalue'] = $scope.status.step.Execute['Rule']['_Elsevalue'];
                }
            } else {
                delete rec.Execute['Rule']['_Elsevalue'];
            }
        } else {
            delete rec.Execute['Rule'];
        }

        console.log('rec', JSON.stringify(rec, null, 2));
        return rec;
    }

    /* Called when Save Step is clicked. */
    $scope.saveArguments = function () {
        var driver = $.trim($scope.status.drivername) || '',
            keyword = $.trim($scope.status.keyword) || '';
        if(!$scope.status.driverCheckbox && !$scope.status.kwCheckbox){
            if (driver == '' || keyword == '' ) {
                sweetAlert({
                    title: "We need the Driver, Keyword and Description definitions for a Step specification.",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131',
                    confirmButtonText: "Ok",
                    type: "error"
                });
                return;
            }
        }
        else{
            if (keyword == '' ) {
                sweetAlert({
                    title: "We need the Keyword definition for a Step specification.",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131',
                    confirmButtonText: "Ok",
                    type: "error"
                });
                return;
            }
            else {
                if($scope.arg_list.length > 1){
                    for(var i=0; i<$scope.arg_list.length; i++){
                        if($scope.arg_list[i]._name == ""){
                            sweetAlert({
                                title: "The Name for Argument " + (i+1) + " has been left empty.",
                                closeOnConfirm: true,
                                confirmButtonColor: '#3b3131',
                                confirmButtonText: "Ok",
                                type: "error"
                            });
                            return;
                        }
                    }
                }
            }
        }

        if($scope.status.step.runmode._type !== "Standard"){
            var value = $.trim($scope.status.step.runmode._value);
            var re = /^[0-9]*$/;
            if( !re.test(value) ) {
                sweetAlert({
                    title: "Run Mode - Value takes in only numeric values",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131',
                    confirmButtonText: "Ok",
                    type: "error"
                });
                return;
            }
            if(value == "Standard"){
                sweetAlert({
                    title: "Run Mode - Value cannot be empty",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131',
                    confirmButtonText: "Ok",
                    type: "error"
                });
                return;
            }
        }

        if($scope.changedIndex !== -1) {
            $scope.original_iter_types[$scope.changedIndex] = $scope.status.step.iteration_type._type;
            $scope.changedIndex = -1;
        }

        var newstep = populate_step(driver, keyword);
        if (newstep == null) {
            return;
        }

        if(!$scope.status.kwCheckbox){
            newstep["_draft"] = "no";
        }
        else{
            newstep["_draft"] = "yes";
            newstep.Arguments.argument = $scope.arg_list;
        }


        if ($scope.status.step_edit_mode == 'New') {
            if($scope.status.stepindex==-1){
                if($scope.model.Testcase.Steps.step === undefined){
                    $scope.model.Testcase.Steps.step = [];
                }
                $scope.model.Testcase.Steps.step.push(newstep);
	        }
            else {
                $scope.model.Testcase.Steps.step.splice($scope.status.stepindex+1,0,newstep)
            }
        }
        else {
            $scope.model.Testcase.Steps.step[$scope.status.stepindex] = newstep;
        }
        $scope.status.step_edit_mode = 'None';
        $scope.kwCheckbox = false;
        $scope.driverCheckbox = false;
        $scope.showStepEdit = false;
        $scope.stepBeingEdited = "None";
        $scope.stepToBeCopied = "None";
        if($scope.insertStep){
            $scope.insertStep = false;
        }
    };

    $scope.testcaseTooltips = [];
        $scope.tcstates = [];

    fileFactory.readtooltipfile('testcase')
        .then(
            function(data) {
                // console.log(data);
                $scope.testcaseTooltips = data;
            },
            function(data) {
                alert(data);
            });

    $scope.cancelTestcaseCap = function() {
        $location.path('/testcases');
    };

    $scope.saveTestcaseCap = function () {

        if($scope.showStepEdit){
            sweetAlert({
                title: "There is a step that has not been saved yet.",
                text: "Either save this step or discard it before saving the Case",
                showCancelButton: false,
                showConfirmButton: true,
                type: "warning",
                closeOnConfirm: true,
                confirmButtonColor: '#3b3131',
                confirmButtonText: "Ok"
            });
            return;
        }

        $scope.model.Testcase.Details.Date = moment().format('YYYY-MM-DD');
        $scope.model.Testcase.Details.Time = moment().format('HH:mm');

        if ($.trim($scope.model.Testcase.Details.Name) == '') {
            sweetAlert({
                title: "A Testcase Name is required.",
                text: "Please do not specify spaces in it. This name will be used as the XML file name.",
                closeOnConfirm: true,
                confirmButtonColor: '#3b3131',
                confirmButtonText: "Ok",
                type: "error"
            });
            return;
        }
        var hasSpace = _.find($.trim($scope.model.Testcase.Details.Name), function (c) {
            return c == ' ';
        });
        if (hasSpace != undefined) {
            sweetAlert({
                title: "Please do not use spaces in the Name field of the Testcase.",
                text: "The name field value is used as the name of the XML file to store this test case. We suggest that you use the underscore character (_) in lieu of the space character.",
                closeOnConfirm: true,
                confirmButtonColor: '#3b3131',
                confirmButtonText: "Ok",
                type: "error"
            });
            return;
        }
        if ($.trim($scope.model.Testcase.Details.Title) == '') {
            sweetAlert({
                title: "A Testcase Title is required.",
                closeOnConfirm: true,
                confirmButtonColor: '#3b3131',
                confirmButtonText: "Ok",
                type: "error"
            });
            return;
        }
        if ($.trim($scope.model.Testcase.Details.Engineer) == '') {
            sweetAlert({
                title: "The Testcase Engineer's name is required.",
                closeOnConfirm: true,
                confirmButtonColor: '#3b3131',
                confirmButtonText: "Ok",
                type: "error"
            });
            return;
        }

        if ($.trim($scope.model.Testcase.Details.State) == 'Add Another'){
            sweetAlert({
                title: "Please add a new testcase state.",
                closeOnConfirm: true,
                confirmButtonColor: '#3b3131',
                confirmButtonText: "Ok",
                type: "error"
            });
            return;
        }

        if ($scope.model.Testcase.Details.InputDataFile == 'No_Data') {
            $scope.model.Testcase.Details.Datatype = '';
        } else {
            if ($scope.model.Testcase.Details.Datatype == '') {
                $scope.status.nodatafile = '0'; // This setting will show the drop down.
                sweetAlert({
                    title: "Data type needs to be selected.",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131',
                    confirmButtonText: "Ok",
                    type: "error"
                });
                return;
            } else {
                // $scope.model.Testcase.Details.Datatype = $scope.status.datatype;
                // We have the Datatype value - that is serviceable.
            }
        }

        var isDetailDefError = $scope.status.default_onError._action == 'goto',
            isBlank = $.trim($scope.status.default_onError._value) == '',
            isNumeric = _.isNumber( + $scope.status.default_onError._value);

        if (isDetailDefError) {
            if ( isBlank || ( ! isNumeric )) {
                sweetAlert({
                    title: "Please specify the Target Step.",
                    text: "This is needed as the default action on error is to go to an error step",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131',
                    confirmButtonText: "Ok",
                    type: "error"
                });
                return;
            }
        }

        /*
        //---- The engineer need not define any requirement entries.
        if ($scope.model.Testcase.Requirements.Requirement.length == 0) {
            alert("You need to define at least one Requirement before you can save this Testcase.");
            return;
        }
        */

        for (var i = 0; i < $scope.model.Testcase.Requirements.Requirement.length; i++) {
            if ($scope.model.Testcase.Requirements.Requirement[i] == '') {
                $scope.model.Testcase.Requirements.Requirement.splice(i, 1);
            }
        }

        if ($scope.model.Testcase.Steps.step.length == 0) {
            sweetAlert({
                title: "You need to define at least one Step before you can save this Testcase.",
                closeOnConfirm: true,
                confirmButtonColor: '#3b3131',
                confirmButtonText: "Ok",
                type: "error"
            });
            return;
        }

        var step_draft_count = 0;

        _.each(_.range(1, $scope.model.Testcase.Steps.step.length+1), function (i) {
            $scope.model.Testcase.Steps.step[i-1]._TS = i;
            if($scope.model.Testcase.Steps.step[i-1].hasOwnProperty("_draft")){
                if($scope.model.Testcase.Steps.step[i-1]._draft == "yes"){
                    step_draft_count = step_draft_count + 1;
                }
            }

        });

        //- Assign the default error action in the details section.
        var def_error_copy = _.clone($scope.status.default_onError);
        console.log('def_error_copy: ', JSON.stringify($scope.status.default_onError));
        if ($scope.status.default_onError._action != 'goto') {
            delete def_error_copy['_value'];
        }
        $scope.model.Testcase.Details.default_onError = def_error_copy;

        console.log("Testcase\n", JSON.stringify(angular.toJson($scope.model.Testcase), null, 2));

        // var x2js = new X2JS();
        // var token = angular.toJson($scope.model);
        // var xmlDoc = x2js.json2xml_str(JSON.parse(token));
        // alert(xmlDoc);
        // console.log(xmlDoc);

        if($scope.model.Testcase.Details.State == "Draft"){
            if(step_draft_count > 0){
                //alert that this testcase has draft steps
                sweetAlert({
                    title: "This Case is in the Draft state and has " + step_draft_count + " step(s) in Draft",
                    showCancelButton: false,
                    showConfirmButton: false,
                    type: "warning",
                    timer: 1500
                });
                setTimeout(function(){check_and_save_file()}, 2000);
            }
            else{
                //alert about the tc is still in draft even though no step is in draft
                sweetAlert({
                    title: "This Case is in the Draft state. Do you still want to go ahead and save this Case?",
                    showCancelButton: true,
                    showConfirmButton: true,
                    cancelButtonText: "Nope.",
                    confirmButtonText: "Yes.",
                    confirmButtonColor: '#3b3131',
                    type: "warning"
                },
                function(isConfirm){
                    if (isConfirm) {
                        check_and_save_file();
                    }
                    else{
                        return false;
                    }
                });
            }
        }
        else{
            if(step_draft_count > 0){
                //alert that there are steps in draft but the tc state is not in draft. make the user change the state to draft
                sweetAlert({
                    title: "This Case is NOT in the Draft state but there are steps in the Case which contain keywords and/or drivers that have not been developed yet.",
                    text: "Please change the Case state to draft.",
                    showCancelButton: false,
                    showConfirmButton: true,
                    confirmButtonText: "Yes.",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131',
                    type: "error"
                });
            }
            else{
                check_and_save_file();
            }
        }

    };
        function check_and_save_file(){
            var filename = $scope.model.Testcase.Details.Name + '.xml';

        fileFactory.checkfileexistwithsubdir(filename, 'testcase', $scope.subdirs)
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

    function save(filename) {
        var x2js = new X2JS();
        var token = angular.toJson($scope.model);

        var xmlDoc = x2js.json2xml_str(JSON.parse(token));

        TestcaseFactory.save(filename, $scope.subdirs, xmlDoc)
            .then(
                function(data) {
                    console.log(data);
                    var engineer = $scope.model.Testcase.Details.Engineer;
                    $scope.model = {
                          "Testcase": {
                            "Details": {
                              "Name": "",
                              "Title": "",
                              "Category": "",
                                "State": "",
                              "Engineer": "",
                              "Date": "",
                              "Time": "",
                              "default_onError": {
                                "_action": "next",
                                "_value": "2"
                              },
                              "InputDataFile": "",
                              "Datatype": "",
                              "Logsdir": "",
                              "Resultsdir": ""
                            },
                            "Requirements": {
                              "Requirement": []
                            },
                            "Steps": {
                              "step": []
                            }
                          }
                        };
                    $scope.status.nodatafile = '0';
                    $scope.model.Testcase.Details.Date = moment().format('YYYY-MM-DD');
                    $scope.model.Testcase.Details.Time = moment().format('HH:mm');
                    $scope.model.Testcase.Details.Engineer = engineer;
                    sweetAlert({
                        title: "File saved: " + filename,
                        showConfirmButton: false,
                        type: "success",
                        timer: 1250
                    });

            if ($scope.savecreateTestcaseCap) {
                     
             }else{
                     $location.path('/testcases');
                 }


                },
                function(data) {
                    alert(data);
                });
    }

    window.S = $scope;

}]);
