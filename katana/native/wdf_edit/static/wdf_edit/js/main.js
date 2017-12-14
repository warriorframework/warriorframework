var wdf = {
    search_and_hide: function(){
        /*
            Scan the systems and hide the addsubsystem button if there are tags in it
        */
        var systems = katana.$activeTab.find(".control-box");
        $.each(systems, function(ind, sys) {
            var sys = $(sys);
            if (!sys.attr("id").startsWith("template")) {
                if (sys.find("#content").length > 0 && sys.find("[name='subsystem_name']").length == 0) {
                    sys.find("[katana-click='wdf.addSubSystem']").hide();
                }
            }
        });
    },

    search_for_password: function(){
        $inputs = katana.$activeTab.find("#content, #subcontent");
        $inputs.each(function(ind, row) {
            $row = $(row);
            $row_key = $row.find("[name$='-key']");
            $row_value = $row.find("[name$='-value']");
            if (typeof $row_key.attr("value") !== "undefined" && $row_key.attr("value").toLowerCase() == "password" ) {
                $row_value.attr("type", "password");
            }
        });
    },

    hide_template: function(){
        /*
            Hide the templates
        */
        katana.$activeTab.find(".tool-bar").remove();
        katana.refreshAutoInit(katana.$activeTab.find("#system_template"));
        katana.refreshAutoInit(katana.$activeTab.find("#tag_template"));
        katana.refreshAutoInit(katana.$activeTab.find("#child_tag_template"));
        katana.refreshAutoInit(katana.$activeTab.find("#subsystem_template"));
        katana.refreshAutoInit(katana.$activeTab.find("#navigator_template"));
        katana.refreshAutoInit(katana.$activeTab.find("#navigator_button_template"));
    },

    toggle: function(){
        // hide all the div with id content under control-box
        $target = $(this).closest(".control-box");
        $target.children("#content").toggle();
        $target.children("#subcontent").toggle();
        if ($(this).hasClass("fa-toggle-down")) {
            $(this).removeClass("fa-toggle-down");
            $(this).addClass("fa-toggle-up");
        } else if ($(this).hasClass("fa-toggle-up")) {
            $(this).removeClass("fa-toggle-up");
            $(this).addClass("fa-toggle-down");
        }
    },

    sysNameChange: function(){
        /*
            Synchronize name change between input field and nav bar
        */
        var input_box = $(this);

        var system_id = input_box.closest(".control-box").attr("sysid");

        if (input_box.val().length != 0) {
            input_box.css("background", "none");
        }

        // find the button that links to the current system
        // Change the label and button text
        var nav_button = katana.$activeTab.find("[linkto='#"+system_id+"-control-box']");
        input_box.attr("value", input_box.val());
        nav_button.find("span").text(" "+input_box.prop("value"));
    },

    subSysNameChange: function(){
        /*
            Synchronize name change between input field and nav bar
        */
        var input_box = $(this);
        var system_id = input_box.closest(".control-box").attr("sysid");
        var subsystem_id = input_box.closest(".subsys-box").attr("subsysid");

        var nav_button = katana.$activeTab.find("[linkto='#"+system_id+"-"+subsystem_id+"-editor']");
        input_box.attr("value", input_box.val());
        nav_button.find("span").text(" "+input_box.prop("value"));
    },

    validateKey: function(){
        $ele = $(this);
        $ele.attr("value", $ele.val());
        $ele.css("background", "#f9f9f9");
        if ($ele.prop("value").indexOf(" ") != -1) {
            alert("Data key cannot contain whitespace");
            $ele.focus()
            // katana.quickAnimation($(this), "wdf-highlight", 1000);
            $ele.css("background", "#ecff91");
        }

        if ($ele.val().toLowerCase() == "password") {
            $ele.next().attr("type", "password");
        } else {
            $ele.next().removeAttr("type");
        }
    },

    deleteTag: function(){
        // empty tag and all of its child tags
        $(this).closest("#content").remove();
        if ($(this).closest(".child_tags").length == 1) {
            $(this).closest(".child_tags").remove();
        }
    },

    deleteChildTag: function(){
        $(this).closest("#subcontent").remove();
        if ($(this).closest(".child_tags").length == 0) {
            $(this).closest(".child_tags").find("[name='value']").show();
        }
    },

    deleteSystem: function(){
        // empty the whole system
        var target = $(this).closest(".control-box");
        var system_id = target.attr("sysid");
        var target_control_box = katana.$activeTab.find("[linkto='#"+system_id+"-control-box']").closest(".wdf-pad");
        // need to update the sysid for the systems below

        var systems_list = katana.$activeTab.find("#wdf-editor-col").find(".control-box");
        $.each(systems_list, function(ind, sys){
            if (ind+1 > parseInt(system_id)){
                // Decrease the system_id by 1 to fill the one being removed
                console.log(ind+1);
                $(sys).attr("sysid", ind);
                $(sys).attr("id", ind+"-control-box");

                var system_nav_button = katana.$activeTab.find("[linkto='#"+(ind+1)+"-control-box']");
                system_nav_button.attr("linkto", "#"+ind+"-control-box");

                var subsys_list = $(sys).find(".subsys-box");
                $.each(subsys_list, function(sub_ind, subsys){
                    $(subsys).attr("id", ind+"-"+(sub_ind+1)+"-editor");

                    var subsys_nav_button = katana.$activeTab.find("[linkto='#"+(ind+1)+"-"+(sub_ind+1)+"-editor']");
                    subsys_nav_button.attr("linkto", "#"+ind+"-"+(sub_ind+1)+"-editor");
                });
            }
        });

        target.remove();
        target_control_box.remove();
    },

    deleteSubSystem: function(){
        // empty the subsystem
        var target = $(this).closest(".control-box");
        var system_id = target.attr("sysid");
        // need to update the sysid for the systems below

        target.remove();
        
        // Update the nav bar
        var nav_button = katana.$activeTab.find("[linkto='#"+system_id+"-control-box']").closest(".wdf-pad");
        nav_button.remove();
    },

    sysDefaultCheck: function(){
        // Check the current sys checkbox and uncheck other sys checkbox
        if ($(this).prop("checked")) {
            var boxes = katana.$activeTab.find(".wdf-sys-checkbox:checked");
            if (boxes.length > 1) {
                $.each(boxes, function(ind, box){
                    $(box).prop("checked", false);
                });
            }
            $(this).prop("checked", true);
        }
    },

    subsysDefaultCheck: function(){
        // Check the current subsys checkbox and uncheck other subsys checkbox under the same sys
        if ($(this).prop("checked")) {
            var boxes = $(this).closest(".control-box").find(".wdf-subsys-checkbox:checked");
            if (boxes.length > 1) {
                $.each(boxes, function(ind, box){
                    $(box).prop("checked", false);
                });
            }
            $(this).prop("checked", true);
        }
    },

    addSystem: function(){
        // Add a system
        var tmp = katana.$activeTab.find("#system_template").clone();
        // There is a template sys with class control-box in it
        // the new system needs to have actual sys count + 1, which is the same as length
        var tmp_id = katana.$activeTab.find(".control-box").length;

        // Add the system to the end of page
        tmp.find("#template-system").attr("sysid", tmp_id);
        tmp.find("#template-system").attr("id", tmp_id+"-control-box");
        tmp.find("#template-subsys-editor").attr("subsysid", 1);
        tmp.find("#template-subsys-editor").attr("id", tmp_id+"-1-editor");
        katana.$activeTab.find("#wdf-editor-col").append(tmp.html());

        katana.$activeTab.find("#"+tmp_id+"-control-box").get(0).scrollIntoView(true);
        katana.quickAnimation(katana.$activeTab.find("#"+tmp_id+"-control-box").find("input"), "wdf-highlight", 1000);

        // Create button in nav bar
        var tmp = katana.$activeTab.find("#navigator_template").clone();
        tmp.find("[linkto='template-nav.linkto']").attr("linkto", "#"+tmp_id+"-control-box");
        katana.$activeTab.find("#wdf-navigator").append(tmp.html());
    },

    addSubSystem: function(){
        // Add a subsystem under the current system
        var target = $(this).closest(".control-box");
        var system_id = target.attr("sysid");
        var subsystem_id = target.find(".subsys-box").length+1;

        if (subsystem_id == 2 && target.find(".subsys-box").length == 0 & target.find("#content".length > 0)){
            alert("Please only add subsystem when top level system doesn't have tag");
        } else {
            var tmp = katana.$activeTab.find("#subsystem_template").clone();

            tmp.find("#template-subsys-editor").attr("subsysid", subsystem_id);
            tmp.find("#template-subsys-editor").attr("id", system_id+"-"+subsystem_id+"-editor");

            target.append(tmp.html());

            // Highlight the new subsystem
            target = katana.$activeTab.find("#"+system_id+"-"+subsystem_id+"-editor")
            target.get(0).scrollIntoView(true);
            katana.quickAnimation(target.find("input"), "wdf-highlight", 1000);

            // Create button in nav bar
            var tmp = katana.$activeTab.find("#navigator_button_template").clone();
            tmp.find("[linkto='template-nav.linkto']").attr("linkto", "#"+system_id+"-"+subsystem_id+"-editor");
            // Find the system box and append current subsys button to it
            katana.$activeTab.find("[linkto='#"+system_id+"-control-box']").closest(".wdf-pad").append(tmp.html()); 
        }
    },

    addTag: function(){
        var tmp = katana.$activeTab.find("#tag_template").clone();
        // go to control box level
        var target = $(this).closest(".control-box");
        target.append(tmp.html());
    },

    addChild: function(){
        var tmp = katana.$activeTab.find("#child_tag_template").clone();
        // go to control box level
        var target = $(this).closest("#content");

        if (target.parent().prop("class") != "child_tags"){
            target.wrap("<div class='child_tags'></div>")
            target.find("[name='value']").hide();
        }

        target = target.parent();
        target.append(tmp.html());
    },

    hide: function(){
        $(this).hide();
    },

    newFile: function(){
        // send a get request to request a empty page
        $.ajax({
            url: "wdf/index",
            type: "GET",
            success: function(data){
                // console.log(data);
                katana.$activeTab.find("#main_info").replaceWith(data);
                wdf.hide_template();
                // console.log("loaded");
            }
        });
    },

    build_tree: function(){
        // get the file system tree from jstree library
        $.ajax({
            url: "wdf/gettree",
            type: "GET",
            dataType: "json",
            success: function(data){
                if (! data.hasOwnProperty("children")) {
                    alert("Data file directory is not set up, please add idr directory in Settings - General Settings");
                    data["text"] = "Data file directory is not set up, please add idr directory in Settings - General Settings"
                }
                katana.$activeTab.find("#jstree").jstree({'core':{'data':[data]}});
                katana.$activeTab.find('#jstree').jstree().hide_dots();
            }
        });

        // change the tree with actual editor page
        katana.$activeTab.find('#jstree').on("select_node.jstree", function (e, data) {
            // console.log("select_node");
            // console.log(data);
            if (data["node"]["icon"] == "jstree-file") {
                // console.log(data["node"]["li_attr"]["data-path"]);
                var csrftoken = katana.$activeTab.find("[name='csrfmiddlewaretoken']").val();
                $.ajax({
                    url: "wdf/index",
                    type: "POST",
                    headers: {'X-CSRFToken':csrftoken},
                    data: {"path": data["node"]["li_attr"]["data-path"]},
                    success: function(data){
                        // console.log(data);
                        katana.$activeTab.find("#main_info").replaceWith(data);
                        wdf.hide_template();
                        wdf.search_and_hide();
                        wdf.search_for_password();
                        // console.log("loaded");
                    }
                });
              // katana.templateAPI.post("wdf/index", csrftoken, {"path": data["node"]["li_attr"]["data-path"]});
            }
        });
    },

    submit: function(){
        // save all the input fields and post it to server
        var csrftoken = katana.$activeTab.find("[name='csrfmiddlewaretoken']").val();
        var data = katana.$activeTab.find("#big-box").find("input[name$='-key']:not([name^='deleted-'])");
        var valid = true;
        $.each(data, function(ind, ele){
            if ($(ele).val().length == 0 || $(ele).val().indexOf(" ") != -1) {
                $(ele).css("background", "#ecff91");
                valid = false;
            }
        });

        var data = katana.$activeTab.find("#big-box").find("input[name$='-subsystem_name']");
        $.each(data, function(ind, ele){
            if ($(ele).val().length == 0 || $(ele).val().indexOf(" ") != -1) {
                $(ele).css("background", "#ecff91");
                valid = false;
            }
        });

        var data = katana.$activeTab.find("#big-box").find("input[name$='-system_name']");
        $.each(data, function(ind, ele){
            if ($(ele).val().length == 0 || $(ele).val().indexOf(" ") != -1) {
                $(ele).focus();
                $(ele).css("background", "#00ffff");
                valid = false;
            }
        });

        if (valid) {
            $.ajax({
                url : "/katana/wdf/post",
                type: "POST",
                data : katana.$activeTab.find("#big-box").serializeArray(),
                headers: {'X-CSRFToken':csrftoken},
                //contentType: 'application/json',
                success: function(data){
                    // load the tree
                    katana.$activeTab.find("#main_info").replaceWith(data);
                    var $toolbar = katana.$activeTab.find(".tool-bar");
                    katana.$activeTab.find(".page-content").prepend($toolbar);
                    katana.refreshAutoInit(katana.$activeTab.find("#jstree"));
                }
            }); 
        } else {
            alert("Invalid name found (empty/has space), please edit the highlighed input box");
        }
    },

    cancel: function(){
        // save all the input fields and post it to server

        $.ajax({
            url : "/katana/wdf/",
            type: "GET",
            //contentType: 'application/json',
            success: function(data){
                // load the tree
                katana.$activeTab.find("#main_info").replaceWith(data);
                var $toolbar = katana.$activeTab.find(".tool-bar");
                katana.$activeTab.find(".page-content").prepend($toolbar);
                katana.refreshAutoInit(katana.$activeTab.find("#jstree"));
            }
        }); 
    },

    jump_to: function(){
        $target = katana.$activeTab.find($(this).attr("linkto"));
        $target.get(0).scrollIntoView(true);
        // $target.find("input").css("background-color", "#ecff91");
        // setTimeout(function(){$target.find("input").css("background-color", "");}, 500);
        katana.quickAnimation($target.find("input"), "wdf-highlight", 1000);
        // $target.find("input").addClass("wdf-highlight");
        // setTimeout(function(){$target.find("input").removeClass("wdf-highlight")}, 1000);
    },
}