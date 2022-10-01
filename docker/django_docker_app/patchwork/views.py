from django.shortcuts import render
from django.http.response import JsonResponse, HttpResponse
from django.db.models import Q

from patchwork.static.utils import TextFile, UndefinedArg
from patchwork.models import *
from patchwork.serializers import *
from datetime import datetime, timezone

from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
# from rest_framework.decorators import api_view

SIZE_LIMIT = 16793600

# Create your views here.
def home_view(request):
    return render(request, 'patchwork/home.html')

class AccountList(APIView):

    def get(self, request, format=None):
        accounts = Accounts.objects.all()

        endpoint_type = request.GET.get("endpoint_type", UndefinedArg())
        username = request.GET.get("username", UndefinedArg())
        email = request.GET.get("email", UndefinedArg())

        query_conditions = Q()
        if not isinstance(endpoint_type, UndefinedArg):
            query_conditions &= Q(original_id__icontains=endpoint_type)
        if not isinstance(username, UndefinedArg):
            query_conditions &= Q(username__iexact=username)
        if not isinstance(email, UndefinedArg):
            query_conditions &= Q(email__iexact=email)
        
        accounts = accounts.filter(query_conditions)

        account_serializer = AccountSerializer(accounts, many=True)
        return JsonResponse(account_serializer.data, safe=False)

    def post(self, request, format=None):
        account_data = JSONParser().parse(request)
        is_many = True if type(account_data) == list else False
        account_serializer = AccountSerializer(data=account_data, many=is_many)

        if account_serializer.is_valid():
            account_serializer.save()
            return JsonResponse(account_serializer.data, status=status.HTTP_201_CREATED, safe=(not is_many))
        
        return JsonResponse(account_serializer.errors, status=status.HTTP_400_BAD_REQUEST, safe=(not is_many))
    

class ProjectList(APIView):
    def get(self, request, format=None):
        projects = Projects.objects.all()

        endpoint_type = request.GET.get("endpoint_type", UndefinedArg())
        project_name = request.GET.get("name", UndefinedArg())

        query_conditions = Q()
        if not isinstance(endpoint_type, UndefinedArg):
            query_conditions &= Q(original_id__icontains=endpoint_type)
        if not isinstance(project_name, UndefinedArg):
            query_conditions &= Q(name__iexact=project_name)

        projects = projects.filter(query_conditions)

        project_serializer = ProjectSerializer(projects, many=True)
        return JsonResponse(project_serializer.data, safe=False)

    def post(self, request, format=None):
        project_data = JSONParser().parse(request)
        is_many = True if type(project_data) == list else False
        project_serializer = ProjectSerializer(data=project_data, many=is_many)

        if project_serializer.is_valid():
            project_serializer.save()
            return JsonResponse(project_serializer.data, status=status.HTTP_201_CREATED, safe=(not is_many))

        return JsonResponse(project_serializer.errors, status=status.HTTP_400_BAD_REQUEST, safe=(not is_many))

# how to retrieve: get all -> separate docs with and without files
class SeriesList(APIView):
    def get(self, request, format=None):
        series = Series.objects.all()

        endpoint_type = request.GET.get("endpoint_type", UndefinedArg())
        series_name = request.GET.get("name", UndefinedArg())
        project_org_id = request.GET.get("project_original_id", UndefinedArg())
        submitter_account_original_id = request.GET.get("submitter_account_original_id", UndefinedArg())
        submitter_user_id = request.GET.get("submitter_user_id", UndefinedArg())

        query_conditions = Q()
        if not isinstance(endpoint_type, UndefinedArg):
            query_conditions &= Q(original_id__icontains=endpoint_type)
        if not isinstance(series_name, UndefinedArg):
            query_conditions &= Q(name__iexact=series_name)
        if not isinstance(project_org_id, UndefinedArg):
            query_conditions &= Q(project_original_id__iexact=project_org_id)
        if not isinstance(submitter_account_original_id, UndefinedArg):
            query_conditions &= Q(submitter_account_original_id__iexact=submitter_account_original_id)
        if not isinstance(submitter_user_id, UndefinedArg):
            query_conditions &= Q(submitter_user_id__iexact=submitter_user_id)
        
        series = series.filter(query_conditions)

        series_serializer = GetSeriesSerializer(series, many=True)
        return JsonResponse(series_serializer.data, safe=False)

    def post(self, request, format=None):
        series_data = JSONParser().parse(request)
        large_documents = list()
        small_documents = list()

        if type(series_data) != list:
            series_data = [series_data]

        for i in range(len(series_data)):
            series = series_data[i]
            if series['cover_letter_content'] and len(series['cover_letter_content']) > SIZE_LIMIT:
                large_documents.append(series)
            else:
                small_documents.append(series)

        if small_documents:
            small_series_serializer = SeriesStandardSerializer(data=small_documents, many=True)
            if small_series_serializer.is_valid():
                small_series_serializer.save()
            else:
                return JsonResponse(small_series_serializer.errors, status=status.HTTP_400_BAD_REQUEST, safe=False)
        if large_documents:
            large_series_serializer = SeriesFileSerializer(data=large_documents, many=True)
            if large_series_serializer.is_valid():
                large_series_serializer.save()
            else:
                return JsonResponse(large_series_serializer.errors, status=status.HTTP_400_BAD_REQUEST, safe=False)

        return HttpResponse('Post request processed.', status=status.HTTP_201_CREATED)


