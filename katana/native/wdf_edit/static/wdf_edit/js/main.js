$(document).ready(function(){

    // $.get("json", function(data, status){
    //     console.log(JSON.stringify(data, null, 2));
    // });

    $("#add").click(function(){
        console.log($("#system_template").html());
        $("#big-box").append($($("#system_template").html()));
    });

    $(".toggle").click(function(){
        $(this).parent().parent().children(".row").toggle();
    });

    $("#submit").click(function(){
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
    });

});