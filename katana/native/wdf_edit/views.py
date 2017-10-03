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
        print data; 
        print request.body,request.method
        filepath = data["path"]
        filepath = filepath.replace(wdfdir, "")
        filepath = filepath[1:] if filepath.startswith(os.sep) else filepath
        data = xmltodict.parse(open(data["path"]).read())
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
                        if k.startswith("@") and k != "@name" and k != "@default":
                            subsys[k[1:]] = v
                            del subsys[k]
                        elif k == "#text":
                            del subsys[k]
            else:
                subsys = sys["subsystem"]
                for k, v in sys["subsystem"].items():
                    if k.startswith("@") and k != "@name" and k != "@default":
                        subsys[k[1:]] = v
                        del subsys[k]
                    elif k == "#text":
                        del subsys[k]
        else:
            for k, v in sys.items():
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

def raw_parser(data):
    """
        Read the html form data in systemId-subsystemId-tagId-childtagId format
        output a nested dict with 4 level
        the last level contains the tag and value inside a list
    """
    result = {}
    # handle description
    if "description" in data:
        result["description"] = data["description"]
    system_keys = [x for x in data.keys() if x.endswith("-system_name")]
    for name in system_keys:
        # Prepare all system to save data
        sys_name = name.replace("-system_name", "").split("-")[0]
        subsys_name = name.replace("-system_name", "").split("-")[1]
        if sys_name in result:
            result[sys_name][subsys_name] = {"system_name":data[name]}
        else:
            result[sys_name] = {subsys_name: {"system_name":data[name]}}

        # Put subsystem name into system if it exists
        current_sys = result[sys_name][subsys_name]
        if sys_name+"-"+subsys_name+"-subsystem_name" in data:
            current_sys.update({"subsystem_name":data[sys_name+"-"+subsys_name+"-subsystem_name"]})

        # Put default info into system and subsys
        if sys_name+"-"+subsys_name+"-default" in data:
            current_sys.update({"default": True})
        if sys_name+"-"+subsys_name+"-default-subsys" in data:
            current_sys.update({"default-subsys": True})

        tags_keys = [x for x in data.keys() if x.startswith(sys_name + "-" + subsys_name + "-") and x.endswith("key")]
        # Parse data
        for k in tags_keys:
            parsed_k = k.split("-")
            sys_name, subsys_name, tag_ind, child_tag_ind = parsed_k[:4]

            if tag_ind in current_sys:
                current_sys[tag_ind][child_tag_ind] = (data[k], data[k[:-4]+"-value"])
            else:
                current_sys[tag_ind] = {child_tag_ind: (data[k], data[k[:-4]+"-value"])}

    print json.dumps(result, indent=4)
    return result

def locate_system(data, name):
    """
        Find the index of system with specific name
    """
    for ind, sys in enumerate(data):
        if sys["@name"] == name:
            return ind
    return -1

