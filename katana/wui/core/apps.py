# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.apps import AppConfig
from utils.directory_traversal_utils import get_parent_directory, get_abs_path
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

        base_directory = get_parent_directory(os.path.dirname(os.path.realpath(__file__)), 2)
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

        print AppInformation.information.apps

        # print "***************You are in Core Katana App Config Class***************"
