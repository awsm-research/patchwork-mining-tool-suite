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
    path('changes1/', views.Change1ListView.as_view()),
    path('changes2/', views.Change2ListView.as_view()),
    path('newseries/', views.NewSeriesListView.as_view()),
    path('mailinglist/', views.MailingListListView.as_view()),
    path('users/', views.UserListView.as_view()),

    path('accounts/create/', views.AccountCreateView.as_view()),
    path('projects/create/', views.ProjectCreateView.as_view()),
    path('series/create/', views.SeriesStandardCreateView.as_view()),
    path('patches/create/', views.PatchStandardCreateView.as_view()),
    path('comments/create/', views.CommentStandardCreateView.as_view()),
    path('changes1/create/', views.Change1CreateView.as_view()),
    path('changes2/create/', views.Change2CreateView.as_view()),
    path('newseries/create/', views.NewSeriesCreateView.as_view()),
    path('mailinglist/create/', views.MailingListCreateView.as_view()),
    path('users/create/', views.UserCreateView.as_view()),

    path('series/create/large_content/', views.SeriesFileCreateView.as_view()),
    path('patches/create/large_content/', views.PatchContentFileCreateView.as_view()),
    path('patches/create/large_diff/', views.PatchDiffFileCreateView.as_view()),
    path('patches/create/large/', views.PatchFileCreateView.as_view()),
    path('comments/create/large_content/', views.CommentFileCreateView.as_view()),

    # path('newseries/<original_id>/update/', views.NewSeriesUpdateView.as_view()),
    path('newseries/<id>/update/', views.NewSeriesUpdateView.as_view()),
]