class PatchList(APIView):
    def get(self, request, format=None):
        patches = Patches.objects.all()

        endpoint_type = request.GET.get("endpoint_type", UndefinedArg())
        patch_name = request.GET.get("name", UndefinedArg())
        state = request.GET.get("state", UndefinedArg())
        change_id1 = request.GET.get("change_id1", UndefinedArg())
        change_id2 = request.GET.get("change_id2", UndefinedArg())
        mailing_list_id = request.GET.get("mailing_list_id", UndefinedArg())
        series_original_id = request.GET.get("series_original_id", UndefinedArg())
        new_series_id = request.GET.get("new_series_id", UndefinedArg())
        submitter_account_original_id = request.GET.get("submitter_account_original_id", UndefinedArg())
        submitter_user_id = request.GET.get("submitter_user_id", UndefinedArg())
        project_original_id = request.GET.get("project_original_id", UndefinedArg())

        query_conditions = Q()
        if not isinstance(endpoint_type, UndefinedArg):
            query_conditions &= Q(original_id__icontains=endpoint_type)
        if not isinstance(patch_name, UndefinedArg):
            query_conditions &= Q(name__iexact=patch_name)
        if not isinstance(state, UndefinedArg):
            query_conditions &= Q(state__iexact=state)
        if not isinstance(change_id1, UndefinedArg):
            query_conditions &= Q(change_id1__iexact=change_id1)
        if not isinstance(change_id2, UndefinedArg):
            query_conditions &= Q(change_id2__iexact=change_id2)
        if not isinstance(mailing_list_id, UndefinedArg):
            query_conditions &= Q(mailing_list_id__iexact=mailing_list_id)
        if not isinstance(series_original_id, UndefinedArg):
            query_conditions &= Q(series_original_id__iexact=series_original_id)
        if not isinstance(new_series_id, UndefinedArg):
            query_conditions &= Q(new_series_id_iexact=new_series_id)
        if not isinstance(submitter_account_original_id, UndefinedArg):
            query_conditions &= Q(submitter_account_original_id__iexact=submitter_account_original_id)
        if not isinstance(submitter_user_id, UndefinedArg):
            query_conditions &= Q(submitter_user_id_iexact=submitter_user_id)
        if not isinstance(project_original_id, UndefinedArg):
            query_conditions &= Q(project_original_id_iexact=project_original_id)
        
        patches = patches.filter(query_conditions)

        patch_serializer = GetPatchSerializer(patches, many=True)
        return JsonResponse(patch_serializer.data, safe=False)


    def post(self, request, format=None):
        
        patch_data = JSONParser().parse(request)
        small_documents = list()
        large_documents = list()
        large_content_documents = list()
        large_diff_documents = list()

        if type(patch_data) != list:
            patch_data = [patch_data]

        for i in range(len(patch_data)):
            patch = patch_data[i]

            if patch['reply_to_msg_id']:
                patch['reply_to_msg_id'] = str(patch['reply_to_msg_id'])

            if (patch['msg_content'] and len(patch['msg_content']) > SIZE_LIMIT) and (patch['code_diff'] and len(patch['code_diff']) > SIZE_LIMIT):
                large_documents.append(patch)
            elif patch['msg_content'] and len(patch['msg_content']) > SIZE_LIMIT:
                large_content_documents.append(patch)
            elif patch['code_diff'] and len(patch['code_diff']) > SIZE_LIMIT:
                large_diff_documents.append(patch)
            else:
                small_documents.append(patch)

        if small_documents:
            small_patch_serializer = PatchStandardSerializer(data=small_documents, many=True)
            if small_patch_serializer.is_valid():
                small_patch_serializer.save()
            else:
                return JsonResponse(small_patch_serializer.errors, status=status.HTTP_400_BAD_REQUEST, safe=False)

        if large_documents:
            large_patch_serializer = PatchFileSerializer(data=large_documents, many=True)
            if large_patch_serializer.is_valid():
                large_patch_serializer.save()
            else:
                return JsonResponse(large_patch_serializer.errors, status=status.HTTP_400_BAD_REQUEST, safe=False)

        if large_content_documents:
            large_content_patch_serializer = PatchFileSerializer(data=large_content_documents, many=True)
            if large_content_patch_serializer.is_valid():
                large_content_patch_serializer.save()
            else:
                return JsonResponse(large_content_patch_serializer.errors, status=status.HTTP_400_BAD_REQUEST, safe=False)

        if large_diff_documents:
            large_diff_patch_serializer = PatchFileSerializer(data=large_diff_documents, many=True)
            if large_diff_patch_serializer.is_valid():
                large_diff_patch_serializer.save()
            else:
                return JsonResponse(large_diff_patch_serializer.errors, status=status.HTTP_400_BAD_REQUEST, safe=False)

        return HttpResponse('Post request processed.', status=status.HTTP_201_CREATED)


