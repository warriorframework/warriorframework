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

app.factory('KwSeqFactory', ['$http', '$routeParams', '$q', function($http, $routeParams, $q) {
    return {
        fetch: function() {
            var deferred = $q.defer();
            $http.get('/testcase/' + $routeParams.testcase + "/" + $routeParams.subdirs)
                .success(function(data, status, headers, config) {
                    deferred.resolve(data);
                })
                .error(function(data, status, headers, config) {
                    deferred.reject("Error fetching XML file: " + status + ' ' + JSON.stringify(headers));
                });
            return deferred.promise;
        },
        search: function(dvname) {
            var deferred = $q.defer();
            $http.post('/searchkw', dvname )
                .success(function(data, status, headers, config) {
                    deferred.resolve(data);
                })
                .error(function(data, status, headers, config) {
                    deferred.reject("Error fetching XML file: " + status + ' ' + JSON.stringify(headers));
                });
            return deferred.promise;
        },
        save: function(xmlObj) {
            var deferred = $q.defer();
            $http.post('/parsexmlobj', xmlObj)
                .success(function(data, status, headers, config) {
                    deferred.resolve(data);
                })
                .error(function(data, status, headers, config) {
                    deferred.reject("Error while saving xml: " + filename  + ' '
                        + status + ' ' + JSON.stringify(headers));
                })
            return deferred.promise;
        }
    };
}]);
