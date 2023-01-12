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
            'user_original_id': ['exact'],
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
            'submitter_user_original_id',
        ]

    filter_overrides = {
        django_models.DateTimeField: {
            'filter_class': django_filters.IsoDateTimeFilter
        },
    }


class PatchFilter(django_filters.FilterSet):
    original_id__icontains = django_filters.DateTimeFilter(field_name='original_id', lookup_expr='icontians')
    name__icontains = django_filters.DateTimeFilter(field_name='name', lookup_expr='icontians')

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
            'original_id__icontains',
            'name',
            'name__icontains',
            'state',
            'date__lt',
            'date__gt',
            'msg_content_contain',
            'code_diff_contain',
            'commit_ref',
            'change1_original_id',
            'change2_original_id',
            'mailing_list_original_id',
            'series_original_id',
            'new_series_original_id',
            'project_original_id',
            'submitter_account_original_id',
            'submitter_user_original_id',
        ]

    filter_overrides = {
        django_models.DateTimeField: {
            'filter_class': django_filters.IsoDateTimeFilter
        },
    }


class CommentFilter(django_filters.FilterSet):
    subject__icontains = django_filters.DateTimeFilter(field_name='subject', lookup_expr='icontians')

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
            'subject__icontains',
            'date__lt',
            'date__gt',
            'msg_content_contain',
            'change1_original_id',
            'change2_original_id',
            'mailing_list_original_id',
            'patch_original_id',
            'project_original_id',
            'submitter_account_original_id',
            'submitter_user_original_id',
        ]

    filter_overrides = {
        django_models.DateTimeField: {
            'filter_class': django_filters.IsoDateTimeFilter
        },
    }


class NewSeriesFilter(django_filters.FilterSet):

    original_id__icontains = django_filters.DateTimeFilter(field_name='original_id', lookup_expr='icontians')

    class Meta:
        model = NewSeries
        fields = [
            'id',
            'original_id',
            'original_id__icontains',
            # 'cover_letter_msg_id',
            'project_original_id',
            # 'submitter_account_original_id',
            # 'submitter_user_original_id',
            # 'series_original_id',
            'inspection_needed',
        ]


class Change1Filter(django_filters.FilterSet):

    original_id__icontains = django_filters.DateTimeFilter(field_name='original_id', lookup_expr='icontians')

    class Meta:
        model = Changes1
        fields = [
            'id',
            'original_id',
            'original_id__icontains',
            'is_accepted',
            'parent_commit_id',
            'merged_commit_id',
            'project_original_id',
            # 'submitter_account_original_id',
            # 'submitter_user_original_id',
            # 'series_original_id',
            # 'new_series_original_id',
            # 'patch_original_id',
            'inspection_needed',
        ]


class Change2Filter(django_filters.FilterSet):

    original_id__icontains = django_filters.DateTimeFilter(field_name='original_id', lookup_expr='icontians')

    class Meta:
        model = Changes2
        fields = [
            'id',
            'original_id',
            'original_id__icontains',
            'is_accepted',
            'parent_commit_id',
            'merged_commit_id',
            'project_original_id',
            # 'submitter_account_original_id',
            # 'submitter_user_original_id',
            # 'series_original_id',
            # 'new_series_original_id',
            # 'patch_original_id',
            'inspection_needed',
        ]


class UserFilter(django_filters.FilterSet):

    original_id__icontains = django_filters.DateTimeFilter(field_name='original_id', lookup_expr='icontians')

    class Meta:
        model = Users
        fields = [
            'id',
            'original_id',
            'original_id__icontains',
            # 'account_original_id',
        ]
    

class MailingListFilter(django_filters.FilterSet):

    original_id__icontains = django_filters.DateTimeFilter(field_name='original_id', lookup_expr='icontians')
    date__lt = django_filters.DateTimeFilter(field_name="date", lookup_expr='lt')
    date__gt = django_filters.DateTimeFilter(field_name="date", lookup_expr='gt')

    class Meta:
        model = MailingLists
        fields = [
            'id',
            'original_id',
            'original_id__icontains',
            'msg_id',
            'subject',
            'date__lt',
            'date__gt',
            'sender_name',
            'project_original_id',
        ]