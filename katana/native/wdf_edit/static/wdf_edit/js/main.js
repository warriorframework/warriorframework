var wdf = {
    toggle: function(){
        $(this).parent().parent().parent().children("#content").toggle();
    },

    submit: function(){
        var csrftoken = $("[name='csrfmiddlewaretoken']").val();

        $.ajax({
            url : "/katana/wdf/post",
            type: "POST",
            data : $("#big-box").serializeArray(),
            headers: {'X-CSRFToken':csrftoken},
            //contentType: 'application/json',
            success: function(data){
                console.log("Sent");
                // console.log(data);
            }
        }); 
    },


    add: function(){
        var $tmp = $("#system_template").clone();
        $tmp.find("#template-system").prop("id", $(".control-box").length+"-control-box")
        $tmp.find("[name='template-system-name']").prop("name", $(".control-box").length+"-system_name");
        $tmp.find("[name='template-system.tag']").prop("name", $(".control-box").length+"-1-key");
        $tmp.find("[name='template-system.value']").prop("name", $(".control-box").length+"-1-value");
        console.log($tmp.html());
        $("#big-box").append($($tmp.html()));
    },

    addtag: function(){
        var $tmp = $("#tag_template").clone();
        var $target = $(this).parent().parent().parent();
        var $count = $target.attr("id").substring(0, $target.attr("id").length-11);
        $tmp.find("[name='template-tag.tag']").prop("name", $count+($target.children("#content").length+1)+"-key");
        $tmp.find("[name='template-tag.value']").prop("name", $count+($target.children("#content").length+1)+"-value");
        $target.append($($tmp.html()));
    },

    hide: function(){
        $(this).hide();
    }
}