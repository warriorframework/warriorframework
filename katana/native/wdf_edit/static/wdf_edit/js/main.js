$(document).ready(function(){
    var counter = 0;

    $.get("json", function(data, status){
        console.log(JSON.stringify(data, null, 2));
    });

    $("#add").click(function(){
        $("#main_row").append('<div class="col-sm-12"><input name=' + counter + ' value=""></input></div>');
        counter = counter + 1;
    });

    $(".toggle").click(function(){
        $(this).parent().toggle();
    });
});