# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
from collections import OrderedDict

from django.apps import AppConfig
from utils.directory_traversal_utils import get_parent_directory, get_abs_path
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
        ordered_json = OrderedDict()
        with open(os.path.join(base_directory, "config.json"), "r") as f:
            json_data = json.load(f)
        if "engineer" not in json_data:
            ordered_json["engineer"] = ""
        else:
            ordered_json["engineer"] = json_data["engineer"]

        ordered_json["pythonsrcdir"] = warrior_dir[:-1] \
            if "pythonsrcdir" not in json_data or json_data["pythonsrcdir"] == "" \
            else json_data["pythonsrcdir"]

        ordered_json["xmldir"] = os.path.join(warrior_dir, "Warriorspace", "Testcases") \
            if "xmldir" not in json_data or json_data["xmldir"] == "" \
            else json_data["xmldir"]

        ordered_json["testsuitedir"] = os.path.join(warrior_dir, "Warriorspace", "Suites") \
            if "testsuitedir" not in json_data or json_data["testsuitedir"] == "" \
            else json_data["testsuitedir"]

        ordered_json["projdir"] = os.path.join(warrior_dir, "Warriorspace", "Projects") \
            if "projdir" not in json_data or json_data["projdir"] == "" \
            else json_data["projdir"]

        ordered_json["idfdir"] = os.path.join(warrior_dir, "Warriorspace", "Data") \
            if "idfdir" not in json_data or json_data["idfdir"] == "" \
            else json_data["idfdir"]

        ordered_json["testdata"] = os.path.join(warrior_dir, "Warriorspace", "Config_files") \
            if "testdata" not in json_data or json_data["testdata"] == "" \
            else json_data["testdata"]

        if "pythonpath" not in json_data:
            ordered_json["pythonpath"] = ""
        else:
            ordered_json["pythonpath"] = json_data["pythonpath"]

        with open(os.path.join(base_directory, "config.json"), "w") as f:
            f.write(json.dumps(ordered_json, indent=4))

        # print "***************You are in Core Katana App Config Class***************"
