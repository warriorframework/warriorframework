
function create_jstree_search(tag_for_tree, tag_for_search_box , sdata) {
  var jdata = { 'core' : { 'data' : sdata },
    					"plugins" : [ "sort" , "search"],
    					}; 
   katana.$activeTab.find(tag_for_tree).jstree(jdata);
  var to = false;
  katana.$activeTab.find(tag_for_search_box).keyup(function () {

    if(to) { clearTimeout(to); }
    to = setTimeout(function () {
      var v = katana.$activeTab.find(tag_for_search_box).val();
      katana.$activeTab.find(tag_for_tree).jstree(true).search(v);
    }, 250);
  });
};

function absFromPrefix(pathToBase, pathToFile) {
	// Converts an absolute path to one that is relative to pathToBase 
	// Input: 
	// 		
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

function jsUcfirst(string) 
{
      return string.toLowerCase();
}