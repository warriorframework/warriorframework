var assembler = {
    init: function(){
        $currentPage = katana.$activeTab;
        $.ajax({
                headers: {
                    'X-CSRFToken': $currentPage.find('input[name="csrfmiddlewaretoken"]').attr('value')
                },
                type: 'POST',
                url: 'assembler/get_config_file/',
                data: {"filepath": false}
            }).done(function(data) {
                data
            });
    }
}