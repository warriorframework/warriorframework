# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from django.views import View


class WappStoreView(View):

    template = 'wappstore/wappstore.html'

    def get(self, request):
        """
        Get Request Method
        """

        banner = "Thank you for visiting the Wapp Store."
        data = "We are still working on building this awesome store for you and we will let you " \
               "know as soon as it is ready!"

        return render(request, WappStoreView.template, {"banner": banner, "data": data})