var blk_duck = {
    build_tree: function(){
    	$.ajax({
            url: "blackduck/gettree",
            type: "GET",
            dataType: "json",
            success: function(data){
                if (! data.hasOwnProperty("children")) {
                    alert("local system directory is not set up, please add directory in Settings");
                    data["text"] = "local system directory is not set up, please add directory in Settings"
                }
                katana.$activeTab.find("#jstree").jstree({'core':{'data':[data]}});
                katana.$activeTab.find('#jstree').jstree().hide_dots();
            }
        });
    },
}