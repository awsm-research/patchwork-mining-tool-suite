from django.shortcuts import render
from patchwork.utils.text_file import TextFile
from patchwork.models import *
from patchwork.serializers import *
from rest_framework.parsers import JSONParser
from datetime import datetime, timezone
from django.http.response import JsonResponse, HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view

SIZE_LIMIT = 16793600

# Create your views here.
def example_view(request):
    return render(request, 'patchwork/example.html')

@api_view(['POST'])
def account_list(request):
    if request.method == 'POST':
        account_data = JSONParser().parse(request)
        if type(account_data) != list:
            account_data = [account_data]
        account_serializer = AccountSerializer(data=account_data, many=True)
        if account_serializer.is_valid():
            account_serializer.save()
            return JsonResponse(account_serializer.data, status=status.HTTP_201_CREATED, safe=False)
        
        return JsonResponse(account_serializer.errors, status=status.HTTP_400_BAD_REQUEST, safe=False)


@api_view(['POST'])
def project_list(request):
    if request.method == 'POST':
        project_data = JSONParser().parse(request)
        if type(project_data) != list:
            project_data = [project_data]
        project_serializer = ProjectSerializer(data=project_data, many=True)
        if project_serializer.is_valid():
            project_serializer.save()
            return JsonResponse(project_serializer.data, status=status.HTTP_201_CREATED, safe=False)
        return JsonResponse(project_serializer.errors, status=status.HTTP_400_BAD_REQUEST, safe=False)


@api_view(['POST'])
def series_list(request):
    if request.method == 'POST':
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
                with open(f"temp_file-series_cover_letter.txt", "w") as f:
                    f.write(series_cover_letter)
                with open(f"temp_file-series_cover_letter.txt", "rb") as f:
                    series_data['cover_letter_content'] = TextFile(f, name=f"{series_data['original_id']}-cover_letter_content")
                    # series_obj.save()

                    series_serializer = SeriesContentFileSerializer(data=series_data)
                    if series_serializer.is_valid():
                        series_serializer.save()
                        return JsonResponse(series_serializer.data, status=status.HTTP_201_CREATED)
            else:
                series_serializer = SeriesStandardSerializer(data=series_data)
                if series_serializer.is_valid():
                    series_serializer.save()
                    return JsonResponse(series_serializer.data, status=status.HTTP_201_CREATED)

            return JsonResponse(series_serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def patch_list(request):

    if request.method == 'POST':
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
                with open(f"temp_file-patch_msg_content.txt", "w") as f:
                    f.write(patch_msg_content)

                with open(f"tmp_file-patch_code_diff.txt", "w") as f:
                    f.write(patch_code_diff)

                f_msg = open(f"temp_file-patch_msg_content.txt", "rb")
                patch_data['msg_content'] = TextFile(f_msg, name=f"{patch_data['original_id']}-msg_content")

                f_code = open(f"tmp_file-patch_code_diff.txt", "rb")
                patch_data['code_diff'] = TextFile(f_code, name=f"{patch_data['original_id']}-code_diff")

                patch_serializer = PatchFileSerializer(data=patch_data)
                if patch_serializer.is_valid():
                    patch_serializer.save()
                    f_msg.close()
                    f_code.close()
                    return HttpResponse('post completed', status=201)

            elif patch_msg_content and len(patch_msg_content) > SIZE_LIMIT:
                with open(f"tmp_file-patch_msg_content.txt", "w") as f:
                    f.write(patch_msg_content)
                with open(f"tmp_file-patch_msg_content.txt", "rb") as f:
                    patch_data['msg_content'] = TextFile(f, name=f"{patch_data['original_id']}-msg_content")
                    
                    patch_serializer = PatchContentFileSerializer(data=patch_data)
                    if patch_serializer.is_valid():
                        patch_serializer.save()
                        return HttpResponse('post completed', status=201)

            elif patch_code_diff and len(patch_code_diff) > SIZE_LIMIT:
                with open(f"tmp_file-patch_code_diff.txt", "w") as f:
                    f.write(patch_code_diff)
                with open(f"tmp_file-patch_code_diff.txt", "rb") as f:
                    patch_data['code_diff'] = TextFile(f, name=f"{patch_data['original_id']}-code_diff")

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

@api_view(['POST'])
def comment_list(request):
    if request.method == 'POST':
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
                with open(f"tmp_file-comment_msg_content.txt", "w") as f:
                    f.write(comment_msg_content)
                with open(f"tmp_file-comment_msg_content.txt", "rb") as f:
                    comment_data['msg_content'] = TextFile(f, name=f"{comment_data['original_id']}-msg_content")

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