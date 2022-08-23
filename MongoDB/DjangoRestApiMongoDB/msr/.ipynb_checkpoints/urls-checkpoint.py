from django.conf.urls import url 
from msr import views 
 
urlpatterns = [
    url(r'^api/msr/people$', views.msr_people_list),
    url(r'^api/msr/projects$', views.msr_project_list),
    url(r'^api/msr/series$', views.msr_series_list),
    url(r'^api/msr/changes$', views.msr_change_list),
    url(r'^api/msr/mailing_list$', views.msr_mailing_list_list),
    url(r'^api/msr/patches$', views.msr_patch_list),
    url(r'^api/msr/comments$', views.msr_comment_list),
    
    url(r'^api/msr/people/(?P<pk>[0-9]+)$', views.msr_people_detail),
    url(r'^api/msr/projects/(?P<pk>[0-9]+)$', views.msr_project_detail),
    url(r'^api/msr/series/(?P<pk>[0-9]+)$', views.msr_series_detail),
    url(r'^api/msr/changes/(?P<pk>[0-9]+)$', views.msr_change_detail),
    url(r'^api/msr/mailing_list/(?P<pk>[0-9]+)$', views.msr_mailing_list_detail),
    url(r'^api/msr/patches/(?P<pk>[0-9]+)$', views.msr_patch_detail),
    url(r'^api/msr/comments/(?P<pk>[0-9]+)$', views.msr_comment_detail)
]