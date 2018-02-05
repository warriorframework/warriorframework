var wdf = {
    search_and_hide: function(){
        /*
            Scan the systems and hide the addsubsystem button if there are tags in it
        */
        var systems = katana.$activeTab.find(".control-box");
        $.each(systems, function(ind, sys) {
            var sys = $(sys);
            if (!sys.attr("id").startsWith("template")) {
                if (sys.find(".wdf-content").length > 0 && sys.find("[name='subsystem_name']").length == 0) {
                    sys.find("[katana-click='wdf.addSubSystem']").hide();
                }
                if (sys.find("[name='subsystem_name']").length > 0) {
                    sys.find(".sys-toolbar").find("[katana-click='wdf.addTag']").hide();
                }
            }
        });
    },

    search_for_password: function(){
        $inputs = katana.$activeTab.find(".wdf-content, .wdf-subcontent");
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
        // hide all the div with id content under control-box/subsys-box
        var target = ($(this).closest(".subsys-box").length == 0 ? $(this).closest(".control-box") : $(this).closest(".subsys-box"));
        if ($(this).hasClass("fa-toggle-down")) {
            $(this).removeClass("fa-toggle-down");
            $(this).addClass("fa-toggle-up");
            target.find(".wdf-content").each(function(ind, ele){$(ele).show()});
            target.find(".wdf-subcontent").each(function(ind, ele){$(ele).show()});
        } else if ($(this).hasClass("fa-toggle-up")) {
            $(this).removeClass("fa-toggle-up");
            $(this).addClass("fa-toggle-down");
            target.find(".wdf-content").each(function(ind, ele){$(ele).hide()});
            target.find(".wdf-subcontent").each(function(ind, ele){$(ele).hide()});
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

        if (subsystem_id == 2 && target.find(".subsys-toolbar").length == 0 && target.find(".wdf-content").length > 0){
            alert("Please only add subsystem when top level system doesn't have tag");
        } else {
            var tmp = katana.$activeTab.find("#subsystem_template").clone();

            if (subsystem_id == 2 && target.find(".subsys-box").length == 1 && target.find(".wdf-content").length == 0) {
                subsystem_id = 1;
            }

            tmp.find("#template-subsys-editor").attr("subsysid", subsystem_id);
            tmp.find("#template-subsys-editor").attr("id", system_id+"-"+subsystem_id+"-editor");

            if (subsystem_id == 2 && target.find(".subsys-box").length == 1 && target.find(".wdf-content".length == 0)) {
                subsystem_id = 1;
            } else {
                target.find(".subsys-box").replaceWith(tmp.html());
            }
            target.find(".sys-toolbar").find("[katana-click='wdf.addTag']").hide();

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
        if ($(this).closest(".subsys-box").length == 0) {
            var target = $(this).closest(".control-box");
            target.find(".sys-toolbar").find("[katana-click='wdf.addSubSystem']").hide();
            target = target.find(".subsys-box");
        } else {
            var target = $(this).closest(".subsys-box");
        }
        target.append(tmp.html());
    },

    addChild: function(){
        var tmp = katana.$activeTab.find("#child_tag_template").clone();
        // go to control box level
        var target = $(this).closest(".wdf-content");

        if (target.parent().prop("class") != "child_tags"){
            target.wrap("<div class='child_tags'></div>")
            target.find("[name='value']").hide();
        }

        target = target.parent();
        target.append(tmp.html());
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
        var system = $(this).closest(".control-box");
        var target = $(this).closest(".subsys-box");
        var system_id = system.attr("sysid");
        var subsystem_id = target.attr("subsysid");
        var target_control_box = katana.$activeTab.find("[linkto='#"+system_id+"-"+subsystem_id+"-editor']").closest(".wdf-subsys-nav");

        // need to update the subsysid for the subsystems below

        var subsystems_list = system.find(".subsys-box");
        $.each(subsystems_list, function(ind, subsys){
            if (ind+1 > parseInt(subsystem_id)){
                // Decrease the system_id by 1 to fill the one being removed
                $(subsys).attr("subsysid", ind);
                $(subsys).attr("id", system_id+"-"+ind+"-editor");

                var subsys_nav_button = katana.$activeTab.find("[linkto='#"+system_id+"-"+(ind+1)+"-editor']");
                subsys_nav_button.attr("linkto", "#"+system_id+"-"+ind+"-editor");
            }
        });

        if (system.find(".subsys-box").length == 1){
            system.find(".sys-toolbar").find("[katana-click='wdf.addTag']").show();
            target.empty();
        } else {
            target.remove();
        }

        target_control_box.remove();

    },

    deleteTag: function(){
        // empty tag and all of its child tags
        if ($(this).closest(".control-box").find(".subsys-toolbar").length == 0 && $(this).closest(".control-box").find(".wdf-content").length == 1){
            $(this).closest(".control-box").find("[katana-click='wdf.addSubSystem']").show();
        }

        if ($(this).closest(".child_tags").length == 1) {
            $(this).closest(".child_tags").remove();
        } else {
            $(this).closest(".wdf-content").remove();
        }
    },

    deleteChildTag: function(){
        if ($(this).closest(".child_tags").find(".wdf-subcontent").length == 1) {
            var tag = $(this).closest(".child_tags").find(".wdf-content");
            tag.find("[name='value']").show();
            $(this).closest(".child_tags").before(tag);
            $(this).closest(".child_tags").remove();
        } else {
            $(this).closest(".wdf-subcontent").remove();
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

        if (input_box.val().length != 0) {
            input_box.css("background", "none");
        }

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

    presubmit_validation: function(){
        var valid = true;
        var editor = katana.$activeTab.find("#wdf-editor-col");

        var data = editor.find("input[name='key']")
        $.each(data, function(ind, ele){
            if ($(ele).val().length == 0 || $(ele).val().indexOf(" ") != -1) {
                $(ele).css("background", "#ecff91");
                valid = false;
            }
        });

        var data = editor.find("input[name='subsystem_name']");
        $.each(data, function(ind, ele){
            if ($(ele).val().length == 0 || $(ele).val().indexOf(" ") != -1) {
                $(ele).css("background", "#00ffff");
                valid = false;
            }
        });

        var data = editor.find("input[name='system_name']");
        $.each(data, function(ind, ele){
            if ($(ele).val().length == 0 || $(ele).val().indexOf(" ") != -1) {
                $(ele).focus();
                $(ele).css("background", "#00ffff");
                valid = false;
            }
        });

        return valid;
    },

    build_data_list: function(sys){
        var sys = $(sys);
        var data = [];

        sys.children().each(function(ind, content){
            if ($(content).hasClass("wdf-content")){
                // Pure content, no child tags
                var key = $(content).find("[name='key']").prop("value");
                var val = $(content).find("[name='value']").prop("value");
                // Can't create a dict with dynamic key...
                var save = {};
                save[key] = val;
                data.push(save);
            } else if ($(content).hasClass("child_tags")){
                // Has child tags
                var key = $(content).find("[name='key']").prop("value");
                var val = []
                $(content).find(".wdf-subcontent").each(function(ind, subcontent){
                    var subkey = $(subcontent).find("[name='key']").prop("value");
                    var subval = $(subcontent).find("[name='value']").prop("value");
                    var save = {};
                    save[subkey] = subval;
                    val.push(save);
                });
                var save = {};
                save[key] = val;
                data.push(save);
            }
        });

        return data;
    },

    build_systems(){
        var systems = katana.$activeTab.find(".control-box");
        // Get rid of template system
        systems = systems.slice(0, -1);
        var data = [];
        systems.each(function(ind, sys){
            var sysname = $(sys).find("input[name='system_name']").prop("value");

            if ($(sys).find(".subsys-toolbar").length == 0){
                var sys_data = wdf.build_data_list($(sys).find(".subsys-box"));
                var current_sys = {"@name": sysname, "values": sys_data};
            } else if ($(sys).find(".subsys-toolbar").length == 1){
                var subsys = $(sys).find(".subsys-box");
                var sys_data = wdf.build_data_list(subsys);
                var subsysname = $(subsys).find("input[name='subsystem_name']").prop("value");
                var current_sys = {"@name": sysname, "subsystem": {"@name": subsysname, "values": sys_data}};
                if ($(subsys).find(".wdf-subsys-checkbox").is(":checked")){
                    current_sys["subsystem"]["@default"] = "yes";
                }
            } else if ($(sys).find(".subsys-toolbar").length > 1){
                var subsystems = $(sys).find(".subsys-box");
                var values = []
                subsystems.each(function(ind, subsys){
                    var sys_data = wdf.build_data_list(subsys);
                    var subsysname = $(subsys).find("input[name='subsystem_name']").prop("value");
                    if ($(subsys).find(".wdf-subsys-checkbox").is(":checked")){
                        values.push({"@name": subsysname, "@default": "yes", "values": sys_data});
                    } else {
                        values.push({"@name": subsysname, "values": sys_data});
                    }
                });
                var current_sys = {"@name": sysname, "subsystem": values};
            }

            if ($(sys).find(".wdf-sys-checkbox").is(":checked")){
                current_sys["@default"] = "yes";
            }
            data.push(current_sys);
        });

        return data;
    },

    submit: function(){
        // save all the input fields and post it to server
        var csrftoken = katana.$activeTab.find("[name='csrfmiddlewaretoken']").val();
        var valid = wdf.presubmit_validation();

        if (valid) {
            var systems = wdf.build_systems();
            var filepath = katana.$activeTab.find("#xml_filepath").prop("value");
            var description = katana.$activeTab.find("#xml_description").prop("value");

            $.ajax({
                url : "/katana/wdf/post",
                type: "POST",
                data : JSON.stringify({"filepath": filepath, "description": description, "systems": systems}),
                headers: {'X-CSRFToken':csrftoken},
                success: function(data){
                    // load the tree
                    katana.$activeTab.find("#main_info").replaceWith(data);
                    var toolbar = katana.$activeTab.find(".tool-bar");
                    katana.$activeTab.find(".page-content").prepend(toolbar);
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