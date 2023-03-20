from django.shortcuts import render
from django.http.response import JsonResponse, HttpResponse
from django.db.models import Q

from patchwork.static.utils import TextFile, UndefinedArg
from patchwork.static.filters import *
from patchwork.models import *
from patchwork.serializers import *
from datetime import datetime, timezone

from rest_framework import status, generics
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.decorators import api_view

SIZE_LIMIT = 16793600

# Create your views here.
def home_view(request):
    return render(request, 'patchwork/home.html')

class APIRootView(APIView):
    name = 'Index'

    def get(self, request, *args, **kwargs):
        return Response({
            'identity': 'http://localhost:8000/patchwork/identity/',
            'project': 'http://localhost:8000/patchwork/project/',
            'series': 'http://localhost:8000/patchwork/series/',
            'patch': 'http://localhost:8000/patchwork/patch/',
            'comment': 'http://localhost:8000/patchwork/comment/',
            'newseries': 'http://localhost:8000/patchwork/newseries/',
            'change1': 'http://localhost:8000/patchwork/change1/',
            'change2': 'http://localhost:8000/patchwork/change2/',
            'individual': 'http://localhost:8000/patchwork/individual/',
            })


class IdentityListView(generics.ListAPIView):

    queryset = Identity.objects.all().prefetch_related("individuals")
    serializer_class = IdentityListSerializer
    filterset_class = IdentityFilter
    search_fields = ['original_id', 'email', 'name']
    ordering_fields = '__all__'
    # name = 'account-list'

class IdentityCreateView(generics.CreateAPIView):

    queryset = Identity.objects.all()
    serializer_class = IdentityCreateSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(IdentityCreateView, self).get_serializer(*args, **kwargs)


class ProjectListView(generics.ListAPIView):

    queryset = Project.objects.all().prefetch_related("maintainer_identity")
    serializer_class = ProjectListSerializer
    filterset_class = ProjectFilter
    search_fields = ['original_id', 'name']
    ordering_fields = '__all__'


class ProjectCreateView(generics.CreateAPIView):

    queryset = Project.objects.all()
    serializer_class = ProjectCreateSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(ProjectCreateView, self).get_serializer(*args, **kwargs)


class ProjectIdentityRelationCreateView(generics.CreateAPIView):

    queryset = ProjectIdentityRelation.objects.all()
    serializer_class = ProjectIdentityRelationCreateSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(ProjectIdentityRelationCreateView, self).get_serializer(*args, **kwargs)


class IndividualIdentityRelationCreateView(generics.CreateAPIView):

    queryset = IndividualIdentityRelation.objects.all()
    serializer_class = IndividualIdentityRelationCreateSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(IndividualIdentityRelationCreateView, self).get_serializer(*args, **kwargs)


class SeriesListView(generics.ListAPIView):

    queryset = Series.objects.all()
    serializer_class = SeriesListSerializer
    filterset_class = SeriesFilter
    search_fields = ['name', 'cover_letter_content']
    ordering_fields = '__all__'


class SeriesStandardCreateView(generics.CreateAPIView):

    queryset = Series.objects.all()
    serializer_class = SeriesStandardSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(SeriesStandardCreateView, self).get_serializer(*args, **kwargs)


class SeriesFileCreateView(generics.CreateAPIView):

    queryset = Series.objects.all()
    serializer_class = SeriesFileSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(SeriesFileCreateView, self).get_serializer(*args, **kwargs)


class PatchListView(generics.ListAPIView):

    # queryset = Patch.objects.all()
    # serializer_class = embedded.PatchSerializer

    queryset = Patch.objects.all().select_related(
        "change1", 
        "change2", 
        "mailinglist", 
        "series", 
        "newseries", 
        "submitter_identity", 
        "submitter_individual", 
        "project"
    )
    serializer_class = PatchListSerializer
    filterset_class = PatchFilter
    search_fields = ['name', 'msg_content', 'code_diff']
    ordering_fields = '__all__'


class PatchStandardCreateView(generics.CreateAPIView):

    queryset = Patch.objects.all()
    serializer_class = PatchStandardSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(PatchStandardCreateView, self).get_serializer(*args, **kwargs)


class PatchContentFileCreateView(generics.CreateAPIView):

    queryset = Patch.objects.all()
    serializer_class = PatchContentFileSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(PatchContentFileCreateView, self).get_serializer(*args, **kwargs)


class PatchDiffFileCreateView(generics.CreateAPIView):

    queryset = Patch.objects.all()
    serializer_class = PatchDiffFileSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(PatchDiffFileCreateView, self).get_serializer(*args, **kwargs)


class PatchFileCreateView(generics.CreateAPIView):

    queryset = Patch.objects.all()
    serializer_class = PatchFileSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(PatchFileCreateView, self).get_serializer(*args, **kwargs)


class CommentListView(generics.ListAPIView):

    queryset = Comment.objects.all().select_related(
        "change1", 
        "change2", 
        "mailinglist", 
        "submitter_identity", 
        "submitter_individual", 
        "patch", 
        "project"
    )
    serializer_class = CommentListSerializer
    filterset_class = CommentFilter
    search_fields = ['subject', 'msg_content']
    ordering_fields = '__all__'


class CommentStandardCreateView(generics.CreateAPIView):

    queryset = Comment.objects.all()
    serializer_class = CommentStandardSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(CommentStandardCreateView, self).get_serializer(*args, **kwargs)


class CommentFileCreateView(generics.CreateAPIView):

    queryset = Comment.objects.all()
    serializer_class = CommentFileSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(CommentFileCreateView, self).get_serializer(*args, **kwargs)


