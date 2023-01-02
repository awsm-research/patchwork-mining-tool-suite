import json
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
    cover_letter_content = serializers.CharField(allow_blank=True, allow_null=True)

    class Meta:
        model = Series
        fields = '__all__'


class SeriesFileSerializer(serializers.ModelSerializer):

    def to_internal_value(self, data):
        if data['cover_letter_content'] == '':
            data['cover_letter_content'] = 'mongodb_gridfs_code_review_empty_file'
        if data['cover_letter_content'] is not None:
            data['cover_letter_content'] = TextFile(data['cover_letter_content'].encode(), name=f"{data['original_id']}-cover_letter_content.txt")
        return super().to_internal_value(data)

    class Meta:
        model = Series
        fields = '__all__'


class PatchStandardSerializer(serializers.ModelSerializer):
    msg_content = serializers.CharField(allow_blank=True, allow_null=True)
    code_diff = serializers.CharField(allow_blank=True, allow_null=True)

    class Meta:
        model = Patches
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)

        try:
            reply_to_msg_id = json.loads(data['reply_to_msg_id'])
        except:
            reply_to_msg_id = data['reply_to_msg_id']
        data['reply_to_msg_id'] = reply_to_msg_id
            
        return data


class PatchContentFileSerializer(serializers.ModelSerializer):
    code_diff = serializers.CharField(allow_blank=True, allow_null=True)

    def to_internal_value(self, data):
        data['msg_content'] = TextFile(data['msg_content'].encode(), name=f"{data['original_id']}-msg_content.txt")
        return super().to_internal_value(data)

    class Meta:
        model = Patches
        fields = '__all__'


class PatchDiffFileSerializer(serializers.ModelSerializer):
    msg_content = serializers.CharField(allow_blank=True, allow_null=True)

    def to_internal_value(self, data):
        data['code_diff'] = TextFile(data['code_diff'].encode(), name=f"{data['original_id']}-code_diff.txt")
        return super().to_internal_value(data)

    class Meta:
        model = Patches
        fields = '__all__'


class PatchFileSerializer(serializers.ModelSerializer):

    def to_internal_value(self, data):
        data['msg_content'] = TextFile(data['msg_content'].encode(), name=f"{data['original_id']}-msg_content.txt")
        data['code_diff'] = TextFile(data['code_diff'].encode(), name=f"{data['original_id']}-code_diff.txt")
        return super().to_internal_value(data)

    class Meta:
        model = Patches
        fields = '__all__'


class CommentStandardSerializer(serializers.ModelSerializer):
    msg_content = serializers.CharField(allow_blank=True, allow_null=True)

    class Meta:
        model = Comments
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)

        try:
            reply_to_msg_id = json.loads(data['reply_to_msg_id'])
        except:
            reply_to_msg_id = data['reply_to_msg_id']
        data['reply_to_msg_id'] = reply_to_msg_id
            
        return data


class CommentFileSerializer(serializers.ModelSerializer):

    def to_internal_value(self, data):
        data['msg_content'] = TextFile(data['msg_content'].encode(), name=f"{data['original_id']}-msg_content.txt")
        return super().to_internal_value(data)

    class Meta:
        model = Comments
        fields = '__all__'


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

        try:
            reply_to_msg_id = json.loads(data['reply_to_msg_id'])
        except:
            reply_to_msg_id = data['reply_to_msg_id']

        data['reply_to_msg_id'] = reply_to_msg_id

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


class GetCommentSerializer(CommentStandardSerializer):

    def to_representation(self, instance):
        data = super().to_representation(instance)

        try:
            reply_to_msg_id = json.loads(data['reply_to_msg_id'])
        except:
            reply_to_msg_id = data['reply_to_msg_id']

        data['reply_to_msg_id'] = reply_to_msg_id

        if data['msg_content'] == f"comment_msg_content/{data['original_id']}-msg_content.txt":
            db = connections['default'].connection
            fs = GridFS(db, 'textfiles.comment_msg_content')
            file_content = fs.find_one({"filename": f"{data['original_id']}-msg_content.txt"}).read().decode()
            data['msg_content'] = file_content

        return data


class Change1Serializer(serializers.ModelSerializer):

    class Meta:
        model = Changes1
        fields = '__all__'


class Change2Serializer(serializers.ModelSerializer):

    class Meta:
        model = Changes2
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Users
        fields = '__all__'


class NewSeriesSerializer(serializers.ModelSerializer):

    class Meta:
        model = NewSeries
        fields = '__all__'


class MailingListSerializer(serializers.ModelSerializer):

    class Meta:
        model = MailingLists
        fields = '__all__'