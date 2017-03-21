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
 * Created by skulkarn on 11/2/2016.
 */
app.controller('aboutCtrl', ['$scope','$routeParams','$http', '$location', 'fileFactory',
    function ($scope, $routeParams, $http, $location, fileFactory) {

        $scope.cfg = "Nope";
        $scope.username = "User";
        $scope.goToConfigFile = false;
        $scope.map_mandatory = {
            "pythonsrcdir": "The Warrior Framework Directory",
            "engineer": "Your Name"
        };
        $scope.flag_mandatory = false;
        $scope.map_optional = {
            "testsuitedir": "Suite",
            "projdir": "Project",
            "xmldir": "Case",
            "idfdir": "Input Data File",
            "testdata": "Test Data File"
        };
        $scope.flag_optional = false;
        $scope.list_mandatory = [];
        $scope.list_optional = [];

        function readConfig(_callback) {
        $http.get('/readconfig')
            .success(function(data, status, headers, config) {
                $scope.cfg = data;
                _callback();
            })
            .error(function(data, status, headers, config) {
                alert("Error fetching config data. ", status, headers);
            });
        }

        function startNew(){
            readConfig();
            setTimeout(function(){
                for(var key in $scope.cfg){
                    if($scope.cfg.hasOwnProperty(key)){
                        if($scope.cfg[key].trim() == ""){
                            if($scope.map_mandatory.hasOwnProperty(key)){
                                $scope.flag_mandatory = true;
                                $scope.list_mandatory.push($scope.map_mandatory[key])
                            }
                            if($scope.map_optional.hasOwnProperty(key)){
                                $scope.flag_optional = true;
                                $scope.list_optional.push($scope.map_optional[key])
                            }
                        }
                        else{
                            if(key == "engineer"){
                                $scope.username = $scope.cfg[key];
                            }
                        }
                    }
                }

                if($scope.flag_mandatory){
                    if($scope.username == "User" && $scope.list_mandatory.length == 2){
                        if($scope.list_optional.length == 5){
                            swal({
                                title: "Hey New User! Good to see you venturing into automation!",
                                text: "Katana has a one time configuration set up that lets you integrate Katana and Warrior. Set it up to start automating cool stuff!",
                                showCancelButton: true,
                                closeOnConfirm: true,
                                confirmButtonColor: '#3b3131',
                                confirmButtonText: "Yes, take me there!",
                                cancelButtonText: "Nah, I like it this way.",
                                animation: "slide-from-top"
                            },
                                function(isConfirm){
                                    if (isConfirm) {
                                        window.location.href = '#/configuration';
                                    }
                                }
                            );
                        }
                        else{
                            swal({
                                title: "Welcome back, New User! Seems like you haven't configured the Warrior directory into Katana.",
                                text: "Set it up so that you can start executing Warrior through Katana!",
                                showCancelButton: true,
                                closeOnConfirm: true,
                                confirmButtonColor: '#3b3131',
                                confirmButtonText: "Yes, I'd like to set up Katana!",
                                cancelButtonText: "I'll do it later.",
                                animation: "slide-from-top"
                            },
                                function(isConfirm){
                                    if (isConfirm) {
                                        window.location.href = '#/configuration';
                                    }
                                }
                            );
                        }
                    }
                    else {
                        swal({
                            title: "Welcome back, " + $scope.username + "! Seems like you haven't finished configuring your Katana!",
                            text: "Set it up so that you can start automating with Warrior!",
                            showCancelButton: true,
                            closeOnConfirm: true,
                            confirmButtonColor: '#3b3131',
                            confirmButtonText: "Let's go!",
                            cancelButtonText: "Not now.",
                            animation: "slide-from-top"
                        },
                            function(isConfirm){
                                if (isConfirm) {
                                    window.location.href = '#/configuration';
                                }
                            }
                        );
                    }
                } else if ($scope.flag_optional) {
                    swal({
                        title: "Hey " + $scope.username + "! Katana Configuration beckons your attention!",
                        text: "Fill it out to start creating all your XMLs!.",
                        showCancelButton: true,
                        closeOnConfirm: true,
                        confirmButtonColor: '#3b3131',
                        confirmButtonText: "Alright! Let's set Katana up!",
                        cancelButtonText: "Not today.",
                        animation: "slide-from-top"
                    },
                        function(isConfirm){
                            if (isConfirm) {
                                window.location.href = '#/configuration';
                            }
                        }
                    );
                }


            }, 2000);
        }

        startNew();
    }]);
