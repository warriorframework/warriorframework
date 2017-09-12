# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json, xmltodict, os
from utils.navigator_util import Navigator
from utils.json_utils import read_json_data
from collections import OrderedDict

from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
def index(request):
    if request.method == "POST":
        data = request.POST
        filepath = data["path"]
        data = xmltodict.parse(open(data["path"]).read())
    else:
        return render(request, 'wdf_edit/index.html', {"data": {"system": []}, "filepath": ""})

    root = data.keys()[0]

    if type(data[root]["system"]) != list:
        data[root]["system"] = [data[root]["system"]]
    for sys in data[root]["system"]:
        if "subsystem" in sys:
            if type(sys["subsystem"]) == list:
                for subsys in sys["subsystem"]:
                    for k, v in subsys.items():
                        if k.startswith("@") and k != "@name":
                            subsys[k[1:]] = v
                            del subsys[k]
                        elif k == "#text":
                            del subsys[k]
            else:
                subsys = sys["subsystem"]
                for k, v in subsys.items():
                    if k.startswith("@") and k != "@name":
                        subsys[k[1:]] = v
                        del subsys[k]
                    elif k == "#text":
                        del subsys[k]
        else:
            for k, v in sys.items():
                if k.startswith("@") and k != "@name":
                    sys[k[1:]] = v
                    del sys[k]
                elif k == "#text":
                    del sys[k]
    print(json.dumps(data, indent=4))

    return render(request, 'wdf_edit/index.html', {"data": data["credentials"], "filepath": filepath})

# def get_json(request):
#     return JsonResponse(xmltodict.parse(open('/home/ka/Desktop/warrior_fnc_tests/warrior_tests/data/cli_tests/cli_def_Data.xml').read()))

def get_jstree_dir(request):
    config = read_json_data(Navigator().get_katana_dir() + os.sep + "config.json")
    data = Navigator().get_dir_tree_json(config["idfdir"])
    data["text"] = config["idfdir"]
    # print json.dumps(data, indent=4)
    return JsonResponse(data)

def file_list(request):
    return render(request, 'wdf_edit/file_list.html', {})

def raw_parser(data):
    """
        Read the html form data in systemid-subsystemid-tagid-childtagid format
        output a nested dict with 4 level
        the last level contains the tag and value inside a list
    """
    result = {}
    system_keys = [x for x in data.keys() if x.endswith("-system_name")]
    for name in system_keys:
        # Prepare all system to save data
        sys_name = name.replace("-system_name", "").split("-")[0]
        subsys_name = name.replace("-system_name", "").split("-")[1]
        if sys_name in result:
            result[sys_name][subsys_name] = {"system_name":data[name]}
        else:
            result[sys_name] = {subsys_name: {"system_name":data[name]}}
        current_sys = result[sys_name][subsys_name]
        if sys_name+"-"+subsys_name+"-subsystem_name" in data:
            current_sys.update({"subsystem_name":data[sys_name+"-"+subsys_name+"-subsystem_name"]})

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
    # First half is to build the system and subsystem tag in the result dict
    sys_keys = [str(y) for y in sorted([int(x) for x in data.keys()])]
    for sys_key in sys_keys:
        sys = data[sys_key]
        subsys_keys = [str(y) for y in sorted([int(x) for x in sys.keys()])]
        for subsys_key in subsys_keys:
            subsys = sys[subsys_key]
            if "subsystem_name" not in subsys:
                result.append(OrderedDict())
                current_sys = result[-1]
                current_sys["@name"] = subsys["system_name"]
            else:
                # There is a subsystem inside the current system
                if locate_system(result, subsys["system_name"]) > -1:
                    # The system already exist in result
                    if "subsystem" in result[locate_system(result, subsys["system_name"])]:
                        result[locate_system(result, subsys["system_name"])]["subsystem"].append(OrderedDict())
                    else:
                        result[locate_system(result, subsys["system_name"])]["subsystem"] = [OrderedDict()]
                    current_sys = result[locate_system(result, subsys["system_name"])]["subsystem"][-1]
                    current_sys["@name"] = subsys["subsystem_name"]
                    current_sys["subsystem"] = []
                else:
                    # The system doesn't exist in result
                    result.append(OrderedDict({"@name": subsys["system_name"], "subsystem":[]}))
                    result[-1]["subsystem"].append(OrderedDict())
                    current_sys = result[-1]["subsystem"][-1]
                    current_sys["@name"] = subsys["subsystem_name"]

    # Second half is to build all tags and values inside the current_sys
            # subsys contains all the tags and values
            # current_sys will fill with tags and values
            tag_keys = [str(y) for y in sorted([int(x) for x in subsys.keys() if x.isdigit()])]
            for tag_key in tag_keys:
                if len(subsys[tag_key]) == 1:
                    # no child tag
                    if subsys[tag_key]["1"][0] not in current_sys:
                        current_sys[subsys[tag_key]["1"][0]] = [subsys[tag_key]["1"][1]]
                    else:
                        current_sys[subsys[tag_key]["1"][0]].append(subsys[tag_key]["1"][1])
                else:
                    # have child tag(s)
                    subtag_keys = [str(y) for y in sorted([int(x) for x in subsys[tag_key].keys() if x.isdigit()])]
                    # subtag first will be the tag name, which values are child tags
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
                        tmp_index = next((i for i, v in enumerate(current_childtags.keys()) if tmp_key in v), None)
                        if tmp_index is not None:
                            # current_childtags[tmp_index] is the dict that shared the same tag name
                            current_childtags[tmp_key].append(subsys[tag_key][subtag_key][1])
                        else:
                            current_childtags.update({tmp_key:[subsys[tag_key][subtag_key][1]]})

    print json.dumps(result, indent=4)
    return result

def on_post(request):
    data = request.POST
    filepath = data["filepath"]
    # print json.dumps(sorted(data.items()), indent=4)
    data = raw_parser(data)
    data = build_xml_dict(data)
    data = {"credentials":{"system":data}}

    from xml.dom.minidom import parseString as miniparse
    print miniparse(xmltodict.unparse(data)).toprettyxml()
    print "Filepath:", filepath
    # return render(request, 'wdf_edit/result.html', {"data": json.dumps(request.POST, indent=4)})
    return render(request, 'wdf_edit/file_list.html', {})