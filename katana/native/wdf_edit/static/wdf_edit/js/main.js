var wdf = {
    search_and_hide: function(){
        /*
            Scan the systems and hide the addsubsystem button if there are tags in it
        */
        $systems = katana.$activeTab.find(".control-box");
        $.each($systems, function(ind, sys) {
            if (! $(sys).attr("id").startsWith("template")) {
                $sys = $(sys);
                $system_id = $sys.attr("id").split("-").slice(0,1);
                $subsystem_id = $sys.attr("id").split("-").slice(1,2);
                // if it has tags
                if ($sys.find("#content").length > 0 && $subsystem_id != "1") {
                    $sys.find("[katana-click='wdf.addSubSystem']").hide();
                } else if ($sys.find("#content").length > 0 && $subsystem_id == "1") {
                    // var $count = 0;
                    // $.each($systems, function(sub_ind, sub_sys) {
                    //     if ($(sub_sys).attr("id").startsWith($system_id+"-")) {
                    //         $count = $count + 1;
                    //     }
                    // });
                    // if ($count > 1) {
                    //     $sys.find("[katana-click='wdf.addSubSystem']").hide();
                    // }
                    // $sys.find("[katana-click='wdf.addSubSystem']").hide();
                }
            }
        });
    },

    hide_template: function(){
        /*
            Hide the templates
        */
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
        $target = $(this);
        $target.prop("value", $target.val());
        var $system_id = $target.attr("name").split("-").slice(0,1);
        var $subsystem_id = $target.attr("name").split("-").slice(1,2);

        if ($target.val().length != 0) {
            $target.css("background", "none");
        }

        // find the button that links to the current system
        // Change the label and button text
        $target = katana.$activeTab.find("[id$='system-box']").find("[linkto='#"+$system_id+"-1-control-box']");
        $target.find("span").text(" "+$(this).prop("value"));

        // Change other system name input field under the same system
        $value = $(this).prop("value");
        $systems = katana.$activeTab.find("[name^='"+$system_id+"'][name$='-system_name']");
        $.each($systems, function(ind, sys){
            $(sys).prop("value", $value);
        });
    },

    subSysNameChange: function(){
        /*
            Synchronize name change between input field and nav bar
        */
        $target = $(this);
        var $system_id = $target.attr("name").split("-").slice(0,1);
        var $subsystem_id = $target.attr("name").split("-").slice(1,2);

        $target = katana.$activeTab.find("[id$='button-box']").find("[linkto='#"+$system_id+"-"+$subsystem_id+"-control-box']");
        $value = $(this).prop("value");
        $target.find("span").text(" "+$value);
    },

    validateKey: function(){
        $(this).prop("value", $(this).val());
        $(this).css("background", "#f9f9f9");
        if ($(this).prop("value").indexOf(" ") != -1) {
            alert("Data key cannot contain whitespace");
            $(this).focus()
            // katana.quickAnimation($(this), "wdf-highlight", 1000);
            $(this).css("background", "#ecff91");
        }
    },

    deleteTag: function(){
        // empty tag and all of its child tags
        $target = $(this).closest(".control-box");
        var $system_id = $target.attr("id").split("-").slice(0,1);
        var $subsystem_id = $target.attr("id").split("-").slice(1,2);

        // When delete the last tag, shows addSubSystem icon
        if ($target.find("#content:has(label)").length == 1 && $subsystem_id == "1") {
            $target.find("[katana-click='wdf.addSubSystem']").show();
        }

        // Get the id that represented the tag
        $target = $(this).closest(".field-inline");
        $raw_id = $target.find("[name*='-key']").attr("name").substring(0, $target.find("[name*='-key']").attr("name").length-4);
        $id = $raw_id.split("-").slice(0,-1).join("-");

        // loop through all child tag and empty them
        $children = $target.parent().find("[name*='"+$id+"-']");
        for (var i=0; i<$children.length; i++) {
            if ($($children.get(i)).prop("name").indexOf("key") !== -1) {
                $child = $($children.get(i)).closest(".field-inline");
                // $child.removeClass("animated fadeIn");
                // $child.addClass("animated bounceOutLeft");
                // closure
                // setTimeout((function(tmp){return function(){tmp.empty();}})($child), 600);
                $child.empty();
                $child.hide();
            }
        }
  
        // $target.removeClass("animated fadeIn");
        // $target.addClass("animated bounceOutLeft");
        // setTimeout(function(){$target.empty();}, 600);
        $target.empty();
        $target.hide();
    },

    deleteChildTag: function(){
        // hide a specific child tag

        // Find the parent tag, can either starts with -0-key or -1- key
        $target = $(this).parent().parent().find("[name*='key']");
        $id = $target.attr("name").split("-").slice(0,3).join("-")+"-0-key";
        $parent_tag = $target.closest(".control-box").find("[name='"+$id+"']");
        if ($parent_tag.length == 0) {
            $id = $target.attr("name").split("-").slice(0,3).join("-")+"-1-key";
            $parent_tag = $target.closest(".control-box").find("[name='"+$id+"']");
        }
        
        $hide_target = $target.parent();
        if ($target.prop("name").indexOf("deleted") == -1) {
            $target.prop("name", "deleted-"+$target.prop("name"));
            // $hide_target.removeClass("animated fadeIn");
            // $hide_target.addClass("animated bounceOutLeft");
            // setTimeout(function(){$hide_target.parent().parent().hide()}, 600);
            $hide_target.hide();

            // If deleting the last child tag, makes the parent tag become a regular tag again
            if (parseInt($parent_tag.attr("child_count")) == 1) {
                $parent_tag.next().show();
            }
            $parent_tag.attr("child_count", parseInt($parent_tag.attr("child_count"))-1);
        }
    },

    deleteSystem: function(){
        // empty the whole system, same function works on subsystem and system
        $target=$(this).closest(".control-box");
        var $system_id = $target.attr("id").split("-").slice(0,1);
        var $subsystem_id = $target.attr("id").split("-").slice(1,2);

        // When delete the 2nd last system, show add tag icon on main system
        if ($target.parent().find("[id^='"+$system_id+"-']:not(:empty)").length == 2) {
            // alert("You delete the last subsystem");
            $target.parent().find("[id^='"+$system_id+"-1-']").find("[katana-click='wdf.addTag']").show()
        }

        if ($target.parent().find("[id^='"+$system_id+"-']:not(:empty)").length > 1 && !($target.find(".sub-tool-bar").hasClass("wdf-indent"))) {
            $target.next().find(".sub-tool-bar").removeClass("wdf-indent");
            $target.next().find(".sub-tool-bar").find("div").show();
        }

        // $target.removeClass("animated fadeIn");
        // $target.addClass("animated bounceOutLeft");
        // setTimeout(function(){$target.empty()}, 600);
        $target.empty();

        // Update the nav bar
        $target=katana.$activeTab.find("[id$='button-box']").find("[linkto='#"+$system_id+"-"+$subsystem_id+"-control-box']");
        $target_sys=$target.closest(".wdf-pad");
        // only 1 subsys remains, 1 btn for sys and 1 btn for subsys
        if ($target_sys.find(".btn").length == 2) {
            $target_sys.remove();
        } else {
            $target.parent().remove();
        }
    },

    sysDefaultCheck: function(){
        // Check the current sys checkbox and uncheck other sys checkbox
        if ($(this).prop("checked")) {
            $boxes = katana.$activeTab.find(".wdf-sys-checkbox:checked");
            if ($boxes.length > 1) {
                $.each($boxes, function(ind, box){
                    $(box).prop("checked", false);
                });
            }
            $(this).prop("checked", true);
        }
    },

    subsysDefaultCheck: function(){
        // Check the current subsys checkbox and uncheck other subsys checkbox under the same sys
        var $system_id = $(this).attr("name").split("-").slice(0,1);
        var $subsystem_id = $(this).attr("name").split("-").slice(1,2);
        if ($(this).prop("checked")) {
            $boxes = katana.$activeTab.find("[id^='"+$system_id+"'][id$='-control-box']").find(".wdf-subsys-checkbox:checked");
            if ($boxes.length > 1) {
                $.each($boxes, function(ind, box){
                    $(box).prop("checked", false);
                });
            }
            $(this).prop("checked", true);
        }
    },

    addSystem: function(){
        // Add a system
        var $tmp = katana.$activeTab.find("#system_template").clone();
        // length-1 is because there are a template sys and template subsys with class control-box in it
        // the new system needs to have actual sys count + 1, which is the same as length-1
        var $tmp_id = katana.$activeTab.find(".control-box").length-1;

        // Replace template content with real content
        $tmp.find("#template-system").prop("id", $tmp_id+"-1-control-box");
        $tmp.find("[name='template-system-name']").prop("name", $tmp_id+"-1-system_name");
        $tmp.find("[name='template-system-default']").prop("name", $tmp_id+"-1-default");
        $tmp.find("[name='template-system.tag']").prop("name", $tmp_id+"-1-1-1-key");
        $tmp.find("[name='template-system.value']").prop("name", $tmp_id+"-1-1-1-value");
        katana.$activeTab.find("#wdf-editor-col").append($($tmp.html()));

        katana.$activeTab.find("#"+$tmp_id+"-1-control-box").get(0).scrollIntoView(true);
        katana.quickAnimation(katana.$activeTab.find("#"+$tmp_id+"-1-control-box").find("input"), "wdf-highlight", 1000);

        // Create button in nav bar
        var $tmp = katana.$activeTab.find("#navigator_template").clone();
        // length-2 as we just attached a new system into the view
        var $tmp_id = katana.$activeTab.find(".control-box").length-2;
        $tmp.find("#template-system-box").prop("id", $tmp_id+"-1-system-box");
        $tmp.find("[linkto='template-nav.linkto']").attr("linkto", "#"+$tmp_id+"-1-control-box");
        katana.$activeTab.find("#wdf-navigator").append($($tmp.html()));
    },

    addSubSystem: function(){
        // Add a subsystem under the current system
        var $target = $(this).closest(".control-box");
        var $system_id = $target.attr("id").split("-").slice(0,1);
        var $subsystem_id = $target.attr("id").split("-").slice(1,2);

        if ($subsystem_id != "1") {
            alert("Please only add subsystem under top level system");
        } else if ($subsystem_id == "1" && $target.find("#content:has(div)").length > 0){
            alert("Please only add subsystem when top level system doesn't have tag");
        } else {
            var $tmp = katana.$activeTab.find("#subsystem_template").clone();
            var $subsystem_count = $target.parent().find("[id^='"+$system_id+"-'][id$='-control-box']").length;

            if (katana.$activeTab.find("[name='"+$system_id+"-1-subsystem_name']").length == 0) {
                // no subsystem structure
                var $tmp_id = $system_id+"-"+$subsystem_count+"-control-box"
                $tmp.find("#template-subsystem").prop("id", $tmp_id);
                $tmp.find("[name='template-system-name']").attr("value", $target.find('[name*="system_name"]').attr("value"));
                $tmp.find("[name='template-system-name']").prop("name", $system_id+"-"+$subsystem_count+"-system_name");

                $tmp.find("[name='template-subsystem-name']").prop("name", $system_id+"-"+$subsystem_count+"-subsystem_name");
                $tmp.find("#content").remove();

                $tmp.find("[name='template-system-default']").prop("name", $system_id+"-"+$subsystem_count+"-default");
                $tmp.find("[name='template-subsystem-default']").prop("name", $system_id+"-"+$subsystem_count+"-default-subsys");

                // Replace the current system with a system with subsystem tag
                var $tags = $target.find(".field-inline");
                katana.$activeTab.find("#"+$system_id+"-"+$subsystem_count+"-control-box").replaceWith($($tmp.html()));
                $.each($tags, function(ind, tag){
                    katana.$activeTab.find("#"+$system_id+"-"+$subsystem_count+"-control-box").append($(tag));
                });

                // Add new subsystem to the nav bar
                var $tmp = katana.$activeTab.find("#navigator_button_template").clone();
                $tmp.find("#template-button-box").prop("id", $system_id+"-"+$subsystem_count+"-button-box");
                $tmp.find("[linkto='template-nav.linkto']").attr("linkto", "#"+$system_id+"-"+$subsystem_count+"-control-box");
                // Add button after the last subsystem under the same system
                katana.$activeTab.find("#"+$system_id+"-1-system-box").after($($tmp.html()));
            } else {
                // already has subsystem structure
                var $tmp_id = $system_id+"-"+($subsystem_count+1)+"-control-box"
                $tmp.find("#template-subsystem").prop("id", $tmp_id);
                $tmp.find("[name='template-system-name']").attr("value", $target.find('[name*="system_name"]').attr("value"));
                $tmp.find("[name='template-system-name']").prop("name", $system_id+"-"+($subsystem_count+1)+"-system_name");

                $tmp.find("[name='template-subsystem-name']").prop("name", $system_id+"-"+($subsystem_count+1)+"-subsystem_name");
                $tmp.find("[name='template-subsystem.tag']").prop("name", $system_id+"-"+($subsystem_count+1)+"-"+($target.children("#content").length+1)+"-1-key");
                $tmp.find("[name='template-subsystem.value']").prop("name", $system_id+"-"+($subsystem_count+1)+"-"+($target.children("#content").length+1)+"-1-value");

                $tmp.find("[name='template-system-default']").prop("name", $system_id+"-"+($subsystem_count+1)+"-default");
                $tmp.find("[name='template-subsystem-default']").prop("name", $system_id+"-"+($subsystem_count+1)+"-default-subsys");
                $tmp.find("[katana-click='wdf.addSubSystem']").hide()

                $tmp.find(".sub-tool-bar").addClass("wdf-indent");
                $tmp.find(".sub-tool-bar").find("div").hide();

                // Add new subsystem after the last subsystem
                katana.$activeTab.find("#"+$system_id+"-"+$subsystem_count+"-control-box").after($($tmp.html()));

                // Add new subsystem to the nav bar
                var $tmp = katana.$activeTab.find("#navigator_button_template").clone();
                $tmp.find("#template-button-box").prop("id", $system_id+"-"+($subsystem_count+1)+"-button-box");
                $tmp.find("[linkto='template-nav.linkto']").attr("linkto", "#"+$system_id+"-"+($subsystem_count+1)+"-control-box");
                // Add button after the last subsystem under the same system
                katana.$activeTab.find("#"+$system_id+"-"+($subsystem_count)+"-button-box").after($($tmp.html()));
            }

            // Highlight the new subsystem
            katana.$activeTab.find("#"+$tmp_id).get(0).scrollIntoView(true);
            katana.quickAnimation(katana.$activeTab.find("#"+$tmp_id).find("input"), "wdf-highlight", 1000);

            // $target.parent().find("[id^='"+$system_id+"-1']").find("[katana-click='wdf.addTag']").hide()
        }
    },

    addTag: function(){
        var $tmp = katana.$activeTab.find("#tag_template").clone();
        // go to control box level
        var $target = $(this).closest(".control-box");
        var $system_id = $target.attr("id").split("-").slice(0,1);
        var $subsystem_id = $target.attr("id").split("-").slice(1,2);

        var $id = $system_id+"-"+$subsystem_id+"-";
        $tmp.find("[name='template-tag.tag']").prop("name", $id+($target.children("#content").length+1)+"-1-key");
        $tmp.find("[name='template-tag.value']").prop("name", $id+($target.children("#content").length+1)+"-1-value");
        $target.append($($tmp.html()));
    },

    addChild: function(){
        var $tmp = katana.$activeTab.find("#child_tag_template").clone();
        // go to control box level
        var $target = $(this).closest("#content");
        var $target_name = $target.find("[name*='-key']").attr("name");
        var $raw_id = $target_name.substring(0, $target_name.length-4);
        var $id = $raw_id.split("-").slice(0,-1).join("-");
        var $new_id = $target.parent().find("[name*='"+$id+"'][name$='-key']").length+1;

        $tmp.find("[name='template-tag.tag']").prop("name", $id+"-"+$new_id+"-key");
        $tmp.find("[name='template-tag.value']").prop("name", $id+"-"+$new_id+"-value");
        $target.parent().find("[name*='"+$id+"'][name$='-key']:last").parent().after($($tmp.html()));

        $input = $target.parent().find("[name*='"+$id+"'][name$='-key']:first");
        if ($input.next().css("display") != "none") {
            $input.next().hide();
        }

        if ($input.attr("child_count")) {
            $input.attr("child_count", parseInt($input.attr("child_count"))+1);
        } else {
            $input.attr("child_count", 1);
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
        var data = katana.$activeTab.find("#big-box").find("input[name$='-key']");
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