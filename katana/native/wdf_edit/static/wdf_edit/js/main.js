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
        console.log($("#system_template").html());
        $("#big-box").append($($("#system_template").html()));
    },

    addtag: function(){
        $(this).parent().parent().parent().append($($("#tag_template").html()));
    },
}