# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import fcntl
from django.apps import AppConfig
from utils.date_time_stamp_utils import get_current_datetime_stamp
from utils.directory_traversal_utils import get_parent_directory, get_abs_path
from utils.error_log_class import ErrorLog
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

        logs_dir = "logs"
        log_file = "logs - {0}.txt".format(get_current_datetime_stamp())
        dummy_file = "dummy.txt"
        file_path = os.path.join(base_directory, logs_dir, log_file)
        dummy_path = os.path.join(base_directory, logs_dir, dummy_file)

        if os.path.exists(dummy_path):
            f = open(dummy_path)
            status = True
            while status:
                try:
                    fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except IOError:
                    pass
                else:
                    status = False
                    file_path = f.read()
                    fcntl.flock(f, fcntl.LOCK_UN)
                    os.remove(dummy_path)
        else:
            f = open(dummy_path, 'w')
            f.write(file_path)
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)

        AppInformation.log_obj = ErrorLog(file_path)

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

        # print "***************You are in Core Katana App Config Class***************"
