# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from utils.directory_traversal_utils import join_path
from utils.json_utils import read_json_data
from utils.navigator_util import Navigator

navigator = Navigator()
CONFIG_FILE = join_path(navigator.get_katana_dir(), "config.json")


class CasesView(View):

    def get(self, request):
        """
        Get Request Method
        """
        return render(request, 'cases/cases.html')


def get_list_of_cases(request):
    config = read_json_data(CONFIG_FILE)
    return JsonResponse({"data": navigator.get_dir_tree_json(config["xmldir"])})
