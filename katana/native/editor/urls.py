from django.conf.urls import url

from . views import Editor as editor_views
from . import views as edit_views

editor = editor_views()

urlpatterns = [
    url(r'^$', editor.index, name='index'),
    url(r'getFiles', editor.get_files),
    url(r'getFileContent', editor.get_file_content),
    url(r'saveFile', editor.save_file_content),
    url(r'getData', editor.get_file_data),

]
