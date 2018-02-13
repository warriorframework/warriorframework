var wappstore = {

    initFunction: function(){
        var $currentPage = katana.$activeTab;

        var $changingIcons = $currentPage.find('#changing-icons');

        var $iconHtml = ['<i class="fa fa-hourglass-start fa-5x blue" style="line-height:inherit!important;"></i>',
                        '<i class="fa fa-hourglass-half fa-5x blue" style="line-height:inherit!important;"></i>',
                        '<i class="fa fa-hourglass-end fa-5x blue" style="line-height:inherit!important;"></i>']

        console.log($changingIcons);

        for(var i=0; i< $iconHtml.length; i++){
            $changingIcons.html($iconHtml[i]);

        }
    }
}