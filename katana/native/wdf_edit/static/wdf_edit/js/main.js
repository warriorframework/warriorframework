var wdf = {
    search_and_hide: function(){
        $systems = $(".control-box");
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
                    $sys.find("[katana-click='wdf.addSubSystem']").hide();
                }
            }
        });
    },

    hide_template: function(){
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
    },

    sysNameChange: function(){
        $target = $(this);
        var $system_id = $target.attr("name").split("-").slice(0,1);
        var $subsystem_id = $target.attr("name").split("-").slice(1,2);

        $target = $("[linkto='#"+$system_id+"-"+$subsystem_id+"-control-box']");
        $target.closest(".wdf-pad").find("label").text(" "+$(this).prop("value"));
        if ($("[name='"+$system_id+"-"+$subsystem_id+"-subsystem_name']").length == 0) {
            $target.find("span").text(" "+$(this).prop("value"));
        }

        $value = $(this).prop("value");
        $systems = $("[name^='"+$system_id+"'][name$='-system_name']");
        $.each($systems, function(ind, sys){
            $(sys).prop("value", $value);
        });
    },

    subSysNameChange: function(){
        $target = $(this);
        var $system_id = $target.attr("name").split("-").slice(0,1);
        var $subsystem_id = $target.attr("name").split("-").slice(1,2);

        $target = $("[linkto='#"+$system_id+"-"+$subsystem_id+"-control-box']");
        $value = $(this).prop("value");
        $target.find("span").text(" "+$value);
    },

    deleteTag: function(){
        // empty tag and all of its child tags
        $target = $(this).closest(".control-box");
        var $system_id = $target.attr("id").split("-").slice(0,1);
        var $subsystem_id = $target.attr("id").split("-").slice(1,2);

        // When delete the last tag, shows addSubSystem icon
        if ($target.find("#content:has(div)").length == 1 && $subsystem_id == "1") {
            $target.find("[katana-click='wdf.addSubSystem']").show();
        }

        $target = $(this).closest(".row");
        $raw_id = $target.find("[name*='-key']").attr("name").substring(0, $target.find("[name*='-key']").attr("name").length-4);
        $id = $raw_id.split("-").slice(0,-1).join("-");

        // loop through all child tag and empty them
        $children = $target.parent().find("[name*='"+$id+"-']");
        for (var i=0; i<$children.length; i++) {
            if ($($children.get(i)).prop("name").indexOf("key") !== -1) {
                $child = $($children.get(i)).closest(".row");
                // $child.removeClass("animated fadeIn");
                // $child.addClass("animated bounceOutLeft");
                // closure
                // setTimeout((function(tmp){return function(){tmp.empty();}})($child), 600);
                $child.empty();
            }
        }
  
        // $target.removeClass("animated fadeIn");
        // $target.addClass("animated bounceOutLeft");
        // setTimeout(function(){$target.empty();}, 600);
        $target.empty();
    },

    deleteChildTag: function(){
        // hide a specific child tag
        $target = $(this).parent().parent().find("[name*='key']");
        $id = $target.attr("name").split("-").slice(0,3).join("-")+"-0-key";
        $parent_tag = $target.closest(".control-box").find("[name='"+$id+"']").parent();
        if ($parent_tag.length == 0) {
            $id = $target.attr("name").split("-").slice(0,3).join("-")+"-1-key";
            $parent_tag = $target.closest(".control-box").find("[name='"+$id+"']").parent();
        }
        
        $hide_target = $target.parent().parent();
        if ($target.prop("name").indexOf("deleted") == -1) {
            $target.prop("name", "deleted-"+$target.prop("name"));
            // $hide_target.removeClass("animated fadeIn");
            // $hide_target.addClass("animated bounceOutLeft");
            // setTimeout(function(){$hide_target.parent().parent().hide()}, 600);
            $hide_target.hide();

            if (parseInt($parent_tag.attr("child_count")) == 1) {
                $parent_tag.removeClass("col-md-10");
                $parent_tag.addClass("col-md-3");
                $parent_tag.next().show();
            }
            $parent_tag.attr("child_count", parseInt($parent_tag.attr("child_count"))-1);
        }
    },

    deleteSystem: function(){
        // empty the whole system
        $target=$(this).closest(".control-box");

        // When delete the 2nd last system, show add tag icon on main system
        var $system_id = $target.attr("id").split("-").slice(0,1);
        var $subsystem_id = $target.attr("id").split("-").slice(1,2);
        if ($target.parent().find("[id^='"+$system_id+"-']:not(:empty)").length == 2) {
            // alert("You delete the last subsystem");
            $target.parent().find("[id^='"+$system_id+"-1-']").find("[katana-click='wdf.addTag']").show()
        }
        // $target.removeClass("animated fadeIn");
        // $target.addClass("animated bounceOutLeft");
        // setTimeout(function(){$target.empty()}, 600);
        $target.empty();

        $target=$("[linkto='#"+$system_id+"-"+$subsystem_id+"-control-box']");
        $label=$target.closest(".wdf-pad");
        if ( $label.find(".btn").length == 1) {
            $label.remove();
        } else {
            $target.parent().remove();
        }
    },

    sysDefaultCheck: function(){
        if ($(this).prop("checked")) {
            $boxes = $(".wdf-sys-checkbox:checked");
            if ($boxes.length > 1) {
                $.each($boxes, function(ind, box){
                    $(box).prop("checked", false);
                });
            }
            $(this).prop("checked", true);
        }
    },

    subsysDefaultCheck: function(){
        var $system_id = $(this).attr("name").split("-").slice(0,1);
        var $subsystem_id = $(this).attr("name").split("-").slice(1,2);
        if ($(this).prop("checked")) {
            $boxes = $("[id^='"+$system_id+"'][id$='-control-box']").find(".wdf-subsys-checkbox:checked");
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
        var $tmp_id = katana.$activeTab.find(".control-box").length-1+"-1-control-box";
        $tmp.find("#template-system").prop("id", $tmp_id);
        $tmp.find("[name='template-system-name']").prop("name", katana.$activeTab.find(".control-box").length-1+"-1-system_name");
        $tmp.find("[name='template-system.tag']").prop("name", katana.$activeTab.find(".control-box").length-1+"-1-1-1-key");
        $tmp.find("[name='template-system.value']").prop("name", katana.$activeTab.find(".control-box").length-1+"-1-1-1-value");
        katana.$activeTab.find("#wdf-editor-col").append($($tmp.html()));

        $("#"+$tmp_id).get(0).scrollIntoView(true);
        katana.quickAnimation($("#"+$tmp_id).find("input"), "wdf-highlight", 1000);

        var $tmp = katana.$activeTab.find("#navigator_template").clone();
        $tmp.find("#template-nav-label").prop("id", katana.$activeTab.find(".control-box").length-2+"-1-ref-label");
        $tmp.find("#template-button-box").prop("id", katana.$activeTab.find(".control-box").length-2+"-1-button-box");
        var $length = katana.$activeTab.find(".control-box").length-2;
        $tmp.find("[linkto='template-nav.linkto']").attr("linkto", "#"+$length+"-1-control-box");
        katana.$activeTab.find("#wdf-navigator").append($($tmp.html()));
    },

    addTag: function(){
        var $tmp = katana.$activeTab.find("#tag_template").clone();
        // go to control box level
        var $target = $(this).closest(".control-box");
        var $system_id = $target.attr("id").split("-").slice(0,1);
        var $subsystem_id = $target.attr("id").split("-").slice(1,2);
        if ($target.parent().find("[id^='"+$system_id+"-']").length > 1 && $subsystem_id == "1") {
            alert("Please only add tag in subsystem");
        } else {
            var $id = $target.attr("id").substring(0, $target.attr("id").length-11);
            $tmp.find("[name='template-tag.tag']").prop("name", $id+($target.children("#content").length+1)+"-1-key");
            $tmp.find("[name='template-tag.value']").prop("name", $id+($target.children("#content").length+1)+"-1-value");
            $target.append($($tmp.html()));
        }
        $target.find("[katana-click='wdf.addSubSystem']").hide();
    },

    addChild: function(){
        var $tmp = katana.$activeTab.find("#child_tag_template").clone();
        // go to control box level
        var $target = $(this).closest("#content");
        var $raw_id = $target.find("[name*='-key']").attr("name").substring(0, $target.find("[name*='-key']").attr("name").length-4);
        var $id = $raw_id.split("-").slice(0,-1).join("-");
        var $new_id = $target.parent().find("[name*='"+$id+"']").length/2+1;
        $tmp.find("[name='template-tag.tag']").prop("name", $id+"-"+$new_id+"-key");
        $tmp.find("[name='template-tag.value']").prop("name", $id+"-"+$new_id+"-value");
        $target.parent().find("[name*='"+$id+"']:last").parent().parent().after($($tmp.html()));

        $input = $target.parent().find("[name*='"+$id+"']:first").parent();
        if ($input.hasClass("col-md-3")) {
            $input.removeClass("col-md-3");
            $input.addClass("col-md-10");
            $input.next().find("input").prop("value", "");
            $input.next().hide();
        }

        if ($input.attr("child_count")) {
            $input.attr("child_count", parseInt($input.attr("child_count"))+1);
        } else {
            $input.attr("child_count", 1);
        }
    },

    addSubSystem: function(){
        var $target = $(this).closest(".control-box");
        var $system_id = $target.attr("id").split("-").slice(0,1);
        var $subsystem_id = $target.attr("id").split("-").slice(1,2);
        if ($subsystem_id != "1") {
            alert("Please only add subsystem under top level system");
        } else if ($subsystem_id == "1" && $target.find("#content:has(div)").length > 0){
            alert("Please only add subsystem when top level system doesn't have tag");
        } else {
            var $tmp = katana.$activeTab.find("#subsystem_template").clone();
            var $system_id = $target.attr("id").split("-")[0];
            var $subsystem_count = $target.parent().find("[id^='"+$system_id+"-']").length;
            if ($("[name='"+$system_id+"-1-subsystem_name']").length == 0) {
                // no subsystem structure
                var $tmp_id = $system_id+"-"+$subsystem_count+"-control-box"
                $tmp.find("#template-subsystem").prop("id", $tmp_id);
                $tmp.find("[name='template-system-name']").attr("value", $target.find('[name*="system_name"]').attr("value"));
                $tmp.find("[name='template-system-name']").prop("name", $system_id+"-"+$subsystem_count+"-system_name");
                $tmp.find("[name='template-subsystem-name']").prop("name", $system_id+"-"+$subsystem_count+"-subsystem_name");
                $tmp.find("[name='template-subsystem.tag']").prop("name", $system_id+"-"+$subsystem_count+"-"+($target.children("#content").length+1)+"-1-key");
                $tmp.find("[name='template-subsystem.value']").prop("name", $system_id+"-"+$subsystem_count+"-"+($target.children("#content").length+1)+"-1-value");
                $tmp.find("[katana-click='wdf.addSubSystem']").hide()
                $("#"+$system_id+"-"+$subsystem_count+"-control-box").replaceWith($($tmp.html()));
            } else {
                // already has subsystem structure
                var $tmp_id = $system_id+"-"+($subsystem_count+1)+"-control-box"
                $tmp.find("#template-subsystem").prop("id", $tmp_id);
                $tmp.find("[name='template-system-name']").attr("value", $target.find('[name*="system_name"]').attr("value"));
                $tmp.find("[name='template-system-name']").prop("name", $system_id+"-"+($subsystem_count+1)+"-system_name");
                $tmp.find("[name='template-subsystem-name']").prop("name", $system_id+"-"+($subsystem_count+1)+"-subsystem_name");
                $tmp.find("[name='template-subsystem.tag']").prop("name", $system_id+"-"+($subsystem_count+1)+"-"+($target.children("#content").length+1)+"-1-key");
                $tmp.find("[name='template-subsystem.value']").prop("name", $system_id+"-"+($subsystem_count+1)+"-"+($target.children("#content").length+1)+"-1-value");
                $tmp.find("[katana-click='wdf.addSubSystem']").hide()
                $("#"+$system_id+"-"+$subsystem_count+"-control-box").after($($tmp.html()));

                var $tmp = katana.$activeTab.find("#navigator_button_template").clone();
                $tmp.find("#template-button-box").prop("id", $system_id+"-"+($subsystem_count+1)+"-button-box");
                $tmp.find("[linkto='template-nav.linkto']").attr("linkto", "#"+$system_id+"-"+($subsystem_count+1)+"-control-box");
                katana.$activeTab.find("#"+$system_id+"-"+($subsystem_count)+"-button-box").after($($tmp.html()));
            }

            $("#"+$tmp_id).get(0).scrollIntoView(true);
            katana.quickAnimation($("#"+$tmp_id).find("input"), "wdf-highlight", 1000);

            $target.parent().find("[id^='"+$system_id+"-1']").find("[katana-click='wdf.addTag']").hide()

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
        var csrftoken = $("[name='csrfmiddlewaretoken']").val();

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