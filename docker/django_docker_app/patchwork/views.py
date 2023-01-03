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

class AccountCreateView(generics.CreateAPIView):

    queryset = Accounts.objects.all()
    serializer_class = AccountSerializer

    # def post(self, request, format=None):
    #     account_data = JSONParser().parse(request)
    #     is_many = True if type(account_data) == list else False
    #     account_serializer = AccountSerializer(data=account_data, many=is_many)

    #     if account_serializer.is_valid():
    #         account_serializer.save()
    #         return JsonResponse(account_serializer.data, status=status.HTTP_201_CREATED, safe=(not is_many))
        
    #     return JsonResponse(account_serializer.errors, status=status.HTTP_400_BAD_REQUEST, safe=(not is_many))
    

class ProjectListView(generics.ListAPIView):

    queryset = Projects.objects.all()
    serializer_class = ProjectSerializer
    filterset_class = ProjectFilter
    search_fields = ['original_id', 'name']


class ProjectCreateView(generics.CreateAPIView):

    queryset = Projects.objects.all()
    serializer_class = ProjectSerializer

    # def post(self, request, format=None):
    #     project_data = JSONParser().parse(request)
    #     is_many = True if type(project_data) == list else False
    #     project_serializer = ProjectSerializer(data=project_data, many=is_many)

    #     if project_serializer.is_valid():
    #         project_serializer.save()
    #         return JsonResponse(project_serializer.data, status=status.HTTP_201_CREATED, safe=(not is_many))

    #     return JsonResponse(project_serializer.errors, status=status.HTTP_400_BAD_REQUEST, safe=(not is_many))




# GridFS files will be auto-retrieved by serialisers
class SeriesListView(generics.ListAPIView):

    queryset = Series.objects.all()
    serializer_class = GetSeriesSerializer
    filterset_class = SeriesFilter
    search_fields = ['name', 'cover_letter_content']


class SeriesCreateView(generics.CreateAPIView):

    queryset = Series.objects.all()

    # override the get_serializer_class method
    def get_serializer_class(self):
        series = self.request.data
        if series['cover_letter_content'] and len(series['cover_letter_content']) > SIZE_LIMIT:
            return SeriesFileSerializer
        else:
            return SeriesStandardSerializer


        # large_documents = list()
        # small_documents = list()

        # if type(series_data) != list:
        #     series_data = [series_data]

        # for i in range(len(series_data)):
        #     series = series_data[i]
        #     if series['cover_letter_content'] and len(series['cover_letter_content']) > SIZE_LIMIT:
        #         large_documents.append(series)
        #     else:
        #         small_documents.append(series)

        # if small_documents:
        #     small_series_serializer = SeriesStandardSerializer(data=small_documents, many=True)
        #     if small_series_serializer.is_valid():
        #         small_series_serializer.save()
        #     else:
        #         return JsonResponse(small_series_serializer.errors, status=status.HTTP_400_BAD_REQUEST, safe=False)
        # if large_documents:
        #     large_series_serializer = SeriesFileSerializer(data=large_documents, many=True)
        #     if large_series_serializer.is_valid():
        #         large_series_serializer.save()
        #     else:
        #         return JsonResponse(large_series_serializer.errors, status=status.HTTP_400_BAD_REQUEST, safe=False)

        # return HttpResponse('Post request processed.', status=status.HTTP_201_CREATED)


