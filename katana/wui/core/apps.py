# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import os
from collections import OrderedDict
from django.apps import AppConfig
from utils.directory_traversal_utils import get_abs_path, join_path
from utils.navigator_util import Navigator
from wui.core.core_utils.app_info_class import AppInformation
from wui.core.core_utils.apps_class import Apps
from wui.core.core_utils.core_index_class_utils import CoreIndex


class CoreConfig(AppConfig):
    name = 'wui.core'
    verbose_name = "Core Katana"

    def ready(self):
        """
        The ready function is trigger only on events like server start up and server reload
        """
        # print "***************You are in Core Katana App Config Class***************"
        nav_obj = Navigator()

        base_directory = nav_obj.get_katana_dir()
        config_file_name = "wf_config.json"
        settings_file_path = get_abs_path(os.path.join("wui", "settings.py"), base_directory)
        core_index_obj = CoreIndex(base_directory, settings_file_path=settings_file_path)

        available_apps = core_index_obj.get_available_apps()
        settings_apps = core_index_obj.get_apps_from_settings_file()

        AppInformation.information = Apps()

        AppInformation.information.set_apps({'base_directory': base_directory,
                                             'config_file_name': config_file_name,
                                             'available_apps': available_apps,
                                             'settings_apps': settings_apps})

        warrior_dir = nav_obj.get_warrior_dir()
        config_json_file = os.path.join(base_directory, "config.json")
        with open(config_json_file, "r") as f:
            json_data = json.load(f)

        ordered_json = validate_config_json(json_data, warrior_dir)

        with open(config_json_file, "w") as f:
            f.write(json.dumps(ordered_json, indent=4))

        # print "***************You are in Core Katana App Config Class***************"


def validate_config_json(json_data, warrior_dir):
    ordered_json = OrderedDict()
    if "engineer" not in json_data:
        ordered_json["engineer"] = ""
    else:
        ordered_json["engineer"] = json_data["engineer"]

    ordered_json["pythonsrcdir"] = warrior_dir[:-1] \
        if "pythonsrcdir" not in json_data or json_data["pythonsrcdir"] == "" \
        else json_data["pythonsrcdir"]

    warrior_dir = ordered_json["pythonsrcdir"]

    if "xmldir" not in json_data or json_data["xmldir"] == "":
        path = get_abs_path(join_path("Warriorspace", "Testcases"), warrior_dir)
        if path is not None:
            ordered_json["xmldir"] = path
        else:
            ordered_json["xmldir"] = ""
            print "-- An Error Occurred -- Path to Cases directory could not be located"
    else:
        ordered_json["xmldir"] = json_data["xmldir"]

    if "testsuitedir" not in json_data or json_data["testsuitedir"] == "":
        path = get_abs_path(join_path("Warriorspace", "Suites"), warrior_dir)
        if path is not None:
            ordered_json["testsuitedir"] = path
        else:
            ordered_json["testsuitedir"] = ""
            print "-- An Error Occurred -- Path to Cases directory could not be located"
    else:
        ordered_json["testsuitedir"] = json_data["testsuitedir"]

    if "projdir" not in json_data or json_data["projdir"] == "":
        path = get_abs_path(join_path("Warriorspace", "Projects"), warrior_dir)
        if path is not None:
            ordered_json["projdir"] = path
        else:
            ordered_json["projdir"] = ""
            print "-- An Error Occurred -- Path to Cases directory could not be located"
    else:
        ordered_json["projdir"] = json_data["projdir"]

    if "idfdir" not in json_data or json_data["idfdir"] == "":
        path = get_abs_path(join_path("Warriorspace", "Data"), warrior_dir)
        if path is not None:
            ordered_json["idfdir"] = path
        else:
            ordered_json["idfdir"] = ""
            print "-- An Error Occurred -- Path to Cases directory could not be located"
    else:
        ordered_json["idfdir"] = json_data["idfdir"]

    if "testdata" not in json_data or json_data["testdata"] == "":
        path = get_abs_path(join_path("Warriorspace", "Config_files"), warrior_dir)
        if path is not None:
            ordered_json["testdata"] = path
        else:
            ordered_json["testdata"] = ""
            print "-- An Error Occurred -- Path to Cases directory could not be located"
    else:
        ordered_json["testdata"] = json_data["testdata"]

    if "pythonpath" not in json_data:
        ordered_json["pythonpath"] = ""
    else:
        ordered_json["pythonpath"] = json_data["pythonpath"]
    return ordered_json
