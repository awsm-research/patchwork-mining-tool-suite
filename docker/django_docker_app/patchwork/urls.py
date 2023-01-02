from django.urls import path
from . import views

app_name = "patchwork"

urlpatterns = [
    path('', views.home_view, name="home"),
    path('accounts/', views.AccountListView.as_view(), name="account_list"),
    path('projects/', views.ProjectListView.as_view()),
    path('series/', views.SeriesListView.as_view()),
    path('patches/', views.PatchListView.as_view()),
    path('comments/', views.CommentListView.as_view()),
    path('accounts/create/', views.AccountCreateView.as_view()),
    path('projects/create/', views.ProjectCreateView.as_view()),
    path('series/create/', views.SeriesCreateView.as_view()),
    path('patches/create/', views.PatchCreateView.as_view()),
    path('comments/create/', views.CommentCreateView.as_view())
]