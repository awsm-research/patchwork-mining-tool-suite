from rest_framework import serializers
from patchwork.models import *

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