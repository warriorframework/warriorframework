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
app.controller('sequentialCtrl', ['$scope', '$http', '$route', 'sequentialFactory', 'executionFactory', 'runFactory', 'descriptionFactory', 'fileFactory',
  function($scope, $http, $route, sequentialFactory, executionFactory, runFactory, descriptionFactory, fileFactory) {
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
    $scope.files = [];
    $scope.chosenFiles = [];
    $scope.executionType = '';
    $scope.description = "Description not available";
    $scope.showPerformanceType = false;
    $scope.showParallelType = false;
    $scope.moduleType = 'Sequential';
    $scope.sequentialTooltip = [];
    $scope.basepathdir = "";
    $scope.temp_nodes = "";
    $scope.node_options = [];
    $scope.autoDefect = "";
    $scope.counter = 0;
    $scope.warning = "";
    if (navigator.appVersion.indexOf("Win") != -1) {
      $scope.warning = "WARNING! If there is an open command prompt window that executed a testcase, you'll have to close that window so that the next execution can proceed. Do not close the command prompt which is running the katana server!";
    }
    $scope.getAutoDefectvalue = function(autodefectvalue) {
      $scope.autoDefect = autodefectvalue;
    };
    fileFactory.readtooltipfile('sequential').then(function(data) {
      console.log(data);
      $scope.sequentialTooltip = data;
    }, function(data) {
      alert(data);
    });
    $scope.getData = function() {
      alert($scope.basepathdir)
    };
    $scope.moduleSelection = function(moduleType) {
      console.log(moduleType);
      readConfig();
      var parameter = "desctype=" + $scope.moduleType;
      descriptionFactory.fetchDescription(parameter).then(function(data) {
        console.log(data);
        $scope.description = data[0].description;
      });
      if (moduleType == 'Run selected files in sequence') {
        $scope.reset();
        $scope.showPerformanceType = false;
        $scope.showParallelType = false;
        $scope.executionType = "";
      } else if (moduleType == 'Run Keywords in Parallel') {
        $scope.reset();
        console.log("Inside para");
        $scope.showPerformanceType = false;
        $scope.showParallelType = true;
        $scope.executionType = "Sequential";
      } else {
        $scope.reset();
        console.log("Inside perf");
        $scope.showPerformanceType = true;
        $scope.showParallelType = false;
        $scope.executionType = "Parallel";
      }
    };
    $scope.selectedFiles = function(file) {
      if (file.done) {
        $scope.chosenFiles.push(file.filename);
      } else {
        for (var i = 0; i < $scope.chosenFiles.length; i++) {
          if (file.filename == $scope.chosenFiles[i]) {
            $scope.chosenFiles.splice(i, 1);
            break;
          }
        }
      }
    };
    $scope.reset = function() {
      $scope.files = [];
      $scope.chosenFiles = [];
      $scope.addDirectory = "";
      $scope.sharedDate = "";
      $scope.selectAll = false;
      $scope.sharedTime = "";
      $scope.iteration = "";
      $scope.schedule = false;
      $scope.showIteration = false;
      document.getElementById("execResultLbl").innerHTML = "";
      document.getElementById('resultLbl').innerHTML = "";
    };
    $scope.fetchFiles = function() {
      console.log("Fetch Files " + $scope.addDirectory);
      var directoryPath = "dirname=" + $scope.addDirectory;
      if (typeof $scope.addDirectory != "undefined" && $scope.addDirectory.trim().length != 0) {
        executionFactory.fetchFiles(directoryPath).then(function(data) {
          console.log("seq ctrl add files " + JSON.stringify(data));
          if (data.length == 0) {
            alert("Specified directory contains no XML files.");
          } else {
            for (var i = 0; i < data.length; i++) {
              $scope.files.push(data[i]);
            }
          }
        });
      }
    };
    $scope.executeFiles = function() {
      console.log("Iter=" + $scope.iteration + "Time= " + $scope.sharedTime + " Date= " + $scope.sharedDate);
      document.getElementById("execResultLbl").innerHTML = "";
      document.getElementById("resultLbl").innerHTML = "";
      if ($scope.chosenFiles.length == 0) {
        document.getElementById('resultLbl').style.color = "Red";
        document.getElementById("resultLbl").innerHTML = "Please select atleast one file... ";
        document.getElementById("execResultLbl").innerHTML = "";
      } else if (($scope.executionType == "Run Multiple Times" || $scope.executionType == "Run Until Failure" || $scope.executionType == "Run Until Pass") && ($scope.iteration === undefined || $scope.iteration == "" || $scope.iteration == null)) {
        document.getElementById('resultLbl').style.color = "Red";
        document.getElementById("resultLbl").innerHTML = "Please enter value for Iteration..."
        document.getElementById("execResultLbl").innerHTML = "";
      } else if ($scope.schedule && (typeof $scope.sharedDate == "undefined" || typeof $scope.sharedTime == "undefined" || $scope.sharedTime == "" || $scope.sharedDate == "")) {
        document.getElementById('resultLbl').style.color = "Red";
        document.getElementById("resultLbl").innerHTML = " Please select date and time for Schedule Run...";
        document.getElementById("execResultLbl").innerHTML = "";
      } else {
        var filenames = $scope.chosenFiles[0];
        var autodefect = '';
        var schedulerun = 'n';
        var datevalue = "";
        var runtype = "";
        var execType = "";
        var iterationval = "";
        document.getElementById('resultLbl').style.color = "";
        document.getElementById('execResultLbl').style.color = "";
        if (typeof $scope.moduleType != "undefined") {
          if ($scope.moduleType == 'Sequential') execType == "";
          else execType = $scope.moduleType;
        }
        /*if($scope.executionType=="Performance"){

        	perfvalue =$scope.optionRadio;

        }*/
        if ($scope.executionType == "Run Multiple Times") {
          runtype = "RMT";
          execType = "Performance"
        } else if ($scope.executionType == "Run Until Failure") {
          runtype = "RUF";
          execType = "Performance"
        } else if ($scope.executionType == "Run Until Pass") {
          runtype = "RUP";
          execType = "Performance"
        } else {
          runtype = $scope.executionType;
        }
        if ($scope.autoDefect !== "" || $scope.autoDefect !== "None") {
          autodefect = $scope.autoDefect
        }
        if ($scope.schedule) {
          schedulerun = 'y';
          datevalue = $scope.sharedDate + "-" + $scope.sharedTime;
        }
        if (typeof $scope.iteration != "undefined") {
          iterationval = $scope.iteration;
        }
        for (var i = 1; i < $scope.chosenFiles.length; i++) filenames += "," + $scope.chosenFiles[i];
        var runParameters = "filenames=" + filenames + '&exectype=' + execType + '&autodefect=' + autodefect + "&schedulerun=" + schedulerun + "&datevalue=" + datevalue + "&iterationval=" + iterationval + "&runtype=" + runtype;
        console.log(runParameters);
        runFactory.executeFiles(runParameters).then(function(data) {
          document.getElementById("resultLbl").innerHTML = "Command to Run: " + data[0].command_to_run;
          document.getElementById("execResultLbl").innerHTML = "Execution Result: " + data[0].Execution_Result;
        });
      }
    };
    $scope.options = []
    $scope.execSelection = function(executionType) {
      console.log(executionType);
      if (executionType == "Run Multiple Times" || executionType == "Run Until Failure" || executionType == "Run Until Pass") {
        //$scope.options=[{text:'Run Multiple Times',value:'RMT'},{text:'Run Until Fail',value:'RUF'}];
        $scope.showIteration = true;
      } else {
        //$scope.options=[];
        $scope.showIteration = false;
      }
    };
    $scope.selectAllFiles = function() {
      console.log("Select All");
      if ($scope.selectAll) {
        for (var i = 0; i < $scope.files.length; i++) {
          $scope.files[i].done = true;
          $scope.chosenFiles.push($scope.files[i].filename);
        }
      } else {
        for (var i = 0; i < $scope.files.length; i++) $scope.files[i].done = false;
        $scope.chosenFiles = [];
      }
    }
    $scope.loadDescription = function() {
      var parameter = "desctype=" + "sequential";
      descriptionFactory.fetchDescription(parameter).then(function(data) {
        console.log(JSON.stringify(data));
        $scope.description = data[0].description;
      })
    };
    $scope.scheduleOperation = function() {
      $scope.sharedDate = "";
      $scope.sharedTime = "";
    }

    function readConfig() {
      $http.get('/readconfig').success(function(data, status, headers, config) {
        // $scope.cfg.pythonsrcdir = data.pythonsrcdir;
        // $scope.cfg.basedir = data.basedir;
        // $scope.cfg.xmldir = data.xmldir;
        // $scope.cfg.testsuitedir = data.testsuitedir;
        // $scope.cfg.projdir = data.projdir;
        $scope.addDirectory = data.xmldir;
        console.log("Seq Ctrl " + $scope.addDirectory);
      }).error(function(data, status, headers, config) {
        alert("Error fetching config data.", status, headers);
      });
    }

    function get_jira_projects() {
      $http.get('/get_jira_projects').success(function(data, status, headers, config) {
        $scope.temp_nodes = data;
      }).error(function(data, status, headers, config) {
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
  }
]);
var printFormater = {
  table: '',
  bar: '',
  levels: ['KeywordRecord', 'TestcaseRecord', 'TestsuiteRecord', 'ProjectRecord'],
  statusFitlers: ['FAIL', 'ERROR', 'SKIPPED', 'PASS'],
  init: function(popup) {
    printFormater.table = popup.find('table');
    printFormater.barRelocate();
    printFormater.initAccordian();
    printFormater.sortingAPI.init();
    printFormater.justifyOrder();
    printFormater.placeData();
  },
  barRelocate: function() {
    printFormater.bar = printFormater.table.find('tr:first-child').insertBefore(printFormater.table).wrap('<div class="nav"></div>');
  },
  placeData: function() {
    setTimeout(function() {
      printFormater.table.find('tr[name] td:not([rowspan])').each(function() {
        var $elem = $(this);
        var useData = $elem.parent().next('tr:not([name])').find('td:nth-child( ' + ($elem.prevAll('tr[name] td:not([rowspan])').length + 1) + ' )').text();
        $elem.append('<span class="useData">' + useData + '</span>');
      });
    }, 60);
  },
  initAccordian: function() {
    printFormater.table.find('tr[name="TestcaseRecord"]').on('click', function() {
      printFormater.openAccordian.call($(this));
    });
    $(window).on('keydown', function(e) {
      if (e.keyCode == 40 && printFormater.table.find('.active').length) {
        e.preventDefault();
        printFormater.openAccordian.call(printFormater.table.find('.active').nextAll('tr[name="TestcaseRecord"]:first'));
      } else if (e.keyCode == 38 && printFormater.table.find('.active').length) {
        e.preventDefault();
        printFormater.openAccordian.call(printFormater.table.find('.active').prevAll('tr[name="TestcaseRecord"]:first'));
      }
    });
  },
  justifyOrder: function() {
    setTimeout(function() {
      printFormater.table.find('tr[name]').each(function() {
        var $elem = $(this);
        var container = $('<div class="hoverConainer"></div>');
        var level = $elem.attr('name');
        for (var i = printFormater.levels.indexOf(level) + 1; printFormater.levels.length > i; i++) container.prepend($elem.prevAll('tr[name="' + printFormater.levels[i] + '"]:first').clone());
        $elem.data(container);
      });
    }, 30);
  },
  openAccordian: function() {
    var $elem = this;
    var isActive = $elem.hasClass('active');
    $elem.parent().find('.active').removeClass('active');
    if (!isActive && !printFormater.table.hasClass('filtering')) $elem.addClass('active');
  },
  sortingAPI: {
    init: function() {
      printFormater.bar.find('th').on('click', function() {
        var $elem = $(this);
        var name = $elem.text();
        $elem.toggleClass('up');
        if (name == 'Status') printFormater.sortingAPI.filterBar(printFormater.statusFitlers, name);
      });
    },
    filterBar: function(filterList, filterScope) {
      if (printFormater.bar.siblings('.filterBar').length != 0) {
        printFormater.table.removeClass('filtering');
        printFormater.sortingAPI.filter();
        setTimeout(function() {
          printFormater.bar.siblings('.filterBar').remove();
        }, 300);
        printFormater.table.find('tr[name]').off('mouseover mouseleave');
      } else {
        printFormater.table.addClass('filtering');
        var bar = $('<div class="filterBar" filterScope="' + ($('.nav tr th:contains("' + filterScope + '")').prevAll().length + 1) + '"></div>');
        for (var i = 0; filterList.length > i; i++) {
          var filter = $('<span>' + filterList[i] + '<input type="checkbox" value="' + filterList[i] + '"></span>').appendTo(bar);
          filter.find('input').on('change', function() {
            printFormater.sortingAPI.filter(bar);
          });
        }
        bar.appendTo('.nav');
        printFormater.table.find('tr[name]').on('mouseover', 'td[rowspan]:nth-child(1)', function() {
          var $elem = $(this).closest('tr');
          $elem.addClass('hover').data().appendTo($elem);
        }).on('mouseleave', 'td[rowspan]:nth-child(1)', function() {
          var $elem = $(this).closest('tr');
          $elem.removeClass('hover').find('.hoverConainer').remove();
        });
      }
    },
    filter: function(bar) {
      if (bar) {
        var activeFilters = bar.find('input:checked').map(function() {
          return $(this).val();
        }).get();
        var filterScope = bar.attr('filterScope');
        printFormater.table.find('td[rowspan]:nth-child(' + filterScope + ')').each(function() {
          var $elem = $(this);
          if (activeFilters.indexOf($elem.text()) != -1 || activeFilters.length == 0) printFormater.sortingAPI.filterAdd($elem.closest('tr'));
          else printFormater.sortingAPI.filterRemove($elem.closest('tr'));
        });
      } else printFormater.table.find('tr').each(function() {
        printFormater.sortingAPI.filterAdd($(this));
      });
    },
    filterAdd: function(row) {
      row.removeClass('hidden');
    },
    filterRemove: function(row) {
      row.addClass('hidden');
    },
  },
};
var popupController = {
  body: $(document.body),
  template: $('<div class="popup"><div class="navbar"><div class="title"></div><div class="min"></div><div class="close"></div></div><div class="page-content"></div></div>'),
  tabTemplate: $('<div class="tab-bar"><div class="tab"></div></div>'),
  open: function(content, title) {
    var popup = this.template.clone().appendTo(popupController.body);
    content && popup.find('.page-content').append(content);
    popupController.initEvents(popup);
    popupController.createTab(popup);
    title && popupController.setTitle(popup, title);
    return popup;
  },
  setTitle: function(popup, title) {
    popup.find('.title').text(title);
    popup.data('tabIndex').text(title);
  },
  createTab: function(popup) {
    if (!popupController.tabBar) {
      popupController.tabBar = popupController.tabTemplate.clone().appendTo(popupController.body.find('nav'));
      popupController.tabBar.find('.tab').remove();
    }
    var tab = popupController.tabTemplate.find('.tab').first().clone().appendTo(popupController.tabBar);
    popup.data('tabIndex', tab);
    tab.on('click', function() {
      popupController.openWindow(popup);
    });
  },
  openWindow: function(popup) {
    var activePopup = popupController.body.find('.popup.active');
    if (activePopup.get(0) != popup.get(0)) {
      activePopup.removeClass('active');
      popup.removeClass('removeing hidden').addClass('active');
    }
  },
  close: function(popup) {
    popup.data('tabIndex').remove();
    popup.addClass('removeing');
    setTimeout(function() {
      popup.remove();
    }, 300);
  },
  updateActiveWindow: function(popup) {
    var activePopup = popupController.body.find('.popup.active');
    if (activePopup.get(0) != popup.get(0)) {
      activePopup.removeClass('active');
      popup.addClass('active');
    }
  },
  min: function(popup) {
    popup.addClass('removeing');
    setTimeout(function() {
      popup.addClass('hidden').removeClass('active');
    }, 300);
  },
  initEvents: function(popup) {
    var pressed = false;
    var xoffset = 0;
    var yoffset = 0;
    var x, y;
    var startPointx = 0;
    var startPointy = 0;
    var $elem;
    popup.find('.navbar .title').on('mousedown', function(e) {
      e.stopPropagation();
      e.preventDefault();
      popupController.updateActiveWindow(popup);
      $elem = $(this).closest('.popup');
      pressed = true;
      xoffset = e.pageX;
      yoffset = e.pageY;
      $elem.removeClass('leftJustify').removeClass('rightJustify');
      popupController.body.addClass('no-select');
      popupController.body.on('mousemove', function(j) {
        if (pressed) {
          x = (j.pageX - xoffset + startPointx);
          y = (j.pageY - yoffset + startPointy);
          $elem.css('transform', 'translate3d( ' + x + 'px, ' + y + 'px,0 )');
        }
      });
      popupController.body.one('mouseup', function() {
        popupController.body.off('mousemove');
        startPointx = x;
        startPointy = y;
        pressed = false;
        popupController.body.removeClass('no-select');
        if ($elem.offset().left < 0) {
          $elem.removeClass('rightJustify').addClass('leftJustify');
          startPointx = 0;
          startPointy = 0;
        } else if ($elem.offset().left > $(this).width() - $elem.width()) {
          $elem.removeClass('leftJustify').addClass('rightJustify');
          startPoinx = $(this).width() - $elem.width();
          startPointy = 0;
        }
      });
    });
    popup.find('.close').one('click', function(e) {
      popupController.close(popup);
      e.stopPropagation();
      e.preventDefault();
    });
    popup.on('click', function() {
      popupController.updateActiveWindow(popup);
    });
    popup.find('.min').on('click', function(e) {
      popupController.min(popup);
      e.stopPropagation();
      e.preventDefault();
    });
  }
};
var executeApi = {
  htmlpopupContent: '',
  tally: 0,
  currentTimeout: '',
  init: function(pathjson, callback, p, maxi) {
    executeApi.paths = pathjson ? pathjson : executeApi.paths;
    executeApi.count = pathjson ? executeApi.getCount(pathjson) : executeApi.count;
    htmlpopupContent = popupController.open().find('.page-content');
    htmlpopupContent.addClass('htmlResults loading');
    executeApi.getHtml(callback, p, maxi);
  },
  getCount(paths) {
    var count = paths.indexOf(',') != -1 ? paths.match(/,/gi).length : 0;
    return count;
  },
  getHtml: function(callback, p, maxi) {
    $.ajax({
      url: location.origin + '/get_html_results',
      dataType: 'text'
    }).done(function(content) {
      if (content != '') {
        var $html = $('<div/>').append(content);
        if ($html.find('.complete').length == 0) executeApi.currentTimeout = window.setTimeout(function() {
          executeApi.getHtml(callback, p, maxi);
        }, 1000);
        else {
          if (executeApi.count > executeApi.tally) {
            executeApi.tally++;
            executeApi.init();
          } else executeApi.tally = 0;
          htmlpopupContent.removeClass('loading');
          window.clearTimeout(executeApi.currentTimeout);
          p++;
          callback(p, maxi);
        }
        executeApi.setHtml($html, htmlpopupContent);
      } else setTimeout(function() {
        executeApi.getHtml(callback, p, maxi);
      }, 400);
    });
  },
  setHtml: function($html, popup) {
    popup.empty();
    var title = executeApi.paths.split(',')[executeApi.tally];
    popupController.setTitle(popup.closest('.popup'), (title ? title.substring(title.lastIndexOf("/") + 1).split('&')[0] : ''));
    $html.find('table').appendTo(popup);
    setTimeout(function() {
      printFormater.init(popup);
    }, 100);
  }
};