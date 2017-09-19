from django.conf.urls import url

from . views import Execution as execution_views
from . import views as exec_views

execution = execution_views()

urlpatterns = [
    url(r'^$', execution.index, name='index'),
    url(r'executeWarrior', execution.execute_warrior),
    url(r'getResultsIndex', execution.get_results_index),
    url(r'getWs', execution.get_ws),
    url(r'updateHtmlResult', exec_views.update_html_results),
    url(r'getHtmlResult', exec_views.get_html_results),
]
