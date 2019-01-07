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

app.controller('configCtrl', ['$scope', '$route', '$http', 'fileFactory', function($scope, $route, $http, fileFactory) {

    // console.log($route);

    $scope.cfg = {};
    $scope.path = "";
    $scope.flag = true;
    $scope.cfg.basedir = "/home/vap/labs/fujitsu/raw/python";
    $scope.cfg.xmldir = "/home/vap/labs/fujitsu/web/chariot/xml";
    $scope.default_paths = {
        "pythonsrcdir": "Warrior",
        "xmldir": "Testcases",
        "testwrapper": "TestWrapper",
        "testsuitedir": "Suites",
        "projdir": "Projects",
        "idfdir": "Data",
        "testdata": "Config_files",
        "warhorn_config": "Warhorn Config Files",
        "python_path": "Python Path"
    };
    $scope.orig = {
        engineer: "",
        pythonsrcdir: "",
        testsuitedir: "",
        projdir: "",
        testwrapper:"",
        idfdir: "",
        testdata: "",
        warhorn_config: "",
        python_path: ""
    };
    $scope.changedInputs = {};
    $scope.saveBtnHighlight = false;

    $scope.highlightSaveBtn = function(identifier){
        var flag = false;
        if(identifier != "all"){
            if($scope.cfg[identifier] == $scope.orig[identifier]){
                $scope.changedInputs[identifier] = false;
            }
            else{
                $scope.changedInputs[identifier] = true;
            }
        }
        for(var key in $scope.changedInputs){
            if($scope.changedInputs.hasOwnProperty(key)){
                if($scope.changedInputs[key]){
                    flag = true;
                    break;
                }
            }
        }
        $scope.saveBtnHighlight = flag;
    };

    $scope.setFlag = function(){
        if($scope.cfg.pythonsrcdir != $scope.orig.pythonsrcdir){
            $scope.flag = true;
        }
        else{
            $scope.flag = false;
        }
        $scope.highlightSaveBtn("pythonsrcdir");
    };

    $scope.saveBaseDir = function() {
        alert("The Python driver/action base directory is: " + $scope.cfg.basedir);
    };

    $scope.saveXmlDir = function() {
        alert("The test-case XML directory is: " + $scope.cfg.xmldir);
    };

    function readConfig(_callback) {
        $http.get('/readconfig')
            .success(function(data, status, headers, config) {
                $scope.cfg = data;
                $scope.orig.engineer = $scope.cfg.engineer;
                $scope.orig.pythonsrcdir = $scope.cfg.pythonsrcdir;
                $scope.orig.testsuitedir = $scope.cfg.testsuitedir;
                $scope.orig.projdir = $scope.cfg.projdir;
                $scope.orig.testwrapper = $scope.cfg.testwrapper;
                $scope.orig.idfdir = $scope.cfg.idfdir;
                $scope.orig.testdata = $scope.cfg.testdata;
                $scope.orig.warhorn_config = $scope.cfg.warhorn_config;
                $scope.orig.python_path = $scope.cfg.python_path;
                _callback();
            })
            .error(function(data, status, headers, config) {
                alert("Error fetching config data. ", status, headers);
            });
    }

    readConfig(function(){
        startUp();
    });

    function startUp(){
        get_path_for_files();
        fileFactory.get_files_and_folders($scope.path);
    }

    function get_path_for_files(){
        var array = [];
        if($scope.cfg["xmldir"].indexOf("\\")>= 0) {
            array = $scope.cfg["xmldir"].split("\\");
        }
        else {
            array = $scope.cfg["xmldir"].split("/");
        }
        var path = "";
        var len = array.length - 1;
        for(var i=len-1; i>=0; i--){
            if(array[i] == "Warriorspace"){
                break;
            }
            else{
                array.pop();
            }
        }
        for(i=0; i<array.length-1; i++){
            path = path + array[i] + ">"
        }
        $scope.path = path.replace(/\>$/, '');
    }

    $scope.saveCfg = function() {

        if($scope.cfg.engineer.trim() == ""){
            swal({
                title: "Engineer Name field is mandatory",
                text: "Your Name:",
                type: "input",
                closeOnConfirm: false,
                animation: "slide-from-top",
                inputPlaceholder: "",
                confirmButtonColor: '#3b3131',
                confirmButtonText: "Ok"
            },
            function(inputValue){

              if (inputValue === "") {
                swal.showInputError("You should enter your name");
                return false
              }
                else{
                  $scope.$apply($scope.cfg.engineer = inputValue);
                  /*swal(
                      {
                          title: "Name saved as: " + inputValue,
                          text: "",
                          timer: 1250,
                          type: "success"
                      }
                  );*/
                  $scope.saveCfg();
              }
            });
        }

        else if($scope.cfg.pythonsrcdir.trim() == ""){
            swal({
                title: "This field is mandatory",
                text: "Location of the Warrior Framework Directory:",
                type: "input",
                closeOnConfirm: true,
                animation: "slide-from-top",
                inputPlaceholder: "",
                confirmButtonColor: '#3b3131',
                confirmButtonText: "Set this location"
            },
            function(inputValue){

              if (inputValue === "") {
                swal.showInputError("You should enter the location of the Warrior Framework Directory.");
                return false
              }
                  else{
                  if(inputValue.indexOf("/") !== -1){
                      var inputValue_list = inputValue.split("/");
                      var test_value = inputValue_list[0];
                      for(var i=1; i<inputValue_list.length; i++){
                          test_value = test_value + "$sep$" + inputValue_list[i];
                      }
                  }
                  else{
                      inputValue_list = inputValue.split("\\");
                      test_value = inputValue_list[0];
                      for(i=1; i<inputValue_list.length; i++){
                          test_value = test_value + "$sep$" + inputValue_list[i];
                      }
                  }
                    fileFactory.checkfilepath(test_value)
                        .then(
                        function(data) {
                            if(data["exists"] == "yes"){
                                $scope.$apply($scope.cfg.pythonsrcdir = inputValue);
                                $scope.flag = true;
                                $scope.autoPopulate();
                            }else{
                                swal.showInputError("This file path doesn't exist.");
                                return false
                            }
                        });
              }
            });
        }

        else{
            console.log("saving json");

            $http.post('/updateconfig', $scope.cfg)
                .success(function(data, status, headers, config) {
                    console.log("Success updating config.json");
                    $scope.changedInputs = {};
                    readConfig($scope.highlightSaveBtn("all"));
                    swal({
                        title: 'Configuration has been saved.',
                        text: "",
                        type: "success",
                        timer: 1250,
                        showConfirmButton: false
                    });
                    get_path_for_files();
                    fileFactory.get_files_and_folders($scope.path)
                })
                .error(function(data, status, headers, config) {

                    console.log("Failed to update config.json");
                    var op = data;
                        var pathsnotfound = _.map(op.notfounds, function (nf) {
                            return nf;
                        });
                    var not_found = "";
                    $scope.changedInputs = {};
                    for(var i=0; i<pathsnotfound.length; i++){
                        var temp_array = [];
                        temp_array = pathsnotfound[i].split("=");
                        for(var j=0; j<temp_array.length; j++){
                            temp_array[j] = temp_array[j].trim();
                        }
                        not_found = not_found + $scope.default_paths[temp_array[0]] + ", ";
                        $scope.changedInputs[temp_array[0]] = true;
                    }
                    not_found = not_found.slice(0, -2);
                    var index = not_found.lastIndexOf(",");
                    if(index != -1){
                        not_found = not_found.substr(0, index) + ' and' + not_found.substr(index+1);
                    }
                    readConfig($scope.highlightSaveBtn("all"));
                    swal({
                        title: "Error writing to configuration file.",
                        text: "The paths for " + not_found + " were not found!",
                        type: "error",
                        showConfirmButton: true,
                        confirmButtonColor: '#3b3131'
                    });
                });
            }
        };

    $scope.autoPopulate = function(){
        if($scope.flag) {
            var inputValue = $scope.cfg.pythonsrcdir;
            if(inputValue.indexOf("/") !== -1){
                var inputValue_list = inputValue.split("/");
                var test_value = inputValue_list[0];
                for(var i=1; i<inputValue_list.length; i++){
                    test_value = test_value + "$sep$" + inputValue_list[i];
                }
            }
            else{
                inputValue_list = inputValue.split("\\");
                test_value = inputValue_list[0];
                for(i=1; i<inputValue_list.length; i++){
                    test_value = test_value + "$sep$" + inputValue_list[i];
                }
            }

            fileFactory.checkfilepath(test_value)
                .then(
                    function(data) {
                        if(data["exists"] == "yes"){
                            $scope.orig_pythonsrcdir = $scope.cfg.pythonsrcdir;
                            swal({
                                    title: "Do you want Katana to populate the fields for Cases, Suites, Projects, Input Data Files, and TestData file with the default values?",
                                    text: "The directories would be relative to " + $scope.cfg.pythonsrcdir,
                                    showCancelButton: true,
                                    closeOnConfirm: false,
                                    animation: "slide-from-top",
                                    inputPlaceholder: "",
                                    confirmButtonColor: '#3b3131',
                                    confirmButtonText: "Yes.",
                                    cancelButtonText: "Keep them as they are."
                                },
                                function (inputValue) {
                                    $scope.flag = false;
                                    if (inputValue === false) {
                                        $scope.saveCfg();
                                        return false;
                                    }
                                    else {
                                        if ($scope.cfg.pythonsrcdir.indexOf("/") !== -1) {
                                            var inputValue_list = $scope.cfg.pythonsrcdir.split("/");
                                            var test_value = inputValue_list[0];
                                            for (var i = 1; i < inputValue_list.length; i++) {
                                                test_value = test_value + "$sep$" + inputValue_list[i];
                                            }
                                        }
                                        else {
                                            inputValue_list = $scope.cfg.pythonsrcdir.split("\\");
                                            test_value = inputValue_list[0];
                                            for (i = 1; i < inputValue_list.length; i++) {
                                                test_value = test_value + "$sep$" + inputValue_list[i];
                                            }
                                        }
                                        fileFactory.checkfilepath(test_value)
                                            .then(
                                                function (data) {
                                                    if (data["exists"] == "yes") {
                                                        fileFactory.populatepaths(test_value)
                                                            .then(
                                                                function (output) {
                                                                    var not_found = "";
                                                                    var found = [];
                                                                    for (var key in output) {
                                                                        if (output.hasOwnProperty(key)) {
                                                                            if (output[key] == "") {
                                                                                not_found = not_found + $scope.default_paths[key] + ", "
                                                                            }
                                                                            else {
                                                                                found.push(key);
                                                                            }
                                                                        }
                                                                    }

                                                                    if (not_found != "") {
                                                                        not_found = not_found.slice(0, -2);
                                                                        var index = not_found.lastIndexOf(",");
                                                                        if (index != -1) {
                                                                            not_found = not_found.substr(0, index) + ' and' + not_found.substr(index + 1);
                                                                        }
                                                                    }

                                                                    if (not_found == "") {
                                                                        for (var i = 0; i < found.length; i++) {
                                                                            $scope.$apply($scope.cfg[found[i]] = output[found[i]]);
                                                                        }
                                                                        /*swal(
                                                                         {
                                                                         title: "Fields Successfully Populated.",
                                                                         text: "",
                                                                         timer: 1250,
                                                                         type: "success",
                                                                         showConfirmButton: false
                                                                         }
                                                                         );*/
                                                                        $scope.saveCfg();
                                                                    }
                                                                    else {
                                                                        for (i = 0; i < found.length; i++) {
                                                                            $scope.$apply($scope.cfg[found[i]] = output[found[i]]);
                                                                        }
                                                                        swal(
                                                                            {
                                                                                title: "Some default paths weren't found.",
                                                                                text: "Paths weren't found for: " + not_found,
                                                                                type: "warning",
                                                                                confirmButtonColor: '#3b3131',
                                                                                confirmButtonText: "Ok.",
                                                                                showConfirmButton: true,
                                                                                closeOnConfirm: false
                                                                            },
                                                                            function () {
                                                                                $scope.saveCfg();
                                                                            }
                                                                        );
                                                                    }

                                                                }
                                                            );
                                                    } else {
                                                        swal.showInputError("This file path doesn't exist.");
                                                        return false
                                                    }
                                                });
                                    }
                                });
                        }
                        else{
                            swal({
                                title: "Oops! This directory path does not exist.",
                                text: "The directory path enter for the Warrior Framework Directory is invalid. Please enter a valid directory path.",
                                type: "error",
                                showCancelButton: false,
                                showConfirmButton: true,
                                closeOnConfirm: true,
                                confirmButtonColor: '#3b3131',
                                confirmButtonText: "Alright!"
                            }
                            )
                        }
                    });
        }
    }

}]);