from django.urls import path
from . import views
from django.conf.urls import url

app_name = "patchwork"

urlpatterns = [
    path('', views.home_view, name="home"),
    path('accounts/', views.AccountList.as_view(), name="account_list"),
    path('projects/', views.ProjectList.as_view()),
    path('series/', views.SeriesList.as_view()),
    path('patches/', views.PatchList.as_view()),
    path('comments/', views.CommentList.as_view())
]