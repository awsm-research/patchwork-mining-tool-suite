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
# from rest_framework.decorators import api_view

SIZE_LIMIT = 16793600

# Create your views here.
def home_view(request):
    return render(request, 'patchwork/home.html')


class AccountListView(generics.ListAPIView):

    queryset = Accounts.objects.all()
    serializer_class = AccountSerializer
    filterset_class = AccountFilter
    search_fields = ['original_id', 'email', 'username', 'user_original_id']
    ordering_fields = '__all__'

class AccountCreateView(generics.CreateAPIView):

    queryset = Accounts.objects.all()
    serializer_class = AccountSerializer


class ProjectListView(generics.ListAPIView):

    queryset = Projects.objects.all()
    serializer_class = ProjectSerializer
    filterset_class = ProjectFilter
    search_fields = ['original_id', 'name']
    ordering_fields = '__all__'


class ProjectCreateView(generics.CreateAPIView):

    queryset = Projects.objects.all()
    serializer_class = ProjectSerializer


class SeriesListView(generics.ListAPIView):

    queryset = Series.objects.all()
    serializer_class = ListSeriesSerializer
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

    queryset = Patches.objects.all()
    serializer_class = ListPatchSerializer
    filterset_class = PatchFilter
    search_fields = ['name', 'msg_content', 'code_diff']
    ordering_fields = '__all__'


class PatchStandardCreateView(generics.CreateAPIView):

    queryset = Patches.objects.all()
    serializer_class = PatchStandardSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(PatchStandardCreateView, self).get_serializer(*args, **kwargs)


class PatchContentFileCreateView(generics.CreateAPIView):

    queryset = Patches.objects.all()
    serializer_class = PatchContentFileSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(PatchContentFileCreateView, self).get_serializer(*args, **kwargs)


class PatchDiffFileCreateView(generics.CreateAPIView):

    queryset = Patches.objects.all()
    serializer_class = PatchDiffFileSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(PatchDiffFileCreateView, self).get_serializer(*args, **kwargs)


class PatchFileCreateView(generics.CreateAPIView):

    queryset = Patches.objects.all()
    serializer_class = PatchFileSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(PatchFileCreateView, self).get_serializer(*args, **kwargs)


class CommentListView(generics.ListAPIView):

    queryset = Comments.objects.all()
    serializer_class = ListCommentSerializer
    filterset_class = CommentFilter
    search_fields = ['subject', 'msg_content']
    ordering_fields = '__all__'


class CommentStandardCreateView(generics.CreateAPIView):

    queryset = Comments.objects.all()
    serializer_class = CommentStandardSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(CommentStandardCreateView, self).get_serializer(*args, **kwargs)


class CommentFileCreateView(generics.CreateAPIView):

    queryset = Comments.objects.all()
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

    queryset = Changes1.objects.all()
    serializer_class = Change1Serializer
    filterset_class = Change1Filter
    ordering_fields = '__all__'


class Change1CreateView(generics.CreateAPIView):

    queryset = Changes1.objects.all()
    serializer_class = Change1Serializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(Change1CreateView, self).get_serializer(*args, **kwargs)


class Change2ListView(generics.ListAPIView):

    queryset = Changes2.objects.all()
    serializer_class = Changes2
    filterset_class = Change2Filter
    ordering_fields = '__all__'


class Change2CreateView(generics.CreateAPIView):

    queryset = Changes2.objects.all()
    serializer_class = Change2Serializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(Change2CreateView, self).get_serializer(*args, **kwargs)


class UserListView(generics.ListAPIView):

    queryset = Changes2.objects.all()
    serializer_class = Changes2
    filterset_class = Change2Filter
    ordering_fields = '__all__'


class UserCreateView(generics.CreateAPIView):

    queryset = Users.objects.all()
    serializer_class = UserSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(UserCreateView, self).get_serializer(*args, **kwargs)


class NewSeriesListView(generics.ListAPIView):

    queryset = NewSeries.objects.all()
    serializer_class = NewSeriesSerializer
    filterset_class = NewSeriesFilter
    ordering_fields = '__all__'


class NewSeriesCreateView(generics.CreateAPIView):

    queryset = NewSeries.objects.all()
    serializer_class = NewSeriesSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(NewSeriesCreateView, self).get_serializer(*args, **kwargs)


class NewSeriesUpdateView(generics.UpdateAPIView):

    queryset = NewSeries.objects.all()
    lookup_field = 'id'
    serializer_class = NewSeriesSerializer


class MailingListListView(generics.ListAPIView):

    queryset = MailingLists.objects.all()
    serializer_class = MailingListSerializer
    filterset_class = MailingListFilter
    ordering_fields = '__all__'


class MailingListCreateView(generics.CreateAPIView):

    queryset = MailingLists.objects.all()
    serializer_class = MailingListSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(MailingListCreateView, self).get_serializer(*args, **kwargs)