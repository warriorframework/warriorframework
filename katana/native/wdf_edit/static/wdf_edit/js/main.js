$(document).ready(function(){
    $("#save").click(function(){
        $.post("post",
            $("#main_info").html(),
            function() {
                alert($('#main_info').html());
            }
        )
    });
});