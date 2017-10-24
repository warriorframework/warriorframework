# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.views import View


class CliDataView(View):

    template = 'cli_data/cli_data.html'

    def get(self, request):
        """
        Get Request Method
        """

        return render(request, CliDataView.template, {"data": "This is the Cli Data App"})