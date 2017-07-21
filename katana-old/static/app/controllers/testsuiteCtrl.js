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

app.controller('testsuiteCtrl', ['$scope', '$http', '$location', 'fileFactory', function($scope, $http, $location, fileFactory) {

    $scope.xml = {};
    $scope.xml.suitefiles = [];
    $scope.xml.suitefolders = [];
    $scope.dir_path = "none";
    $scope.base_dir = undefined;
    $scope.dirs = [];

    $scope.inputDataFileChanged = function(element) {

        $scope.$apply(function(scope) {
            var thefile = element.files[0];
            alert('thefile' + JSON.stringify(thefile))
                /*

            var reader = new FileReader();
             reader.onload = function(e) {
                ...
             };
             reader.readAsDataURL(photofile);
             */
        });

    };

    function readConfig(){
        $http.get('/readconfig')
            .success(function(data, status, headers, config) {
                var temp = data["testsuitedir"];
                $scope.base_dir = temp.split('\\').pop().split('/').pop();
                if(temp == ""){
                    setTimeout(function(){
                        swal({
                            title: "The Configuration for the Suites Directory hasn't been set up yet. Do you want to set it up?",
                            text: "By setting up the configuration, you would be able to view existing files or create and save new ones.",
                            showCancelButton: true,
                            closeOnConfirm: true,
                            confirmButtonColor: '#3b3131',
                            confirmButtonText: "Lets set it up!",
                            cancelButtonText: "Nah, I was just lookin'.",
                            animation: "slide-from-top"
                        },
                            function(isConfirm){
                                if (isConfirm) {
                                    setTimeout(function(){
                                        swal({
                                            title: "The Suites Directory Configuration",
                                            text: "Location of the Suites Directory:",
                                            type: "input",
                                            showCancelButton: true,
                                            closeOnConfirm: false,
                                            animation: "slide-from-top",
                                            inputPlaceholder: "",
                                            confirmButtonColor: '#3b3131',
                                            confirmButtonText: "Set this location",
                                            cancelButtonText: "Nah, I don't want to."
                                        },
                                        function(inputValue){
                                          if (inputValue === false) return false;

                                          if (inputValue === "") {
                                            swal.showInputError("You should enter the location of the Suites Directory.");
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
                                                            fileFactory.updateconfigfromtab("testsuitedir", test_value)
                                                            .then(
                                                                function(data) {
                                                                    if(data["updated"] == "yes") {
                                                                        readConfig();
                                                                        readTestSuiteFolderNames("none");
                                                                        readTestSuiteFileNames("none");
                                                                        swal({
                                                                            title: "Saved the Suites Directory Path: ",
                                                                            text: inputValue,
                                                                            timer: 1250,
                                                                            type: "success",
                                                                            showConfirmButton: false
                                                                        });
                                                                    }
                                                                    else{
                                                                        swal({
                                                                            title: "Configuration could not be updated!",
                                                                            text: "",
                                                                            timer: 1250,
                                                                            type: "error",
                                                                            showConfirmButton: false
                                                                        });
                                                                    }
                                                                    });
                                                                }
                                                        else{
                                                            swal.showInputError("This file path doesn't exist.");
                                                            return false
                                                        }
                                                    });
                                          }
                                        });
                                    }, 250);
                                }
                            }
                        );
                    }, 500);
                }
            })
            .error(function(data, status, headers, config) {
                alert("Error fetching config data.", status, headers);
            });
    }

    readConfig();

    function readTestSuiteFileNames(directory) {
        $http.get('/testsuitefilenames/' + directory)
            .success(function(data, status, headers, config) {
                $scope.xml.suitefiles = data;
                console.log('testsuitefilenames: ' + JSON.stringify(data));
            })
            .error(function(data, status, headers, config) {
                alert("Error fetching suite file names.", status, headers);
            });
    }

    readTestSuiteFileNames("none");

    function readTestSuiteFolderNames(directory) {
        $http.get('/testsuitefoldernames/' + directory)
            .success(function(data, status, headers, config) {
                $scope.xml.suitefolders = data;
                console.log('testsuitefoldernames: ' + JSON.stringify(data));
            })
            .error(function(data, status, headers, config) {
                alert("Error fetching suite folder names.", status, headers);
            });
    }

    readTestSuiteFolderNames("none");

    $scope.navigateToCreateTestsuitePage = function() {
        console.log('in');
        $location.path('/newtestsuite');
    };

    $scope.getSubFilesAndFolders = function(directory){
        $scope.xml.suitefiles = [];
        $scope.xml.suitefolders = [];
        if($scope.dir_path == undefined || $scope.dir_path == "none"){
            $scope.dir_path = directory;
            $scope.dirs.push(directory)
        }
        else{
            $scope.dir_path = $scope.dir_path + "," + directory;
            $scope.dirs.push(directory)
        }
        readTestSuiteFolderNames($scope.dir_path);
        readTestSuiteFileNames($scope.dir_path);
    };

    $scope.getParentFilesAndFolders = function(){
        $scope.xml.suitefiles = [];
        $scope.xml.suitefolders = [];
        $scope.dirs = $scope.dir_path.split(",");
        $scope.dirs.pop();
        var temp_dir_path = "none";
        for(var i=0; i<$scope.dirs.length; i++){
            if(i == 0){
                temp_dir_path = $scope.dirs[i];
            }
            else{
                temp_dir_path = temp_dir_path + "," + $scope.dirs[i]
            }
        }
        if(temp_dir_path == "none"){
            $scope.dir_path = "none";
        }
        else{
            $scope.dir_path = temp_dir_path;
        }
        readTestSuiteFolderNames(temp_dir_path);
        readTestSuiteFileNames(temp_dir_path);
    };

    $scope.goToDir = function(directory){
        var dirs = $scope.dir_path.split(",");
        var num = 0;
        var len = dirs.length;
        var flag = false;

        for(var i=(len - 1); i>=0; i--){
            if(dirs[i] == directory){
                num = i;
                flag = true;
                break;
            }
        }

        if(flag){
            num = num+1;
        }

        for(i=(len-1); i>num; i--){
            dirs.pop();
        }

        for(i=0; i<dirs.length; i++){
            if(i == 0){
                $scope.dir_path = dirs[i]
            }
            else{
                $scope.dir_path = $scope.dir_path + "," + dirs[i]
            }
        }

        $scope.getParentFilesAndFolders();
    };

}]);