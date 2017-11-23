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

app.controller('kwSeqCtrlr', ['$scope','$routeParams','$http', '$location', '$anchorScroll', 'KwSeqFactory', 'fileFactory', 'getConfigFactory', 'subdirs',
    function ($scope, $routeParams, $http, $location, $anchorScroll, KwSeqFactory, fileFactory, getConfigFactory, subdirs) {

    'use strict';

        $scope.step_numbers = [];
        $scope.stepToBeCopied = "None";
        $scope.stepBeingEdited = "None";
        $scope.subdirs = subdirs;
        $scope.xml = {};
        $scope.xml.file = '';
        $scope.xml.check = '';
        $scope.xml.json = '';
        $scope.xml.pycs = {};
        $scope.xml.args = {};
        $scope.arg_list = [{"_name": "", "_value": ""}];
        $scope.showStepEdit = false;
        $scope.insertStep = false;
        $scope.res1 = [];
        $scope.resNew = [];
        $scope.myList = [];

        //Angular Model for Wrapper Keyword
        $scope.model = {
            "WrapperKeyword": {
                "Details": {
                    "WrapperName": "",
                    "dvname" : "",
                    "ActionFile": "",
                    "Description": "",

                },

                "Subkeyword": {
                    "Skw": [
                    ]
                }
            }
        };


        $scope.keweqTooltips = [];

        //To Read Tooltip
        fileFactory.readtooltipfile('kwseq')
            .then(
                function(data) {
                    $scope.keweqTooltips = data;
                },
                function(data) {
                    alert(data);
                });
        //To Read Config File
        function readConfig(){
            getConfigFactory.readconfig()
            .then(function (data) {
               $scope.cfg = data;
            });
        }

        readConfig();

        $scope.addAnotherArgumentToList = function (){
            $scope.arg_list.push({"_name": "", "_value": ""});
        };

        $scope.deleteArgFromList = function(index){
            if($scope.arg_list.length > 1){
                $scope.arg_list.splice(index, 1);
            }
            else{
                $scope.arg_list = [{"_name": "", "_value": ""}];
            }
        };

        $scope.xml.mapargs = {};
        $scope.xml.arglist = [];
        $scope.changedIndex = -1;

        $scope.savecreateTestcaseCap = false;
        $scope.new_state = "";

        $scope.updateNewStateValue = function(tab){
            if(tab.indexOf('%') === -1) {
              $scope.new_state = tab;
            }
            else {
                sweetAlert({
                        title: "No percentage character (%) allowed!",
                        closeOnConfirm: true,
                        confirmButtonColor: '#3b3131',
                        confirmButtonText: "Ok",
                        type: "error"
                    });
            }
        };

    //To Copy the existing Subkeyword Step
        $scope.copyStep = function(){

            if($scope.stepToBeCopied == "None"){
                swal({
                    title: "Please select a subkeyword number from the dropdown.",
                    type: "error",
                    showConfirmButton: true,
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131',
                    confirmButtonText: "Ok"
                });
                return;
            }

            $scope.status.driverCheckbox = false;
            $scope.status.kwCheckbox = false;

            $scope.status.drivername = $scope.model.WrapperKeyword.Subkeyword.Skw[$scope.stepToBeCopied - 1]._Driver;
            $scope.status.keyword = $scope.model.WrapperKeyword.Subkeyword.Skw[$scope.stepToBeCopied - 1]._Keyword;

            var drivers = $scope.xml.pycs[$scope.status.drivername];
            if(drivers == undefined){
                $scope.status.driverCheckbox = true;
                $scope.status.kwCheckbox = true;
            }
            else{
                var ads = [];
                _.each(drivers, function (driver) {
                    ads.push(_.filter(driver, function(d) {
                        return d.type === 'fn' && d.fn !== '__init__';
                    }));
                });
                var kwds = _.flatten(ads);
                kwds = _.sortBy(kwds, function(r) {return r.fn});
                if(!kwds.hasOwnProperty(length)){
                    kwds = [kwds];
                }
                var kw_list = [];
                for(i=0; i<kwds.length; i++){
                    kw_list.push(kwds[i].fn);
                }
                var index_of_kw = kw_list.indexOf($scope.status.keyword);
                if(index_of_kw == -1){
                    $scope.status.kwCheckbox = true;
                }
                else{
                    $scope.xml.keywords = kwds;
                    $scope.status.description = kwds[index_of_kw].wdesc;
                    $scope.xml.args.def = kwds[index_of_kw].def;
                    $scope.xml.args.comment = kwds[index_of_kw].comment;
                }
            }

            $scope.status.Skw.Description = $scope.model.WrapperKeyword.Subkeyword.Skw[$scope.stepToBeCopied - 1].Description;
            if(!$scope.model.WrapperKeyword.Subkeyword.Skw[$scope.stepToBeCopied - 1].Arguments.argument.hasOwnProperty(length)){
                $scope.model.WrapperKeyword.Subkeyword.Skw[$scope.stepToBeCopied - 1].Arguments.argument = [$scope.model.WrapperKeyword.Subkeyword.Skw[$scope.stepToBeCopied - 1].Arguments.argument];
            }
            if($scope.status.kwCheckbox){
                $scope.arg_list = $scope.model.WrapperKeyword.Subkeyword.Skw[$scope.stepToBeCopied - 1].Arguments.argument;
            }
            else{
                var mapped_arg_obj = {};
                for(var i=0; i<$scope.model.WrapperKeyword.Subkeyword.Skw[$scope.stepToBeCopied - 1].Arguments.argument.length; i++){
                    mapped_arg_obj[$scope.model.WrapperKeyword.Subkeyword.Skw[$scope.stepToBeCopied - 1].Arguments.argument[i]._name] = $scope.model.WrapperKeyword.Subkeyword.Skw[$scope.stepToBeCopied - 1].Arguments.argument[i]._value;
                }
                $scope.xml.mapargs = mapped_arg_obj;
                $scope.xml.args = _.where($scope.xml.keywords, { fn: $scope.status.keyword })[0];
                $scope.xml.arglist = _.map($scope.xml.args.args, function (a) {
                    return a.split('=')[0];
                });
            }

        };

        //To Read the file
    function readTestCaseFile() {
        KwSeqFactory.fetch()
            .then(function (data) {
                $scope.xml.file = data.xml;
                $scope.xml.pycs = data.pycmts;
                $scope.xml.drivers = _.sortBy(_.keys(data.pycmts), function (d) { return d; });
                $scope.xml.keywords = {};

                var x2js = new X2JS();
                var jsonObj = x2js.xml_str2json($scope.xml.file);
                if (jsonObj == null) {
                    sweetAlert({
                        title: "There was an error reading the Case: " + data["filename"],
                        text: "This XML file may be malformed.",
                        closeOnConfirm: true,
                        confirmButtonColor: '#3b3131',
                        confirmButtonText: "Ok",
                        type: "error"
                    });
                    return;
                }

                if ($scope.model.WrapperKeyword.Subkeyword === undefined) {
                    $scope.model.WrapperKeyword.Subkeyword = {};
                    $scope.model.WrapperKeyword.Subkeyword.Skw = [];
                }
                if (_.isEmpty($scope.model.WrapperKeyword.Subkeyword)) {
                    var ok = delete $scope.model.WrapperKeyword.Subkeyword;
                    $scope.model.WrapperKeyword.Subkeyword = {};
                    $scope.model.WrapperKeyword.Subkeyword.Skw = [];
                }
                if ($scope.model.WrapperKeyword.Subkeyword == '' || _.size($scope.model.WrapperKeyword.Subkeyword) == 0) {
                    $scope.model.WrapperKeyword.Subkeyword["Skw"] = [];
                }

                if(!$scope.model.WrapperKeyword.Subkeyword.Skw.hasOwnProperty(length)){
                    if($scope.model.WrapperKeyword.Subkeyword.Skw.length === 0){

                    }
                    else{
                        $scope.model.WrapperKeyword.Subkeyword.Skw = [$scope.model.WrapperKeyword.Subkeyword.Skw];
                    }
                }

                if (  ! _.isArray($scope.model.WrapperKeyword.Subkeyword['Skw'])) {
                    var xstep = $scope.model.WrapperKeyword.Subkeyword['Skw'];
                    delete $scope.model.WrapperKeyword.Subkeyword['Skw'];
                    $scope.model.WrapperKeyword.Subkeyword['Skw'] = [xstep];
                }
                if (_.isString($scope.model.WrapperKeyword.Subkeyword['Skw'])) {
                    var xstep = $scope.model.WrapperKeyword.Subkeyword['Skw'];
                    $scope.model.WrapperKeyword.Subkeyword['Skw'] = [xstep];
                }

                $scope.xml.json = JSON.stringify(jsonObj, null, 2);
                console.log('$scope.model.WrapperKeyword', JSON.stringify($scope.model.WrapperKeyword, null, 2));

            }, function (msg) {
                alert(msg);
            });

    }

    readTestCaseFile();

    //Model
    $scope.status = {

        nodatafile: '0',
        idfclass: '',
        index: 0,
        step_edit_mode: 'None',
        stepindex: 0,
        Skws: [],
        Skw: {},
        drivername: '',
        keyword: '',
        kwCheckbox: false,
        driverCheckbox: false
    };


    $scope.putReqEditorOutOfSight = function () {
        if ($scope.status.reqedtype != 'None') {
            $scope.status.reqedtype = 'None';
        }
    };

    //To Delete Subkeyword
    $scope.delKwseq = function (index) {

        sweetAlert({
            title: "Are you sure you want to delete Subkeyword #" + (index+1) + "?",
            closeOnConfirm: false,
            confirmButtonColor: '#3b3131',
            confirmButtonText: "Ok",
            showCancelButton: true,
            cancelButtonText: "Nope. I want to keep this Subkeyword.",
            type: "warning"
        },
        function(isConfirm){
            if (isConfirm) {
                $scope.$apply($scope.model.WrapperKeyword.Subkeyword.Skw.splice(index, 1));
                swal({
                    title: "Subkeyword deleted.",
                    timer: 1250,
                    type: "success",
                    showConfirmButton: false
                });
            }
        });
    };

    $scope.hasNoSteps = function () {
        var output = false;
        if($scope.model.WrapperKeyword.Subkeyword.Skw.length == 0){
            output = true;
        }
        else if($scope.model.WrapperKeyword.Subkeyword.Skw.length == 1){
            if($scope.showStepEdit && $scope.stepBeingEdited !== "None"){
                output = true;
            }
        }
        return output
    };

    $scope.startStepEdit = function (edtype, val, index) {
        if($scope.showStepEdit){
            swal({
                title: "You have a Subkeyword open in the Subkeyword editor that should be saved before creating a new Subkeyword.",
                text: "Please save that Subkeyword.",
                type: "warning",
                confirmButtonText: "Ok",
                closeOnConfirm: true,
                confirmButtonColor: '#3b3131'
            });
        }
        else {
            startStepCap(edtype, val, index);
        }
    };

        function startStepCap(edtype, val, index){
            $scope.step_numbers = [];
            $scope.stepToBeCopied = "None";
            for(var i=0; i<$scope.model.WrapperKeyword.Subkeyword.Skw.length; i++){
                $scope.step_numbers.push(i+1);
            }
            $scope.showStepEdit = true;
            $scope.status.step_edit_mode = edtype;
            $scope.status.stepindex = index;
            $scope.status.Skw = mkNewStep();
            if (edtype == 'New') {
                $scope.driverSelected('');
            }
            $scope.status.driverCheckbox = false;
            $scope.status.kwCheckbox = false;
            if($scope.insertStep){
                $scope.insertStep = false;
            }
        }

        $scope.showTopTable = function(index){
            if($scope.insertStep){
                return index > $scope.stepBeingEdited
            }
            else{
                return index >= $scope.stepBeingEdited
            }

        };

        //To Add Subkeyword
    $scope.addKwseq = function (index) {
        if($scope.showStepEdit){
            swal({
                title: "You have a Subkeyword open in the Subkeyword editor that should be saved before editing a new Subkeyword.",
                text: "Please save that Subkeyword.",
                type: "warning",
                confirmButtonText: "Ok",
                closeOnConfirm: true,
                confirmButtonColor: '#3b3131'
            });
        }
        else {

            $scope.status.step_edit_mode = 'New';
            $scope.status.stepindex = index;
            $scope.status.Skw = mkNewStep();
            $scope.driverSelected('');
            $scope.stepBeingEdited = index;
            $scope.showStepEdit = true;
            $scope.step_numbers = [];
            $scope.stepToBeCopied = "None";
            for(var i=0; i<$scope.model.WrapperKeyword.Subkeyword.Skw.length; i++){
                $scope.step_numbers.push(i+1);
            }
            $scope.insertStep = true;
        }
    };

    $scope.reqStepEdTypeAsString = function () {
        return ($scope.status.step_edit_mode == 'Edit') ? 'Edit' : 'New';
    };

    // Allow Edit op for the Step at the given index within the Steps array.
    // Event handler when the driver name is selected in the Step Grid.
    $scope.editStep = function (drivername, index) {

        if($scope.showStepEdit){
            swal({
                title: "You have a Subkeyword open in the Subkeyword editor that should be saved before editing a new Subkeyword.",
                text: "Please save that Subkeyword.",
                type: "warning",
                confirmButtonText: "Ok",
                closeOnConfirm: true,
                confirmButtonColor: '#3b3131'
            });
        }
        else {
            openStepCap(drivername, index);
        }
    };

        function openStepCap(drivername, index){
            $scope.stepBeingEdited = index;
            $scope.step_numbers = [];
            $scope.stepToBeCopied = "None";
            for(var i=0; i<$scope.model.WrapperKeyword.Subkeyword.Skw.length; i++){
                if(i !== index){
                    $scope.step_numbers.push(i+1);
                }
            }
            $scope.showStepEdit = true;
            $scope.status.driverCheckbox = false;
            $scope.status.kwCheckbox = false;
            $scope.putReqEditorOutOfSight();
            $scope.status.stepindex = index;

            $scope.status.Skw = $scope.model.WrapperKeyword.Subkeyword.Skw[index];

            $scope.changedIndex = index;
            $scope.driverSelected(drivername);
            var flag_kwd_length = true;
            if($scope.xml.keywords.length > 0){
                var kwd = _.find ($scope.xml.keywords, function (kw) {
                    return kw.fn == $scope.status.Skw._Keyword;
                });
                if(kwd == undefined){
                    flag_kwd_length = false;
                    kwd = get_unavailable_kwd_data(index);
                }
            }
            else{
                flag_kwd_length = false;
                kwd = get_unavailable_kwd_data(index);
            }
            console.log('kwd: ', JSON.stringify(kwd));

            $scope.status.keyword = kwd.fn;
            if(flag_kwd_length){
                $scope.selectKeyword(kwd.fn);  // Do this before setting the values of args.
            }


            var args = _.map(kwd.args, function (a) {
                return $.trim(a.split('=')[0]);
            });

            //-- mapargs management.
            if (kwd.args[0] == 'self') {
                $scope.xml.mapargs['self'] = '';
            }
            else{
                $scope.status.driverCheckbox = true;
                $scope.status.kwCheckbox = true;
            }

            if(!$scope.status.Skw.Arguments.argument.hasOwnProperty(length)){
                $scope.status.Skw.Arguments.argument = [$scope.status.Skw.Arguments.argument];
            }

            var vals = _.pluck($scope.status.Skw.Arguments.argument, '_name');

            console.log('vals ', JSON.stringify(vals));
            console.log('kwd-arg-a ', JSON.stringify(kwd, null, 2));

            // Clear the map, so that if another item is selected in the UI, the args look good.

            $scope.xml.mapargs = {};
            _.each(kwd.argsmap, function (v, k) {
                $scope.xml.mapargs[k] = '';
            });

            _.each($scope.status.Skw.Arguments.argument, function (a, i) {
                $scope.xml.mapargs[a._name] = a._value;
            });

            console.log('MAPARGS: ', JSON.stringify($scope.xml.mapargs, null, 2));
            $scope.status.step_edit_mode = 'Edit';
            if($scope.insertStep){
                $scope.insertStep = false;
            }

            }

    $scope.showStepEditor = function () {
        return $scope.status.step_edit_mode != 'None';
    };

        function get_unavailable_kwd_data(index){
            var kwd = {};
            kwd["fn"] = $scope.model.WrapperKeyword.Subkeyword.Skw[index]._Keyword;
            kwd["type"] = "fn";
            kwd["wdesc"] = "No WDescription available as this Keyword has not been defined yet.";
            kwd["def"] = "A signature for this Keyword has not been defined yet.";
            var var_argsmap = {};
            var var_args = [];
            if($scope.model.WrapperKeyword.Subkeyword.Skw[index].Arguments.argument.hasOwnProperty(length)){
                $scope.arg_list = $scope.model.WrapperKeyword.Subkeyword.Skw[index].Arguments.argument;
            }
            else{
                $scope.arg_list = [$scope.model.WrapperKeyword.Subkeyword.Skw[index].Arguments.argument];
            }
            for(var i=0; i<$scope.arg_list.length; i++){
                var_argsmap[$scope.arg_list[i]._name] = $scope.arg_list[i]._value;
                if($scope.arg_list[i]._value != ""){
                    var_args.push($scope.arg_list[i]._name + "=" + $scope.arg_list[i]._value + "");
                }
                else{
                    var_args.push($scope.arg_list[i]._name);
                }
            }
            kwd["argsmap"] = var_argsmap;
            kwd["line"] = 0;
            kwd["args"] = var_args;
            kwd["comment"] = ["No Comments available."];
            return kwd;
        }

    $scope.cancelArguments = function () {
        $scope.status.Skw = mkNewStep();
        $scope.showStepEdit = false;
        $scope.stepBeingEdited = "None";
        $scope.stepToBeCopied = "None";
        if($scope.insertStep){
            $scope.insertStep = false;
        }
        return $scope.status.step_edit_mode = 'None';
    };

//To auto populate Actionfile path
        $scope.driverSelectedUp = function(drivername){
            var abc = "<root>" + drivername + "</root>";
            if($scope.myList != ''){
                $scope.myList = '';
                               
                $scope.myList = [];
                $scope.checkField(abc);
            }
            else{
               $scope.checkField(abc);
            }
        };

        $scope.checkField = function(abc){

            KwSeqFactory.search(abc)
                .then(
                    function (data) {
                        $scope.res1.push(data);
                        var xx = JSON.stringify($scope.res1);
                        var count = (xx.match(/py/g) || []).length;
                        for (var i=0;i<count;i++){
                            var temp = xx.split('.py')[i];
                            if(i==0){
                              temp = temp.split('[\"')[1];
                            }
                            $scope.resNew = temp + ".py";
                            $scope.myList.push($scope.resNew);
							
                        }
                      });
            $scope.res1 = '';
            $scope.res1 = [];

        };


        //Driver related fucntionalities
    $scope.driverSelected = function (drivername) {

        $scope.putReqEditorOutOfSight();
        $scope.status.drivername = drivername;
        $scope.status.keyword = '';

        var drivers = $scope.xml.pycs[drivername];
        var ads = [];
        _.each(drivers, function (driver) {
            ads.push(_.filter(driver, function(d) {
                return d.type === 'fn' && d.fn !== '__init__';
            }));
        });
        var kwds = _.flatten(ads);
        kwds = _.sortBy(kwds, function(r) {return r.fn});
        $scope.xml.keywords = kwds;

        return kwds;
    };

    //Keyword related functionalities
    $scope.selectKeyword = function (keyword) {
        $scope.putReqEditorOutOfSight();
        console.log('In selectKeyword(' + keyword + ')');
        var k = _.findWhere ($scope.xml.keywords, { fn: keyword });
        if (k['wdesc'] != '') {
            $scope.status.stepdescription = k['wdesc'];
        } else {
            $scope.status.stepdescription = k['fn'];
        }
        $scope.xml.args = _.where($scope.xml.keywords, { fn: keyword })[0];
        $scope.xml.arglist = _.map($scope.xml.args.args, function (a) {
            return a.split('=')[0];
        });
        $scope.xml.mapargs = {};
        _.each($scope.xml.arglist, function (v) {
            $scope.xml.mapargs[v] = '';
        });
        console.log('xml.args', JSON.stringify($scope.xml.args));
        return $scope.xml.args;
    };

    function mkNewStep() {
        var rec = {
          "Arguments": {
            "argument": []
          },

          "_Driver": '',
          "_Keyword": ''
        };
        $scope.xml.mapargs = {};
        return rec;
    }

    function populate_step(driver, funname) {
        var rec = {
          "Arguments": {
            "argument": []
          },
            "_Number": "1",
            "_Driver": '',
            "_Keyword": ''
        };
        console.log('mapargs', JSON.stringify($scope.xml.mapargs, null, 2));
        rec._Driver = driver;
        rec._Keyword = funname;
        console.log('$scope.xml.mapargs: ', JSON.stringify($scope.xml.mapargs));
        _.each($scope.xml.mapargs, function (v, k) {
            if (k != 'self' && $.trim(v) != '') {
                rec.Arguments.argument.push({'_name': k, '_value': v });
            }
        });

        console.log('rec', JSON.stringify(rec, null, 2));
        return rec;
    }

    //Called when Subkeyword is saved
    $scope.saveArguments = function () {
        var driver = $.trim($scope.status.drivername) || '',
            keyword = $.trim($scope.status.keyword) || '';
        if(!$scope.status.driverCheckbox && !$scope.status.kwCheckbox){
            if (driver == '' || keyword == '' ) {
                sweetAlert({
                    title: "We need the Driver & Keyword definitions for a Subkeyword specification.",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131',
                    confirmButtonText: "Ok",
                    type: "error"
                });
                return;
            }
        }
        else{
            if (keyword == '' ) {
                sweetAlert({
                    title: "We need the Keyword definition for a Subkeyword specification.",
                    closeOnConfirm: true,
                    confirmButtonColor: '#3b3131',
                    confirmButtonText: "Ok",
                    type: "error"
                });
                return;
            }
            else {
                if($scope.arg_list.length > 1){
                    for(var i=0; i<$scope.arg_list.length; i++){
                        if($scope.arg_list[i]._name == ""){
                            sweetAlert({
                                title: "The Name for Argument " + (i+1) + " has been left empty.",
                                closeOnConfirm: true,
                                confirmButtonColor: '#3b3131',
                                confirmButtonText: "Ok",
                                type: "error"
                            });
                            return;
                        }
                    }
                }
            }
        }


        var newstep = populate_step(driver, keyword);
        if (newstep == null) {
            return;
        }

        if ($scope.status.step_edit_mode == 'New') {
            if($scope.status.stepindex==-1){
                if($scope.model.WrapperKeyword.Subkeyword.Skw === undefined){
                    $scope.model.WrapperKeyword.Subkeyword.Skw = [];
                }
                $scope.model.WrapperKeyword.Subkeyword.Skw.push(newstep);
	        }
            else {
                $scope.model.WrapperKeyword.Subkeyword.Skw.splice($scope.status.stepindex+1,0,newstep)
            }
        }
        else {
            $scope.model.WrapperKeyword.Subkeyword.Skw[$scope.status.stepindex] = newstep;
        }
        $scope.status.step_edit_mode = 'None';
        $scope.kwCheckbox = false;
        $scope.driverCheckbox = false;
        $scope.showStepEdit = false;
        $scope.stepBeingEdited = "None";
        $scope.stepToBeCopied = "None";
        if($scope.insertStep){
            $scope.insertStep = false;
        }
    };

    $scope.cancelKwseqCap = function() {
        $location.path('/kwseq');
    };

    //Called when Wrapper Keyword is saved
    $scope.saveKwseqCap = function () {

        if($scope.showStepEdit){
            sweetAlert({
                title: "There is a Subkeyword that has not been saved yet.",
                text: "Either save this Subkeyword or discard it before saving the Wrapper Keyword",
                showCancelButton: false,
                showConfirmButton: true,
                type: "warning",
                closeOnConfirm: true,
                confirmButtonColor: '#3b3131',
                confirmButtonText: "Ok"
            });
            return;
        }

        if ($.trim($scope.model.WrapperKeyword.Details.WrapperName) == '') {
            sweetAlert({
                title: "A Wrapper Name is required.",
                text: "Please do not specify spaces in it.",
                closeOnConfirm: true,
                confirmButtonColor: '#3b3131',
                confirmButtonText: "Ok",
                type: "error"
            });
            return;
        }

        var hasSpace = _.find($.trim($scope.model.WrapperKeyword.Details.WrapperName), function (c) {
            return c == ' ';
        });

        if (hasSpace != undefined) {
            sweetAlert({
                title: "Please do not use spaces in the Name field of the Wrapper Keyword Name.",
                closeOnConfirm: true,
                confirmButtonColor: '#3b3131',
                confirmButtonText: "Ok",
                type: "error"
            });
            return;
        }
        if ($.trim($scope.model.WrapperKeyword.Details.ActionFile) == '') {
            sweetAlert({
                title: "Actionfile Name is required.",
                closeOnConfirm: true,
                confirmButtonColor: '#3b3131',
                confirmButtonText: "Ok",
                type: "error"
            });
            return;
        }

        if ($scope.model.WrapperKeyword.Subkeyword.Skw.length == 0) {
            sweetAlert({
                title: "You need to define at least one Subkeyword before you can save this Wrapper Keyword.",
                closeOnConfirm: true,
                confirmButtonColor: '#3b3131',
                confirmButtonText: "Ok",
                type: "error"
            });
            return;
        }

        check_and_save_file();
    };

    function check_and_save_file(){
            var filename = $scope.model.WrapperKeyword.Details.WrapperName + '.xml';

        fileFactory.checkfileexistwithsubdir(filename, 'testcase', $scope.subdirs)
            .then(
                function(data) {
                    console.log(data);
                        save(filename);

                },
                function(data) {
                    alert(data);
                });
        }

    function save(filename) {

        var x2js = new X2JS();
        var token = angular.toJson($scope.model);
        var xmlDoc = x2js.json2xml_str(JSON.parse(token));

        $scope.final = xmlDoc;

        KwSeqFactory.save(xmlDoc)
            .then(
                function(data) {
                    console.log(data);
                    var dlist = data.split(';');
                    var typ;
                    if(dlist[0].search('saved') != -1) {
                        typ = "success";
                        $location.path('/kwseq');
                    } else if(dlist[0].search('already exist') != -1) {
                        typ = "warning";
                    } else {
                        typ = "error";
                    }

                    sweetAlert({
                                 title: dlist[0],
                                 text: dlist[1],
                                 closeOnConfirm: true,
                                 confirmButtonColor: '#3b3131',
                                 confirmButtonText: "Ok",
                                 type: typ
                        });
                });

    }

    window.S = $scope;
}]);

