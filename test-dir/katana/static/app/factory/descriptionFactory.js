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

app.factory('descriptionFactory', ['$http', '$routeParams', '$q', function($http, $routeParams, $q) {
    return {
        fetchDescription: function(path) {
            var deferred = $q.defer();
            // console.log('fetchDescription(): path: ' + JSON.stringify(path));
            // path example: "desctype=parallel"
	        // $http.defaults.headers.post["Content-Type"] = "application/text";
            var parts = path.split('='),
                k = parts[0],
                v = parts[1];
            var payload = { 'desctype': v };
            $http.get('/showdescription', { params: payload })
                .success(function(data, status, headers, config) {
                    // console.log('fetchDescription(): success: data ' + JSON.stringify(data));
                    // data is something like this:
                    // [{"description":"This talks about the description of the performance process. This will explain about how the tests being executed using Warrior. Like what the format is."}]
                    deferred.resolve(data);
                })
                .error(function(data, status, headers, config) {
                    deferred.reject("Error reading execution description data file for " + parts[1]);
                })
            return deferred.promise;
        }
    };
}]);
