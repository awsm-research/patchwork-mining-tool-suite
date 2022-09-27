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
        # if type(account_data) != list:
        #     account_data = [account_data]
        account_serializer = AccountSerializer(data=account_data)
        if account_serializer.is_valid():
            account_serializer.save()
            return HttpResponse('post completed', status=201)
        
        return JsonResponse(account_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

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
        if type(project_data) != list:
            project_data = [project_data]
        project_serializer = ProjectSerializer(data=project_data, many=True)
        if project_serializer.is_valid():
            project_serializer.save()
            return HttpResponse('post completed', status=201)
        return JsonResponse(project_serializer.errors, status=status.HTTP_400_BAD_REQUEST, safe=False)

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

        if type(series_data) == list:
            small_series_data = list()
            large_series_data = list()

            for i in range(len(series_data)):
                
                item_date = datetime.strptime(series_data[i]['date'], '%Y-%m-%d %H:%M:%S')
                new_item_date = item_date.replace(tzinfo=timezone.utc)
                series_data[i]['date'] = new_item_date

                series_cover_letter = series_data[i]['cover_letter_content']

                if series_cover_letter and len(series_cover_letter) > SIZE_LIMIT:
                    large_series_data.append(series_data[i])
                else:
                    small_series_data.append(series_data[i])

            # insert small patch data
            series_serializer = SeriesStandardSerializer(data=small_series_data, many=True)
            if series_serializer.is_valid():
                series_serializer.save()

                # if large comments exist, return them back and the layer will then post them separately
                return JsonResponse(large_series_data, status=status.HTTP_201_CREATED, safe=False)
            else:
                return JsonResponse(series_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            series_cover_letter = series_data['cover_letter_content']

            if series_cover_letter and len(series_cover_letter) > SIZE_LIMIT:
                series_data['cover_letter_content'] = TextFile(series_cover_letter.encode(), name=f"{series_data['original_id']}-cover_letter_content.txt")

                series_serializer = SeriesContentFileSerializer(data=series_data)
                if series_serializer.is_valid():
                    series_serializer.save()
                    return HttpResponse('post completed', status=201)
            else:
                series_serializer = SeriesStandardSerializer(data=series_data)
                if series_serializer.is_valid():
                    series_serializer.save()
                    return JsonResponse('post completed', status=201)

            return JsonResponse(series_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

        # separate small patch data and large patch data
        if type(patch_data) == list:
            small_patch_data = list()
            large_patch_data = list()

            for i in range(len(patch_data)):
                item_date = datetime.strptime(patch_data[i]['date'], '%Y-%m-%d %H:%M:%S')
                new_item_date = item_date.replace(tzinfo=timezone.utc)
                patch_data[i]['date'] = new_item_date

                patch_msg_content = patch_data[i]['msg_content']
                patch_code_diff = patch_data[i]['code_diff']

                if (patch_msg_content and len(patch_msg_content) > SIZE_LIMIT) or (patch_code_diff and len(patch_code_diff) > SIZE_LIMIT):
                    large_patch_data.append(patch_data[i])
                else:
                    small_patch_data.append(patch_data[i])

            # insert small patch data
            patch_serializer = PatchStandardSerializer(data=small_patch_data, many=True)
            if patch_serializer.is_valid():

                patch_serializer.save()

                # if large patches exist, return them back and the layer will then post them separately
                return JsonResponse(large_patch_data, status=status.HTTP_201_CREATED, safe=False)
            else:
                return JsonResponse(patch_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        else:
            patch_msg_content = patch_data['msg_content']
            patch_code_diff = patch_data['code_diff']

            if (patch_msg_content and len(patch_msg_content) > SIZE_LIMIT) and (patch_code_diff and len(patch_code_diff) > SIZE_LIMIT):
                
                patch_data['msg_content'] = TextFile(patch_msg_content.encode(), name=f"{patch_data['original_id']}-msg_content.txt")
                patch_data['code_diff'] = TextFile(patch_code_diff.encode(), name=f"{patch_data['original_id']}-code_diff.txt")

                patch_serializer = PatchFileSerializer(data=patch_data)
                if patch_serializer.is_valid():
                    patch_serializer.save()
                    return HttpResponse('post completed', status=201)

            elif patch_msg_content and len(patch_msg_content) > SIZE_LIMIT:
                patch_data['msg_content'] = TextFile(patch_msg_content.encode(), name=f"{patch_data['original_id']}-msg_content.txt")
                
                patch_serializer = PatchContentFileSerializer(data=patch_data)
                if patch_serializer.is_valid():
                    patch_serializer.save()
                    return HttpResponse('post completed', status=201)

            elif patch_code_diff and len(patch_code_diff) > SIZE_LIMIT:
                patch_data['code_diff'] = TextFile(patch_code_diff.encode(), name=f"{patch_data['original_id']}-code_diff.txt")
                
                patch_serializer = PatchDiffFileSerializer(data=patch_data)
                if patch_serializer.is_valid():
                    patch_serializer.save()
                    return HttpResponse('post completed', status=201)
            else:
                patch_serializer = PatchStandardSerializer(data=patch_data)
                if patch_serializer.is_valid():
                    patch_serializer.save()
                    return HttpResponse('post completed', status=201)

            return JsonResponse(patch_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

        if type(comment_data) == list:
            small_comment_data = list()
            large_comment_data = list()

            for i in range(len(comment_data)):
                item_date = datetime.strptime(comment_data[i]['date'], '%Y-%m-%d %H:%M:%S')
                new_item_date = item_date.replace(tzinfo=timezone.utc)
                comment_data[i]['date'] = new_item_date

                comment_msg_content = comment_data[i]['msg_content']

                if comment_msg_content and len(comment_msg_content) > SIZE_LIMIT:
                    large_comment_data.append(comment_data[i])
                else:
                    small_comment_data.append(comment_data[i])

            # insert small patch data
            comment_serializer = CommentStandardSerializer(data=small_comment_data, many=True)
            if comment_serializer.is_valid():
                comment_serializer.save()

                # if large comments exist, return them back and the layer will then post them separately
                return JsonResponse(large_comment_data, status=status.HTTP_201_CREATED, safe=False)
            else:
                return JsonResponse(comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            item_date = datetime.strptime(comment_data['date'], '%Y-%m-%d %H:%M:%S')
            new_item_date = item_date.replace(tzinfo=timezone.utc)
            comment_data['date'] = new_item_date
            
            comment_msg_content = comment_data['msg_content']

            if comment_msg_content and len(comment_msg_content) > SIZE_LIMIT:
                comment_data['msg_content'] = TextFile(comment_msg_content.encode(), name=f"{comment_data['original_id']}-msg_content.txt")

                comment_serializer = CommentContentFileSerializer(data=comment_data)
                if comment_serializer.is_valid():
                    comment_serializer.save()
                    return HttpResponse('post completed', status=201)
            else:
                comment_serializer = CommentStandardSerializer(data=comment_data)
                if comment_serializer.is_valid():
                    comment_serializer.save()
                    HttpResponse('post completed', status=201)
            
            return JsonResponse(comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

