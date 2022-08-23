from rest_framework import serializers 
from msr.models import *

class PeopleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = People
        fields = ('id',
                  'original_id',
                  'email',
                  'username',
                  'api_url')


class ProjectSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Project
        fields = ('id',
                  'original_id',
                  'name',
                  'repo_url',
                  'api_url',
                  'web_url',
                  'list_id',
                  'list_address',
                  'maintainers')


class SeriesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Series
        fields = ('id',
                  'original_id',
                  'name',
                  'created_date',
                  'version',
                  'total',
                  'received_total',
                  'cover_letter_content',
                  'api_url',
                  'web_url',
                  'project_original_id',
                  'submitter_original_id')


class ChangeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Change
        fields = ('id',
                  'status',
                  'parent_commit_id',
                  'merged_commit_id',
                  'commit_date',
                  'project_original_id',
                  'series_original_id')


class MailingListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MailingList
        fields = ('id',
                  'web_url',
                  'date',
                  'sender_email',
                  'subject',
                  'content',
                  'project_original_id')


class PatchSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Patch
        fields = ('id',
                  'original_id',
                  'name',
                  'state',
                  'date',
                  'msg_id',
                  'msg_content',
                  'code_diff',
                  'api_url',
                  'web_url',
                  'change_id',
                  'mailing_list_id',
                  'series_original_id',
                  'submitter_original_id',
                  'project_original_id')


class CommentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Comment
        fields = ('id',
                  'original_id',
                  'msg_id',
                  'msg_content',
                  'date',
                  'subject',
                  'reply_to_msg_id',
                  'web_url',
                  'change_id',
                  'mailing_list_id',
                  'submitter_original_id',
                  'patch_original_id',
                  'project_original_id')