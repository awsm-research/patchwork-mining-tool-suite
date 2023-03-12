import json
from symbol import import_as_name
from rest_framework import serializers
from patchwork import models
from django.db import connections
from gridfs import GridFS
from code_review_mining import settings
from bson import ObjectId
from patchwork.static.utils import TextFile


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
            'in_reply_to'
        )
        read_only_fields = fields


class CommentSerializer(serializers.ModelSerializer):

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
            'web_url'
        )
        read_only_fields = fields