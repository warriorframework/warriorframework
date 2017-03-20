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

app.controller('baseChariotCtrl', ['$scope', '$http', function($scope, $http) {
    this.readConfig = function() {
        $http.get('/readconfig')
            .success(function(data, status, headers, config) {
                $scope.cfg = data;
				$scope.testsuitedir = data["testsuitedir"];
				$scope.projdir = data["projdir"];
				if($scope.testsuitedir.lastIndexOf("\\") === -1) {
					$scope.datadirpath = $scope.testsuitedir.substring(0, $scope.testsuitedir.lastIndexOf("/"));
					$scope.datadirpath = $scope.datadirpath + "/Data";
				}
				else{
					$scope.datadirpath = $scope.testsuitedir.substring(0, $scope.testsuitedir.lastIndexOf("\\"));
					$scope.datadirpath = $scope.datadirpath + "\\Data";
				}
            })
            .error(function(data, status, headers, config) {
                alert("Error fetching config data.", status, headers);
            });
    };

    this.readConfig();

	this.getDateTime = function() {
		var now     = new Date(); 
		var year    = now.getFullYear();
		var month   = now.getMonth()+1; 
		var day     = now.getDate();
		var hour    = now.getHours();
		var minute  = now.getMinutes();
		var second  = now.getSeconds(); 
		if(month.toString().length == 1) {
			var month = '0'+month;
		}
		if(day.toString().length == 1) {
			var day = '0'+day;
		}   
		if(hour.toString().length == 1) {
			var hour = '0'+hour;
		}
		if(minute.toString().length == 1) {
			var minute = '0'+minute;
		}
		if(second.toString().length == 1) {
			var second = '0'+second;
		}   
		var dateTime = month+'/'+day+'/'+year+' '+hour+':'+minute+':'+second;   
		return dateTime;
	}

	this.getDate = function() {
		var now     = new Date(); 
		var year    = now.getFullYear();
		var month   = now.getMonth()+1; 
		var day     = now.getDate();
		
		if(month.toString().length == 1) {
			var month = '0'+month;
		}
		if(day.toString().length == 1) {
			var day = '0'+day;
		}   
		
		var dateTime = month+'/'+day+'/'+year;   
		return dateTime;
	}	

	this.getTime = function() {
		var now     = new Date(); 
		var hour    = now.getHours();
		var minute  = now.getMinutes();
		var second  = now.getSeconds(); 

		if(hour.toString().length == 1) {
			var hour = '0'+hour;
		}
		if(minute.toString().length == 1) {
			var minute = '0'+minute;
		}
		if(second.toString().length == 1) {
			var second = '0'+second;
		}   
		var time = hour+':'+minute+':'+second;   
		return time;
	}

	this.checkfileexist = function(filename, filetype) {
        $http.get('/checkfileexist/' + filename + '/' + filetype)
            .success(function(data, status, headers, config) {
            	alert(JSON.stringify(data));
                return data.response
                
            })
            .error(function(data, status, headers, config) {
                alert("Error checking file exist.", status, headers);
            });
    }

}]);