class CommentUpdateView(generics.UpdateAPIView):

    lookup_field = ['id', 'original_id']

    # override the get_serializer_class method
    def get_serializer_class(self):
        comment = self.request.data
        if comment['msg_content'] and len(comment['msg_content']) > SIZE_LIMIT:
            return CommentFileSerializer
        else:
            return CommentStandardSerializer


class Change1ListView(generics.ListAPIView):

    queryset = Change1.objects.all().prefetch_related("project", "submitter_identity", "submitter_individual", "series", "newseries", "patches", "comments")
    serializer_class = Change1ListSerializer
    filterset_class = Change1Filter
    ordering_fields = '__all__'


class Change1CreateView(generics.CreateAPIView):

    queryset = Change1.objects.all()
    serializer_class = Change1CreateSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(Change1CreateView, self).get_serializer(*args, **kwargs)


class Change2ListView(generics.ListAPIView):

    queryset = Change2.objects.all().prefetch_related("project", "submitter_identity", "submitter_individual", "series", "newseries", "patches", "comments")
    serializer_class = Change2ListSerializer
    filterset_class = Change2Filter
    ordering_fields = '__all__'


class Change2CreateView(generics.CreateAPIView):

    queryset = Change2.objects.all()
    serializer_class = Change2CreateSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(Change2CreateView, self).get_serializer(*args, **kwargs)


class IndividualListView(generics.ListAPIView):

    queryset = Individual.objects.all()
    serializer_class = IndividualListSerializer
    filterset_class = IndividualFilter
    ordering_fields = '__all__'


class IndividualCreateView(generics.CreateAPIView):

    queryset = Individual.objects.all()
    serializer_class = IndividualCreateSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(IndividualCreateView, self).get_serializer(*args, **kwargs)
    
    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
        
    #     return super().create(request, *args, **kwargs)


class NewSeriesListView(generics.ListAPIView):

    queryset = NewSeries.objects.all()
    serializer_class = NewSeriesListSerializer
    filterset_class = NewSeriesFilter
    ordering_fields = '__all__'


class NewSeriesCreateView(generics.CreateAPIView):

    queryset = NewSeries.objects.all()
    serializer_class = NewSeriesCreateSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(NewSeriesCreateView, self).get_serializer(*args, **kwargs)


class NewSeriesUpdateView(generics.UpdateAPIView):

    queryset = NewSeries.objects.all()
    lookup_field = 'id'
    serializer_class = NewSeriesCreateSerializer


class NewSeriesIdentityRelationCreateView(generics.CreateAPIView):

    queryset = NewSeriesIdentityRelation.objects.all()
    serializer_class = NewSeriesIdentityRelationCreateSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(NewSeriesIdentityRelationCreateView, self).get_serializer(*args, **kwargs)


class NewSeriesIndividualRelationCreateView(generics.CreateAPIView):

    queryset = NewSeriesIndividualRelation.objects.all()
    serializer_class = NewSeriesIndividualRelationCreateSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(NewSeriesIndividualRelationCreateView, self).get_serializer(*args, **kwargs)


class NewSeriesSeriesRelationCreateView(generics.CreateAPIView):

    queryset = NewSeriesSeriesRelation.objects.all()
    serializer_class = NewSeriesSeriesRelationCreateSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(NewSeriesSeriesRelationCreateView, self).get_serializer(*args, **kwargs)


class Change1IdentityRelationCreateView(generics.CreateAPIView):

    queryset = Change1IdentityRelation.objects.all()
    serializer_class = Change1IdentityRelationCreateSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(Change1IdentityRelationCreateView, self).get_serializer(*args, **kwargs)


class Change1IndividualRelationCreateView(generics.CreateAPIView):

    queryset = Change1IndividualRelation.objects.all()
    serializer_class = Change1IndividualRelationCreateSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(Change1IndividualRelationCreateView, self).get_serializer(*args, **kwargs)


class Change1SeriesRelationCreateView(generics.CreateAPIView):

    queryset = Change1SeriesRelation.objects.all()
    serializer_class = Change1SeriesRelationCreateSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(Change1SeriesRelationCreateView, self).get_serializer(*args, **kwargs)


class Change1NewSeriesRelationCreateView(generics.CreateAPIView):

    queryset = Change1NewSeriesRelation.objects.all()
    serializer_class = Change1NewSeriesRelationCreateSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(Change1NewSeriesRelationCreateView, self).get_serializer(*args, **kwargs)


class Change2IdentityRelationCreateView(generics.CreateAPIView):

    queryset = Change2IdentityRelation.objects.all()
    serializer_class = Change2IdentityRelationCreateSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(Change2IdentityRelationCreateView, self).get_serializer(*args, **kwargs)


class Change2IndividualRelationCreateView(generics.CreateAPIView):

    queryset = Change2IndividualRelation.objects.all()
    serializer_class = Change2IndividualRelationCreateSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(Change2IndividualRelationCreateView, self).get_serializer(*args, **kwargs)


class Change2SeriesRelationCreateView(generics.CreateAPIView):

    queryset = Change2SeriesRelation.objects.all()
    serializer_class = Change2SeriesRelationCreateSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(Change2SeriesRelationCreateView, self).get_serializer(*args, **kwargs)


class Change2NewSeriesRelationCreateView(generics.CreateAPIView):

    queryset = Change2NewSeriesRelation.objects.all()
    serializer_class = Change2NewSeriesRelationCreateSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(Change2NewSeriesRelationCreateView, self).get_serializer(*args, **kwargs)


class MailingListListView(generics.ListAPIView):

    queryset = MailingList.objects.all()
    serializer_class = MailingListSerializer
    filterset_class = MailingListFilter
    ordering_fields = '__all__'


class MailingListCreateView(generics.CreateAPIView):

    queryset = MailingList.objects.all()
    serializer_class = MailingListSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(MailingListCreateView, self).get_serializer(*args, **kwargs)