import django_filters

from patchwork.models import *
from patchwork.serializers import *
from django.db import models as django_models
from djongo import models as djongo_models

class FileFilter(django_filters.Filter):
    field_class = djongo_models.FileField


class AccountFilter(django_filters.FilterSet):

    class Meta:
        model = Accounts
        fields = {
            'id': ['exact'],
            'original_id': ['exact', 'icontains'],
            'username': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
            'user_id': ['exact'],
        }


class ProjectFilter(django_filters.FilterSet):

    class Meta:
        model = Projects
        fields = {
            'id': ['exact'],
            'original_id': ['exact', 'icontains'],
            'name': ['exact', 'icontains'],
        }


class SeriesFilter(django_filters.FilterSet):
    date__lt = django_filters.DateTimeFilter(field_name="date", lookup_expr='lt')
    date__gt = django_filters.DateTimeFilter(field_name="date", lookup_expr='gt')
    cover_letter_content_contain = django_filters.CharFilter(field_name='cover_letter_content', method='filter_file')

    def filter_file(self, queryset, name, value):
        lookup = '__'.join([name, 'icontains'])
        return queryset.filter(**{lookup: value})

    class Meta:
        model = Series
        fields = [
            'id',
            'original_id',
            'name',
            'date__lt',
            'date__gt',
            'cover_letter_content_contain',
            'project_original_id',
            'submitter_account_original_id',
            'submitter_user_id',
        ]

    filter_overrides = {
        django_models.DateTimeField: {
            'filter_class': django_filters.IsoDateTimeFilter
        },
    }


class PatchFilter(django_filters.FilterSet):
    date__lt = django_filters.DateTimeFilter(field_name="date", lookup_expr='lt')
    date__gt = django_filters.DateTimeFilter(field_name="date", lookup_expr='gt')
    msg_content_contain = django_filters.CharFilter(field_name='msg_content', method='filter_file')
    code_diff_contain = django_filters.CharFilter(field_name='code_diff', method='filter_file')

    def filter_file(self, queryset, name, value):
        lookup = '__'.join([name, 'icontains'])
        return queryset.filter(**{lookup: value})

    class Meta:
        model = Patches
        fields = [
            'id',
            'original_id',
            'name',
            'state',
            'date__lt',
            'date__gt',
            'msg_content_contain',
            'code_diff_contain',
            'commit_ref',
            'change_id1',
            'change_id2',
            'mailing_list_id',
            'series_original_id',
            'new_series_id',
            'project_original_id',
            'submitter_account_original_id',
            'submitter_user_id',
        ]

    filter_overrides = {
        django_models.DateTimeField: {
            'filter_class': django_filters.IsoDateTimeFilter
        },
    }


class CommentFilter(django_filters.FilterSet):
    date__lt = django_filters.DateTimeFilter(field_name="date", lookup_expr='lt')
    date__gt = django_filters.DateTimeFilter(field_name="date", lookup_expr='gt')
    msg_content_contain = django_filters.CharFilter(field_name='msg_content', method='filter_file')

    def filter_file(self, queryset, name, value):
        lookup = '__'.join([name, 'icontains'])
        return queryset.filter(**{lookup: value})

    class Meta:
        model = Comments
        fields = [
            'id',
            'original_id',
            'subject',
            'date__lt',
            'date__gt',
            'msg_content_contain',
            'change_id1',
            'change_id2',
            'mailing_list_id',
            'patch_original_id',
            'project_original_id',
            'submitter_account_original_id',
            'submitter_user_id',
        ]

    filter_overrides = {
        django_models.DateTimeField: {
            'filter_class': django_filters.IsoDateTimeFilter
        },
    }