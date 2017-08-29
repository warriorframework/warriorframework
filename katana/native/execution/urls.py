from django.conf.urls import url

from . import views
from views import Execution as execution_views

execution = execution_views()

urlpatterns = [
    url(r'^$', execution.index, name='index'),
    url(r'executeWarrior', execution.execute_warrior)
]
