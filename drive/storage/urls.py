from django.conf.urls import url

from drive.storage import views

urlpatterns = [
    url(r'^file/(?P<file_id>[\w\-]+)/$', views.get_file, name='get_file'),
    url(r'^(?P<folder_type>[\w\-]+)/$', views.FolderView.as_view(), name='root_content'),
    url(r'^update/(?P<folder_id>[\w\-]+)/$', views.FolderUpdateView.as_view(), name='folder_update_content'),
    url(r'^(?P<folder_type>[\w\-]+)/(?P<folder_id>[\w\-]+)/$', views.FolderView.as_view(), name='folder_content'),
    url(r'^(?P<folder_type>[\w\-]+)/(?P<folder_id>[\w\-]+)/(?P<action>[\w\-]+)/$', views.FolderView.as_view(),
        name='folder_content_action'),
]
