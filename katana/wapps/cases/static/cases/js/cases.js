var cases = {

    mappings: {
        newStep: {
            savedContent: false,
            title:  "New Step",
            contents: function () {
                return Promise.resolve(
                    $.ajax({
                        headers: {
                            'X-CSRFToken': katana.$activeTab.find('input[name="csrfmiddlewaretoken"]').attr('value')
                        },
                        type: 'POST',
                        url: 'cases/get_steps_template/',
                        data: {"data": false}
                    }).then(data => { return data })
                );
            },
        },
        newReq: {
            savedContent: false,
            title: "New Requirement",
            contents: function () {
                return Promise.resolve(
                    $.ajax({
                        headers: {
                            'X-CSRFToken': katana.$activeTab.find('input[name="csrfmiddlewaretoken"]').attr('value')
                        },
                        type: 'POST',
                        url: 'cases/get_reqs_template/',
                        data: {"data": false}
                    }).then(data => { return data })
                );
            },
        },
        editDetails: {
            savedContent: false,
            title: "Edit Details",
            contents: function () {
                var contextData = JSON.stringify(katana.$activeTab.find('#detail-block').find('table').data().dataObject);
                return Promise.resolve(
                    $.ajax({
                        headers: {
                            'X-CSRFToken': katana.$activeTab.find('input[name="csrfmiddlewaretoken"]').attr('value')
                        },
                        type: 'POST',
                        url: 'cases/get_details_template/',
                        data: {"data": contextData}
                    }).then(data => { return data })
                );
            },
        }
    },

    header: {
        toggleContents: function() {
            var $elem = $(this);
            if ($elem.attr('collapsed') === 'false') {
                $elem.attr('collapsed', 'true');
                $elem.removeClass('fa-chevron-circle-up');
                $elem.addClass('fa-chevron-circle-down');
                $elem.closest('.cases-header').next().hide()
            } else {
                $elem.attr('collapsed', 'false');
                $elem.removeClass('fa-chevron-circle-down');
                $elem.addClass('fa-chevron-circle-up');
                $elem.closest('.cases-header').next().show()
            }
        },

        editDetails: function() {
            var $elem = $(this);
            var $closedDrawerDiv = $elem.closest('#main-div').find('.cases-side-drawer-closed');
            if ($closedDrawerDiv.is(":hidden")){
                var $switchElem = $closedDrawerDiv.siblings('.cases-side-drawer-open').find('.sidebar').children([0]).children('i');
                cases.drawer.open.switchView($switchElem);
            } else {
                var $openElem = $($closedDrawerDiv.children('div')[1]);
                cases.drawer.openDrawer($openElem);
            }
        },

        newReq: function() {
            var $elem = $(this);
            var $closedDrawerDiv = $elem.closest('#main-div').find('.cases-side-drawer-closed');
            if ($closedDrawerDiv.is(":hidden")){
                var $switchElem = $closedDrawerDiv.siblings('.cases-side-drawer-open').find('.sidebar').children([1]).children('i');
                cases.drawer.open.switchView($switchElem);
            } else {
                var $openElem = $($elem.closest('#main-div').find('.cases-side-drawer-closed').children('div')[2]);
                cases.drawer.openDrawer($openElem);
            }
        },

        newStep: function() {
            var $elem = $(this);
            var $closedDrawerDiv = $elem.closest('#main-div').find('.cases-side-drawer-closed');
            if ($closedDrawerDiv.is(":hidden")){
                var $switchElem = $closedDrawerDiv.siblings('.cases-side-drawer-open').find('.sidebar').children([2]).children('i');
                cases.drawer.open.switchView($switchElem);
            } else {
                var $openElem = $($elem.closest('#main-div').find('.cases-side-drawer-closed').children('div')[3]);
                cases.drawer.openDrawer($openElem);
            }
        },
    },

    drawer: {

        toggleDrawer: function(){
            var $parent = $(this);
            var $elem = $parent.children('i');
            if ($elem.attr('collapsed') === 'true') {
                $elem.closest('.cases-side-drawer-closed').hide();
                $elem.closest('.cases-side-drawer-closed').siblings('.cases-side-drawer-open').show();
            } else {
                $elem.closest('.cases-side-drawer-open').hide();
                $elem.closest('.cases-side-drawer-open').siblings('.cases-side-drawer-closed').show();
            }
        },

        open: {

            switchView: function($elem){
                if ($elem === undefined){
                    $elem = $(this);
                }
                var $sidebar = $elem.closest('.sidebar');
                var $highlighted = $sidebar.find('.cases-icon-bg-color');
                $highlighted.removeClass('cases-icon-bg-color');
                $elem.parent().addClass('cases-icon-bg-color');
                var marker = $elem.attr('ref');
                $elem.closest('.cases-side-drawer-open').find('.cases-header-title').html(cases.mappings[marker].title);
                if (!cases.mappings[marker].savedContent) {
                    var promise = cases.mappings[marker].contents();
                    promise.then(function(data) {
                        cases.mappings[marker].savedContent = data;
                        $elem.closest('.cases-side-drawer-open').find('.content').html(data);
                    });
                } else {
                    $elem.closest('.cases-side-drawer-open').find('.content').html(cases.mappings[marker].savedContent);
                }
            }
        },

        detailsChange: function(){
            var $elem = $(this);
            console.log($elem);
            var $parent = $elem.closest('.cases-drawer-open-body');
            $parent.find('.fa-list-alt').attr('draft', 'true');
            $parent.find('.fa-list-alt').children('i').show();
            $parent.parent().siblings('.cases-side-drawer-closed').find('.fa-list-alt').children('i').show();
        },

        reqsChange: function () {
            var $elem = $(this);
            var $parent = $elem.closest('.cases-drawer-open-body');
            $parent.find('.fa-tags').attr('draft', 'true');
            $parent.find('.fa-tags').children('i').show();
            $parent.parent().siblings('.cases-side-drawer-closed').find('.fa-tags').children('i').show();
        },

        stepsChange: function () {
            var $elem = $(this);
            var $parent = $elem.closest('.cases-drawer-open-body');
            $parent.find('.fa-star').attr('draft', 'true');
            $parent.find('.fa-star').children('i').show();
            $parent.parent().siblings('.cases-side-drawer-closed').find('.fa-star').children('i').show();
        },

        openDrawer: function ($elem) {
            if($elem === undefined){
                $elem = $(this);
            }
            var $toggler = $elem.parent().find('[katana-click="cases.drawer.toggleDrawer"]').children('i');
            var $drawerClosedDiv = $toggler.closest('.cases-side-drawer-closed');
            var $drawerOpenDiv = $toggler.closest('.cases-side-drawer-closed').siblings('.cases-side-drawer-open');
            $drawerClosedDiv.hide();
            $drawerOpenDiv.show();
            var index = $elem.index() - 1;
            var $switchElem = $($drawerOpenDiv.find('.sidebar').children()[index]).children('i');
            cases.drawer.open.switchView($switchElem);
        },

        openFileExplorer: {

            logsdir: function () {
                katana.fileExplorerAPI.openFileExplorer("Select a Path", false,
                    katana.$activeTab.find('input[name="csrfmiddlewaretoken"]').attr('value'), false,
                    function (inputValue){
                        console.log(inputValue);
                    },
                    false)
            },

            resultsdir: function () {
                katana.fileExplorerAPI.openFileExplorer("Select a Path", false,
                    katana.$activeTab.find('input[name="csrfmiddlewaretoken"]').attr('value'), false,
                    function (inputValue){
                        console.log(inputValue);
                    },
                    false)
            },

            inputdatafile: function () {
                katana.fileExplorerAPI.openFileExplorer("Select a Path", false,
                    katana.$activeTab.find('input[name="csrfmiddlewaretoken"]').attr('value'), false,
                    function (inputValue){
                        console.log(inputValue);
                    },
                    false)
            }
        },
    },

    tvArgs: {
        "collapseIcon": "fa fa-minus-circle",
        "expandIcon": "fa fa-plus-circle",
        "levels": 0,
        "onhoverColor": "#b1dfbb",
        "expandOnHover": true
    },

    invert: function(){
        var toolbarButtons = katana.$activeTab.find('.tool-bar').find('button');
        for(var i=0; i<toolbarButtons.length; i++){
            if($(toolbarButtons[i]).is(":hidden")){
                $(toolbarButtons[i]).show();
            } else {
                $(toolbarButtons[i]).hide();
            }
        }
        var divs = katana.$activeTab.find('#body-div').children();
        for(i=0; i<divs.length; i++){
            if($(divs[i]).is(":hidden")){
                $(divs[i]).show();
            } else {
                $(divs[i]).hide();
            }
        }
    },

    landing: {
        init: function(){
            $.ajax({
                type: 'GET',
                url: 'cases/get_list_of_cases/'
            }).done(function(data){
                katana.jsTreeAPI.createJstree(katana.$activeTab.find('#tree-div'), data.data);
                katana.$activeTab.find('#tree-div').on("select_node.jstree", function (e, data){
                    if (data["node"]["icon"] === "jstree-file") {
                        $.ajax({
                            headers: {
                                'X-CSRFToken': katana.$activeTab.find('.csrf-container').html()
                            },
                            type: 'GET',
                            url: 'cases/get_file/',
                            data: {"path": data["node"]["li_attr"]["data-path"]}
                        }).done(function(data){
                            if(data.status){
                                cases.invert();
                                var $detailBlock = katana.$activeTab.find('#detail-block');
                                $detailBlock.html(data.details);
                                $detailBlock.find('table').data({"data-object": data.case_data_json.Testcase.Details});

                                var $reqBlock = katana.$activeTab.find('#req-block');
                                $reqBlock.html(data.requirements);
                                var $reqBlockTable = $reqBlock.find('table');
                                for(var i=0; i<data.case_data_json.Testcase.Requirements.Requirement.length; i++){
                                    $reqBlockTable.find('[req-number=' + (i+1) +']').data({"data-object": data.case_data_json.Testcase.Requirements.Requirement[i]})
                                }

                                var $stepBlock = katana.$activeTab.find('#step-block');
                                $stepBlock.html(data.steps);
                                var $allTrElements = $stepBlock.find('tbody').children('tr');
                                for (var i=0; i<$allTrElements.length; i++){
                                    $($allTrElements[i]).data({"data-object": data.case_data_json.Testcase.Steps.step[i]});
                                }
                            } else {
                                katana.openAlert({"alert_type": "danger",
                                    "heading": "Could not open file",
                                    "text": "Errors: " + data.message,
                                    "show_cancel_btn": false})
                            }
                        });
                    }
                });
            })
        },

        openNewFile: function(){
            $.ajax({
                headers: {
                    'X-CSRFToken': katana.$activeTab.find('.csrf-container').html()
                },
                type: 'GET',
                url: 'cases/get_file/',
                data: {"path": false}
            }).done(function(data){
                if(data.status){
                    cases.invert();
                    var $detailBlock = katana.$activeTab.find('#detail-block');
                    $detailBlock.html(data.details);
                    $detailBlock.find('table').data({"data-object": data.case_data_json.Testcase.Details});

                    var $reqBlock = katana.$activeTab.find('#req-block');
                    $reqBlock.html(data.requirements);
                    var $reqBlockTable = $reqBlock.find('table');
                    for(var i=0; i<data.case_data_json.Testcase.Requirements.Requirement.length; i++){
                        $reqBlockTable.find('[req-number=' + (i+1) +']').data({"data-object": data.case_data_json.Testcase.Requirements.Requirement[i]})
                    }

                    var $stepBlock = katana.$activeTab.find('#step-block');
                    $stepBlock.html(data.steps);
                    var $allTrElements = $stepBlock.find('tbody').children('tr');
                    for (var i=0; i<$allTrElements.length; i++){
                        $($allTrElements[i]).data({"data-object": data.case_data_json.Testcase.Steps.step[i]});
                    }
                } else {
                    katana.openAlert({"alert_type": "danger",
                        "heading": "Could not open file",
                        "text": "Errors: " + data.message,
                        "show_cancel_btn": false})
                }
            });
        },
    },

    caseViewer:  {
        close: function () {
            cases.invert();
        }
    },

    reqSection: {
        deleteReq: function () {
            var $elem = $(this);
            var $tdParent = $elem.closest('td');
            var reqNumber = $tdParent.siblings('th').html();
            var $toBeDeleted = $elem.closest('tr');
            var $topLevel = $elem.closest('.cases-intentional-space-x');
            katana.openAlert({
                "alert_type": "danger",
                "heading": "Delete Requirement " + reqNumber + "?",
                "text": "Are you sure you want to delete the requirement? This cannot be undone."
            }, function(){
                $toBeDeleted.remove();
                var $tbody = $topLevel.find('tbody');
                var tempList = [];
                var $leftTrs = $($tbody[0]).children('tr');
                for (var i=0; i<$leftTrs.length; i++){
                    $($leftTrs[i]).children('th').html(i + 1);
                    tempList.push($($leftTrs[i]).detach());
                }
                var $rightTrs = $($tbody[1]).children('tr');
                for (i=0; i<$rightTrs.length; i++){
                    $($rightTrs[i]).children('th').html($leftTrs.length + i + 1);
                    tempList.push($($rightTrs[i]).detach());
                }
                $($tbody[0]).html();
                $($tbody[1]).html();
                for (i=0; i<tempList.length/2; i++) {
                    $($tbody[0]).append(tempList[i]);
                }
                for (i=Math.ceil(tempList.length/2); i<tempList.length; i++) {
                    $($tbody[1]).append(tempList[i]);
                }
            });
        },

        editReq: function () {

        },
    },

    stepSection: {
        selectStep: function () {
            var $elem = $(this);
            var $allTrElems = $elem.parent().children('tr');
            if ($elem.attr('marked') === 'true') {
                $elem.attr('marked', 'false');
                $elem.css('background-color', 'white');
            } else {
                var multiselect = katana.$activeTab.find('.cases-step-toolbar').find('.fa-th-list').attr('multiselect');
                if (multiselect === 'off'){
                    for (var i=0; i<$allTrElems.length; i++){
                        $($allTrElems[i]).attr('marked', 'false');
                        $($allTrElems[i]).css('background-color', 'white');
                    }
                }
                $elem.attr('marked', 'true');
                $elem.css('background-color', 'khaki');
            }
        },

        toolbar: {
            multiselect: function() {
                var $elem = $(this);
                var $iconElem = $elem.children('i');
                if ($iconElem.attr('multiselect') === 'on'){
                    $iconElem.attr('multiselect', 'off');
                    $iconElem.removeClass('badged');
                    $iconElem.children('i').hide();
                    var $allTrElems = katana.$activeTab.find('#step-block').find('tbody').children('tr');
                    for (var i=0; i<$allTrElems.length; i++){
                        $($allTrElems[i]).attr('marked', 'false');
                        $($allTrElems[i]).css('background-color', 'white');
                    }
                } else {
                    $iconElem.attr('multiselect', 'on');
                    $iconElem.addClass('badged');
                    $iconElem.children('i').show()
                }
            },

            deleteStep: function () {
                var $tbodyElem = katana.$activeTab.find('#step-block').find('tbody');
                var $allTrElems = $tbodyElem.children('tr[marked="true"]');
                if ($allTrElems.length === 0) {
                    katana.openAlert({"alert_type": "danger",
                        "heading": "No step selected for deletion",
                        "text": "Please select at least one step to delete",
                        "show_cancel_btn": "false"})
                } else {
                    var stepNumbers = "";
                    for (var i=0; i<$allTrElems.length; i++){
                        stepNumbers += ($($allTrElems[i]).index() + 1).toString() + ", "
                    }
                    stepNumbers = stepNumbers.slice(0, -2);
                    katana.openAlert({"alert_type": "warning",
                        "heading": "This would delete Steps " + stepNumbers,
                        "text": "Are you sure you want to delete these steps?"},
                        function(){
                            for (i=0; i<$allTrElems.length; i++){
                                $($allTrElems[i]).remove();
                            }
                            $allTrElems = $tbodyElem.children('tr');
                            for (i=0; i<$allTrElems.length; i++){
                                $($($allTrElems[i]).children('td')[0]).html(i+1);
                            }
                        })
                }
            },

            insertStep: function () {
                var $tbodyElem = katana.$activeTab.find('#step-block').find('tbody');
                var $allTrElems = $tbodyElem.children('tr[marked="true"]');
                if ($allTrElems.length === 0) {
                    var insertAtIndex = $tbodyElem.children('tr').length;
                } else if ($allTrElems.length > 1) {
                    katana.openAlert({
                        "alert_type": "danger",
                        "heading": "Multiple Steps Selected",
                        "text": "Only one step can be inserted at a time. Please select only one " +
                        "step above which you want to insert another step.",
                        "show_cancel_btn": false
                    })
                    return;
                } else {
                    insertAtIndex = $($allTrElems[0]).index();
                    //insert tr
                }
                console.log(insertAtIndex);
            },

            editStep: function () {
                var $tbodyElem = katana.$activeTab.find('#step-block').find('tbody');
                var $allTrElems = $tbodyElem.children('tr[marked="true"]');
                if ($allTrElems.length === 0) {
                    katana.openAlert({
                        "alert_type": "danger",
                        "heading": "No Step Selected",
                        "text": "Please select a step to edit.",
                        "show_cancel_btn": false
                    });
                    return;
                } else if ($allTrElems.length > 1) {
                    katana.openAlert({
                        "alert_type": "danger",
                        "heading": "Multiple Steps Selected",
                        "text": "Only one step can be edited at a time. Please select only one " +
                        "step to edit.",
                        "show_cancel_btn": false
                    });
                    return;
                } else {
                    var editIndex = $($allTrElems[0]).index();
                }
                console.log(editIndex);
            },
        }
    },
};