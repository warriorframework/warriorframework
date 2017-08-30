
/**
 *   json_xml - tradução XML <=> JSON
 *   --------------------------------
 * @author: Cau Guanabara <caugb@ibest.com.br>
 * @date: 05-2006
 */

// --- texto XML <=> objeto JSON
function json_xml() {
this.XMLString = '';
this.JSONObject = '';

// --- objeto JSON para texto XML
	this.toXML = function(jsobj, enc, vers) {
  this.XMLString = ''; 
	  for(var i in jsobj) {
		this.XMLString += this.makeTag(i, jsobj[i]).replace(/></g,'>\n<');
		break;
		}
		if(this.XMLString != '')
			this.XMLString = '<?xml version="'+(vers ? vers : '1.0')+'" encoding="'+
											 (enc ? enc : 'iso-8859-1')+'"?>\n'+this.XMLString; 
	return this.XMLString;
	};
	
	this.makeTag = function(name,obj) {
	var ret = '<'+name, closing = '</'+name+'>\n', innerHTML = '';
		for(var j in obj) { 
			if(/^@(.+)$/.test(j) && j != '@xmlns') { // namespace
			ret += ' '+RegExp.$1+'="'+obj[j]+'"';
			} else if(j == '$') { // innerText
			innerHTML += obj[j];
			} else if(/^\$\d+$/.test(j)) { // fragmento
			innerHTML = innerHTML.replace(/\n*$/,'')+'\n'+obj[j]+'\n';
			} else if(/^\!\d+$/.test(j)) { // comentario
			innerHTML = innerHTML.replace(/\n*$/,'')+'\n<!-- '+obj[j].replace(/\\n/g,'\n')+' -->\n';
			} else if(/^\#\d+$/.test(j)) { // CDATA
			innerHTML = innerHTML.replace(/\n*$/,'')+'\n<![CDATA['+obj[j]+']]>\n';
			} else if(_typeof(obj[j]) == 'object') { // tag
				if(j == '@xmlns') {
					for(var z in obj[j]) {
						if(z == '$') ret += ' xmlns="'+obj[j][z]+'"';
						else ret += ' xmlns:'+z+'="'+obj[j][z]+'"';
					}
				} else innerHTML += this.makeTag(j, obj[j]);
			} else if(_typeof(obj[j]) == 'array') { // tags iguais em sequencia
				for(var i = 0; i < obj[j].length; i++) innerHTML += this.makeTag(j, obj[j][i]);
			}
		}
	ret += innerHTML != '' ? '>'+innerHTML+''+closing : ' />\n';
	return ret;
	};

// --- texto XML para objeto JSON
	this.toJSON = function(xml) {
	  if(typeof(XMLParse || false) == 'boolean') {
		alert( 'O arquivo "xmlparser.js" não foi encontrado.\n'+
					 'As funções de tradução só estarão disponíveis se '+
					 '"xmlparser.js" for incluído corretamente...' );
		return null;
		} else if(/<[^>]+>/.test(xml)) this.xparser = new XMLParse(xml); 
		else return null;
	return this.JSONObject = this.addToJSONObj({}, this.xparser.root[0]);
	};
	
	this.addToJSONObj = function(jobj, eobj) {
	var thisel = {};
	  if(count(eobj.properties) > 0) 
		  for(var i in eobj.properties) thisel[i] = eobj.properties[i];
		if((eobj.childrenIds || false) && eobj.childrenIds.length > 0) 
		  for(var i = 0; i < eobj.childrenIds.length; i++) 
				thisel = this.addToJSONObj(thisel,this.xparser.root[eobj.childrenIds[i]]);
		if(eobj.type == 'fragment') jobj[eobj.name] = eobj.text;
		if(eobj.type == 'comment' || eobj.type == 'cdata') jobj[eobj.name] = ASCIIDecode(eobj.text);
		if(_typeof(jobj[eobj.tagName]) == 'object') jobj[eobj.tagName] = [jobj[eobj.tagName]];
		if(_typeof(jobj[eobj.tagName]) == 'array') jobj[eobj.tagName].push(thisel);
		else if(!jobj[eobj.tagName] && !/fragment|comment|cdata/.test(eobj.type)) jobj[eobj.tagName] = thisel;
	return jobj;
	};
}

// --- support
function count(obj) { var cnt = 0; for(var i in obj) cnt++; return cnt; }
