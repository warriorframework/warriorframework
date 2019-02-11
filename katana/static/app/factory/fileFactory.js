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

app.factory('fileFactory', ['$http', '$routeParams', '$q', function($http, $routeParams, $q) {
    return {

         
        checkfileexist: function(filename, filetype) {
            var deferred = $q.defer();
            $http.get('/checkfileexist/' + filename + '/' + filetype)
                .success(function(data, status, headers, config) {
                    deferred.resolve(data);
                })
                .error(function(data, status, headers, config) {
                    deferred.reject("Error checking file exist: " + status + ' ' + JSON.stringify(headers));
                });
            return deferred.promise;
        },

        checkfileexistwithsubdir: function(filename, filetype, subdirs) {
            var deferred = $q.defer();
            $http.get('/checkfileexistwithsubdir/' + filename + '/' + filetype + '/' + subdirs)
                .success(function(data, status, headers, config) {
                    deferred.resolve(data);
                })
                .error(function(data, status, headers, config) {
                    deferred.reject("Error checking file exist: " + status + ' ' + JSON.stringify(headers));
                });
            return deferred.promise;
        },
        
        readtooltipfile: function(tooltiptype) {
            var deferred = $q.defer();
            $http.get('/readtooltip/' + tooltiptype)
                .success(function(data, status, headers, config) {  
                    deferred.resolve(data);
                })
                .error(function(data, status, headers, config) {
                    deferred.reject("Error reading tootip file : " + status + ' ' + JSON.stringify(headers));
                });
            return deferred.promise;
        },

        readstatesfile: function() {
            var deferred = $q.defer();
            $http.get('/readstates')
                .success(function(data, status, headers, config) {
                    deferred.resolve(data);
                })
                .error(function(data, status, headers, config) {
                        deferred.reject("Error reading states file : " + status + ' ' + JSON.stringify(headers));
                        });
            return deferred.promise;
        },
        readdatafile: function() {
            var deferred = $q.defer();
            $http.get('/readdatafile')
                .success(function(data, status, headers, config) {
                    deferred.resolve(data);
                })
                .error(function(data, status, headers, config) {
                        deferred.reject("Error reading tootip file : " + status + ' ' + JSON.stringify(headers));
                });
            return deferred.promise;
        },

        updatestatesfile: function(tab) {
            var deferred = $q.defer();
            $http.get('/updatestates/' + tab)
            .success(function(data, status, headers, config) {
                    deferred.resolve(data);
                })
                .error(function(data, status, headers, config) {
                    deferred.reject("Error reading states file : " + status + ' ' + JSON.stringify(headers));
                });
            return deferred.promise;
        },

        updatedeftagsfile: function(tab) {
            var deferred = $q.defer();
            $http.get('/updatedeftags/' + tab)
            .success(function(data, status, headers, config) {
                    deferred.resolve(data);
                })
                .error(function(data, status, headers, config) {
                    deferred.reject("Error updating default tags file : " + status + ' ' + JSON.stringify(headers));
                });
            return deferred.promise;
        },

        get_files_and_folders: function(path) {

            var deferred = $q.defer();
            $http.get('/get_paths/' + path)
                .success(function(data, status, headers, config) {
                    deferred.resolve(data);
                })
                .error(function(data, status, headers, config) {
                    deferred.reject("Could not retrieve file paths: " + status + ' ' + JSON.stringify(headers));
                });
            return deferred.promise;
        },

        checkfilepath: function(path_json) {
            var deferred = $q.defer();
            $http.get('/checkfilepath/' + path_json)
                .success(function(data, status, headers, config) {
                    deferred.resolve(data);
                })
                .error(function(data, status, headers, config) {
                    deferred.reject("Could not retrieve file paths: " + status + ' ' + JSON.stringify(headers));
                });
            return deferred.promise;
        },

        populatepaths: function(path_json) {
            var deferred = $q.defer();
            $http.get('/populatepaths/' + path_json)
                .success(function(data, status, headers, config) {
                    deferred.resolve(data);
                })
                .error(function(data, status, headers, config) {
                    deferred.reject("Could not retrieve file paths: " + status + ' ' + JSON.stringify(headers));
                });
            return deferred.promise;
        },

        readdeftagsfile: function() {
            var deferred = $q.defer();
            $http.get('/readdeftagsfile')
                .success(function(data, status, headers, config) {
                    deferred.resolve(data);
                })
                .error(function(data, status, headers, config) {
                        deferred.reject("Error reading tootip file : " + status + ' ' + JSON.stringify(headers));
                });
            return deferred.promise;
        },

        updateconfigfromtab: function(directory, path) {
            var deferred = $q.defer();
            $http.post('/updateconfigfromtab/' + directory + '/' + path)
                .success(function(data, status, headers, config) {
                    deferred.resolve(data);
                })
                .error(function(data, status, headers, config) {
                        deferred.reject("Error reading tootip file : " + status + ' ' + JSON.stringify(headers));
                });
            return deferred.promise;
        },

        getSystems: function(path) {
     
            var deferred = $q.defer();
            $http.get('/datafilepath/' + path)
                .success(function(data, status, headers, config) {
                    deferred.resolve(data);
                })
                .error(function(data, status, headers, config) {
                    //deferred.reject("Could not retrieve file paths: " + status + ' ' + JSON.stringify(headers));
                });
            return deferred.promise;
        },

        getSubsys: function(path,name) {
               
            var deferred = $q.defer();
            $http.get('/sysName/' + path + '/' + name)
                .success(function(data, status, headers, config) {
                    deferred.resolve(data);
                })
                .error(function(data, status, headers, config) {
                    //deferred.reject("Could not retrieve file paths: " + status + ' ' + JSON.stringify(headers));
                });
            return deferred.promise;
        }

        };
}]);
