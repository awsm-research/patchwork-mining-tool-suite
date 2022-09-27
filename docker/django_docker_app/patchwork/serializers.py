import re
from symbol import import_as_name
from rest_framework import serializers
from patchwork.models import *
from django.db import connections
from gridfs import GridFS
from code_review_mining import settings
from bson import ObjectId


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Accounts
        fields = (
            'id',
            'original_id',
            'email',
            'username',
            'api_url',
            'user_id'
        )


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Projects
        fields = (
            'id',
            'original_id',
            'name',
            'repository_url',
            'api_url',
            'web_url',
            'list_id',
            'list_address',
            'maintainer_account_original_id',
            'maintainer_user_id'
        )


class SeriesStandardSerializer(serializers.ModelSerializer):
    cover_letter_content = serializers.CharField(allow_blank=True, allow_null=True)

    class Meta:
        model = Series
        fields = (
            'id',
            'original_id',
            'name',
            'date',
            'version',
            'total',
            'received_total',
            'cover_letter_msg_id',
            'cover_letter_content',
            'api_url',
            'web_url',
            'project_original_id',
            'submitter_account_original_id',
            'submitter_user_id'
        )


class SeriesContentFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Series
        fields = (
            'id',
            'original_id',
            'name',
            'date',
            'version',
            'total',
            'received_total',
            'cover_letter_msg_id',
            'cover_letter_content',
            'api_url',
            'web_url',
            'project_original_id',
            'submitter_account_original_id',
            'submitter_user_id'
        )


class PatchStandardSerializer(serializers.ModelSerializer):
    msg_content = serializers.CharField(allow_blank=True, allow_null=True)
    code_diff = serializers.CharField(allow_blank=True, allow_null=True)

    class Meta:
        model = Patches
        fields = (
            'id',
            'original_id',
            'name',
            'state',
            'date',
            'msg_id',
            'msg_content',
            'code_diff',
            'api_url',
            'web_url',
            'commit_ref',
            'reply_to_msg_id',
            'change_id1',
            'change_id2',
            'mailing_list_id',
            'series_original_id',
            'new_series_id',
            'submitter_account_original_id',
            'submitter_user_id',
            'project_original_id'
        )


class PatchContentFileSerializer(serializers.ModelSerializer):
    code_diff = serializers.CharField(allow_blank=True, allow_null=True)

    class Meta:
        model = Patches
        fields = (
            'id',
            'original_id',
            'name',
            'state',
            'date',
            'msg_id',
            'msg_content',
            'code_diff',
            'api_url',
            'web_url',
            'commit_ref',
            'reply_to_msg_id',
            'change_id1',
            'change_id2',
            'mailing_list_id',
            'series_original_id',
            'new_series_id',
            'submitter_account_original_id',
            'submitter_user_id',
            'project_original_id'
        )


class PatchDiffFileSerializer(serializers.ModelSerializer):
    msg_content = serializers.CharField(allow_blank=True, allow_null=True)

    class Meta:
        model = Patches
        fields = (
            'id',
            'original_id',
            'name',
            'state',
            'date',
            'msg_id',
            'msg_content',
            'code_diff',
            'api_url',
            'web_url',
            'commit_ref',
            'reply_to_msg_id',
            'change_id1',
            'change_id2',
            'mailing_list_id',
            'series_original_id',
            'new_series_id',
            'submitter_account_original_id',
            'submitter_user_id',
            'project_original_id'
        )

class PatchFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Patches
        fields = (
            'id',
            'original_id',
            'name',
            'state',
            'date',
            'msg_id',
            'msg_content',
            'code_diff',
            'api_url',
            'web_url',
            'commit_ref',
            'reply_to_msg_id',
            'change_id1',
            'change_id2',
            'mailing_list_id',
            'series_original_id',
            'new_series_id',
            'submitter_account_original_id',
            'submitter_user_id',
            'project_original_id'
        )



class CommentStandardSerializer(serializers.ModelSerializer):
    msg_content = serializers.CharField(allow_blank=True, allow_null=True)

    class Meta:
        model = Comments
        fields = (
            'id',
            'original_id',
            'msg_id',
            'msg_content',
            'date',
            'subject',
            'reply_to_msg_id',
            'web_url',
            'change_id1',
            'change_id2',
            'mailing_list_id',
            'submitter_account_original_id',
            'submitter_user_id',
            'patch_original_id',
            'project_original_id'
        )


class CommentContentFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comments
        fields = (
            'id',
            'original_id',
            'msg_id',
            'msg_content',
            'date',
            'subject',
            'reply_to_msg_id',
            'web_url',
            'change_id1',
            'change_id2',
            'mailing_list_id',
            'submitter_account_original_id',
            'submitter_user_id',
            'patch_original_id',
            'project_original_id'
        )


class GetSeriesSerializer(SeriesStandardSerializer):

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if data['cover_letter_content'] == f"series_cover_letter_content/{data['original_id']}-cover_letter_content.txt":
            db = connections['default'].connection

            fs = GridFS(db, 'textfiles.series_cover_letter_content')

            file_content = fs.find_one({"filename": f"{data['original_id']}-cover_letter_content.txt"}).read().decode()
            data['cover_letter_content'] = file_content

        return data


class GetPatchSerializer(PatchStandardSerializer):

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if data['msg_content'] == f"patch_msg_content/{data['original_id']}-msg_content.txt":
            db = connections['default'].connection

            fs = GridFS(db, 'textfiles.patch_msg_content')

            file_content = fs.find_one({"filename": f"{data['original_id']}-msg_content.txt"}).read().decode()
            data['msg_content'] = file_content

        if data['code_diff'] == f"patch_code_diff/{data['original_id']}-code_diff.txt":
            db = connections['default'].connection

            fs = GridFS(db, 'textfiles.patch_code_diff')

            file_content = fs.find_one({"filename": f"{data['original_id']}-code_diff.txt"}).read().decode()
            data['code_diff'] = file_content

        return data


class GetCommentSerializer(CommentStandardSerializer):

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if data['msg_content'] == f"comment_msg_content/{data['original_id']}-msg_content.txt":
            db = connections['default'].connection

            fs = GridFS(db, 'textfiles.comment_msg_content')

            file_content = fs.find_one({"filename": f"{data['original_id']}-msg_content.txt"}).read().decode()
            data['msg_content'] = file_content

        return data
