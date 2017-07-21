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

app.controller('sequentialCtrl', ['$scope','$http','$route', 'sequentialFactory','executionFactory','runFactory','descriptionFactory','fileFactory',
	function($scope,$http,$route, sequentialFactory, executionFactory, runFactory, descriptionFactory, fileFactory) {
//    (function($) {

        /*var extensionsMap = {
            ".zip": "fa-file-archive-o",
            ".gz": "fa-file-archive-o",
            ".bz2": "fa-file-archive-o",
            ".xz": "fa-file-archive-o",
            ".rar": "fa-file-archive-o",
            ".tar": "fa-file-archive-o",
            ".tgz": "fa-file-archive-o",
            ".tbz2": "fa-file-archive-o",
            ".z": "fa-file-archive-o",
            ".7z": "fa-file-archive-o",
            ".mp3": "fa-file-audio-o",
            ".cs": "fa-file-code-o",
            ".c++": "fa-file-code-o",
            ".cpp": "fa-file-code-o",
            ".js": "fa-file-code-o",
            ".xls": "fa-file-excel-o",
            ".xlsx": "fa-file-excel-o",
            ".png": "fa-file-image-o",
            ".jpg": "fa-file-image-o",
            ".jpeg": "fa-file-image-o",
            ".gif": "fa-file-image-o",
            ".mpeg": "fa-file-movie-o",
            ".pdf": "fa-file-pdf-o",
            ".ppt": "fa-file-powerpoint-o",
            ".pptx": "fa-file-powerpoint-o",
            ".txt": "fa-file-text-o",
            ".log": "fa-file-text-o",
            ".doc": "fa-file-word-o",
            ".docx": "fa-file-word-o",
        };

        function getFileIcon(ext) {
            return (ext && extensionsMap[ext.toLowerCase()]) || 'fa-file-o';
        }

        var dataset = ['a', 'b', 'c'];

        var options = {
            "data": dataset,
            "columns": [{
                "sTitle": "",
                "mData": null,
                "bSortable": false,
                "sClass": "head0",
                "sWidth": "55px",
                "render": function(data, type, row, meta) {
                    if (data.IsDirectory) {
                        return "<a href='#' target='_blank'><i class='fa fa-folder'></i>&nbsp;" + data.Name + "</a>";
                    } else {
                        return "<a href='/" + data.Path + "' target='_blank'><i class='fa " + getFileIcon(data.Ext) + "'></i>&nbsp;" + data.Name + "</a>";
                    }
                }
            }]
        };

        var table = $(".linksholder").dataTable(options);*/

     /*   sequentialFactory.fetchFilesnFolders({
            "directory": "e:/git/fujitsu/app/web/chariot"
        }).then(function(data) {
            console.log(data);
            /*table.fnClearTable();
            table.fnAddData(data);
        });

    })(jQuery);*/

	$scope.optionRadio = 'RMT';
	$scope.files=[];
    $scope.chosenFiles = [];
	$scope.executionType = '';
	$scope.description="Description not available";
	$scope.showPerformanceType=false;
	$scope.showParallelType=false;
	$scope.moduleType = 'Sequential';
	$scope.sequentialTooltip = [];
		$scope.basepathdir = "";
		$scope.temp_nodes = "";
		$scope.node_options = [];
		$scope.autoDefect = "";
		$scope.counter = 0;
		$scope.warning = "";
		if (navigator.appVersion.indexOf("Win")!=-1) {
			$scope.warning = "WARNING! If there is an open command prompt window that executed a testcase, you'll have to close that window so that the next execution can proceed. Do not close the command prompt which is running the katana server!";
		}


		$scope.getAutoDefectvalue = function(autodefectvalue){
			$scope.autoDefect = autodefectvalue;
		};

   fileFactory.readtooltipfile('sequential')
    .then(
        function(data) {
            console.log(data);
            $scope.sequentialTooltip = data;
        },
        function(data) {
            alert(data);
        });

		$scope.getData = function(){
			alert($scope.basepathdir)
		};

	$scope.moduleSelection = function(moduleType)
	{
		console.log(moduleType);
		readConfig();
		var parameter = "desctype="+$scope.moduleType;
		descriptionFactory.fetchDescription(parameter)
			.then(function(data) {
				console.log(data);
				$scope.description = data[0].description;
			});
		if (moduleType == 'Run selected files in sequence') {
			$scope.reset();
			$scope.showPerformanceType=false;
			$scope.showParallelType=false;
			$scope.executionType = "";
		} else if (moduleType == 'Run Keywords in Parallel') {
			$scope.reset();
			console.log("Inside para");
			$scope.showPerformanceType=false;
			$scope.showParallelType=true;
			$scope.executionType = "Sequential";
		} else {
			$scope.reset();
			console.log("Inside perf");
			$scope.showPerformanceType=true;
			$scope.showParallelType=false;
			$scope.executionType = "Parallel";
		}
	};

    $scope.selectedFiles = function(file) {
        if (file.done) {
			$scope.chosenFiles.push(file.filename);
		}
        else {
			for (var i=0;i<$scope.chosenFiles.length;i++) {
				if (file.filename == $scope.chosenFiles[i]){
					$scope.chosenFiles.splice(i, 1);
					break;
				}
			}
		}
	};

    $scope.reset = function(){
		$scope.files=[];
		$scope.chosenFiles = [];
		$scope.addDirectory ="";
		$scope.sharedDate = "";
		$scope.selectAll = false;
		$scope.sharedTime = "";
		$scope.iteration="";
		$scope.schedule = false;
		$scope.showIteration = false;
		document.getElementById("execResultLbl").innerHTML = "";
		document.getElementById('resultLbl').innerHTML = "";
     };

     $scope.fetchFiles = function() {
		console.log("Fetch Files " + $scope.addDirectory );
		var directoryPath = "dirname=" + $scope.addDirectory;
		if (typeof $scope.addDirectory != "undefined" && $scope.addDirectory.trim().length != 0) {
    		executionFactory.fetchFiles(directoryPath)
                .then(function(data) {
    				console.log("seq ctrl add files "+ JSON.stringify(data));
    				if (data.length == 0) {
    					alert("Specified directory contains no XML files.");
    				} else {
                        for(var i=0;i<data.length;i++){
                            $scope.files.push(data[i]);
                        }
                    }
    			});
    		}
        };

    $scope.executeFiles = function() {
		console.log( "Iter="+$scope.iteration+"Time= " +$scope.sharedTime +" Date= " + $scope.sharedDate );
		document.getElementById("execResultLbl").innerHTML = "";
		document.getElementById("resultLbl").innerHTML = "";
		if( $scope.chosenFiles.length == 0)
		{
			document.getElementById('resultLbl').style.color="Red";
			document.getElementById("resultLbl").innerHTML = "Please select atleast one file... ";
			document.getElementById("execResultLbl").innerHTML = "";
		}
		else if( ($scope.executionType == "Run Multiple Times" || $scope.executionType == "Run Until Failure" || $scope.executionType == "Run Until Pass")
			&& ($scope.iteration === undefined || $scope.iteration == "" || $scope.iteration == null))
		{
			document.getElementById('resultLbl').style.color="Red";
			document.getElementById("resultLbl").innerHTML = "Please enter value for Iteration..."
			document.getElementById("execResultLbl").innerHTML = "";
		}
		else if( $scope.schedule && ( typeof $scope.sharedDate == "undefined" || typeof $scope.sharedTime == "undefined" || $scope.sharedTime =="" || $scope.sharedDate =="")  )
		{
			document.getElementById('resultLbl').style.color="Red";
			document.getElementById("resultLbl").innerHTML =" Please select date and time for Schedule Run...";
			document.getElementById("execResultLbl").innerHTML = "";
		}
		else
		{
			var filenames =$scope.chosenFiles[0];
			var autodefect = '';
			var schedulerun = 'n';
			var datevalue = "";
			var runtype = "";
			var execType = "";
			var iterationval = "";

			document.getElementById('resultLbl').style.color="";
			document.getElementById('execResultLbl').style.color="";
			if(typeof $scope.moduleType != "undefined")
			{
				if( $scope.moduleType == 'Sequential')
					execType == "";
				else
					execType = $scope.moduleType;
			}
			/*if($scope.executionType=="Performance"){
				perfvalue =$scope.optionRadio;
			}*/

			if($scope.executionType == "Run Multiple Times")
			{
				runtype = "RMT";
				execType = "Performance"
			}
			else if( $scope.executionType == "Run Until Failure" )
			{
				runtype = "RUF";
				execType = "Performance"
			}
			else if( $scope.executionType == "Run Until Pass" )
			{
				runtype = "RUP";
				execType = "Performance"
			}
			else
			{
				runtype = $scope.executionType;
			}

			if($scope.autoDefect !== "" || $scope.autoDefect !=="None"){
				autodefect =  $scope.autoDefect
			}


			if($scope.schedule){
				schedulerun='y';
					datevalue = $scope.sharedDate+"-"+$scope.sharedTime;
			}

			if( typeof $scope.iteration != "undefined" )
			{
				iterationval = $scope.iteration;
			}

			for (var i=1;i<$scope.chosenFiles.length;i++)
				filenames += ","+ $scope.chosenFiles[i];

			var runParameters = "filenames="+filenames+'&exectype='+execType+'&autodefect='+autodefect+"&schedulerun="+schedulerun+"&datevalue="+datevalue+"&iterationval="+iterationval+"&runtype="+runtype;
			console.log(runParameters);

			 runFactory.executeFiles(runParameters
				).then(function(data) {
					document.getElementById("resultLbl").innerHTML ="Command to Run: "+data[0].command_to_run;
					document.getElementById("execResultLbl").innerHTML =  "Execution Result: "+data[0].Execution_Result;
				});
		}

    };


	$scope.options = []

	$scope.execSelection=function(executionType){
		console.log(executionType);
		if(executionType=="Run Multiple Times" || executionType == "Run Until Failure" || executionType == "Run Until Pass")
		{
	          //$scope.options=[{text:'Run Multiple Times',value:'RMT'},{text:'Run Until Fail',value:'RUF'}];
			  $scope.showIteration = true;
		}
		else{
			//$scope.options=[];
			$scope.showIteration = false;
		}
 	};

	$scope.selectAllFiles=function()
	{
		console.log("Select All");

		if($scope.selectAll)
		{
			for (var i=0; i < $scope.files.length; i++)
			{
				$scope.files[i].done=true;
				$scope.chosenFiles.push($scope.files[i].filename);
			}
		}
		else
		{
			for (var i=0; i < $scope.files.length; i++)
				$scope.files[i].done=false;

			$scope.chosenFiles = [];
		}
	}

	$scope.loadDescription = function()
	{
		var parameter = "desctype="+"sequential";
		descriptionFactory.fetchDescription(parameter)
            .then(function(data) {
				console.log(JSON.stringify(data));
				$scope.description = data[0].description;
		    }
	)};

	$scope.scheduleOperation = function()
	{
			$scope.sharedDate = "";
			$scope.sharedTime = "";
	}


	function readConfig() {
        $http.get('/readconfig')
            .success(function(data, status, headers, config) {
                // $scope.cfg.pythonsrcdir = data.pythonsrcdir;
				// $scope.cfg.basedir = data.basedir;
                // $scope.cfg.xmldir = data.xmldir;
                // $scope.cfg.testsuitedir = data.testsuitedir;
                // $scope.cfg.projdir = data.projdir;
				$scope.addDirectory = data.xmldir;
				console.log("Seq Ctrl "+$scope.addDirectory);
            })
            .error(function(data, status, headers, config) {
                alert("Error fetching config data.", status, headers);
            });
    }

		function  get_jira_projects(){
        $http.get('/get_jira_projects')
            .success(function(data, status, headers, config) {
				$scope.temp_nodes = data;
            })
            .error(function(data, status, headers, config) {
                alert("Error fetching config data.", status, headers);
            });
    };

		$scope.repeatSelect = null;

    readConfig();
		get_jira_projects();



    /*$scope.upTheDirectory = function() {
        if (!currentPath) return;
        var idx = currentPath.lastIndexOf("/");
        var path = currentPath.substr(0, idx);
        $.get('/querydirectory').then(function(data) {
            table.fnClearTable();
            table.fnAddData(data);
            currentPath = path;
        });
        console.log("span clicked!");
        console.log("up");
    }*/
}])
