import django_filters

from patchwork.models import *
from patchwork.serializers import *
from django.db import models as django_models
from djongo import models as djongo_models


class FileFilter(django_filters.Filter):
    field_class = djongo_models.FileField


class IdentityFilter(django_filters.FilterSet):

    class Meta:
        model = Identity
        fields = {
            'id': ['exact'],
            'original_id': ['exact', 'icontains'],
            'name': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
            # 'individual': ['exact'],
        }


class ProjectFilter(django_filters.FilterSet):

    class Meta:
        model = Project
        fields = {
            'id': ['exact'],
            'original_id': ['exact', 'icontains'],
            'name': ['exact', 'icontains'],
        }


class SeriesFilter(django_filters.FilterSet):
    date__lt = django_filters.DateTimeFilter(
        field_name="date", lookup_expr='lt')
    date__gt = django_filters.DateTimeFilter(
        field_name="date", lookup_expr='gt')
    cover_letter_content_contain = django_filters.CharFilter(
        field_name='cover_letter_content', method='filter_file')

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
            'project',
            'submitter_identity',
            'submitter_individual',
        ]

    filter_overrides = {
        django_models.DateTimeField: {
            'filter_class': django_filters.IsoDateTimeFilter
        },
    }


class PatchFilter(django_filters.FilterSet):
    original_id__icontains = django_filters.CharFilter(
        field_name='original_id', lookup_expr='icontains')
    name__icontains = django_filters.CharFilter(
        field_name='name', lookup_expr='icontains')

    date__lt = django_filters.DateTimeFilter(
        field_name="date", lookup_expr='lt')
    date__gt = django_filters.DateTimeFilter(
        field_name="date", lookup_expr='gt')
    msg_content_contain = django_filters.CharFilter(
        field_name='msg_content', method='filter_file')
    code_diff_contain = django_filters.CharFilter(
        field_name='code_diff', method='filter_file')

    def filter_file(self, queryset, name, value):
        lookup = '__'.join([name, 'icontains'])
        return queryset.filter(**{lookup: value})

    class Meta:
        model = Patch
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
            'change1',
            'change2',
            'mailinglist',
            'series',
            'newseries',
            'project',
            'submitter_identity',
            'submitter_individual',
        ]

    filter_overrides = {
        django_models.DateTimeField: {
            'filter_class': django_filters.IsoDateTimeFilter
        },
    }


class CommentFilter(django_filters.FilterSet):
    subject__icontains = django_filters.CharFilter(
        field_name='subject', lookup_expr='icontains')

    date__lt = django_filters.DateTimeFilter(
        field_name="date", lookup_expr='lt')
    date__gt = django_filters.DateTimeFilter(
        field_name="date", lookup_expr='gt')
    msg_content_contain = django_filters.CharFilter(
        field_name='msg_content', method='filter_file')

    def filter_file(self, queryset, name, value):
        lookup = '__'.join([name, 'icontains'])
        return queryset.filter(**{lookup: value})

    class Meta:
        model = Comment
        fields = [
            'id',
            'original_id',
            'subject',
            'subject__icontains',
            'date__lt',
            'date__gt',
            'msg_content_contain',
            'change1',
            'change2',
            'mailinglist',
            'patch',
            'project',
            'submitter_identity',
            'submitter_individual',
        ]

    filter_overrides = {
        django_models.DateTimeField: {
            'filter_class': django_filters.IsoDateTimeFilter
        },
    }


class NewSeriesFilter(django_filters.FilterSet):

    original_id__icontains = django_filters.CharFilter(
        field_name='original_id', lookup_expr='icontains')

    class Meta:
        model = NewSeries
        fields = [
            'id',
            'original_id',
            'original_id__icontains',
            # 'cover_letter_msg_id',
            'project',
            # 'submitter_identity',
            # 'submitter_individual',
            # 'series',
            'inspection_needed',
        ]


class ExactBoWGroupFilter(django_filters.FilterSet):

    original_id__icontains = django_filters.CharFilter(
        field_name='original_id', lookup_expr='icontains')

    class Meta:
        model = ExactBoWGroup
        fields = [
            'id',
            'original_id',
            'original_id__icontains',
            'is_accepted',
            'parent_commit_id',
            'merged_commit_id',
            'project',
            # 'submitter_identity',
            # 'submitter_individual',
            # 'series',
            # 'newseries',
            # 'patch',
            'inspection_needed',
        ]


class OWDiffGroupFilter(django_filters.FilterSet):

    original_id__icontains = django_filters.CharFilter(
        field_name='original_id', lookup_expr='icontains')

    class Meta:
        model = OWDiffGroup
        fields = [
            'id',
            'original_id',
            'original_id__icontains',
            'is_accepted',
            'parent_commit_id',
            'merged_commit_id',
            'project',
            # 'submitter_identity',
            # 'submitter_individual',
            # 'series',
            # 'newseries',
            # 'patch',
            'inspection_needed',
        ]


class IndividualFilter(django_filters.FilterSet):

    original_id__icontains = django_filters.CharFilter(
        field_name='original_id', lookup_expr='icontains')

    class Meta:
        model = Individual
        fields = [
            'id',
            'original_id',
            'original_id__icontains',
            # 'identity',
        ]


class MailingListFilter(django_filters.FilterSet):

    original_id__icontains = django_filters.CharFilter(
        field_name='original_id', lookup_expr='icontains')
    date__lt = django_filters.DateTimeFilter(
        field_name="date", lookup_expr='lt')
    date__gt = django_filters.DateTimeFilter(
        field_name="date", lookup_expr='gt')

    class Meta:
        model = MailingList
        fields = [
            'id',
            'original_id',
            'original_id__icontains',
            'msg_id',
            'subject',
            'date__lt',
            'date__gt',
            'sender_name',
            'project',
        ]
