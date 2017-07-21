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

app.controller('TestcaseCapCtrl', ['$scope','$routeParams','$http', '$location', 'TestcaseFactory', 'fileFactory',
    function ($scope, $routeParams, $http, $location, TestcaseFactory, fileFactory) {

    'use strict';

    $scope.xml = {};
    $scope.xml.file = '';
    $scope.xml.json = '';
    $scope.xml.pycs = {};
    $scope.xml.args = {};
    // $scope.xml.capargs = [];        // where the arguments are captured in the form.

    $scope.xml.mapargs = {};
    $scope.xml.arglist = [];

    $scope.savecreateTestcaseCap = false;

    $scope.model = {
          "Testcase": {
            "Details": {
              "Name": "",
              "Title": "",
              "Engineer": "",
              "Date": "",
              "Time": "",
              "default_onError": {
                "_action": "next",
                "_value": "2"
              },
              "InputDataFile": "",
              "Datatype": "",
              "Logsdir": "",
              "Resultsdir": "",
              "Category": ""
            },
            "Requirements": {
              "Requirement": []
            },
            "Steps": {
              "step": [/*
                {
                  "Arguments": {
                    "argument": {
                      "_name": "count",
                      "_value": "1"
                    }
                  },
                  "onError": {
                    "_action": "goto",
                    "_value": "2"
                  },
                  "impact": "noimpact",
                  "context": "positive",
                  "_Driver": "DriverName",
                  "_Keyword": "KeywordName"
                }*/
              ]
            }
          }
        };

    function readTestCaseFile() {
        TestcaseFactory.fetch()
            .then(function (data) {
                $scope.xml.file = data.xml;
                $scope.xml.pycs = data.pycmts;
                $scope.xml.drivers = _.sortBy(_.keys(data.pycmts), function (d) { return d; });
                $scope.xml.keywords = {}; // mkKeywordMap($scope.xml.drivers, data.pycmts);

                var x2js = new X2JS();
                var jsonObj = x2js.xml_str2json($scope.xml.file);
                if (jsonObj == null) {
                    alert("There was an error reading XML file: " + $routeParams.testcase);
                    return;
                }
                $scope.model = jsonObj;

                $scope.model.Testcase.Details.Date = moment().format('YYYY-MM-DD');
                $scope.model.Testcase.Details.Time = moment().format('HH:mm');
                $scope.model.Testcase.Details.Engineer = data.engineer;

                if ($scope.model.Testcase.Requirements === undefined) {
                    $scope.model.Testcase.Requirements = {};
                    $scope.model.Testcase.Requirements.Requirement = [];
                }
                if (_.isEmpty($scope.model.Testcase.Requirements)) {
                    var ok = delete $scope.model.Testcase.Requirements;
                    $scope.model.Testcase.Requirements = {};
                    $scope.model.Testcase.Requirements.Requirement = [];
                    // console.log('Req', JSON.stringify($scope.model.Testcase.Requirements, null, 2));
                }
                if ($scope.model.Testcase.Requirements == '' ||
                    _.size($scope.model.Testcase.Requirements) == 0) {
                    $scope.model.Testcase.Requirements["Requirement"] = [];
                }
                if (_.isString($scope.model.Testcase.Requirements['Requirement'])) {
                    var req = $scope.model.Testcase.Requirements['Requirement'];
                    $scope.model.Testcase.Requirements['Requirement'] = [req];
                }

                for (var i = 0; i < $scope.model.Testcase.Requirements.Requirement.length; i++) {
                    if ($scope.model.Testcase.Requirements.Requirement[i] == '') {
                        $scope.model.Testcase.Requirements.Requirement.splice(i, 1);
                    }
                }

                //---- Steps normalization.
                if ($scope.model.Testcase.Steps === undefined) {
                    $scope.model.Testcase.Steps = {};
                    $scope.model.Testcase.Steps.step = [];
                }
                if (_.isEmpty($scope.model.Testcase.Steps)) {
                    var ok = delete $scope.model.Testcase.Steps;
                    $scope.model.Testcase.Steps = {};
                    $scope.model.Testcase.Steps.step = [];
                }
                if ($scope.model.Testcase.Steps == '' || _.size($scope.model.Testcase.Steps) == 0) {
                    $scope.model.Testcase.Steps["step"] = [];
                }
                if (  ! _.isArray($scope.model.Testcase.Steps['step'])) {
                    var xstep = $scope.model.Testcase.Steps['step'];
                    delete $scope.model.Testcase.Steps['step'];
                    $scope.model.Testcase.Steps['step'] = [xstep];
                }
                if (_.isString($scope.model.Testcase.Steps['step'])) {
                    var xstep = $scope.model.Testcase.Steps['step'];
                    $scope.model.Testcase.Steps['step'] = [xstep];
                }

                $scope.xml.json = JSON.stringify(jsonObj, null, 2);
                console.log('$scope.model.Testcase', JSON.stringify($scope.model.Testcase, null, 2));

                // Set up some $scope values that are not directly referring into the test case itself.
                $scope.status.default_onError = { _action: 'next', _value: '' };
                $scope.status.default_onError._action = $scope.model.Testcase.Details.default_onError._action;
                $scope.status.default_onError._value = $scope.model.Testcase.Details.default_onError._value || '';

                $scope.status.nodatafile = ($scope.model.Testcase.Details.InputDataFile == 'No_Data') ? '1' : '0';
                $scope.status.datatype = $scope.model.Testcase.Details.Datatype || 'Iterative';

            }, function (msg) {
                alert(msg);
            });
    }

    readTestCaseFile();

    $scope.status = {

        nodatafile: '0',
        idfclass: '',               // allows edit when zero length, else is set to 'disabled'.

        datatype: 'Iterative',      // Custom
        datatypes: ['Iterative', 'Custom'],

        reqedtype: 'None',          // Requirement editor type: 'New'/'Edit'/'None'; when None, the form is not showing.
        requirement: '',            // User makes a new req or edits existing req here.

        index: 0,

        step_edit_mode: 'None',     // Step editor type: 'New'/'Edit'/'None'; when None, the form is not showing.

        stepindex: 0,               // which'th step were we editing.
        steps: [],
        step: {},

        drivername: '',             // currently selected driver - in the select control.
        keyword: '',                // currently selected keyword - in the select box.

        default_onError: {          // This is the default_onError as it appears in the Details section.
            _action: 'next',
            _value: ""
        },

        stepsimpacts: ['impact', 'noimpact'],

        steperrors: ['next', 'abort', 'goto'],

        stepsexecutes: ['If', 'If Not', 'Yes', 'No'],

        stepexecuteerrors: ['next', 'abort', 'goto'],

        stepscontexts: ['positive', 'negative'],
    };

    $scope.grabDefaultStepNum = function () {

    };

    $scope.noteInputDataStatus = function () {
        var idfval = '', // 'Data File Required'
            clazz = '';
        if ($scope.status.nodatafile == '1') {
            idfval = 'No_Data';
            clazz = 'disabled';
        }
        $scope.status.idfclass = clazz;
        $scope.model.Testcase.Details.InputDataFile = idfval;
    };

    //-- Requirements Editor -----------------------------------------------

    $scope.putReqEditorOutOfSight = function () {
        if ($scope.status.reqedtype != 'None') {
            $scope.status.reqedtype = 'None';
        }
    };

    $scope.hasNoReqs = function () {
        return ($scope.model.Testcase.Requirements.Requirement.length == 0)
                || ($scope.model.Testcase.Requirements.Requirement.length == 1 &&
                                   $scope.model.Testcase.Requirements.Requirement[0] == '');
    };

    $scope.newReq = function () {
        return $scope.status.reqedtype == 'New'
    }

    $scope.reqEdTypeAsString = function () {
        if ($scope.status.reqedtype == 'None') {
            return 'New';
        }
        return $scope.status.reqedtype;
    }

    $scope.editReq = function () {
        return $scope.status.reqedtype == 'Edit'
    }

    $scope.startReqEdit = function (edtype, val, index) {
        $scope.status.reqedtype = edtype;
        $scope.status.index = index;
        $scope.status.requirement = val;
    };

    $scope.saveReq = function () {
        if ($.trim($scope.status.requirement) == '') {
            alert("Requirement field cannot be blank.");
            return;
        }
        if (_.size($scope.model.Testcase.Requirements) == 0) {
            $scope.model.Testcase.Requirements['Requirement'] = [];
        }
        var sa = $scope.model.Testcase.Requirements['Requirement'],
            ix = sa.indexOf($scope.status.requirement); // The value edited by our user.
        if (ix < 0) {
            if ($scope.status.reqedtype == 'New') {
                $scope.model.Testcase.Requirements['Requirement'].push($scope.status.requirement);
            } else {
                $scope.model.Testcase.Requirements['Requirement'][$scope.status.index] = $scope.status.requirement;
            }
            $scope.status.requirement = '';     // Clear to capture next requirement.
            $scope.putReqEditorOutOfSight();
        } else {
            alert('This item already exists in the list.');
        }
    };

    $scope.delReq = function (index) {
        if (confirm('Are you sure you wish to delete this Requirement?')) {
            $scope.model.Testcase.Requirements['Requirement'].splice(index, 1);
        }
    }

    /**
     * Show the Req editor if the reqedtype is New or Edit.
     * @return bool should show Req editor or not.
     */
    $scope.showReqEditor = function () {
        var ed = $scope.status.reqedtype;
        $('#reqeditor').focus();
        return ed === 'New' || ed === 'Edit';
    }

    $scope.cancelReq = function () {
        $scope.status.reqedtype = 'None';
    };

    //---------------------------------------------------------------
    //- STEPS -------------------------------------------------------
    //---------------------------------------------------------------

    $scope.delStep = function (index) {
        if (confirm("Delete step # " + (index+1) + " ?")) {
            $scope.model.Testcase.Steps.step.splice(index, 1);
        }
    };

    $scope.hasNoSteps = function () {
        return $scope.model.Testcase.Steps.step.length === 0;           // false;
    };

    $scope.startStepEdit = function (edtype, val, index) {
        $scope.cancelReq();
        $scope.status.step_edit_mode = edtype;
        $scope.status.stepindex = index;
        $scope.status.step = mkNewStep();
        if (edtype == 'New') {
            $scope.driverSelected('');
        }
    };

    $scope.reqStepEdTypeAsString = function () {
        return ($scope.status.step_edit_mode == 'Edit') ? 'Edit' : 'New';
    };

    // Allow Edit op for the Step at the given index within the Steps array.
    // Event handler when the driver name is selected in the Step Grid.
    $scope.editStep = function (drivername, index) {
        $scope.putReqEditorOutOfSight();
        $scope.status.stepindex = index;
        console.log("Editing step: " + drivername + ' @ ' + index);
        console.log('$scope.model: ' + JSON.stringify($scope.model));
        $scope.status.step = $scope.model.Testcase.Steps.step[index];
        console.log('Step to edit: ' + JSON.stringify($scope.status.step));
        $scope.driverSelected(drivername);
        var kwd = _.find ($scope.xml.keywords, function (kw) {
            return kw.fn == $scope.status.step._Keyword;
        });
        console.log('kwd: ', JSON.stringify(kwd));

        $scope.status.keyword = kwd.fn;
        $scope.selectKeyword(kwd.fn);  // Do this before setting the values of args.

        var args = _.map(kwd.args, function (a) {
            return $.trim(a.split('=')[0]);
        });

        //-- mapargs management.
        if (kwd.args[0] == 'self') {
            $scope.xml.mapargs['self'] = '';
        }

        var vals = _.pluck($scope.status.step.Arguments.argument, '_name');

        console.log('vals ', JSON.stringify(vals));
        console.log('kwd-arg-a ', JSON.stringify(kwd, null, 2));

        // Clear the map, so that if another item is selected in the UI, the args look good.

        $scope.xml.mapargs = {};
        _.each(kwd.argsmap, function (v, k) {
            $scope.xml.mapargs[k] = '';
        });

        _.each($scope.status.step.Arguments.argument, function (a, i) {
            $scope.xml.mapargs[a._name] = a._value;
        });

        console.log('MAPARGS: ', JSON.stringify($scope.xml.mapargs, null, 2));
        $scope.status.step_edit_mode = 'Edit';

    };

    $scope.showStepEditor = function () {
        return $scope.status.step_edit_mode != 'None';
    };

    $scope.cancelArguments = function () {
        $scope.status.step = mkNewStep();
        return $scope.status.step_edit_mode = 'None';
    };

    // On change of the Driver name select control.
    // Gather function names for the selected driver.
    $scope.driverSelected = function (drivername) {

        $scope.putReqEditorOutOfSight();

        $scope.status.drivername = drivername;
        $scope.status.keyword = '';                     // When driver is selected, clear the keyword.
        $scope.status.stepdescription = '';            // And, the description field.

        var drivers = $scope.xml.pycs[drivername];
        var ads = [];
        _.each(drivers, function (driver) {
            ads.push(_.filter(driver, function(d) {
                return d.type === 'fn' && d.fn !== '__init__';
            }));
        });
        var kwds = _.flatten(ads);
        kwds = _.sortBy(kwds, function(r) {return r.fn});
        $scope.xml.keywords = kwds;         // Function's details (comments, params, &c) of selected driver.

        return kwds;
    };

    // Gather arguments for currently selected keyword/fun.
    // keyword is the fun name.
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
        })
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
          "onError": {
            "_action": "next", // next, abort, goto
            "_value": ""
          },
          "Description": "",
          "Execute": {
            "_ExecType": "Yes",
            "Rule": {
                "_Condition":"",
                "_Condvalue":"",
                "_Else":"next",
                "_Elsevalue":"",
            }
          },
          "context": "positive",    // negative, positive
          "impact": "noimpact",     // impact, noimpact
          "_TS": "1",
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
          "onError": {
            "_action": "goto", // next, abort, goto
            "_value": "9"
          },
          "Description": "",
          "Execute": {
            "_ExecType": "Yes",
            "Rule": {
                "_Condition":"",
                "_Condvalue":"",
                "_Else":"next",
                "_Elsevalue":"",
            }
          },
          "context": "positive",    // negative, positive
          "impact": "noimpact",     // impact, noimpact
          "_TS": "1",
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
        rec.Description = $scope.status.stepdescription;
        rec.onError['_action'] = $scope.status.step.onError['_action'];
        if (rec.onError['_action'] == 'goto') {
            if ($.trim($scope.status.step.onError._value) == '') {
                alert("A Step # is required when 'On Error' is goto.");
                return null;
            } else {
                rec.onError['_value'] = $scope.status.step.onError['_value'];
            }
        } else {
            delete rec.onError['_value'];
        }
        rec.context = $scope.status.step.context;
        rec.impact = $scope.status.step.impact;

        rec.Execute['_ExecType'] = $scope.status.step.Execute['_ExecType'];

        if (rec.Execute['_ExecType'] == 'If' || rec.Execute['_ExecType'] == 'If Not') {
            rec.Execute['Rule']['_Condition'] = $scope.status.step.Execute['Rule']['_Condition'];
            rec.Execute['Rule']['_Condvalue'] = $scope.status.step.Execute['Rule']['_Condvalue'];
            rec.Execute['Rule']['_Else'] = $scope.status.step.Execute['Rule']['_Else'];

            if (rec.Execute['Rule']['_Else'] == 'goto') {
                if ($.trim($scope.status.step.Execute['Rule']['_Elsevalue']) == '') {
                    alert("A Step # is required when 'On Error' is goto.");
                    return null;
                } else {
                    rec.Execute['Rule']['_Elsevalue'] = $scope.status.step.Execute['Rule']['_Elsevalue'];
                }
            } else {
                delete rec.Execute['Rule']['_Elsevalue'];
            }
        } else {
            delete rec.Execute['Rule'];
        }

        console.log('rec', JSON.stringify(rec, null, 2));
        return rec;
    }

    /* Called when Save Step is clicked. */
    $scope.saveArguments = function () {
        var driver = $.trim($scope.status.drivername) || '',
            keyword = $.trim($scope.status.keyword) || '';
        if (driver == '' || keyword == '' || $.trim($scope.status.stepdescription) == '') {
            alert("We need the Driver, Keyword and Description definitions for a Step specification.");
            return;
        }
        var newstep = populate_step(driver, keyword);
        if (newstep == null) {
            return;
        }
        if ($scope.status.step_edit_mode == 'New') {
            $scope.model.Testcase.Steps.step.push(newstep);
        } else {
            $scope.model.Testcase.Steps.step[$scope.status.stepindex] = newstep;
        }
        $scope.status.step_edit_mode = 'None';
    };

    $scope.testcaseTooltips = [];

    fileFactory.readtooltipfile('testcase')
        .then(
            function(data) {
                // console.log(data);
                $scope.testcaseTooltips = data;
            },
            function(data) {
                alert(data);
            });

    $scope.cancelTestcaseCap = function() {
        $location.path('/testcases');
    }

    $scope.saveTestcaseCap = function () {

        $scope.model.Testcase.Details.Date = moment().format('YYYY-MM-DD');
        $scope.model.Testcase.Details.Time = moment().format('HH:mm');

        if ($.trim($scope.model.Testcase.Details.Name) == '') {
            alert('A Testcase Name is required.\n\nPlease do not specify spaces in it.\n\nThis name will be used as the XML file name.');
            return;
        }
        var hasSpace = _.find($.trim($scope.model.Testcase.Details.Name), function (c) {
            return c == ' ';
        });
        if (hasSpace != undefined) {
            alert("Please do not use spaces in the Name field of the Testcase.\n\n" +
                  "The name field value is used as the name of the XML file to store this test case.\n\n" +
                  "We suggest that you use the underscore character (_) in lieu of the space character.");
            return;
        }
        if ($.trim($scope.model.Testcase.Details.Title) == '') {
            alert('A Testcase Title is required.');
            return;
        }
        if ($.trim($scope.model.Testcase.Details.Engineer) == '') {
            alert("The Testcase Engineer's name is required.");
            return;
        }

        var isDetailDefError = $scope.status.default_onError._action == 'goto',
            isBlank = $.trim($scope.status.default_onError._value) == '',
            isNumeric = _.isNumber( + $scope.status.default_onError._value);

        if (isDetailDefError) {
            if ( isBlank || ( ! isNumeric )) {
                alert("Since the Default Action on Error is to Go to an Error Step, please specify the Target Step");
                return;
            }
        }

        /*
        //---- The engineer need not define any requirement entries.
        if ($scope.model.Testcase.Requirements.Requirement.length == 0) {
            alert("You need to define at least one Requirement before you can save this Testcase.");
            return;
        }
        */

        for (var i = 0; i < $scope.model.Testcase.Requirements.Requirement.length; i++) {
            if ($scope.model.Testcase.Requirements.Requirement[i] == '') {
                $scope.model.Testcase.Requirements.Requirement.splice(i, 1);
            }
        }

        if ($scope.model.Testcase.Steps.step.length == 0) {
            alert("You need to define at least one Step before you can save this Testcase.");
            return;
        }

        _.each(_.range(1, $scope.model.Testcase.Steps.step.length+1), function (i) {
            $scope.model.Testcase.Steps.step[i-1]._TS = i;
        });

        $scope.model.Testcase.Details.Datatype =
            ($scope.model.Testcase.Details.InputDataFile == 'No_Data') ? '' : $scope.status.datatype;

        //- Assign the default error action in the details section.
        var def_error_copy = _.clone($scope.status.default_onError);
        console.log('def_error_copy: ', JSON.stringify($scope.status.default_onError));
        if ($scope.status.default_onError._action != 'goto') {
            delete def_error_copy['_value'];
        }
        $scope.model.Testcase.Details.default_onError = def_error_copy;

        console.log("Testcase\n", JSON.stringify(angular.toJson($scope.model.Testcase), null, 2));

        // var x2js = new X2JS();
        // var token = angular.toJson($scope.model);
        // var xmlDoc = x2js.json2xml_str(JSON.parse(token));
        // alert(xmlDoc);
        // console.log(xmlDoc);

        var filename = $scope.model.Testcase.Details.Name + '.xml'

        fileFactory.checkfileexist(filename, 'testcase')
            .then(
                function(data) {
                    console.log(data);
                    var fileExist = data.response;

                    if (fileExist == 'yes') {
                        var ok = confirm("File " + filename + " already exists.\n\nDo you want to overwrite it?");
                        if (ok) {
                            save(filename);
                        } else {
                            return false;
                        }
                    } else {
                        save(filename);
                    }
                },
                function(data) {
                    alert(data);
                });

    };

    function save(filename) {
        var x2js = new X2JS();
        var token = angular.toJson($scope.model);

        var xmlDoc = x2js.json2xml_str(JSON.parse(token));

        TestcaseFactory.save(filename, xmlDoc)
            .then(
                function(data) {
                    console.log(data);
                    var engineer = $scope.model.Testcase.Details.Engineer;
                    $scope.model = {
                          "Testcase": {
                            "Details": {
                              "Name": "",
                              "Title": "",
                              "Engineer": "",
                              "Date": "",
                              "Time": "",
                              "default_onError": {
                                "_action": "next",
                                "_value": "2"
                              },
                              "InputDataFile": "",
                              "Datatype": "",
                              "Logsdir": "",
                              "Resultsdir": "",
                              "Category": ""
                            },
                            "Requirements": {
                              "Requirement": []
                            },
                            "Steps": {
                              "step": []
                            }
                          }
                        };
                    $scope.status.nodatafile = 0;
                    $scope.model.Testcase.Details.Date = moment().format('YYYY-MM-DD');
                    $scope.model.Testcase.Details.Time = moment().format('HH:mm');
                    $scope.model.Testcase.Details.Engineer = engineer;
                    alert("File saved: " + filename);
                },
                function(data) {
                    alert(data);
                });

        if ($scope.savecreateTestcaseCap) {
            $location.path('testcase/__new__');
        }  else {
            $location.path('/testcases');
        }
    };

    window.S = $scope;

}]);
