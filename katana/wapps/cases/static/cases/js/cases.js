var cases = {

    utils: {

        updateData: function (data, key, value) {
            if (key.indexOf('[') > -1) {
                var temp = key.split('[');
                new_key = false;
                var index = false;
                if (temp[0].indexOf('(') > -1){
                    var temp2 = temp[0].split('(');
                    var new_key = temp2[0];
                    index = parseInt(temp2[1].slice(0, -1));
                }
                var remaining = "";
                for (var i=1; i<temp.length; i++){
                    remaining += temp[i] + "[";
                    remaining += temp[i] + "[";
                }
                if (remaining.endsWith("[")){
                    remaining = remaining.slice(0, -1);
                }
                if (new_key) {
                    data[new_key][index] = cases.utils.updateData(data[new_key][index], remaining.slice(0, -1), value)
                } else {
                    data[temp[0]] = cases.utils.updateData(data[temp[0]], remaining.slice(0, -1), value)
                }
            } else {
                data[key] = value;
            }
            return data
        },

        getRelativeFilepath: function (basePath, path) {
            if (basePath.indexOf('\\') > -1) {
                basePath = basePath.replace('\\', '/');
            }
            if (path.indexOf('\\') > -1) {
                path = path.replace('\\', '/');
            }
            var basePathSeries = basePath.split('/');
            var pathSeries = path.split('/');
            var hold = 0;
            for (var i=0; i<basePathSeries.length && i < pathSeries.length; i++) {
                if (basePathSeries[i] !== pathSeries[i]){
                    hold = i;
                    break;
                }
            }
            var output = "";
            for (i=(basePathSeries.length-1); i > hold; i--) {
                output += "../"
            }
            if (output !== "") {
                output = output.slice(0, -1);
            }
            for (i=hold; i<pathSeries.length; i++) {
                output += "/" + pathSeries[i]
            }
            if (output.startsWith("/")) {
                output = output.slice(1, output.length);
            }
            return output
        },

        getAbsoluteFilepath: function (basePath, relativePath) {
            if (basePath.indexOf('\\') > -1) {
                basePath = basePath.replace('\\', '/');
            }
            if (relativePath.indexOf('\\') > -1) {
                relativePath = relativePath.replace('\\', '/');
            }
            var basePathSeries = basePath.split('/');
            var relativePathSeries = relativePath.split('/');
            var i = 0;
            var hold = 0;
            while (relativePathSeries[i] === ".."){
                hold += 1;
                i += 1;
            }
            var output = "";
            for (i=0; i<(basePathSeries.length - hold - 1); i++) {
                output += basePathSeries[i] + "/"
            }
            for (i=hold; i<relativePathSeries.length; i++) {
                output += relativePathSeries[i] + "/"
            }
            output = output.slice(0, -1);
            return output
        },
    },

    mappings: {
        newStep: {
            savedContent: false,
            title:  "New Step",
            contents: function () {
                if (katana.$activeTab.find('#step-block').find('[being-edited="true"]').length > 0){
                    var contextData = JSON.stringify(katana.$activeTab.find('#step-block').find('[being-edited="true"]').data().dataObject);
                    var ts = false;
                } else {
                    contextData = false;
                    ts = katana.$activeTab.find('#step-block').find('tr').length;
                }
                return Promise.resolve(
                    $.ajax({
                        headers: {
                            'X-CSRFToken': katana.$activeTab.find('input[name="csrfmiddlewaretoken"]').attr('value')
                        },
                        type: 'POST',
                        url: 'cases/get_steps_template/',
                        data: {"data": contextData, "ts": ts}
                    }).then(data => { return data })
                );
            },
        },
        newReq: {
            savedContent: false,
            title: "New Requirement",
            contents: function () {
                if (katana.$activeTab.find('#req-block').find('[being-edited="true"]').length > 0){
                    var contextData = JSON.stringify(katana.$activeTab.find('#req-block').find('[being-edited="true"]').data().dataObject);
                } else {
                    contextData = JSON.stringify("");
                }
                return Promise.resolve(
                    $.ajax({
                        headers: {
                            'X-CSRFToken': katana.$activeTab.find('input[name="csrfmiddlewaretoken"]').attr('value')
                        },
                        type: 'POST',
                        url: 'cases/get_reqs_template/',
                        data: {"data": contextData}
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
            var data = $elem.parent().parent().siblings('#detail-block').find('table').data();
            var $closedDrawerDiv = $elem.closest('#main-div').find('.cases-side-drawer-closed');
            var $switchElem = $($closedDrawerDiv.siblings('.cases-side-drawer-open').find('.sidebar').children()[0]).children('i');
            $switchElem.data(data);
            if ($closedDrawerDiv.is(":hidden")){
                cases.drawer.open.switchView.details($switchElem);
            } else {
                var $openElem = $($closedDrawerDiv.children('div')[1]);
                cases.drawer.openDrawer.details($openElem);
            }
        },

        newReq: function() {
            var $elem = $(this);
            var data = {dataObject: ""};
            var $closedDrawerDiv = $elem.closest('#main-div').find('.cases-side-drawer-closed');
            var $switchElem = $closedDrawerDiv.siblings('.cases-side-drawer-open').find('.sidebar').children([1]).children('i');
            $switchElem.data(data);
            if ($closedDrawerDiv.is(":hidden")){
                cases.drawer.open.switchView.requirements($switchElem);
            } else {
                var $openElem = $($elem.closest('#main-div').find('.cases-side-drawer-closed').children('div')[2]);
                cases.drawer.openDrawer.requirements($openElem);
            }
        },

        newStep: function() {
            var $elem = $(this);
            var $closedDrawerDiv = $elem.closest('#main-div').find('.cases-side-drawer-closed');
            if ($closedDrawerDiv.is(":hidden")){
                var $switchElem = $closedDrawerDiv.siblings('.cases-side-drawer-open').find('.sidebar').children([2]).children('i');
                cases.drawer.open.switchView.steps($switchElem);
            } else {
                var $openElem = $($elem.closest('#main-div').find('.cases-side-drawer-closed').children('div')[3]);
                cases.drawer.openDrawer.steps($openElem);
            }
        },
    },

    drawer: {

        openDatafile: function () {
            var $elem = $(this);
            var $inputElem = $elem.parent().prev().children('input');
            var tcPath = katana.$activeTab.find('#main-div').attr("current-file");
            var idfPath = cases.utils.getAbsoluteFilepath(tcPath, $inputElem.val());
            $.ajax({
                headers: {
                    'X-CSRFToken': katana.$activeTab.find('input[name="csrfmiddlewaretoken"]').attr('value')
                },
                type: 'POST',
                url: 'check_if_file_exists/',
                data: {"path": idfPath}
            }).done(function(data){
                var pd = { type: 'POST',
                    headers: {'X-CSRFToken': katana.$activeTab.find('input[name="csrfmiddlewaretoken"]').attr('value')},
                    data:  {"path": idfPath}};
                if (data.exists) {
                    katana.templateAPI.load('/katana/wdf/index/', '/static/wdf_edit/js/main.js,',
                        null, 'WDF Editor', null, pd)
                } else {
                    katana.openAlert({
                        "alert_type": "danger",
                        "heading": "Problem Opening " + $inputElem.val(),
                        "text": "It seems like the file may not be available for viewing.",
                        "show_cancel_btn": false
                    });
                }
            });
        },

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

            switchView: {

                details: function($elem) {
                    if ($elem === undefined){
                        $elem = $(this);
                    }
                    if ($elem.attr('draft') !== 'true'){
                        $elem.data({"data-object": $elem.closest('#main-div').find('#detail-block').find('table').data().dataObject})
                    }
                    var $sidebar = $elem.closest('.sidebar');
                    var $highlighted = $sidebar.find('.cases-icon-bg-color');
                    if ($highlighted.children('i').attr('ref') === "newReq") {
                        cases.mappings.newReq.savedContent = $elem.closest('.cases-side-drawer-open').find('.content').html();
                    } else if ($highlighted.children('i').attr('ref') === "newStep"){
                        cases.mappings.newStep.savedContent = $elem.closest('.cases-side-drawer-open').find('.content').html();
                    }
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
                },

                requirements: function($elem) {
                    if ($elem === undefined){
                        $elem = $(this);
                    }
                    if ($elem.attr('draft') !== 'true'){
                        if($elem.closest('#main-div').find('#req-block').find('[being-edited="true"]').length > 0){
                            $elem.data({"data-object": $elem.closest('#main-div').find('#req-block').find('[being-edited="true"]').data().dataObject});
                        }
                    }
                    var $sidebar = $elem.closest('.sidebar');
                    var $highlighted = $sidebar.find('.cases-icon-bg-color');
                    $highlighted.removeClass('cases-icon-bg-color');
                    if ($highlighted.children('i').attr('ref') === "editDetails") {
                        cases.mappings.editDetails.savedContent = $elem.closest('.cases-side-drawer-open').find('.content').html();
                    } else if ($highlighted.children('i').attr('ref') === "newStep"){
                        cases.mappings.newStep.savedContent = $elem.closest('.cases-side-drawer-open').find('.content').html();
                    }
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
                },

                steps: function($elem) {
                    if ($elem === undefined){
                        $elem = $(this);
                    }
                    if ($elem.attr('draft') !== 'true'){
                        if($elem.closest('#main-div').find('#step-block').find('[being-edited="true"]').length > 0){
                            $elem.data({"data-object": $elem.closest('#main-div').find('#step-block').find('[being-edited="true"]').data().dataObject});
                        }
                    }
                    var $sidebar = $elem.closest('.sidebar');
                    var $highlighted = $sidebar.find('.cases-icon-bg-color');
                    $highlighted.removeClass('cases-icon-bg-color');
                    if ($highlighted.children('i').attr('ref') === "newReq") {
                        cases.mappings.newReq.savedContent = $elem.closest('.cases-side-drawer-open').find('.content').html();
                    } else if ($highlighted.children('i').attr('ref') === "editDetails"){
                        cases.mappings.editDetails.savedContent = $elem.closest('.cases-side-drawer-open').find('.content').html();
                    }
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
                },

            },

            saveContents: function () {
                var $elem = $(this);
                var $openDrawer = $elem.closest('.cases-side-drawer-open');
                var $switchElem = $openDrawer.find('.cases-drawer-open-body').find('.sidebar').find('.cases-icon-bg-color').children('i');
                if ($switchElem) {
                    var reference = $switchElem.attr('ref');
                    if (reference === "editDetails") {
                        cases.drawer.open._saveContents.details($switchElem.data(), $switchElem);
                    } else if (reference === "newReq") {
                        cases.drawer.open._saveContents.requirements($switchElem.data(), $switchElem);
                    } else if (reference === "newStep") {
                        cases.drawer.open._saveContents.steps($switchElem.data(), $switchElem);
                    }
                }
            },

            _saveContents: {

                details: function (data, $source) {
                    $.ajax({
                        headers: {
                            'X-CSRFToken': katana.$activeTab.find('input[name="csrfmiddlewaretoken"]').attr('value')
                        },
                        url: 'cases/get_details_display_template/',
                        type: 'POST',
                        data: {"data": JSON.stringify(data.dataObject)}
                    }).done(function(html_data){
                        $source.closest('#main-div').find('#detail-block').html(html_data);
                        $source.closest('#main-div').find('#detail-block').find('table').data({'data-object': data.dataObject});
                        $source.children('i').hide();
                        $source.attr('draft', 'false');
                        $source.closest('.cases-side-drawer-open').hide();
                        $source.closest('.cases-side-drawer-open').siblings('.cases-side-drawer-closed').find('.fa-list-alt').children('i').hide();
                        $source.closest('.cases-side-drawer-open').siblings('.cases-side-drawer-closed').show();
                        cases.mappings.editDetails.savedContent = false;
                    });
                },

                requirements: function (data, $source) {
                    var $allTrs = $source.closest('#main-div').find('#req-block').find('tr');
                    var completeData = [];
                    var flag = true;
                    for (var i=0; i < $allTrs.length; i++) {
                        if($($allTrs[i]).attr('being-edited') !== 'true'){
                            completeData.push($($allTrs[i]).data().dataObject);
                        } else {
                            flag = false;
                            completeData.push(data.dataObject);
                        }
                    }
                    if (flag) {
                        completeData.push(data.dataObject);
                    }
                    $.ajax({
                        headers: {
                            'X-CSRFToken': katana.$activeTab.find('input[name="csrfmiddlewaretoken"]').attr('value')
                        },
                        url: 'cases/get_reqs_display_template/',
                        type: 'POST',
                        data: {"data": JSON.stringify(completeData)}
                    }).done(function(html_data){
                        $source.closest('#main-div').find('#req-block').html(html_data);
                        $allTrs = $source.closest('#main-div').find('#req-block').find('tr');
                        for (i=0; i < $allTrs.length; i++) {
                            $($allTrs[i]).data({"data-object": completeData[i]})
                        }
                        $source.children('i').hide();
                        $source.attr('draft', 'false');
                        $source.closest('.cases-side-drawer-open').hide();
                        $source.closest('.cases-side-drawer-open').siblings('.cases-side-drawer-closed').find('.fa-tags').children('i').hide();
                        $source.closest('.cases-side-drawer-open').siblings('.cases-side-drawer-closed').show();
                        cases.mappings.newReq.savedContent = false;
                    });
                },

                steps: function (data, $source) {
                    var $allTrs = $source.closest('#main-div').find('#step-block').find('tbody').find('tr');
                    var completeData = [];
                    var ts = false;
                    var flag = true;
                    for (var i=0; i < $allTrs.length; i++) {
                        if($($allTrs[i]).attr('being-edited') !== 'true'){
                            completeData.push($($allTrs[i]).data().dataObject);
                        } else {
                            flag = false;
                            completeData.push(data.dataObject);
                            ts = completeData.length - 1 ;
                        }
                    }
                    if (flag) {
                        completeData.push(data.dataObject);
                        ts = completeData.length - 1;
                    }
                    $.ajax({
                        headers: {
                            'X-CSRFToken': katana.$activeTab.find('input[name="csrfmiddlewaretoken"]').attr('value')
                        },
                        url: 'cases/get_steps_display_template/',
                        type: 'POST',
                        data: {"data": JSON.stringify(completeData), "ts": ts}
                    }).done(function(html_data){
                        $source.closest('#main-div').find('#step-block').html(html_data);
                        $allTrs = $source.closest('#main-div').find('#step-block').find('tr');
                        for (i=0; i < $allTrs.length; i++) {
                            $($allTrs[i]).data({"data-object": completeData[i]})
                        }
                        $source.children('i').hide();
                        $source.attr('draft', 'false');
                        $source.closest('.cases-side-drawer-open').hide();
                        $source.closest('.cases-side-drawer-open').siblings('.cases-side-drawer-closed').find('.fa-star').children('i').hide();
                        $source.closest('.cases-side-drawer-open').siblings('.cases-side-drawer-closed').show();
                        cases.mappings.newStep.savedContent = false;
                    });
                },
            },

            discardContents: function () {

            },
        },

        detailsChange: function($elem, value){
            if ($elem === undefined) {
                $elem = $(this);
                value = $elem.val();
            }
            $elem.attr('value', value);
            var $parent = $elem.closest('.cases-drawer-open-body');
            var $switchElem = $parent.find('.fa-list-alt');
            $switchElem.attr('draft', 'true');
            $switchElem.children('i').show();
            $parent.parent().siblings('.cases-side-drawer-closed').find('.fa-list-alt').children('i').show();
            $switchElem.data({"data-object": cases.utils.updateData($switchElem.data().dataObject, $elem.attr('key'), $elem.val())});
        },

        reqsChange: function () {
            var $elem = $(this);
            $elem.attr('value', $elem.val());
            var $parent = $elem.closest('.cases-drawer-open-body');
            var $switchElem = $parent.find('.fa-tags');
            $switchElem.attr('draft', 'true');
            $switchElem.children('i').show();
            $parent.parent().siblings('.cases-side-drawer-closed').find('.fa-tags').children('i').show();
            $switchElem.data({"data-object": $elem.val()});
        },

        stepsChange: function () {
            var $elem = $(this);
            $elem.attr('value', $elem.val());
            var $parent = $elem.closest('.cases-drawer-open-body');
            var $switchElem = $parent.find('.fa-star');
            $switchElem.attr('draft', 'true');
            $switchElem.children('i').show();
            $parent.parent().siblings('.cases-side-drawer-closed').find('.fa-star').children('i').show();
            $switchElem.data({"data-object": cases.utils.updateData($switchElem.data().dataObject, $elem.attr('key'), $elem.val())});
        },

        openDrawer: {

            details: function ($elem) {
                if($elem === undefined){
                    $elem = $(this);
                }
                var $toggler = $elem.parent().find('[katana-click="cases.drawer.toggleDrawer"]').children('i');
                var $drawerClosedDiv = $toggler.closest('.cases-side-drawer-closed');
                var $drawerOpenDiv = $toggler.closest('.cases-side-drawer-closed').siblings('.cases-side-drawer-open');
                $drawerClosedDiv.hide();
                $drawerOpenDiv.show();
                var $switchElem = $($drawerOpenDiv.find('.sidebar').children()[0]).children('i');
                cases.drawer.open.switchView.details($switchElem);
            },

            requirements: function ($elem) {
                if($elem === undefined){
                    $elem = $(this);
                }
                var $toggler = $elem.parent().find('[katana-click="cases.drawer.toggleDrawer"]').children('i');
                var $drawerClosedDiv = $toggler.closest('.cases-side-drawer-closed');
                var $drawerOpenDiv = $toggler.closest('.cases-side-drawer-closed').siblings('.cases-side-drawer-open');
                $drawerClosedDiv.hide();
                $drawerOpenDiv.show();
                var $switchElem = $($drawerOpenDiv.find('.sidebar').children()[1]).children('i');
                cases.drawer.open.switchView.requirements($switchElem);
            },

            steps: function ($elem) {
                if($elem === undefined){
                    $elem = $(this);
                }
                var $toggler = $elem.parent().find('[katana-click="cases.drawer.toggleDrawer"]').children('i');
                var $drawerClosedDiv = $toggler.closest('.cases-side-drawer-closed');
                var $drawerOpenDiv = $toggler.closest('.cases-side-drawer-closed').siblings('.cases-side-drawer-open');
                $drawerClosedDiv.hide();
                $drawerOpenDiv.show();
                var $switchElem = $($drawerOpenDiv.find('.sidebar').children()[2]).children('i');
                cases.drawer.open.switchView.steps($switchElem);
            },
        },

        openFileExplorer: {

            logsdir: function () {
                var $elem = $(this);
                var $inputElem = $elem.parent().prev().children('input');
                katana.fileExplorerAPI.openFileExplorer("Select a Path", false,
                    katana.$activeTab.find('input[name="csrfmiddlewaretoken"]').attr('value'), false,
                    function (inputValue){
                        cases.drawer.detailsChange($inputElem, inputValue);
                    },
                    false)
            },

            resultsdir: function () {
                var $elem = $(this);
                var $inputElem = $elem.parent().prev().children('input');
                katana.fileExplorerAPI.openFileExplorer("Select a Path", false,
                    katana.$activeTab.find('input[name="csrfmiddlewaretoken"]').attr('value'), false,
                    function (inputValue){
                        cases.drawer.detailsChange($inputElem, inputValue);
                    },
                    false)
            },

            inputdatafile: function () {
                var $elem = $(this);
                var $inputElem = $elem.parent().prev().children('input');
                katana.fileExplorerAPI.openFileExplorer("Select a Path", false,
                    katana.$activeTab.find('input[name="csrfmiddlewaretoken"]').attr('value'), false,
                    function (inputValue){
                        var tcPath = katana.$activeTab.find('#main-div').attr("current-file");
                        var relPath = cases.utils.getRelativeFilepath(tcPath, inputValue);
                        cases.drawer.detailsChange($inputElem, relPath)
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

                                katana.$activeTab.find('#main-div').attr("current-file", data.filepath);

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
                                for (i=0; i<$allTrElements.length; i++){
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

                    katana.$activeTab.find('#main-div').attr("current-file", data.filepath);

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
                    for (i=0; i<$allTrElements.length; i++){
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
            var $elem = $(this);
            var $trElem = $elem.closest('tr');
            var $allTrs = $trElem.closest('.cases-intentional-space-x').find('[being-edited="true"]');
            var $mainDiv = $trElem.closest('#main-div');
            if ($allTrs.length > 0){
                if ($mainDiv.find('.cases-side-drawer-open').is(':visible')){
                    var draft = $mainDiv.find('.cases-side-drawer-open').find('.sidebar').find('.fa-tags').attr("draft") === 'true';
                } else {
                    draft = $mainDiv.find('.cases-side-drawer-closed').find('.fa-tags').children('i').is(':visible')
                }
                if (draft) {
                    katana.openAlert({
                        "alert_type": "warning",
                        "heading": "Another req is being edited in the Requirements Editor.",
                        "text": "Please save or discard that requirement before editing or creating a new requirement.",
                        "show_cancel_btn": false
                    });
                    return;
                }
            }
            for (var i=0; i<$allTrs.length; i++){
                $($allTrs[i]).attr('being-edited', 'false');
                cases.mappings.newReq.savedContent = false;
            }
            $trElem.attr('being-edited', 'true');
            var data = $trElem.data();
            var $closedDrawerDiv = $elem.closest('#main-div').find('.cases-side-drawer-closed');
            var $switchElem = $($closedDrawerDiv.siblings('.cases-side-drawer-open').find('.sidebar').children()[1]).children('i');
            $switchElem.data(data);
            if ($closedDrawerDiv.is(":hidden")){
                cases.drawer.open.switchView.requirements($switchElem);
            } else {
                var $openElem = $($closedDrawerDiv.children('div')[2]);
                cases.drawer.openDrawer.requirements($openElem);
            }
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
                    });
                    return;
                } else {
                    insertAtIndex = $($allTrElems[0]).index();
                    //insert tr
                }
                console.log(insertAtIndex);
            },

            editStep: function () {
                var $elem = $(this);
                var $tbodyElem = katana.$activeTab.find('#step-block').find('tbody');
                var $allTrElems = $tbodyElem.children('tr[marked="true"]');
                if ($allTrElems.length === 0) {
                    katana.openAlert({
                        "alert_type": "danger",
                        "heading": "No Step Selected",
                        "text": "Please select a step to edit.",
                        "show_cancel_btn": false
                    });
                } else if ($allTrElems.length > 1) {
                    katana.openAlert({
                        "alert_type": "danger",
                        "heading": "Multiple Steps Selected",
                        "text": "Only one step can be edited at a time. Please select only one " +
                        "step to edit.",
                        "show_cancel_btn": false
                    });
                } else {
                    var $allEditedTrElems = $tbodyElem.children('tr[being-edited="true"]');
                    var $mainDiv = $tbodyElem.closest('#main-div');
                    if($allEditedTrElems.length > 0){
                        if ($mainDiv.find('.cases-side-drawer-open').is(':visible')){
                            var draft = $mainDiv.find('.cases-side-drawer-open').find('.sidebar').find('.fa-star').attr("draft") === 'true';
                        } else {
                            draft = $mainDiv.find('.cases-side-drawer-closed').find('.fa-star').children('i').is(':visible')
                        }
                        if (draft) {
                            katana.openAlert({
                                "alert_type": "warning",
                                "heading": "Another Step is being edited in the Step Editor.",
                                "text": "Please save or discard that Step before editing or creating a new one.",
                                "show_cancel_btn": false
                            });
                            return;
                        }
                    }
                    for (var i=0; i<$allEditedTrElems.length; i++) {
                        $($allEditedTrElems[i]).attr('being-edited', 'false');
                        cases.mappings.newStep.savedContent = false;
                    }
                    $allTrElems.attr('being-edited', 'true');
                    var data = $allTrElems.data();
                    var $closedDrawerDiv = $elem.closest('#main-div').find('.cases-side-drawer-closed');
                    var $switchElem = $($closedDrawerDiv.siblings('.cases-side-drawer-open').find('.sidebar').children()[2]).children('i');
                    $switchElem.data(data);
                    if ($closedDrawerDiv.is(":hidden")){
                        cases.drawer.open.switchView.steps($switchElem);
                    } else {
                        var $openElem = $($closedDrawerDiv.children('div')[3]);
                        cases.drawer.openDrawer.steps($openElem);
                    }
                }
            },
        }
    },
};