from django.urls import path
from . import views

app_name = "patchwork"

urlpatterns = [
    path('', views.APIRootView.as_view()),
    path('identity/', views.IdentityListView.as_view(), name='account-list'),
    path('project/', views.ProjectListView.as_view()),
    path('series/', views.SeriesListView.as_view()),
    path('patch/', views.PatchListView.as_view()),
    path('comment/', views.CommentListView.as_view()),
    path('change1/', views.Change1ListView.as_view()),
    path('change2/', views.Change2ListView.as_view()),
    path('newseries/', views.NewSeriesListView.as_view()),
    path('mailinglist/', views.MailingListListView.as_view()),
    path('individual/', views.IndividualListView.as_view()),

    path('identity/create/', views.IdentityCreateView.as_view()),
    path('project/create/', views.ProjectCreateView.as_view()),
    path('series/create/', views.SeriesStandardCreateView.as_view()),
    path('patch/create/', views.PatchStandardCreateView.as_view()),
    path('comment/create/', views.CommentStandardCreateView.as_view()),
    path('change1/create/', views.Change1CreateView.as_view()),
    path('change2/create/', views.Change2CreateView.as_view()),
    path('newseries/create/', views.NewSeriesCreateView.as_view()),
    path('mailinglist/create/', views.MailingListCreateView.as_view()),
    path('individual/create/', views.IndividualCreateView.as_view()),

    path('projectidentityrelation/create/', views.ProjectIdentityRelationCreateView.as_view()),
    path('individualidentityrelation/create/', views.IndividualIdentityRelationCreateView.as_view()),

    path('series/create/large_content/', views.SeriesFileCreateView.as_view()),
    path('patch/create/large_content/', views.PatchContentFileCreateView.as_view()),
    path('patch/create/large_diff/', views.PatchDiffFileCreateView.as_view()),
    path('patch/create/large/', views.PatchFileCreateView.as_view()),
    path('comment/create/large_content/', views.CommentFileCreateView.as_view()),

    # path('newseries/<original_id>/update/', views.NewSeriesUpdateView.as_view()),
    path('newseries/<id>/update/', views.NewSeriesUpdateView.as_view()),
]