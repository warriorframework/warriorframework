"""
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

# -*- coding: utf-8 -*-
#from __future__ import unicode_literals


from native.settings.settings import Settings
# Create your views here.

from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.template.context_processors import csrf
import os, sys, glob, copy 
from collections import OrderedDict
from django.http import HttpResponse, JsonResponse
from django.template import loader, RequestContext
from xml.sax.saxutils import escape, unescape

from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.template import Library

import json
#from katana.utils.navigator_util import get_dir_tree_json
import xmltodict
from utils.navigator_util import Navigator


def old_index(request):
    return render(request, 'settings/index.html', {"data": controls.get_location()})

## MUST MOVE TO CLASS !!!!
## List all your projects ...
##
def index(request):
	navigator = Navigator();
	path_to_config = navigator.get_katana_dir() + os.sep + "config.json"
	config = json.loads(open(path_to_config).read())
	fpath = config['projdir']
	template = loader.get_template("./listAllProjects.html")
	files = glob.glob(fpath+"*/*.xml")

	print fpath

	#tt = { 'text': 'Projects', "icon" : "jstree-file",  
	#		'state': { 'opened': True },
	#		'children' : [] }

	#for fn in files: 
	#		item = { "text": fn, "icon" : "jstree-file", 
	#			"li_attr" : { 'data-path': fn} , 
	#			}
	#		tt['children'].append(item);


	tt = navigator.get_dir_tree_json(fpath)
	tt['state']= { 'opened': True };
	print tt
	context = { 
		'title' : 'List of Projects',	
		'docSpec': 'projectSpec',
		'treejs'  : tt, 
		'listOfFiles': files	
	}
	context.update(csrf(request))
	return HttpResponse(template.render(context, request))


## MUST MOVE TO CLASS !!!!
## List all your project as editable UI.
##
def editProject(request):
	"""
	Set up JSON object for editing a project file. 
	"""
	navigator = Navigator();
	path_to_config = navigator.get_katana_dir() + os.sep + "config.json"
	config = json.loads(open(path_to_config).read())
	fpath = config['projdir']

	template = loader.get_template("./editProject.html")
	filename = request.GET.get('fname','NEW')

	
	# Create Mandatory empty object.
	xml_r = {} ; 
	xml_r["Project"] = {}
	xml_r["Project"]["Details"] = {}
	xml_r["Project"]["Details"]["Name"] = "" # ""
	xml_r["Project"]["Details"]["Title"] = "" #OrderedDict([('$', '')])
	xml_r["Project"]["Details"]["Category"] = "" #OrderedDict([('$', '')])
	xml_r["Project"]["Details"]["State"] = "" #OrderedDict([('$', 'New')])
	xml_r["Project"]["Details"]["Date"] = "" #OrderedDict([('$', '')])
	xml_r["Project"]["Details"]["Time"] = "" #OrderedDict([('$', '')])
	xml_r["Project"]["Details"]["Datatype"] = "" #OrderedDict([('$', '')])
	xml_r["Project"]["Details"]["Engineer"] = "" #OrderedDict([('$', '')])
	xml_r["Project"]["Details"]["default_onError"] = "" #OrderedDict([('$', '')])
	xml_r["Project"]["Testsuites"] = []
	xml_r['Project']['filename'] = "" #OrderedDict([('$', filename)]);

	if filename != 'NEW':
		xlines = open(filename.strip()).read()
		#xml_d = bf.data(fromstring(xlines)); #
		xml_d = xmltodict.parse(xlines);

		# Map the input to the response collector
		for xstr in ["Name", "Title", "Category", "Date", "Time", "Engineer", \
			"Datatype", "default_onError"]:
			try:
				xml_r["Project"]["Details"][xstr]= xml_d["Project"]["Details"][xstr];
			except: 
				pass

		try:
			xml_r['Project']['Testsuites'] = copy.copy(xml_d['Project']['Testsuites']);
		except:
			xml_r["Project"]["Testsuites"] = []
	else:
		filename = path_to_config + os.sep + "new.xml"

 
	context = { 
		'savefilename': os.path.split(filename)[1], 
		'savefilepath': fpath,
		'fullpathname': filename, 
		'myfile': filename,
		'docSpec': 'projectSpec',
		'projectName': xml_r["Project"]["Details"]["Name"],
		'projectTitle': xml_r["Project"]["Details"]["Title"],
		'projectState': xml_r["Project"]["Details"]["State"],
		'projectEngineer': xml_r["Project"]["Details"]["Engineer"],
		'projectCategory': xml_r["Project"]["Details"]["Category"],
		'projectDate': xml_r["Project"]["Details"]["Date"],
		'projectTime': xml_r["Project"]["Details"]["Time"],
		'projectdefault_onError': xml_r["Project"]["Details"]["default_onError"],
		'fulljson': xml_r['Project']
		}
	# 
	# I have to add json objects for every test suite.
	# 
	return HttpResponse(template.render(context, request))


import HTMLParser



def getProjectDataBack(request):
	print "Got something back in request";
	navigator = Navigator();
	path_to_config = navigator.get_katana_dir() + os.sep + "config.json"
	config = json.loads(open(path_to_config).read())
	fpath = config['projdir']
	fname = request.POST.get(u'filetosave')
	ijs = request.POST.get(u'json')  # This is a json string 
	print ijs;
	#print "--------------TREE----------------"
	if fname.find(".xml") < 2: fname = fname + ".xml"

	#fd = open(fpath + os.sep + fname+ ".json",'w');
	#fd.write(ijs);
	#fd.close();
 	
	xml = xmltodict.unparse(json.loads(ijs), pretty=True)
	print "save to ", fpath + os.sep + fname 
	fd = open(fpath + os.sep + fname,'w');
	fd.write(xml);
	fd.close();
	return redirect(request.META['HTTP_REFERER'])
