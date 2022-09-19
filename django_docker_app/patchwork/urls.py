from django.urls import path
from . import views
from django.conf.urls import url

urlpatterns = [
    path('', views.example_view),
    url(r'^accounts$', views.account_list),
    url(r'^projects$', views.project_list),
    url(r'^series$', views.series_list),
    url(r'^patches$', views.patch_list),
    url(r'^comments$', views.comment_list)
]