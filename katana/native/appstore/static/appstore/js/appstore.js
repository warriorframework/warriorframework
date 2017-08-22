var appstore = {

    uninstallAnApp: function(){
        var $elem = $(this);
        var app_details = $elem.attr('app_details');
        $.ajax({
            headers: {
                'X-CSRFToken': appstore.getCookie('csrftoken')
            },
            type: 'POST',
            url: 'appstore/uninstall_an_app/',
            data: {"app_details": app_details},
        });
    },

    getCookie: function(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}