def build_xml_dict(data):
    """
        Read in the nested dict from raw_parser
        output the dicttoxml format dict
    """
    result = []
    desc = ""
    # First half of this function is to build the system and subsystem tag in the result dict
    if "description" in data:
        desc = data.pop("description")
    sys_keys = [str(y) for y in sorted([int(x) for x in data.keys()])]
    for sys_key in sys_keys:
        sys = data[sys_key]
        subsys_keys = [str(y) for y in sorted([int(x) for x in sys.keys()])]
        for subsys_key in subsys_keys:
            subsys = sys[subsys_key]
            if "subsystem_name" not in subsys:
                # The system doesn't have subsystem
                result.append(OrderedDict())
                current_sys = result[-1]
                current_sys["@name"] = subsys["system_name"]
                if "default" in subsys:
                    current_sys["@default"] = "yes"
            else:
                # There is a subsystem inside the current system
                if locate_system(result, subsys["system_name"]) > -1:
                    # The system already exist in the temp result dict
                    if "subsystem" in result[locate_system(result, subsys["system_name"])]:
                        # There are other subsystems saved under this system
                        result[locate_system(result, subsys["system_name"])]["subsystem"].append(OrderedDict())
                    else:
                        result[locate_system(result, subsys["system_name"])]["subsystem"] = [OrderedDict()]
                    current_sys = result[locate_system(result, subsys["system_name"])]["subsystem"][-1]
                    current_sys["@name"] = subsys["subsystem_name"]
                    current_sys["subsystem"] = []
                else:
                    # The system doesn't exist in the temp result dict
                    result.append(OrderedDict({"@name": subsys["system_name"], "subsystem":[]}))
                    result[-1]["subsystem"].append(OrderedDict())
                    current_sys = result[-1]["subsystem"][-1]
                    current_sys["@name"] = subsys["subsystem_name"]
                if "default" in subsys:
                    result[locate_system(result, subsys["system_name"])]["@default"] = "yes"
                if "default-subsys" in subsys:
                    current_sys["@default"] = "yes"

    # Second half is to build all tags and values inside the current_sys
            # subsys is the raw data, contains all the tags and values in indices format
            # current_sys will fill with tags as keys and values
            tag_keys = [str(y) for y in sorted([int(x) for x in subsys.keys() if x.isdigit()])]
            for tag_key in tag_keys:
                if len(subsys[tag_key]) == 1:
                    # raw data doesn't have child tag
                    if subsys[tag_key]["1"][0] not in current_sys:
                        current_sys[subsys[tag_key]["1"][0]] = [subsys[tag_key]["1"][1]]
                    else:
                        current_sys[subsys[tag_key]["1"][0]].append(subsys[tag_key]["1"][1])
                else:
                    # raw data have child tag(s)
                    subtag_keys = [str(y) for y in sorted([int(x) for x in subsys[tag_key].keys() if x.isdigit()])]
                    # first subtag will be the tag name, which values are child tags
                    subtag_first = subsys[tag_key][subtag_keys[0]][0]
                    if subtag_first not in current_sys:
                        current_sys[subtag_first] = [OrderedDict()]
                    else:
                        current_sys[subtag_first].append(OrderedDict())

                    # point to the dict for the current tag, all childtags live in this dict
                    current_childtags = current_sys[subtag_first][-1]
                    # loop through the remaining child tags
                    for subtag_key in subtag_keys[1:]:
                        tmp_key = subsys[tag_key][subtag_key][0]
                        # check if tmp_key exists in the current_childtags
                        tmp_index = next((i for i, v in enumerate(current_childtags.keys()) if tmp_key in v), None)
                        if tmp_index is not None:
                            # current_childtags[tmp_index] is the dict that shared the same tag name
                            current_childtags[tmp_key].append(subsys[tag_key][subtag_key][1])
                        else:
                            current_childtags.update({tmp_key:[subsys[tag_key][subtag_key][1]]})

    print json.dumps(result, indent=4)
    return result, desc

def on_post(request):
    """
        Main function that handles a post request with edited xml data
    """
    data = request.POST
    filepath = data["filepath"]
    print json.dumps(data.items(), indent=4)
    data = raw_parser(data)
    data, desc = build_xml_dict(data)
    result = {"credentials":OrderedDict()}
    if desc:
        result["credentials"]["description"] = desc
    result["credentials"]["system"] = data

    from xml.dom.minidom import parseString as miniparse
    print miniparse(xmltodict.unparse(result)).toprettyxml()

    config = read_json_data(Navigator().get_katana_dir() + os.sep + "config.json")
    wdfdir = config["idfdir"]
    filepath = os.path.join(wdfdir, filepath)
    print "Filepath:", filepath
    f = open(filepath, "w")
    f.write(miniparse(xmltodict.unparse(result)).toprettyxml())
    # return render(request, 'wdf_edit/result.html', {"data": json.dumps(request.POST, indent=4)})
    return render(request, 'wdf_edit/file_list.html', {})