
/**
 *   json - Javascript Object Notation
 *   ---------------------------------
 * @adaptation: Cau Guanabara <caugb@ibest.com.br>
 * @date: 05-2006
 *   
 *   Este script é uma adaptação do original distribuído no site json.org,
 *   em 'http://www.json.org/json.js'.
 *   O arquivo original adiciona novas funções a objetos e arrays, mas como
 *   em certas funcionalidades eu me baseio no estado dos objetos e arrays,
 *   isso me atrapalhou um pouco, pois ao criar 
       var obj = {};
 *   na verdade o resultado era:
       var obj = {'toJSONString': function() {...}};
 *   Resolvi transformando a função original em uma classe.
 *   --------------------------------------------------------------------------------
 *   Se o arquivo badgerfish estiver presente, a propriedade 'translate' do objeto 
 *   json() será uma instância do objeto json_xml(), que faz a tradução XML <=> JSON.
 *   Se não, ao chamar as funções de tradução, uma mensagem de erro será mostrada.
 */

function json() {
	try { this.translate = new json_xml(); } 
	catch(e) { 
	var fnc = function() { return 'O arquivo "badgerfish.js" não foi encontrado.\n'+
	                              'As funções de tradução só estarão disponíveis se '+
																'"badgerfish.js" for incluído corretamente...'; };
	this.translate = { 'toXML': fnc, 'toJSON': fnc };
	}

	this.JSONFromArray = function(arr) {
	var ret = [];
		for(var i = 0; i < arr.length; i++) ret.push(this.stringfy(arr[i]));
	return '[ '+ret.join(', ')+' ]';
	};
	
	this.JSONFromObject = function(obj) {
	var ret = [];
		for(var i in obj) ret.push(this.stringfy(i)+': '+this.stringfy(obj[i]));
		if(ret.length == 0 && !obj) return 'null';
	return '{ '+ret.join(', ')+' }';
	};
	
	this.parseJSONString = function(str) {
		if(/[^,:{}\[\]0-9.\-+Eaeflnr-u \n\r\t]/.test(str.replace(/"(\\.|[^"\\])*"/g, '')) == false)
			return new Function('return '+str.replace(/([^\\])\'/g,'$1\\\'')+';')();
	return null;
	};

	this.stringfy = function(val) {
	  switch(_typeof(val)) {
		  case "array": return this.JSONFromArray(val);
		  case "object": return this.JSONFromObject(val);
			case "function": 
				var ret = String(val).replace(/([^\\])(\'|\")/g,'$1\\\$2');
			  return ret.replace(/function anonymous\(/,'function(').replace(/\n/g,' ');
		  case "string": 
        if(/^[0-9]+$/.test(val)) return val;
				if(/["\\\x00-\x1f]/.test(val)) return '"'+val.replace(/([\x00-\x1f\\"])/g, rFunc)+'"';
			  else return '"'+val.replace(/\'/g,'\\\'')+'"';
		  default: return String(val);
		}
		function rFunc(a, b) {
		var tosub = { '\b': '\\b', '\t': '\\t', '\n': '\\n', '\f': '\\f', 
									'\r': '\\r', '"' : '\\"', '\\': '\\\\' }, subs = '';
			if(subs = (tosub[b] || false)) return subs;
		subs = b.charCodeAt();
		return '\\u00'+Math.floor(subs / 16).toString(16)+(subs % 16).toString(16);
		}
	};
}

// --- support
function _typeof(x) { 
	if(typeof(x) != 'object' && typeof(x) != 'function') return typeof x; 
	if(typeof(x) == 'object' && !x) return 'null';
_varToTest = x;
var isinst = function(objName) { return new Function('return (_varToTest instanceof '+objName+');')(); },
types = {'RegExp': 'regexp', 'Array': 'array', 'Date': 'date', 'Function': 'function'}, ret = 'object';
	for(var i in types) if(isinst(i)) ret = types[i];
return ret;
}