class PatchListView(generics.ListAPIView):

    queryset = Patches.objects.all()
    serializer_class = GetPatchSerializer
    filterset_class = PatchFilter
    search_fields = ['name', 'msg_content', 'code_diff']


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

    # def post(self, request, format=None):
        
    #     patch_data = JSONParser().parse(request)
    #     small_documents = list()
    #     large_documents = list()
    #     large_content_documents = list()
    #     large_diff_documents = list()

    #     if type(patch_data) != list:
    #         patch_data = [patch_data]

    #     for i in range(len(patch_data)):
    #         patch = patch_data[i]

    #         if patch['reply_to_msg_id'] and type(patch['reply_to_msg_id']) == list:
    #             patch['reply_to_msg_id'] = json.dumps(patch['reply_to_msg_id'])

    #         if (patch['msg_content'] and len(patch['msg_content']) > SIZE_LIMIT) and (patch['code_diff'] and len(patch['code_diff']) > SIZE_LIMIT):
    #             large_documents.append(patch)
    #         elif patch['msg_content'] and len(patch['msg_content']) > SIZE_LIMIT:
    #             large_content_documents.append(patch)
    #         elif patch['code_diff'] and len(patch['code_diff']) > SIZE_LIMIT:
    #             large_diff_documents.append(patch)
    #         else:
    #             small_documents.append(patch)

    #     if small_documents:
    #         small_patch_serializer = PatchStandardSerializer(data=small_documents, many=True)
    #         if small_patch_serializer.is_valid():
    #             small_patch_serializer.save()
    #         else:
    #             return JsonResponse(small_patch_serializer.errors, status=status.HTTP_400_BAD_REQUEST, safe=False)

    #     if large_documents:
    #         large_patch_serializer = PatchFileSerializer(data=large_documents, many=True)
    #         if large_patch_serializer.is_valid():
    #             large_patch_serializer.save()
    #         else:
    #             return JsonResponse(large_patch_serializer.errors, status=status.HTTP_400_BAD_REQUEST, safe=False)

    #     if large_content_documents:
    #         large_content_patch_serializer = PatchFileSerializer(data=large_content_documents, many=True)
    #         if large_content_patch_serializer.is_valid():
    #             large_content_patch_serializer.save()
    #         else:
    #             return JsonResponse(large_content_patch_serializer.errors, status=status.HTTP_400_BAD_REQUEST, safe=False)

    #     if large_diff_documents:
    #         large_diff_patch_serializer = PatchFileSerializer(data=large_diff_documents, many=True)
    #         if large_diff_patch_serializer.is_valid():
    #             large_diff_patch_serializer.save()
    #         else:
    #             return JsonResponse(large_diff_patch_serializer.errors, status=status.HTTP_400_BAD_REQUEST, safe=False)

    #     return HttpResponse('Post request processed.', status=status.HTTP_201_CREATED)


class CommentListView(generics.ListAPIView):

    queryset = Comments.objects.all()
    serializer_class = GetCommentSerializer
    filterset_class = CommentFilter
    search_fields = ['subject', 'msg_content']


class CommentCreateView(generics.CreateAPIView):

    queryset = Comments.objects.all()

    # override the get_serializer_class method
    def get_serializer_class(self):
        comment = self.request.data
        if comment['msg_content'] and len(comment['msg_content']) > SIZE_LIMIT:
            return CommentFileSerializer
        else:
            return CommentStandardSerializer

    # def post(self, request, format=None):

    #     comment_data = JSONParser().parse(request)
    #     small_documents = list()
    #     large_documents = list()

    #     if type(comment_data) != list:
    #         comment_data = [comment_data]

    #     for i in range(len(comment_data)):
    #         comment = comment_data[i]

    #         if comment['reply_to_msg_id'] and type(comment['reply_to_msg_id']) == list:
    #             comment['reply_to_msg_id'] = json.dumps(comment['reply_to_msg_id'])

    #         if comment['msg_content'] and len(comment['msg_content']) > SIZE_LIMIT:
    #             large_documents.append(comment)
    #         else:
    #             small_documents.append(comment)

    #     if small_documents:
    #         small_comment_serializer = CommentStandardSerializer(data=small_documents, many=True)
    #         if small_comment_serializer.is_valid():
    #             small_comment_serializer.save()
    #         else:
    #             return JsonResponse(small_comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST, safe=False)
    #     if large_documents:
    #         large_comment_serializer = CommentFileSerializer(data=large_documents, many=True)
    #         if large_comment_serializer.is_valid():
    #             large_comment_serializer.save()
    #         else:
    #             return JsonResponse(large_comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST, safe=False)

    #     return HttpResponse('Post request processed.', status=status.HTTP_201_CREATED)


class Change1ListView(generics.ListAPIView):

    queryset = Changes1.objects.all()
    serializer_class = Change1Serializer
    filterset_class = Change1Filter


class Change1CreateView(generics.CreateAPIView):

    queryset = Changes1.objects.all()
    serializer_class = Change1Serializer


class Change2ListView(generics.ListAPIView):

    queryset = Changes2.objects.all()
    serializer_class = Changes2
    filterset_class = Change2Filter


class Change2CreateView(generics.CreateAPIView):

    queryset = Changes2.objects.all()
    serializer_class = Change2Serializer


class UserListView(generics.ListAPIView):

    queryset = Changes2.objects.all()
    serializer_class = Changes2
    filterset_class = Change2Filter


class UserCreateView(generics.CreateAPIView):

    queryset = Users.objects.all()
    serializer_class = UserSerializer


class NewSeriesListView(generics.ListAPIView):

    queryset = NewSeries.objects.all()
    serializer_class = NewSeriesSerializer
    filterset_class = NewSeriesFilter


class NewSeriesCreateView(generics.CreateAPIView):

    queryset = NewSeries.objects.all()
    serializer_class = NewSeriesSerializer


class MailingListListView(generics.ListAPIView):

    queryset = MailingLists.objects.all()
    serializer_class = MailingListSerializer
    filterset_class = MailingListFilter


class MailingListCreateView(generics.CreateAPIView):

    queryset = MailingLists.objects.all()
    serializer_class = MailingListSerializer