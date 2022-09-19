from django.shortcuts import render
from patchwork.utils.text_file import TextFile
from patchwork.models import *
from patchwork.serializers import *
from rest_framework.parsers import JSONParser
from datetime import datetime, timezone
from django.http.response import JsonResponse, HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view

# Create your views here.
def example_view(request):
    return render(request, 'patchwork/example.html')

@api_view(['POST'])
def account_list(request):
    if request.method == 'POST':
        account_data = JSONParser().parse(request)
        account_serializer = AccountSerializer(data=account_data)
        if account_serializer.is_valid():
            account_serializer.save()
            return JsonResponse(account_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(account_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def project_list(request):
    if request.method == 'POST':
        project_data = JSONParser().parse(request)
        project_serializer = ProjectSerializer(data=project_data)
        if project_serializer.is_valid():
            project_serializer.save()
            return JsonResponse(project_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(project_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def series_list(request):
    if request.method == 'POST':
        series_data = JSONParser().parse(request)
        
        series_cover_letter = series_data['cover_letter_content']
        
        idx = Series.objects.count() + 1
        series_obj = Series(
            id = idx,
            original_id = series_data['original_id'],
            name = series_data['name'],
            created_date = series_data['created_date'],
            version = series_data['version'],
            total = series_data['total'],
            received_total = series_data['received_total'],
            # cover_letter_content = series_data['cover_letter_content'],
            api_url = series_data['api_url'],
            web_url = series_data['web_url'],
            project_original_id = series_data['project_original_id'],
            submitter_account_original_id = series_data['submitter_account_original_id'],
            submitter_user_id = series_data['submitter_user_id']
        )

        if series_cover_letter and len(series_cover_letter) > 16793600:
            with open(f"temp_file-series_cover_letter.txt", "w") as f:
                f.write(series_cover_letter)
            with open(f"temp_file-series_cover_letter.txt", "rb") as f:
                series_obj.cover_letter_content = TextFile(f, name=f"{series_data['original_id']}-cover_letter_content.txt")
                series_obj.save()
        else:
            series_obj.cover_letter_content = series_cover_letter
            series_obj.save()

        return HttpResponse("series post success")



@api_view(['POST'])
def patch_list(request):
    if request.method == 'POST':
        patch_data = JSONParser().parse(request)

        item_date = datetime.strptime(patch_data['date'], '%Y-%m-%d %H:%M:%S')
        new_item_date = item_date.replace(tzinfo=timezone.utc)

        patch_msg_content = patch_data['msg_content']
        patch_code_diff = patch_data['code_diff']

        idx = Patches.objects.count() + 1
        patch_obj = Patches(
            id = idx,
            original_id = patch_data['original_id'],
            name = patch_data['name'],
            state = patch_data['state'],
            date = new_item_date,
            msg_id = patch_data['msg_id'],
            # msg_content = patch_data['msg_content'],
            # code_diff = patch_data['code_diff'],
            api_url = patch_data['api_url'],
            web_url = patch_data['web_url'],
            commit_ref = patch_data['commit_ref'],
            change_id1 = None,
            change_id2 = None,
            mailing_list_id = None,
            series_original_id = patch_data['series_original_id'],
            submitter_account_original_id = patch_data['submitter_account_original_id'],
            submitter_user_id = None,
            project_original_id = patch_data['project_original_id'],
        )

        if (patch_msg_content and len(patch_msg_content) > 16793600) and (patch_code_diff and len(patch_code_diff) > 16793600):
            with open(f"temp_file-patch_msg_content.txt", "w") as f:
                f.write(patch_msg_content)

            with open(f"tmp_file-patch_code_diff.txt", "w") as f:
                f.write(patch_code_diff)

            f_msg = open(f"temp_file-patch_msg_content.txt", "rb")
            patch_obj.msg_content = TextFile(f_msg, name=f"{patch_data['original_id']}-msg_content")

            f_code = open(f"tmp_file-patch_code_diff.txt", "rb")
            patch_obj.code_diff = TextFile(f_code, name=f"{patch_data['original_id']}-code_diff")

            patch_obj.save()

            f_msg.close()
            f_code.close()

        elif patch_msg_content and len(patch_msg_content) > 16793600:
            patch_obj.code_diff = patch_code_diff

            with open(f"tmp_file-patch_msg_content.txt", "w") as f:
                f.write(patch_msg_content)
            with open(f"tmp_file-patch_msg_content.txt", "rb") as f:
                patch_obj.msg_content = TextFile(f, name=f"{patch_data['original_id']}-msg_content")
                patch_obj.save()

        elif patch_code_diff and len(patch_code_diff) > 16793600:
            patch_obj.msg_content = patch_msg_content

            with open(f"tmp_file-patch_code_diff.txt", "w") as f:
                f.write(patch_code_diff)
            with open(f"tmp_file-patch_code_diff.txt", "rb") as f:
                patch_obj.code_diff = TextFile(f, name=f"{patch_data['original_id']}-code_diff")
                patch_obj.save()

        else:
            patch_obj.msg_content = patch_msg_content
            patch_obj.code_diff = patch_code_diff
            patch_obj.save()

        return HttpResponse("patch post success")

@api_view(['POST'])
def comment_list(request):
    if request.method == 'POST':
        comment_data = JSONParser().parse(request)

        item_date = datetime.strptime(comment_data['date'], '%Y-%m-%d %H:%M:%S')
        new_item_date = item_date.replace(tzinfo=timezone.utc)

        comment_msg_content = comment_data['msg_content']

        idx = Comments.objects.count() + 1
        comment_obj = Comments(
            id = idx,
            original_id = comment_data['original_id'],
            msg_id = comment_data['msg_id'],
            # msg_content = comment_data['msg_content'],
            date = new_item_date,
            subject = comment_data['subject'],
            reply_to_msg_id = comment_data['reply_to_msg_id'],
            web_url = comment_data['web_url'],
            change_id1 = None,
            change_id2 = None,
            mailing_list_id = None,
            submitter_account_original_id = comment_data['submitter_account_original_id'],
            submitter_user_id = None,
            patch_original_id = comment_data['patch_original_id'],
            project_original_id = comment_data['project_original_id'],
        )

        if comment_msg_content and len(comment_msg_content) > 16793600:
            with open(f"tmp_file-comment_msg_content.txt", "w") as f:
                f.write(comment_msg_content)
            with open(f"tmp_file-comment_msg_content.txt", "rb") as f:
                comment_obj.msg_content = TextFile(f, name=f"{comment_data['original_id']}-msg_content")
                comment_obj.save()
        else:
            comment_obj.msg_content = comment_msg_content
            comment_obj.save()
        
        return HttpResponse("comment post success")