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
app.config(function($routeProvider) {
    $routeProvider
        // .when('/', {
        //     templateUrl: '/assets/app/partials/about.tmpl.html'
        // })
        // .when('/testcases', {
        //     templateUrl: '/assets/app/partials/testcases.tmpl.html',
        //     controller: 'testcaseCtrl',
        //     resolve: {
        //         app: function($q) {
        //             var defer = $q.defer();
        //             defer.resolve();
        //             return defer.promise;
        //         }
        //     }
        // })
        .when('/', {
            templateUrl: '/assets/app/partials/about.tmpl.html',
            controller: 'aboutCtrl'
        })
        .when('/testcases', {
            templateUrl: '/assets/app/partials/testcases.tmpl.html',
            controller: 'TestcaseCtrl' /* ,
            resolve: {
                app: function ($q) {
                    var defer = $q.defer();
                    defer.resolve();
                    return defer.promise;
                }
            } */
        })

          .when('/wrapper_files', {
            templateUrl: '/assets/app/partials/TestWrapperfilecases.tmpl.html',
            controller: 'TestWrapperfilecaseCtrl' /* ,
            resolve: {
                app: function ($q) {
                    var defer = $q.defer();
                    defer.resolve();
                    return defer.promise;
                }
            } */
        })

        .when('/testsuites', {
            templateUrl: '/assets/app/partials/testsuite.tmpl.html',
            controller: 'testsuiteCtrl',
            resolve: {
                app: function($q) {
                    var defer = $q.defer();
                    defer.resolve();
                    return defer.promise;
                }
            }
        })
        .when('/newtestsuite', {
            templateUrl: '/assets/app/partials/newtestsuite.tmpl.html',
            controller: 'newTestsuiteCtrl',
            resolve: {
                subdirs: function () {
                    return "none"
                }
            }
        })
        .when('/testsuite/:testsuite/:subdirs', {
            templateUrl: '/assets/app/partials/testsuitecapture.tmpl.html',
            controller: 'testsuiteCapCtrl',
            resolve: {
                subdirs: function ($route) {
                    return $route.current.params.subdirs;
                },
                app: function($q) {
                    var defer = $q.defer();
                    defer.resolve();
                    return defer.promise;
                }
            }
        })
        .when('/projects', {
            templateUrl: '/assets/app/partials/projects.tmpl.html',
            controller: 'projectCtrl',
            resolve: {
                subdirs: function ($route) {
                    return $route.current.params.subdirs;
                },
                app: function($q) {
                    var defer = $q.defer();
                    defer.resolve();
                    return defer.promise;
                }
            }
        })
        .when('/datafiles', {
            templateUrl: '/assets/app/partials/datafiles.tmpl.html',
            controller: 'datafileCtrl',
            resolve: {
                app: function($q) {
                    var defer = $q.defer();
                    defer.resolve();
                    return defer.promise;
                }
            }
        })
        .when('/newproject', {
            templateUrl: '/assets/app/partials/newproject.tmpl.html',
            controller: 'newProjectCtrl',
            resolve: {
                subdirs: function () {
                    return "none"
                }
            }
        })
        .when('/newdatafile', {
            templateUrl: '/assets/app/partials/newdatafile.tmpl.html',
            controller: 'newDataFileCtrl',
            newFile: "yes",
            resolve: {
                subdirs: function () {
                    return "none"
                }
            }
        })

        .when('/datafile/:datafile/:subdirs', {
            templateUrl: '/assets/app/partials/newdatafile.tmpl.html',
            controller: 'newDataFileCtrl',
            newFile: "no",
            resolve: {
                subdirs: function ($route) {
                    return $route.current.params.subdirs;
                },
                app: function ($q) {
                    var defer = $q.defer();
                    defer.resolve();
                    return defer.promise;
                }
            }
        })

        .when('/project/:project/:subdirs', {
            templateUrl: '/assets/app/partials/projectcapture.tmpl.html',
            controller: 'projectCapCtrl',
            resolve: {
                subdirs: function ($route) {
                    return $route.current.params.subdirs;
                },
                app: function($q) {
                    var defer = $q.defer();
                    defer.resolve();
                    return defer.promise;
                }
            }
        })
        .when('/configuration', {
            templateUrl: '/assets/app/partials/configuration.tmpl.html',
            controller: 'configCtrl',
            resolve: {
                app: function($q) {
                    var defer = $q.defer();
                    defer.resolve();
                    return defer.promise;
                }
            }
        })

        // .when('/testcase/:testcase', {
        //     templateUrl: '/assets/app/partials/testcasecapture.tmpl.html',
        //     controller: 'testcaseCapCtrl',
        //     resolve: {
        //         app: function($q) {
        //             var defer = $q.defer();
        //             defer.resolve();
        //             return defer.promise;
        //         }
        //     }
        // })

        .when('/testDatafiles', {
            templateUrl: '/assets/app/partials/testdatafiles.tmpl.html',
            controller: 'testdatafileCtrl',
            resolve: {
                app: function($q) {
                    var defer = $q.defer();
                    defer.resolve();
                    return defer.promise;
                }
            }
        })

        .when('/newtestDatafile', {
            templateUrl: '/assets/app/partials/newtestdatafile.tmpl.html',
            controller: 'newTestDataFileCtrl',
            newFile: "yes",
            resolve: {
                subdirs: function () {
                    return "none"
                }
            }
        })

        .when('/kwseq/:testcase/:subdirs', {
            templateUrl: '/assets/app/partials/kwseq.tmpl.html',
            controller: 'kwSeqCtrlr',
            resolve: {
                subdirs: function ($route) {
                    return $route.current.params.subdirs;
                },
                app: function ($q) {
                    var defer = $q.defer();
                    defer.resolve();
                    return defer.promise;
                }
            }

        })

        .when('/testDatafile/:testdatafile/:subdirs', {
            templateUrl: '/assets/app/partials/newtestdatafile.tmpl.html',
            controller: 'newTestDataFileCtrl',
            newFile: "no",
            resolve: {
                subdirs: function ($route) {
                    return $route.current.params.subdirs;
                },
                app: function ($q) {
                    var defer = $q.defer();
                    defer.resolve();
                    return defer.promise;
                }
            }
        })


        .when('/testcase/:testcase/:subdirs', {
            templateUrl: '/assets/app/partials/testcasecapture.tmpl.html',
            controller: 'TestcaseCapCtrl',
            resolve: {
                subdirs: function ($route) {
                    return $route.current.params.subdirs;
                },
                app: function ($q) {
                    var defer = $q.defer();
                    defer.resolve();
                    return defer.promise;
                }
            }
        })


        .when('/TestWrapperfilecase/:TestWrapperfilecase/:subdirs', {
            templateUrl: '/assets/app/partials/TestWrapperfilecasecapture.tmpl.html',
            controller: 'TestWrapperfilecaseCapCtrl',
            resolve: {
                subdirs: function ($route) {
                    return $route.current.params.subdirs;
                },
                app: function ($q) {
                    var defer = $q.defer();
                    defer.resolve();
                    return defer.promise;
                }
            }
        })
        .when('/warhornconfigfiles', {
            templateUrl: '/assets/app/partials/warhornconfigfiles.tmpl.html',
            controller: 'warhornconfigfileCtrl',
            resolve: {
                app: function($q) {
                    var defer = $q.defer();
                    defer.resolve();
                    return defer.promise;
                }
            }
        })

        .when('/newwarhornconfigfile', {
            templateUrl: '/assets/app/partials/newwarhornconfigfile.tmpl.html',
            controller: 'newWarhornConfigFileCtrl',
            newFile: "yes",
            resolve: {
                subdirs: function () {
                    return "none"
                }
            }
        })

        .when('/warhornconfigfile/:warhornconfigfile/:subdirs', {
            templateUrl: '/assets/app/partials/newwarhornconfigfile.tmpl.html',
            controller: 'newWarhornConfigFileCtrl',
            newFile: "no",
            resolve: {
                subdirs: function ($route) {
                    return $route.current.params.subdirs;
                },
                app: function ($q) {
                    var defer = $q.defer();
                    defer.resolve();
                    return defer.promise;
                }
            }
        })

        .when('/newtestcase', {
            templateUrl: '/assets/app/partials/newtestcase.tmpl.html',
            controller: 'newTestcaseCtrl',
            resolve: {
                subdirs: function () {
                    return ""
                }
            }
        })
        .when('/sequential', {
            templateUrl: '/assets/app/partials/sequential.html',
            controller: 'sequentialCtrl'
        })
        .when('/parallel', {
            templateUrl: '/assets/app/partials/parallel.html',
            controller: 'parallelCtrl'
        })
        .when('/performance', {
            templateUrl: '/assets/app/partials/performance.html',
            controller: 'performanceCtrl'
        })
        .when('/kwseq', {
            templateUrl: '/assets/app/partials/kwsequencer.html',
            controller: 'KwSeqCtrl'
        })
        .otherwise({
            redirectTo: '/'
        });
});
