
/**
 *   XMLParse - XML para objeto Javascript
 *   -------------------------------------
 * @author: Cau Guanabara <caugb@ibest.com.br>
 * @date: 05-2006
 */


// --- parse XML to the objects list
function XMLParse(xml) {
this.originalText = (xml || '');
this.xmlText = '';
this.root = null;
this.rootName = '';
  
	this.getRootName = function() {
	/\/([a-z_\-\:]+)>\s*$/.test(this.originalText);
	return this.rootName = RegExp.$1;
	};
	
  this.prepare = function(xml) {
	var xmltext = xml;
	  if(new RegExp('<\\/'+this.rootName+'>\\s*$').test(xmltext)) 
		  xmltext = xmltext.replace(new RegExp('^[^?]*(<'+this.rootName+'[^?]*<\\/'+
																this.rootName+'>)\\s*$'),'$1');
	xmltext = xmltext.replace(/\s*(<[^>]+>)\s*/g,'$1');
	xmltext = xmltext.replace(/<[^>]*[\n\r][^>]*>/g, 
		                        function(s) { 
														return s.replace(/[\r\n]{1,2}/g,'\\n').replace(/\s+/g,' ').replace(/ *>$/,'>');
														});
	xmltext = xmltext.replace(/<\!\[CDATA\[.+\]\]>|<\!\-\-[^>]*\-\->/g,
														function(s) { return s.replace(/[\r\n]{1,2}/g,'\\n'); });
	xmltext = this.prepareCDATA(xmltext);
	xmltext = this.prepareComment(xmltext);
	xmltext = xmltext.replace(/(<[^>]+>)/g,'\n$1\n').replace(/\n+/g,'\n').replace(/(^\s*|\s*$)/g,'');
  return xmltext;
	};
	
	this.prepareCDATA = function(xml) {
	var arr = xml.split(/<\!\[CDATA\[/); 
	var str = arr[0];
	  for(var i = 1; i < arr.length; i++) {
		var arr2 = arr[i].split(/\]\]>/);
	  str += '<![CDATA['+ASCIIEncode(arr2[0])+']]>';
		  if(arr2[1]) str += arr2[1];
		}
	return str;
	};
	
	this.prepareComment = function(xml) {
	var arr = xml.split(/<\!\-\-/); 
	var str = arr[0];
	  for(var i = 1; i < arr.length; i++) {
		var arr2 = arr[i].split(/\-\->/);
	  str += '<!--'+ASCIIEncode(arr2[0])+'-->';
		  if(arr2[1]) str += arr2[1];
		}
	return str;
	};
	
	this.xmlParser = function(txt, parentId) {
	txt || (txt = this.xmlText); 
	var arr = txt.split(/\n/), tagIsOpen = false, tagName = '', 
	    tagStr = '', tagobj = {}, frag = {}, comm = {}, cdt = {};
		for(var i = 0; i < arr.length; i++) {
		  if((this.isTagOpening(arr[i]) || this.isSingleTag(arr[i])) && !tagIsOpen) { 
			tagStr = '';
			tagIsOpen = true;
			tagName = this.getTagName(arr[i]);
			} 
			//-------------------
			if(tagIsOpen) tagStr += arr[i]+'\n';
			else if(!/<[^>]+>/.test(arr[i])) {
				if(frag[parentId] || false) ++frag[parentId];
				else frag[parentId] = 1;
			var newel = this.makeFragment(arr[i], parentId, frag[parentId]); 
			} else if(this.isCDATA(arr[i])) {
					if(typeof parentId == 'number') {
						if(cdt[parentId] || false) ++cdt[parentId];
						else cdt[parentId] = 1;
					this.makeCDATA(arr[i], parentId, cdt[parentId]);
					}
			} else if(this.isComment(arr[i])) {
				if(typeof parentId == 'number') { 
					if(comm[parentId] || false) ++comm[parentId];
					else comm[parentId] = 1;
				this.makeComment(arr[i], parentId, comm[parentId]);
				}
			} 
			//-------------------
			if(((this.isTagClosing(arr[i]) && tagIsOpen) || this.isSingleTag(arr[i])) 
			   && new RegExp('<\/?'+tagName).test(arr[i])) {
			tagIsOpen = false;
			tagobj = this.parseTag(tagStr);
			var newel = this.makeElement(tagStr, parentId); 
			  if(typeof(tagobj.innerHTML) != 'undefined') { 
					this.xmlParser(tagobj.innerHTML, newel.uid);
				}
			}
		}
	};
	
	this.makeCDATA = function(tag, pid, cdnum) {
	typeof pid == 'number' || (pid = -1);
	var cdat = new _cdata();
	cdat.text = tag.replace(/^<\!\[CDATA\[|\]\]>$/g,'');
	cdat.parentId = pid;
	cdat.name = '#'+cdnum;
	cdat.getParent().newChild(cdat.uid);
	};
	
	this.makeComment = function(tag, pid, cmnum) { 
	typeof pid == 'number' || (pid = -1);
	var cm = new _comment();
	cm.text = tag.replace(/^<\!\-\-|\-\->$/g,''); 
	cm.parentId = pid;
	  if(cmnum) cm.name = '!'+cmnum;
	  if(pid > -1) cm.getParent().newChild(cm.uid); //alert(cm.getParent().type);
	return cm;
	};
	
	this.makeFragment = function(tag, pid, fragnum) {
	var frag = new _fragment();
	frag.text = tag;
	frag.name = '$'+fragnum;
	frag.parentId = pid;
	frag.getParent().newChild(frag.uid);
	};
	
	this.makeElement = function(tag, pid) {
	var obj = this.parseTag(tag); 
	var elem = new _element();
	elem.tagName = obj.name;
	  if(obj.properties.$ || false) elem.innerText = obj.properties.$;
	  if(obj.innerHTML || false) elem.innerHTML = obj.innerHTML;
	  if(typeof pid == 'number') {
		elem.parentId = pid;
		elem.getParent().newChild(elem.uid);
		} 
		for(var i in obj.properties) {
			if(!(elem.properties || false)) elem.properties = {};
		elem.properties[i] = obj.properties[i];
		}
	return elem;
	};
	
	this.parseTag = function(tag) {
		if(/^(<([a-z0-9\:_\-]+)\s*([^>]*)?>)/.test(tag)) {
		var ret = { 'name': RegExp.$2, 'properties': (this.tagProperties(RegExp.$1) || {}) };
		  if(this.haveChildren(tag)) ret.innerHTML = this.getTagContents(tag);
			else if(this.getTagContents(tag) != '') ret['properties']['$'] = this.getTagContents(tag);
		return ret;
		}
	return {};
	};
	
	this.tagProperties = function(tag) {
	var ret = null;
		if(/^<[a-z0-9:-_]+\s+([^>]+)>$/.test(tag)) {
		ret = {};
		var props = RegExp.$1;
		 while(/([a-z0-9:-_]+)\s*=\s*\"([^\"]+)\"\s*/.test(props)) {
			var name = RegExp.$1, value = RegExp.$2; 
			 if(/^xmlns/.test(name)) {
				 if(typeof(ret['@xmlns']) != 'object') ret['@xmlns'] = {};
				 if(name == 'xmlns') ret['@xmlns']['$'] = value;
				 else if(/xmlns\:([a-z0-9]+)/.test(name)) ret['@xmlns'][RegExp.$1] = value;
			 } else ret['@'+name] = value;
		 props = props.replace(/[a-z0-9:-_]+\s*=\s*\"[^\"]+\"\s*/,'');
		 }
		} 
	return ret;
	};
	
	this.getTagContents = function(tag) { 
	var arr = tag.split(/\n/);
	arr.shift(); arr.pop();
	return arr.join('\n');
	};
  
	this.getTagName = function(tag) { return tag.replace(/^<\/?([\w:\-]+)\s*([^>]*)?( \/)?>$/,'$1'); };
	this.haveChildren = function(tag) { return (/<[^>]+>/.test(this.getTagContents(tag))); };
	this.isTagOpening = function(line) { return (/^<([\w:\-]+)\s*([^>]*)?[^\/]>$/.test(line)); };
	this.isTagClosing = function(line) { return (/^<\/([\w:\-]+)\s*>$/.test(line)); };
	this.isSingleTag = function(line) { return (/^<([\w:\-]+)\s*([^>]*)?\s*\/>$/.test(line)); };
	this.isComment = function(line) { return (/^<\!\-\-.+\-\->$/.test(line)); };
	this.isCDATA = function(line) { return (/^<\!\[CDATA\[.+\]\]>$/.test(line)); };
	this.isPI = function(line) { return (/^<\?.+\?>$/.test(line)); };
	
	this.parseXML = function(xml) {
		if(!/<[^>]+>/.test(xml)) alert('O valor enviado não parece ser um XML válido.\n'+
																	 'Possivelmente haverá erros...');
	_elementsCounter = 0;
	_elementsIndex = {};
	this.originalText = xml;
	this.getRootName();
	this.xmlText = this.prepare(xml); 
	this.xmlParser();
	this.root = _elementsIndex;
	return _elementsIndex;
	};
	
  if(xml) this.parseXML(xml);
}

// --- support 
var _elementsCounter = 0, _elementsIndex = {}; 

function _element() { 
this.uid = _elementsCounter++;
_elementsIndex[this.uid] = this;
this.parentId = -1;
this.type = 'element';
this.childrenIds = [];
	this.newChild = function(childId) { this.childrenIds.push(childId); };
	this.getParent = function() { 
		if(this.parentId > -1) return _elementsIndex[this.parentId]; 
	};
}

function _fragment() { this.uid = _elementsCounter++;
_elementsIndex[this.uid] = this;
this.parentId = -1;
this.type = 'fragment';
	this.getParent = function() { 
	return _elementsIndex[this.parentId]; 
	};
}

function _comment() { this.uid = _elementsCounter++;
_elementsIndex[this.uid] = this;
this.parentId = -1;
this.type = 'comment';
	this.getParent = function() { 
	return this.parentId > -1 ? _elementsIndex[this.parentId] : null; 
	};
}

function _cdata() { this.uid = _elementsCounter++;
_elementsIndex[this.uid] = this;
this.parentId = -1;
this.type = 'cdata';
 this.getParent = function() { return _elementsIndex[this.parentId]; };
}

function quote(txt) {
return txt.replace(/([\"\'\[\]\{\}\-\!\\])/g,'\\'+'$1');
}

function ASCIIEncode(s) {
var l = s.length, cooked = "";
	for (var i = 0; i < l; i++) {
		switch (s.charAt(i)) {
			case "'": cooked += "&apos;"; break;
			case '<': cooked += "&lt;"; break;
			case '>': cooked += "&gt;"; break;
			case '&': cooked += "&amp;"; break;
			case '"': cooked += "&quot;"; break;
			default:  cooked += s.charAt(i); 
		}
	}	
return cooked.replace(/[\r\n]{1,2}/g,'\\n');
}

function ASCIIDecode(s) {
s = s.replace(/&apos;/g,"'").replace(/&quot;/g,'"');
s = s.replace(/&lt;/g,'<').replace(/&gt;/g,'>');
return s.replace(/&amp;/g,'&').replace(/\\n/g,'\n');
}

