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

        banner = "Thank you for visiting the Wapp Store. We are still working at building this " \
                 "awesome store for you! Please return in a few days for more information!"

        return render(request, WappStoreView.template, {"data": banner})