# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json, xmltodict, os, copy
from utils.navigator_util import Navigator
from utils.json_utils import read_json_data
from collections import OrderedDict
from django.template.defaulttags import register

from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
def index(request):
    """
        Read an xml file and return the editor page with xml content in it
    """
    # Check to open new/existing file
    config = read_json_data(Navigator().get_katana_dir() + os.sep + "config.json")
    wdfdir = config["idfdir"]

    if request.method == "POST":
        data = request.POST
        filepath = data["path"]
        filepath = filepath.replace(wdfdir, "")
        filepath = filepath[1:] if filepath.startswith(os.sep) else filepath
        if os.path.isfile(data["path"]):
            data = xmltodict.parse(open(data["path"]).read())
        else:
            return render(request, 'wdf_edit/failure.html')
    else:
        sample_data = {"system": [{"@name": "Example system", "Example key": "Example value"}]}
        ref_dict = copy.deepcopy(sample_data)
        return render(request, 'wdf_edit/index.html', {"data": sample_data, "data_read": ref_dict, "filepath": ""})

    # xml should only has 1 root
    root = data.keys()[0]

    # handle attributes
    if type(data[root]["system"]) != list:
        data[root]["system"] = [data[root]["system"]]
    for sys in data[root]["system"]:
        if "subsystem" in sys:
            if type(sys["subsystem"]) == list:
                for subsys in sys["subsystem"]:
                    for k, v in subsys.items():
                        subsys[k] = "" if subsys[k] is None else subsys[k]
                        if k.startswith("@") and k != "@name" and k != "@default":
                            subsys[k[1:]] = v
                            del subsys[k]
                        elif k == "#text":
                            del subsys[k]
            else:
                subsys = sys["subsystem"]
                for k, v in sys["subsystem"].items():
                    subsys[k] = "" if subsys[k] is None else subsys[k]
                    if k.startswith("@") and k != "@name" and k != "@default":
                        subsys[k[1:]] = v
                        del subsys[k]
                    elif k == "#text":
                        del subsys[k]
        else:
            for k, v in sys.items():
                sys[k] = "" if sys[k] is None else sys[k]
                if k.startswith("@") and k != "@name" and k != "@default":
                    sys[k[1:]] = v
                    del sys[k]
                elif k == "#text":
                    del sys[k]
    print(json.dumps(data[root], indent=4))

    ref_dict = copy.deepcopy(data[root])
    return render(request, 'wdf_edit/index.html', {"data": data[root], "data_read": ref_dict, "filepath": filepath, "desc":data[root].get("description", "")})

def get_jstree_dir(request):
    """
        Prepare the json for jstree to use
    """
    config = read_json_data(Navigator().get_katana_dir() + os.sep + "config.json")
    data = Navigator().get_dir_tree_json(config["idfdir"])
    data["text"] = config["idfdir"]
    # print json.dumps(data, indent=4)
    return JsonResponse(data)

def file_list(request):
    return render(request, 'wdf_edit/file_list.html', {})

@register.filter
def remove_name(data):
    """
        remove @name and @default key from dict
    """
    if type(data) == dict or type(data) == OrderedDict:
        if "@name" in data:
            del data["@name"]
        if "@default" in data:
            del data["@default"]
    return data

# Separation for functions used before/after saving the edited xml

def combine_values(data):
    """
        Take a list of dict and combine them into one dict
    """
    result = OrderedDict()
    for pair in data:
        result.update(pair)
    return result

def build_xml_dict(data):
    """
        Build a list of systems that can be unparsed into xmltodict format xml file
    """
    import pprint
    pprint.pprint(data)

    result = []
    for sys in data:
        current_sys = OrderedDict()
        current_sys["@name"] = sys["@name"]
        if "values" in sys:
            current_sys.update(combine_values(sys["values"]))
        elif "subsystem" in sys and isinstance(sys["subsystem"], dict):
            current_sys["subsystem"] = OrderedDict({"@name": sys["subsystem"]["@name"]})
            current_sys["subsystem"].update(combine_values(sys["subsystem"]["values"]))
        elif "subsystem" in sys and isinstance(sys["subsystem"], list):
            current_sys["subsystem"] = []
            for subsys in sys["subsystem"]:
                current_subsys = OrderedDict({"@name": subsys["@name"]})
                current_subsys.update(combine_values(subsys["values"]))
                current_sys["subsystem"].append(current_subsys)
        result.append(current_sys) 
    return result

def on_post(request):
    """
        Main function that handles a post request with edited xml data
    """
    data = json.loads(request.body)
    filepath = data.get("filepath", None)
    desc = data.get("description", "")
    systems = build_xml_dict(data["systems"])
    result = {"credentials":OrderedDict()}
    if desc:
        result["credentials"]["description"] = desc
    result["credentials"]["system"] = systems

    from xml.dom.minidom import parseString as miniparse
    print miniparse(xmltodict.unparse(result)).toprettyxml()

    config = read_json_data(Navigator().get_katana_dir() + os.sep + "config.json")
    wdfdir = config["idfdir"]
    filepath = os.path.join(wdfdir, filepath)
    print "Filepath:", filepath
    # f = open(filepath, "w")
    # f.write(miniparse(xmltodict.unparse(result)).toprettyxml())
    # return render(request, 'wdf_edit/result.html', {"data": json.dumps(request.POST, indent=4)})
    return render(request, 'wdf_edit/file_list.html', {})