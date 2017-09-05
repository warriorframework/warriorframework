var wdf = {
    toggle: function(){
        $(this).parent().parent().parent().children("#content").toggle();
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
                katana.$activeTab.find("#main_info").replaceWith(data);
                katana.refreshAutoInit(katana.$activeTab.find("#jstree"));
            }
        }); 
    },


    add: function(){
        var $tmp = katana.$activeTab.find("#system_template").clone();
        $tmp.find("#template-system").prop("id", katana.$activeTab.find(".control-box").length+"-control-box")
        $tmp.find("[name='template-system-name']").prop("name", katana.$activeTab.find(".control-box").length+"-system_name");
        $tmp.find("[name='template-system.tag']").prop("name", katana.$activeTab.find(".control-box").length+"-1-key");
        $tmp.find("[name='template-system.value']").prop("name", katana.$activeTab.find(".control-box").length+"-1-value");
        katana.$activeTab.find("#big-box").append($($tmp.html()));
    },

    addtag: function(){
        var $tmp = katana.$activeTab.find("#tag_template").clone();
        var $target = $(this).parent().parent().parent();
        var $count = $target.attr("id").substring(0, $target.attr("id").length-11);
        $tmp.find("[name='template-tag.tag']").prop("name", $count+($target.children("#content").length+1)+"-key");
        $tmp.find("[name='template-tag.value']").prop("name", $count+($target.children("#content").length+1)+"-value");
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
                        // console.log("loaded");
                    }
                });
              // katana.templateAPI.post("wdf/index", csrftoken, {"path": data["node"]["li_attr"]["data-path"]});
            }
        });
    }


}