# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.


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

navigator = Navigator();
path_to_src_python_file = navigator.get_katana_dir() + os.sep + "config.json"


def index(request):
	path_to_config_file = navigator.get_katana_dir() + os.sep + "config.json"   
	x= json.loads(open(path_to_config_file).read());
	path_to_files = x['pythonsrcdir'];
	context = { 
		'title' : 'Editor',	
 		'pythonsrcdir': path_to_files + os.sep + "Actions/",
		'savesubdir': path_to_files
	}
	return render(request, './index.html', context)

def getFileData(request):
	path_to_config_file = navigator.get_katana_dir() + os.sep + "config.json"   
	x= json.loads(open(path_to_config_file).read());
	path_to_files = x['pythonsrcdir'];
	filename = request.GET.get('filename');
	try:
		tdata = open(filename).read();
	except:
		tdata = "";

	extn  = str(os.path.splitext(filename)[1]);
	mode = ""
	try:
		extn = extn.lower();
	except:
		pass
	if extn == '.py': mode = "python";
	# if extn == '.pl': mode = "perl";
	# if extn == '.xml': mode = "xml";
	# if extn == '.js': mode = "js";
	print "Setting mode ", mode, extn

	responseBack = { 'fulltext': tdata , 'fname': filename, 'mode': mode }
	return JsonResponse(responseBack)


def editFile(request):
	return getFileData(request);
	
	#return JsonResponse(responseBack)


def saveFile(request):
	print "Got something back in request";
	navigator = Navigator();
	path_to_config = navigator.get_katana_dir() + os.sep + "config.json"
	config = json.loads(open(path_to_config).read())
	fpath = config['pythonsrcdir']
	fname = request.POST.get(u'filetosave');
	tdata = request.POST.get(u'texttosave');
	fd = open(fpath + os.sep + fname,'w');
	fd.write(tdata);
	fd.close();
	return redirect(request.META['HTTP_REFERER'])