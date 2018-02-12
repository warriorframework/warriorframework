"""wui URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^katana/', include('wui.core.urls')),
    url(r'^$', RedirectView.as_view(url='/katana/')),
    url(r'^katana/settings/', include('native.settings.urls')),
    url(r'^katana/wapp_management/', include('native.wapp_management.urls')),
    url(r'^katana/wappstore/', include('native.wappstore.urls')),
    url(r'^katana/wdf/', include('wapps.wdf_edit.urls')),
    url(r'^katana/projects/', include('wapps.projects.urls')),
    url(r'^katana/suites/', include('wapps.suites.urls')),
    url(r'^katana/cases/', include('wapps.cases.urls')),
    url(r'^katana/execution/', include('wapps.execution.urls')),
    url(r'^katana/assembler/', include('wapps.assembler.urls')),
    url(r'^katana/cli_data/', include('wapps.cli_data.urls')),
]
