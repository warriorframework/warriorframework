$(document).ready(function(){
    var counter = 0;

    $.get("json", function(data, status){
        // console.log(JSON.stringify(data, null, 2));
    });

    $("#add").click(function(){
        $("#big-box").append('<div class="col-sm-12"><input name=' + counter + ' value=""></input></div>');
        counter = counter + 1;
    });

    $(".toggle").click(function(){
        $(this).parent().parent().find(".row").toggle();
    });

    $("#submit").click(function(){
        var csrftoken = $("[name='csrfmiddlewaretoken']").val();

        $.ajax({
            url : "post",
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

    // $("#two-col").click(function(){
    //     // console.log($(".control-box").length);
    //     boxes = $(".control-box")
    //     for (i = 0; i < boxes.length; i++) {
    //         console.log(boxes[i]);

    //         if (i % 2 == 0) {
    //             boxes.eq(i).before('<div class="row"><div class="col-sm-6">');
    //             boxes.eq(i).after('</div>');
    //             // boxes.eq(i).html(function(i, origText){
    //             //     return '<div class="row"><div class="col-sm-6">' + origText + '</div>';
    //             // });
    //         } else {
    //             boxes.eq(i).before('<div class="col-sm-6">');
    //             boxes.eq(i).after('</div></div>');
    //             // boxes.eq(i).html(function(i, origText){
    //             //     return '<div class="col-sm-6">' + origText + '</div></div>';
    //             // });
    //         }
    //     }
    //     if (boxes.length % 2) {
    //         boxes.eq(boxes.length-1).after('</div>');
    //         // boxes.eq(boxes.length-1).html(function(i, origText){
    //         //     return origText + '</div>';
    //         // });
    //     }

    // });
});