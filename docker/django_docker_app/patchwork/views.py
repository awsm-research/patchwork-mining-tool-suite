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


class SeriesCreateView(generics.CreateAPIView):

    queryset = Series.objects.all()

    # override the get_serializer_class method
    def get_serializer_class(self):
        series = self.request.data
        if series['cover_letter_content'] and len(series['cover_letter_content']) > SIZE_LIMIT:
            return SeriesFileSerializer
        else:
            return SeriesStandardSerializer


class PatchListView(generics.ListAPIView):

    queryset = Patches.objects.all()
    serializer_class = ListPatchSerializer
    filterset_class = PatchFilter
    search_fields = ['name', 'msg_content', 'code_diff']
    ordering_fields = '__all__'


class PatchCreateView(generics.CreateAPIView):

    queryset = Patches.objects.all()

    # override the get_serializer_class method
    def get_serializer_class(self):
        patch = self.request.data
        if (patch['msg_content'] and len(patch['msg_content']) > SIZE_LIMIT) and (patch['code_diff'] and len(patch['code_diff']) > SIZE_LIMIT):
            return PatchFileSerializer
        elif patch['msg_content'] and len(patch['msg_content']) > SIZE_LIMIT:
            return PatchContentFileSerializer
        elif patch['code_diff'] and len(patch['code_diff']) > SIZE_LIMIT:
            return PatchDiffFileSerializer
        else:
            return PatchStandardSerializer


class CommentListView(generics.ListAPIView):

    queryset = Comments.objects.all()
    serializer_class = ListCommentSerializer
    filterset_class = CommentFilter
    search_fields = ['subject', 'msg_content']
    ordering_fields = '__all__'


class CommentCreateView(generics.CreateAPIView):

    queryset = Comments.objects.all()

    # override the get_serializer_class method
    def get_serializer_class(self):
        comment = self.request.data
        if comment['msg_content'] and len(comment['msg_content']) > SIZE_LIMIT:
            return CommentFileSerializer
        else:
            return CommentStandardSerializer


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


class Change2ListView(generics.ListAPIView):

    queryset = Changes2.objects.all()
    serializer_class = Changes2
    filterset_class = Change2Filter
    ordering_fields = '__all__'


class Change2CreateView(generics.CreateAPIView):

    queryset = Changes2.objects.all()
    serializer_class = Change2Serializer


class UserListView(generics.ListAPIView):

    queryset = Changes2.objects.all()
    serializer_class = Changes2
    filterset_class = Change2Filter
    ordering_fields = '__all__'


class UserCreateView(generics.CreateAPIView):

    queryset = Users.objects.all()
    serializer_class = UserSerializer


class NewSeriesListView(generics.ListAPIView):

    queryset = NewSeries.objects.all()
    serializer_class = NewSeriesSerializer
    filterset_class = NewSeriesFilter
    ordering_fields = '__all__'


class NewSeriesCreateView(generics.CreateAPIView):

    queryset = NewSeries.objects.all()
    serializer_class = NewSeriesSerializer


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