class CommentList(APIView):
    def get(self, request, format=None):
        comments = Comments.objects.all()

        endpoint_type = request.GET.get("endpoint_type", UndefinedArg())
        subject = request.GET.get("subject", UndefinedArg())
        change_id1 = request.GET.get("change_id1", UndefinedArg())
        change_id2 = request.GET.get("change_id2", UndefinedArg())
        mailing_list_id = request.GET.get("mailing_list_id", UndefinedArg())
        submitter_account_original_id = request.GET.get("submitter_account_original_id", UndefinedArg())
        submitter_user_id = request.GET.get("submitter_user_id", UndefinedArg())
        patch_original_id = request.GET.get("patch_original_id", UndefinedArg())
        project_original_id = request.GET.get("project_original_id", UndefinedArg())

        query_conditions = Q()
        if not isinstance(endpoint_type, UndefinedArg):
            query_conditions &= Q(original_id__icontains=endpoint_type)
        if not isinstance(subject, UndefinedArg):
            query_conditions &= Q(subject_iexact=subject)
        if not isinstance(change_id1, UndefinedArg):
            query_conditions &= Q(change_id1__iexact=change_id1)
        if not isinstance(change_id2, UndefinedArg):
            query_conditions &= Q(change_id2__iexact=change_id2)
        if not isinstance(mailing_list_id, UndefinedArg):
            query_conditions &= Q(mailing_list_id__iexact=mailing_list_id)
        if not isinstance(submitter_account_original_id, UndefinedArg):
            query_conditions &= Q(submitter_account_original_id__iexact=submitter_account_original_id)
        if not isinstance(submitter_user_id, UndefinedArg):
            query_conditions &= Q(submitter_user_id_iexact=submitter_user_id)
        if not isinstance(patch_original_id, UndefinedArg):
            query_conditions &= Q(patch_original_id__iexact=patch_original_id)
        if not isinstance(project_original_id, UndefinedArg):
            query_conditions &= Q(project_original_id_iexact=project_original_id)
        
        comments = comments.filter(query_conditions)

        comment_serializer = GetCommentSerializer(comments, many=True)
        return JsonResponse(comment_serializer.data, safe=False)

    def post(self, request, format=None):

        comment_data = JSONParser().parse(request)
        small_documents = list()
        large_documents = list()

        if type(comment_data) != list:
            comment_data = [comment_data]

        for i in range(len(comment_data)):
            comment = comment_data[i]

            if comment['reply_to_msg_id']:
                comment['reply_to_msg_id'] = str(comment['reply_to_msg_id'])

            if comment['msg_content'] and len(comment['msg_content']) > SIZE_LIMIT:
                large_documents.append(comment)
            else:
                small_documents.append(comment)

        if small_documents:
            small_comment_serializer = CommentStandardSerializer(data=small_documents, many=True)
            if small_comment_serializer.is_valid():
                small_comment_serializer.save()
            else:
                return JsonResponse(small_comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST, safe=False)
        if large_documents:
            large_comment_serializer = CommentFileSerializer(data=large_documents, many=True)
            if large_comment_serializer.is_valid():
                large_comment_serializer.save()
            else:
                return JsonResponse(large_comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST, safe=False)

        return HttpResponse('Post request processed.', status=status.HTTP_201_CREATED)


class MailingListList(APIView):
    def get(self, request, format=None):
        pass

    def post(self, request, format=None):
        pass


class Change1List(APIView):
    def get(self, request, format=None):
        pass

    def post(self, request, format=None):
        pass


class Change2List(APIView):
    def get(self, request, format=None):
        pass

    def post(self, request, format=None):
        pass


class UserList(APIView):
    def get(self, request, format=None):
        pass

    def post(self, request, format=None):
        pass


class NewSeriesList(APIView):
    def get(self, request, format=None):
        pass

    def post(self, request, format=None):
        pass

