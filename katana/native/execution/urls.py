from django.conf.urls import url

from . views import Execution as execution_views
from . import views as exec_views

execution = execution_views()

urlpatterns = [
    url(r'^$', execution.index, name='index'),
    url(r'executeWarrior', execution.execute_warrior),
    url(r'getResultsIndex', execution.get_results_index),
    url(r'getWs', execution.get_ws),
    url(r'getHtmlResult', execution.get_html_results),
    url(r'deleteLiveHtmlFile', execution.delete_live_html_file),
    url(r'cleanupDataLiveDir', execution.cleanup_data_live_dir),
    url(r'getLogFileContents', execution.get_logfile_contents),
]
