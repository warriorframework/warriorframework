 var kw_sequencer = {

    addKeyword: function(){
        $.ajax({
            url: "kw_sequencer/addkeyword",
            type: "GET",
            success: function(data){
                // set kw-sequencer-new div html with loaded url data
                katana.$activeTab.find(".new-keyword-div").html(data);
                // Disable 'Add new Keyword' button
                katana.$activeTab.find("#new-keyword-button").prop('disabled', true);
            }
        });
    },

    closeKeyword: function(){
        katana.$activeTab.find(".new-keyword-div").empty();
        katana.$activeTab.find("#new-keyword-button").prop('disabled', false);
    },

    saveKeyword: function(){
        //console.log("Keyword saved successfully");
        katana.$activeTab.find(".new-keyword-div").empty();
        katana.$activeTab.find("#new-keyword-button").prop('disabled', false);
    }


};
