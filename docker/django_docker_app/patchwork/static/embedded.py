import json
from rest_framework import serializers
from patchwork import models
from django.db import connections
from gridfs import GridFS


class IdentitySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Identity
        fields = ('id', 'original_id', 'email', 'name', 'api_url')
        read_only_fields = fields


class IndividualSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Individual
        fields = ('id', 'original_id', 'project')
        read_only_fields = fields


class MaintainerSerializer(serializers.ModelSerializer):
    individual = IndividualSerializer(many=True, read_only=True)

    class Meta:
        model = models.Identity
        fields = ('id', 'original_id', 'email', 'name', 'api_url', 'individual')
        read_only_fields = fields


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Project
        fields = ('id', 'original_id', 'name', 'repository_url', 'api_url', 'web_url', 'list_id', 'list_address')
        read_only_fields = fields


class PatchSerializer(serializers.ModelSerializer):

    msg_content = serializers.CharField(allow_blank=True, allow_null=True)
    code_diff = serializers.CharField(allow_blank=True, allow_null=True)

    submitter_identity = serializers.SlugRelatedField(slug_field="original_id", read_only=True)
    submitter_individual = serializers.SlugRelatedField(slug_field="original_id", read_only=True)

    class Meta:
        model = models.Patch
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
            'in_reply_to',
            'submitter_identity',
            'submitter_individual'
        )
        read_only_fields = fields
    
    def to_representation(self, instance):
        data = super().to_representation(instance)

        try:
            in_reply_to = json.loads(data['in_reply_to'])
        except:
            in_reply_to = data['in_reply_to']

        data['in_reply_to'] = in_reply_to

        db = connections['default'].connection

        if data['msg_content'] == f"patch_msg_content/{data['original_id']}-msg_content.txt":
            content_fs = GridFS(db, 'textfiles.patch_msg_content')
            content_file_content = content_fs.find_one({"filename": f"{data['original_id']}-msg_content.txt"}).read().decode()
            data['msg_content'] = content_file_content

        if data['code_diff'] == f"patch_code_diff/{data['original_id']}-code_diff.txt":
            diff_fs = GridFS(db, 'textfiles.patch_code_diff')
            diff_file_content = diff_fs.find_one({"filename": f"{data['original_id']}-code_diff.txt"}).read().decode()
            if diff_file_content == 'mongodb_gridfs_code_review_empty_file':
                diff_file_content = ''
            data['code_diff'] = diff_file_content

        return data



class CommentSerializer(serializers.ModelSerializer):
    
    msg_content = serializers.CharField(allow_blank=True, allow_null=True)

    submitter_identity = serializers.SlugRelatedField(slug_field="original_id", read_only=True)
    submitter_individual = serializers.SlugRelatedField(slug_field="original_id", read_only=True)

    class Meta:
        model = models.Comment
        fields = (
            'id',
            'original_id', 
            'msg_id', 
            'msg_content', 
            'date', 
            'subject',
            'in_reply_to',
            'submitter_identity',
            'submitter_individual',
            'web_url'
        )
        read_only_fields = fields