import re
from symbol import import_as_name
from rest_framework import serializers
from patchwork.models import *
from django.db import connections
from gridfs import GridFS
from code_review_mining import settings
from bson import ObjectId
from patchwork.static.utils import TextFile


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Accounts
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Projects
        fields = '__all__'


class SeriesStandardSerializer(serializers.ModelSerializer):

    def to_internal_value(self, data):
        data['cover_letter_content'] = TextFile(data['cover_letter_content'].encode(), name=f"{data['original_id']}-cover_letter_content.txt")
        return super().to_internal_value(data)

    class Meta:
        model = Series
        fields = '__all__'


class PatchStandardSerializer(serializers.ModelSerializer):

    def to_internal_value(self, data):
        data['msg_content'] = TextFile(data['msg_content'].encode(), name=f"{data['original_id']}-msg_content.txt")
        data['code_diff'] = TextFile(data['code_diff'].encode(), name=f"{data['original_id']}-code_diff.txt")
        return super().to_internal_value(data)

    class Meta:
        model = Patches
        fields = '__all__'


class CommentStandardSerializer(serializers.ModelSerializer):

    def to_internal_value(self, data):
        data['msg_content'] = TextFile(data['msg_content'].encode(), name=f"{data['original_id']}-msg_content.txt")
        return super().to_internal_value(data)

    class Meta:
        model = Comments
        fields = '__all__'


class GetSeriesSerializer(SeriesStandardSerializer):

    def to_representation(self, instance):
        data = super().to_representation(instance)

        db = connections['default'].connection
        fs = GridFS(db, 'textfiles.series_cover_letter_content')

        file_obj_id = data['cover_letter_content'].split("/")[-1]
        file_content = fs.get(ObjectId(file_obj_id)).read().decode()
        data['cover_letter_content'] = file_content

        return data


class GetPatchSerializer(PatchStandardSerializer):

    def to_representation(self, instance):
        data = super().to_representation(instance)

        db = connections['default'].connection
        content_fs = GridFS(db, 'textfiles.patch_msg_content')
        diff_fs = GridFS(db, 'textfiles.patch_code_diff')

        content_file_obj_id = data['msg_content'].split("/")[-1]
        content_file_content = content_fs.get(ObjectId(content_file_obj_id)).read().decode()
        data['msg_content'] = content_file_content

        diff_file_obj_id = data['code_diff'].split("/")[-1]
        diff_file_content = diff_fs.get(ObjectId(diff_file_obj_id)).read().decode()
        data['code_diff'] = diff_file_content

        return data


class GetCommentSerializer(CommentStandardSerializer):

    def to_representation(self, instance):
        data = super().to_representation(instance)

        db = connections['default'].connection
        fs = GridFS(db, 'textfiles.comment_msg_content')

        file_obj_id = data['msg_content'].split("/")[-1]
        file_content = fs.get(ObjectId(file_obj_id)).read().decode()
        data['msg_content'] = file_content

        return data
