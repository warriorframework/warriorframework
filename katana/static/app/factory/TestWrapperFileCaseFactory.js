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

app.factory('TestWrapperfilecaseFactory', ['$http', '$routeParams', '$q', function($http, $routeParams, $q) {
    return {
        fetch: function() {

            var deferred = $q.defer();
            $http.get('/TestWrapperfilecase/' + $routeParams.TestWrapperfilecase + "/" + $routeParams.subdirs)
                .success(function(data, status, headers, config) {
                    deferred.resolve(data);
                })
                .error(function(data, status, headers, config) {
                    deferred.reject("Error fetching Testcase XML file: " + status + ' ' + JSON.stringify(headers));
                });
            return deferred.promise;
        },

        save: function(filename, subdirs, xmlObj) {

            var deferred = $q.defer();
            $http.post('/saveTestWrapperfilecase/' + filename + '/' + subdirs, xmlObj)
                .success(function(data, status, headers, config) {
                    deferred.resolve(data);
                    console.log(data)
                })
                .error(function(data, status, headers, config) {
                    sweetAlert({
                        title: "Permission Denied.",
                        closeOnConfirm: false,
                        confirmButtonColor: '#3b3131',
                        confirmButtonText: "Ok",
                        text: "Please edit the directory permissions so that Katana can save this file.",
                        type: "warning"
                });

                })
            return deferred.promise;
        }
    };
}]);
