var wdf = {
    toggle: function(){
        // hide all the div with id content under control-box
        $(this).parent().parent().parent().children("#content").toggle();
    },

    deleteTag: function(){
        $(this).parent().parent().empty();
    },

    deleteSystem: function(){
        $(this).parent().parent().parent().empty();
    },

    submit: function(){
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


    add: function(){
        // Add a system
        var $tmp = katana.$activeTab.find("#system_template").clone();
        $tmp.find("#template-system").prop("id", katana.$activeTab.find(".control-box").length-1+"-control-box")
        $tmp.find("[name='template-system-name']").prop("name", katana.$activeTab.find(".control-box").length-1+"-system_name");
        $tmp.find("[name='template-system.tag']").prop("name", katana.$activeTab.find(".control-box").length-1+"-1-key");
        $tmp.find("[name='template-system.value']").prop("name", katana.$activeTab.find(".control-box").length-1+"-1-value");
        katana.$activeTab.find("#big-box").append($($tmp.html()));
    },

    addtag: function(){
        var $tmp = katana.$activeTab.find("#tag_template").clone();
        // go to control box level
        var $target = $(this).parent().parent().parent();
        var $id = $target.attr("id").substring(0, $target.attr("id").length-11);
        $tmp.find("[name='template-tag.tag']").prop("name", $id+($target.children("#content").length+1)+"-key");
        $tmp.find("[name='template-tag.value']").prop("name", $id+($target.children("#content").length+1)+"-value");
        $target.append($($tmp.html()));
    },

    addSubSystem: function(){
        var $tmp = katana.$activeTab.find("#subsystem_template").clone();
        var $target = $(this).parent().parent().parent();
        var $system_id = $target.attr("id").split("-")[0];
        var $subsystem_count = $target.attr("id").split("-")[1];
        $tmp.find("[name='template-system-name']").attr("value", $target.find('[name*="system_name"]').attr("value"));
        $tmp.find("[name='template-system-name']").prop("name", $system_id+"-"+($subsystem_count+1)+"-system_name");
        $tmp.find("[name='template-subsystem-name']").prop("name", $system_id+"-"+($subsystem_count+1)+"-subsystem_name");
        $tmp.find("[name='template-tag.tag']").prop("name", $system_id+"-"+($subsystem_count+1)+"-"+($target.children("#content").length+1)+"-key");
        $tmp.find("[name='template-tag.value']").prop("name", $system_id+"-"+($subsystem_count+1)+"-"+($target.children("#content").length+1)+"-value");
        $target.append($($tmp.html()));
    },

    hide: function(){
        $(this).hide();
    },

    build_tree: function(){
        $.ajax({
            url: "wdf/gettree",
            type: "GET",
            dataType: "json",
            success: function(data){
                katana.$activeTab.find("#jstree").jstree({'core':{'data':[data]}});
            }
        });

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
                        katana.refreshAutoInit(katana.$activeTab.find("#system_template"));
                        katana.refreshAutoInit(katana.$activeTab.find("#tag_template"));
                        katana.refreshAutoInit(katana.$activeTab.find("#subsystem_template"));
                        // console.log("loaded");
                    }
                });
              // katana.templateAPI.post("wdf/index", csrftoken, {"path": data["node"]["li_attr"]["data-path"]});
            }
        });
    }


}