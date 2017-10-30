
function absFromPrefix(pathToBase, pathToFile) {
	// Converts an absolute path to one that is relative to pathToBase 
	// Input: 
	// 		
	if (!pathToBase || !pathToFile) return "";
	var bf = pathToBase.split('/');
	var rf = pathToFile.split('/');
	var nrf = pathToFile.split('/');
	console.log("Removing", nrf, bf);
	
	for (var i=0;i< rf.length; i++) {
		if (rf[i] == "..")  { 
			bf.pop();
			nrf.splice(0,1);
			console.log("Removing", nrf, bf);
	
		} else {
			break;
		}
	}
	return bf.join('/') + '/' + nrf.join('/');
}

function prefixFromAbs(pathToBase, pathToFile) {
	if (!pathToBase || !pathToFile) return "";
	
	var stack = []; 
    var upem  = [];
	var bf = pathToBase.split('/');
	var rf = pathToFile.split('/');
	for (var i=0;i< rf.length; i++) {
		if (rf[i] == bf[i]) { 
			stack.push(bf[i]);
		} else {
			break;
		}
	}
	var tlen = bf.length - stack.length; 
	var blen = stack.length;
	console.log("bf=",bf);
	console.log("rf=",rf);
	console.log("prefixFromAbs", rf, tlen, blen, stack);
    for (var k=0;k < tlen; k++) {
		upem.push("..");
	}
	var tail = rf.splice(blen,rf.length);
	console.log('tail=', tail);
	return upem.join("/") + "/" +   tail.join('/');
}


var wsedit = { 

	myCodeEdit: null,
	//location.hash : "#cobalt",


 	init: function() { 
 		//console.log("Start....",	katana.$activeTab.find("#wsedit-file-menu"));
 		//extraKeys: {"Ctrl-Q": function(cm){ wsedit.myCodeEdit.foldCode(wsedit.myCodeEdit.getCursor()); }},
    		
 		wsedit.myCodeEdit = CodeMirror.fromTextArea(katana.$activeTab.find('#wsedit-scrollable-source-text')[0],
 			{ value: "",
 			foldGutter: true,
 			extraKeys: {"Ctrl-Q": function(cm){ console.log(cm); cm.foldCode(cm.getCursor()); }},
    
    		gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"],
 		} );
		console.log("Started....",wsedit.myCodeEdit );
 		

 	},

	openFileFromServer: function() {

			var tag = '#wsedit-filename';
			var callback_on_accept = function(selectedValue) { 
	  		//console.log(selectedValue);
	  		var savefilepath = katana.$activeTab.find('#wsedit-savesubdir').text();
	  		console.log("File path ==", savefilepath);
	  		var nf = prefixFromAbs(savefilepath, selectedValue);
	  		katana.$activeTab.find(tag).val(selectedValue);
	  		katana.$activeTab.find(tag).attr("fullpath", selectedValue);
			console.log("fullpath ",selectedValue );
			// Now get the file from the server and display the data. ..

			jQuery.getJSON("./wsedit/getFileData/?filename="+selectedValue).done(function(data) {
				var sdata = data['fulltext'];
				wsedit.sdata = data;
				// katana.$activeTab.find('#wsedit-scrollable-source-text').show();
				// katana.$activeTab.find('#wsedit-scrollable-source-text').html(sdata);
				console.log("received", data['mode']);
				
				// if (wsedit.myCodeEdit == null) {

				// 	wsedit.myCodeEdit = CodeMirror.fromTextArea(katana.$activeTab.find('#wsedit-scrollable-source-text')[0],
				//  	{ value: sdata } );

				// 	wsedit.myCodeEdit.on('change', wsedit.textModifiedCB ) ;


				// } else { 
				// 	wsedit.myCodeEdit.setValue(sdata);
				// }
				wsedit.myCodeEdit.setValue(sdata);
				wsedit.myCodeEdit.setOption("lineNumbers", true);
				wsedit.myCodeEdit.setOption("lineWrapping", true);
				wsedit.myCodeEdit.setOption("mode", data['mode']);
				wsedit.myCodeEdit.setOption("min-height","100%");
				wsedit.myCodeEdit.setOption("matchBrackets", true);
				wsedit.myCodeEdit.setOption("styleActiveLine", true);
				katana.$activeTab.find("#wsedit-saveme-btn").html("");
				//wsedit.myCodeEdit.setOption("extraKeys",{"Ctrl-Q": function(cm){ cm.foldCode(cm.getCursor()); }});
 				wsedit.myCodeEdit.setOption("foldGutter", true);
    			//wsedit.myCodeEdit.setOption("gutters": ["CodeMirror-linenumbers", "CodeMirror-foldgutter"]);

			});

			

			};
	  var callback_on_dismiss =  function(){ 
	  		console.log("Dismissed");
	 };
	 var pdir = katana.$activeTab.find("#wsedit-pythonsrcdir")[0].innerText; 
	 console.log("Pdir = ", pdir);
	 katana.fileExplorerAPI.openFileExplorer("Select a file", pdir , $("[name='csrfmiddlewaretoken']").val(), false, callback_on_accept, callback_on_dismiss,".py");
	  
	},

	
	selectTheme: function() {
		var theme = katana.$activeTab.find('#wsedit-select').val();
		wsedit.myCodeEdit.setOption("theme", theme);

	},

	onThemeChange: function()  { 
		wsedit.selectTheme();
	},

	toggleCodeFold: function() { 
		wsedit.myCodeEdit.foldCode(wsedit.myCodeEdit.getCursor());
	},

	toggleLineWrap: function() {
		var wrap = !wsedit.myCodeEdit.getOption("lineWrapping");
		wsedit.myCodeEdit.setOption("lineWrapping", wrap);
	},
	toggleLineNumber: function() {
		var numbers = !wsedit.myCodeEdit.getOption("lineNumbers");
		wsedit.myCodeEdit.setOption("lineNumbers", numbers);
	},

	textModifiedCB: function(how, where) {
		console.log("...modified...");
		katana.$activeTab.find("#wsedit-saveme-btn").html("(modified)");
	},

	saveFileToServer: function() {
	  var url = "./wsedit/saveFile";
		var csrftoken = katana.$activeTab.find("[name='csrfmiddlewaretoken']").val();
		//console.log("sending case 2");
		$.ajaxSetup({
				function(xhr, settings) {
				xhr.setRequestHeader("X-CSRFToken", csrftoken)
			}
		});
		var xfname = katana.$activeTab.find('#wsedit-filename').val();	
		var xstr = wsedit.myCodeEdit.getValue();
		var topNode  = { 'Filename' : katana.$activeTab.find('#wsedit-filename').val(),
				'Text': xstr }; 
		console.log("jsontosave", topNode);
		$.ajax({
		url : url,
		type: "POST",
		data : { 
			'jsontosave': JSON.stringify(topNode),	
			'texttosave': xstr,
			'filetosave': katana.$activeTab.find('#wsedit-filename').val(),
			},
		headers: {'X-CSRFToken':csrftoken},
		success: function( data ){
			// The following causes an exception
			//xdata = { 'heading': "Sent", 'text' : "sent the file... "+data}
			//katana.openAlert(xdata);
			alert("Saved...");
	
		},
	});
	},


};
