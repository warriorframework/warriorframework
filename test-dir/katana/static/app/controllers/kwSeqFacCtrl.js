app.factory('KwSeqFactCtrl', ['$http', '$routeParams', '$q', function($http, $routeParams, $q) {
    return {
        fetch: function() {
           
            var deferred = $q.defer();
            $http.get('/testcase/' + $routeParams.testcase + "/" + $routeParams.subdirs)
                .success(function(data, status, headers, config) {
                    deferred.resolve(data);
                })
                .error(function(data, status, headers, config) {
                    deferred.reject("Error fetching Testcase XML file: " + status + ' ' + JSON.stringify(headers));
                });
            return deferred.promise;
        },

        save: function(xmlObj) {
        alert("factory");
            var deferred = $q.defer();
            $http.post('/parsexmlobj', xmlObj)
                .success(function(data, status, headers, config) {
                    deferred.resolve(data);
                })
                .error(function(data, status, headers, config) {
                    deferred.reject("Error while saving testcase xml: " + filename  + ' '
                                    + status + ' ' + JSON.stringify(headers));
                })
            return deferred.promise;
        }
    };
}]);
