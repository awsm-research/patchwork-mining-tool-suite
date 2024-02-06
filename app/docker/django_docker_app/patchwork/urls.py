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
    path('change1/', views.ExactBoWGroupListView.as_view()),
    path('change2/', views.OWDiffGroupListView.as_view()),
    path('newseries/', views.NewSeriesListView.as_view()),
    path('mailinglist/', views.MailingListListView.as_view()),
    path('individual/', views.IndividualListView.as_view()),

    path('identity/create/', views.IdentityCreateView.as_view()),
    path('project/create/', views.ProjectCreateView.as_view()),
    path('series/create/', views.SeriesStandardCreateView.as_view()),
    path('patch/create/', views.PatchStandardCreateView.as_view()),
    path('comment/create/', views.CommentStandardCreateView.as_view()),
    path('change1/create/', views.ExactBoWGroupCreateView.as_view()),
    path('change2/create/', views.OWDiffGroupCreateView.as_view()),
    path('newseries/create/', views.NewSeriesCreateView.as_view()),
    path('mailinglist/create/', views.MailingListStandardCreateView.as_view()),
    path('individual/create/', views.IndividualCreateView.as_view()),

    path('projectidentityrelation/create/',
         views.ProjectIdentityRelationCreateView.as_view()),
    path('individualidentityrelation/create/',
         views.IndividualIdentityRelationCreateView.as_view()),

    path('newseriesidentityrelation/create/',
         views.NewSeriesIdentityRelationCreateView.as_view()),
    path('newseriesindividualrelation/create/',
         views.NewSeriesIndividualRelationCreateView.as_view()),
    path('newseriesseriesrelation/create/',
         views.NewSeriesSeriesRelationCreateView.as_view()),

    path('change1identityrelation/create/',
         views.ExactBoWGroupIdentityRelationCreateView.as_view()),
    path('change1individualrelation/create/',
         views.ExactBoWGroupIndividualRelationCreateView.as_view()),
    path('change1seriesrelation/create/',
         views.ExactBoWGroupSeriesRelationCreateView.as_view()),
    path('change1newseriesrelation/create/',
         views.ExactBoWGroupNewSeriesRelationCreateView.as_view()),

    path('change2identityrelation/create/',
         views.OWDiffGroupIdentityRelationCreateView.as_view()),
    path('change2individualrelation/create/',
         views.OWDiffGroupIndividualRelationCreateView.as_view()),
    path('change2seriesrelation/create/',
         views.OWDiffGroupSeriesRelationCreateView.as_view()),
    path('change2newseriesrelation/create/',
         views.OWDiffGroupNewSeriesRelationCreateView.as_view()),

    path('series/create/large_content/', views.SeriesFileCreateView.as_view()),
    path('patch/create/large_content/', views.PatchFileCreateView.as_view()),
    path('comment/create/large_content/',
         views.CommentFileCreateView.as_view()),
    path('mailinglist/create/large_content/',
         views.MailingListFileCreateView.as_view()),

    path('newseries/<id>/update/', views.NewSeriesUpdateView.as_view()),
]
