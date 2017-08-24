var appstore = {

    uninstallAnApp: function(){
        var $elem = $(this);
        var app_path = $elem.attr('app_path');
        var app_type = $elem.attr('app_type');
        $.ajax({
            headers: {
                'X-CSRFToken': appstore.getCookie('csrftoken')
            },
            type: 'POST',
            url: 'appstore/uninstall_an_app/',
            data: {"app_path": app_path, "app_type": app_type},
        }).done(function(data) {
            setTimeout(function(){location.reload();}, 1000);
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