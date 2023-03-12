import json
from symbol import import_as_name
from rest_framework import serializers
from patchwork import models
from django.db import connections
from gridfs import GridFS
from code_review_mining import settings
from bson import ObjectId
from patchwork.static import embedded
from patchwork.static.utils import TextFile


class ProjectBulkCreateSerializer(serializers.ListSerializer):
    
    # def create(self, validated_data):
    #     identity_project_map = []
    #     project_objs = []
    #     for item in validated_data:
    #         identities_data = item.pop('maintainer_identity', [])
    #         identity_project_map.extend([(identity_data.original_id, item['original_id']) for identity_data in identities_data])
    #         project_objs.append(models.Project(**item))

    #     instance = models.Project.objects.bulk_create(project_objs)

    #     through_objs = [models.Project.maintainer_identity.through(identity_id=x, project_id=y) for x, y in identity_project_map]

    #     if through_objs:
    #         models.Project.maintainer_identity.through.objects.bulk_create(through_objs)

    #     return instance

    def create(self, validated_data):
        result = [models.Project(**item) for item in validated_data]

        return models.Project.objects.bulk_create(result)


class IndividualBulkCreateSerializer(serializers.ListSerializer):
    
    # def create(self, validated_data):
    #     identity_individual_map = []
    #     individual_objs = []
    #     for item in validated_data:
    #         identities_data = item.pop('identity', [])
    #         identity_individual_map.extend([(identity_data.original_id, item['original_id']) for identity_data in identities_data])
    #         individual_objs.append(models.Individual(**item))

    #     instance = models.Individual.objects.bulk_create(individual_objs)

    #     through_objs = [models.Individual.identity.through(identity_id=x, individual_id=y) for x, y in identity_individual_map]

    #     if through_objs:
    #         models.Individual.identity.through.objects.bulk_create(through_objs)


    #     # return models.Individual.objects.bulk_create(result)
    #     return instance

    def create(self, validated_data):
        result = [models.Individual(**item) for item in validated_data]

        return models.Individual.objects.bulk_create(result)


class ProjectIdentityRelationBulkCreateSerializer(serializers.ListSerializer):

    def create(self, validated_data):
        result = [models.ProjectIdentityRelation(**item) for item in validated_data]

        return models.ProjectIdentityRelation.objects.bulk_create(result)


class IndividualIdentityRelationBulkCreateSerializer(serializers.ListSerializer):

    def create(self, validated_data):
        result = [models.IndividualIdentityRelation(**item) for item in validated_data]

        return models.IndividualIdentityRelation.objects.bulk_create(result)


class SeriesBulkCreateSerializer(serializers.ListSerializer):
    
    def create(self, validated_data):
        result = [models.Series(**item) for item in validated_data]

        return models.Series.objects.bulk_create(result)


class NewSeriesBulkCreateSerializer(serializers.ListSerializer):
    
    # def create(self, validated_data):
    #     identity_newseries_map = []
    #     individual_newseries_map = []
    #     series_newseries_map = []
    #     newseries_objs = []

    #     for item in validated_data:
    #         identities_data = item.pop('submitter_identity', [])
    #         individuals_data = item.pop('submitter_individual', [])
    #         series_data = item.pop('series')

    #         identity_newseries_map.extend([(identity_data.original_id, item['original_id']) for identity_data in identities_data])
    #         individual_newseries_map.extend([(individual_data.original_id, item['original_id']) for individual_data in individuals_data])
    #         if series_data:
    #             series_newseries_map.extend([(series_item.original_id, item['original_id']) for series_item in series_data])
    #         newseries_objs.append(models.NewSeries(**item))
        
    #     instance = models.NewSeries.objects.bulk_create(newseries_objs)

    #     identity_through_objs = [models.NewSeries.submitter_identity.through(identity_id=x, newseries_id=y) for x, y in identity_newseries_map]
    #     individual_through_objs = [models.NewSeries.submitter_individual.through(individual_id=x, newseries_id=y) for x, y in individual_newseries_map]
    #     series_through_objs = [models.NewSeries.series.through(series_id=x, newseries_id=y) for x, y in series_newseries_map]
        
    #     if identity_through_objs:
    #         models.NewSeries.submitter_identity.through.objects.bulk_create(identity_through_objs)
    #     if individual_through_objs:
    #         models.NewSeries.submitter_individual.through.objects.bulk_create(individual_through_objs)
    #     if series_through_objs:
    #         models.NewSeries.series.through.objects.bulk_create(series_through_objs)

    #     # result = [models.NewSeries(**item) for item in validated_data]

    #     # return models.NewSeries.objects.bulk_create(result)
    #     return instance

    def create(self, validated_data):
        result = [models.NewSeries(**item) for item in validated_data]

        return models.NewSeries.objects.bulk_create(result)


class PatchBulkCreateSerializer(serializers.ListSerializer):
    
    def create(self, validated_data):
        result = [models.Patch(**item) for item in validated_data]

        return models.Patch.objects.bulk_create(result)


class CommentBulkCreateSerializer(serializers.ListSerializer):
    
    def create(self, validated_data):
        result = [models.Comment(**item) for item in validated_data]

        return models.Comment.objects.bulk_create(result)


class Change1BulkCreateSerializer(serializers.ListSerializer):
    
    # def create(self, validated_data):
    #     identity_change1_map = []
    #     individual_change1_map = []
    #     series_change1_map = []
    #     newseries_change1_map = []

    #     change1_objs = []

    #     for item in validated_data:
    #         identities_data = item.pop('submitter_identity', [])
    #         individuals_data = item.pop('submitter_individual', [])
    #         series_data = item.pop('series', [])
    #         newseries_data = item.pop('newseries', [])

    #         identity_change1_map.extend([(identity_data.original_id, item['original_id']) for identity_data in identities_data])
    #         individual_change1_map.extend([(individual_data.original_id, item['original_id']) for individual_data in individuals_data])
    #         if series_data:
    #             series_change1_map.extend([(series_item.original_id, item['original_id']) for series_item in series_data])
    #         if newseries_data:
    #             newseries_change1_map.extend([(newseries_item.original_id, item['original_id']) for newseries_item in newseries_data])
            
            
    #         change1_objs.append(models.Change1(**item))

    #     instance = models.Change1.objects.bulk_create(change1_objs)

    #     identity_through_objs = [models.Change1.submitter_identity.through(identity_id=x, change1_id=y) for x, y in identity_change1_map]
    #     individual_through_objs = [models.Change1.submitter_individual.through(individual_id=x, change1_id=y) for x, y in individual_change1_map]
    #     series_through_objs = [models.Change1.series.through(series_id=x, change1_id=y) for x, y in series_change1_map]
    #     newseries_through_objs = [models.Change1.newseries.through(newseries_id=x, change1_id=y) for x, y in newseries_change1_map]

    #     if identity_through_objs:
    #         models.Change1.submitter_identity.through.objects.bulk_create(identity_through_objs)

    #     if individual_through_objs:
    #         models.Change1.submitter_individual.through.objects.bulk_create(individual_through_objs)

    #     if series_through_objs:
    #         models.Change1.series.through.objects.bulk_create(series_through_objs)

    #     if newseries_through_objs:
    #         models.Change1.newseries.through.objects.bulk_create(newseries_through_objs)

    #     return instance

    def create(self, validated_data):
        result = [models.Change1(**item) for item in validated_data]

        return models.Change1.objects.bulk_create(result)

class Change2BulkCreateSerializer(serializers.ListSerializer):
    
    # def create(self, validated_data):
    #     identity_change2_map = []
    #     individual_change2_map = []
    #     series_change2_map = []
    #     newseries_change2_map = []

    #     change2_objs = []

    #     for item in validated_data:
    #         identities_data = item.pop('submitter_identity', [])
    #         individuals_data = item.pop('submitter_individual', [])
    #         series_data = item.pop('series', [])
    #         newseries_data = item.pop('newseries', [])

    #         identity_change2_map.extend([(identity_data.original_id, item['original_id']) for identity_data in identities_data])
    #         individual_change2_map.extend([(individual_data.original_id, item['original_id']) for individual_data in individuals_data])
    #         if series_data:
    #             series_change2_map.extend([(series_item.original_id, item['original_id']) for series_item in series_data])
    #         if newseries_data:
    #             newseries_change2_map.extend([(newseries_item.original_id, item['original_id']) for newseries_item in newseries_data])
            
            
    #         change2_objs.append(models.Change2(**item))

    #     instance = models.Change2.objects.bulk_create(change2_objs)

    #     identity_through_objs = [models.Change2.submitter_identity.through(identity_id=x, change2_id=y) for x, y in identity_change2_map]
    #     individual_through_objs = [models.Change2.submitter_individual.through(individual_id=x, change2_id=y) for x, y in individual_change2_map]
    #     series_through_objs = [models.Change2.series.through(series_id=x, change2_id=y) for x, y in series_change2_map]
    #     newseries_through_objs = [models.Change2.newseries.through(newseries_id=x, change2_id=y) for x, y in newseries_change2_map]

    #     if identity_through_objs:
    #         models.Change2.submitter_identity.through.objects.bulk_create(identity_through_objs)

    #     if individual_through_objs:
    #         models.Change2.submitter_individual.through.objects.bulk_create(individual_through_objs)

    #     if series_through_objs:
    #         models.Change2.series.through.objects.bulk_create(series_through_objs)

    #     if newseries_through_objs:
    #         models.Change2.newseries.through.objects.bulk_create(newseries_through_objs)

    #     return instance
    
    def create(self, validated_data):
        result = [models.Change2(**item) for item in validated_data]

        return models.Change2.objects.bulk_create(result)


##########################################################################################################################################




class ProjectCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Project
        fields = '__all__'
        list_serializer_class = ProjectBulkCreateSerializer


class ProjectListSerializer(serializers.ModelSerializer):
    maintainer_identity = embedded.MaintainerSerializer(many=True, read_only=True)

    class Meta:
        model = models.Project
        fields = '__all__'


class IndividualCreateSerializer(serializers.ModelSerializer):
    project = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Project.objects.all(), read_only=False)

    class Meta:
        model = models.Individual
        fields = '__all__'
        list_serializer_class = IndividualBulkCreateSerializer


class IdentityCreateSerializer(serializers.ModelSerializer):
    individuals = IndividualCreateSerializer(many=True, read_only=True)

    class Meta:
        model = models.Identity
        fields = ('id', 'original_id', 'email', 'name', 'api_url', 'is_maintainer', 'individuals')


class ProjectIdentityCreateSerializer(serializers.ModelSerializer):
    project_original_id = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Project.objects.all(), read_only=False)
    identity_original_id = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Identity.objects.all(), read_only=False)

    class Meta:
        model = models.ProjectIdentityRelation
        fields = '__all__'
        list_serializer_class = ProjectIdentityRelationBulkCreateSerializer


class IndividualIdentityCreateSerializer(serializers.ModelSerializer):
    individual_original_id = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Individual.objects.all(), read_only=False)
    identity_original_id = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Identity.objects.all(), read_only=False)

    class Meta:
        model = models.IndividualIdentityRelation
        fields = '__all__'
        list_serializer_class = IndividualIdentityRelationBulkCreateSerializer


class IndividualListSerializer(serializers.ModelSerializer):
    project = embedded.ProjectSerializer(read_only=True)
    identity = embedded.IdentitySerializer(many=True, read_only=True)

    class Meta:
        model = models.Individual
        fields = ('id', 'original_id', 'project', 'identity')


class IdentityListSerializer(serializers.ModelSerializer):
    individuals = embedded.IndividualSerializer(many=True, read_only=True)

    class Meta:
        model = models.Identity
        fields = ('id', 'original_id', 'email', 'name', 'api_url', 'is_maintainer', 'individuals')


class SeriesStandardSerializer(serializers.ModelSerializer):
    project = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Project.objects.all(), read_only=False)
    submitter_identity = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Identity.objects.all(), read_only=False)
    submitter_individual = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Individual.objects.all(), read_only=False, allow_null=True)

    cover_letter_content = serializers.CharField(allow_blank=True, allow_null=True)

    class Meta:
        model = models.Series
        fields = '__all__'
        list_serializer_class = SeriesBulkCreateSerializer


class SeriesFileSerializer(serializers.ModelSerializer):
    project = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Project.objects.all(), read_only=False)
    submitter_identity = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Identity.objects.all(), read_only=False)
    submitter_individual = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Individual.objects.all(), read_only=False, allow_null=True)


    def to_internal_value(self, data):
        data['cover_letter_content'] = TextFile(data['cover_letter_content'].encode(), name=f"{data['original_id']}-cover_letter_content.txt")
        return super().to_internal_value(data)

    class Meta:
        model = models.Series
        fields = '__all__'
        list_serializer_class = SeriesBulkCreateSerializer


class SeriesListSerializer(SeriesStandardSerializer):

    project = embedded.ProjectSerializer(read_only=True)
    submitter_identity = embedded.IdentitySerializer(read_only=True)
    submitter_individual = embedded.IndividualSerializer(read_only=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if data['cover_letter_content'] == f"series_cover_letter_content/{data['original_id']}-cover_letter_content.txt":
            db = connections['default'].connection
            fs = GridFS(db, 'textfiles.series_cover_letter_content')
            file_content = fs.find_one({"filename": f"{data['original_id']}-cover_letter_content.txt"}).read().decode()
            data['cover_letter_content'] = file_content

        return data


class NewSeriesCreateSerializer(serializers.ModelSerializer):
    project = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Project.objects.all(), read_only=False)
    patches = serializers.SlugRelatedField(slug_field="original_id", many=True, read_only=True)

    class Meta:
        model = models.NewSeries
        fields = (
            'id',
            'original_id',
            'cover_letter_msg_id',
            'project',
            'patches',
            'inspection_needed',
        )
        list_serializer_class = NewSeriesBulkCreateSerializer


    def to_internal_value(self, data):
        if type(data['cover_letter_msg_id']) == list:
            data['cover_letter_msg_id'] = json.dumps(data['cover_letter_msg_id'])
        
        return super().to_internal_value(data)

    def to_representation(self, instance):
        data = super().to_representation(instance)

        try:
            data['cover_letter_msg_id'] = json.loads(data['cover_letter_msg_id'])
        except:
            return data
        
        return data


class PatchStandardSerializer(serializers.ModelSerializer):
    msg_content = serializers.CharField(allow_blank=True, allow_null=True)
    code_diff = serializers.CharField(allow_blank=True, allow_null=True)

    change1 = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Change1.objects.all(), read_only=False, allow_null=True)
    change2 = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Change2.objects.all(), read_only=False, allow_null=True)
    mailinglist = serializers.SlugRelatedField(slug_field="original_id", queryset=models.MailingList.objects.all(), read_only=False, allow_null=True)
    series = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Series.objects.all(), read_only=False, allow_null=True)
    newseries = serializers.SlugRelatedField(slug_field="original_id", queryset=models.NewSeries.objects.all(), read_only=False, allow_null=True)
    submitter_identity = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Identity.objects.all(), read_only=False)
    submitter_individual = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Individual.objects.all(), read_only=False, allow_null=True)
    project = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Project.objects.all(), read_only=False)


    class Meta:
        model = models.Patch
        fields = '__all__'
        list_serializer_class = PatchBulkCreateSerializer

    def to_internal_value(self, data):
        if type(data['in_reply_to']) == list:
            data['in_reply_to'] = json.dumps(data['in_reply_to'])
        return super().to_internal_value(data)

    def to_representation(self, instance):
        data = super().to_representation(instance)

        try:
            in_reply_to = json.loads(data['in_reply_to'])
        except:
            in_reply_to = data['in_reply_to']
        data['in_reply_to'] = in_reply_to
            
        return data


class PatchContentFileSerializer(serializers.ModelSerializer):
    code_diff = serializers.CharField(allow_blank=True, allow_null=True)

    change1 = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Change1.objects.all(), read_only=False, allow_null=True)
    change2 = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Change2.objects.all(), read_only=False, allow_null=True)
    mailinglist = serializers.SlugRelatedField(slug_field="original_id", queryset=models.MailingList.objects.all(), read_only=False, allow_null=True)
    series = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Series.objects.all(), read_only=False, allow_null=True)
    newseries = serializers.SlugRelatedField(slug_field="original_id", queryset=models.NewSeries.objects.all(), read_only=False, allow_null=True)
    submitter_identity = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Identity.objects.all(), read_only=False)
    submitter_individual = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Individual.objects.all(), read_only=False, allow_null=True)
    project = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Project.objects.all(), read_only=False)


    class Meta:
        model = models.Patch
        fields = '__all__'
        list_serializer_class = PatchBulkCreateSerializer

    def to_internal_value(self, data):
        if type(data['in_reply_to']) == list:
            data['in_reply_to'] = json.dumps(data['in_reply_to'])

        data['msg_content'] = TextFile(data['msg_content'].encode(), name=f"{data['original_id']}-msg_content.txt")
        return super().to_internal_value(data)


class PatchDiffFileSerializer(serializers.ModelSerializer):
    msg_content = serializers.CharField(allow_blank=True, allow_null=True)

    change1 = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Change1.objects.all(), read_only=False, allow_null=True)
    change2 = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Change2.objects.all(), read_only=False, allow_null=True)
    mailinglist = serializers.SlugRelatedField(slug_field="original_id", queryset=models.MailingList.objects.all(), read_only=False, allow_null=True)
    series = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Series.objects.all(), read_only=False, allow_null=True)
    newseries = serializers.SlugRelatedField(slug_field="original_id", queryset=models.NewSeries.objects.all(), read_only=False, allow_null=True)
    submitter_identity = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Identity.objects.all(), read_only=False)
    submitter_individual = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Individual.objects.all(), read_only=False, allow_null=True)
    project = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Project.objects.all(), read_only=False)


    class Meta:
        model = models.Patch
        fields = '__all__'
        list_serializer_class = PatchBulkCreateSerializer

    def to_internal_value(self, data):
        if type(data['in_reply_to']) == list:
            data['in_reply_to'] = json.dumps(data['in_reply_to'])

        data['code_diff'] = TextFile(data['code_diff'].encode(), name=f"{data['original_id']}-code_diff.txt")
        return super().to_internal_value(data)


class PatchFileSerializer(serializers.ModelSerializer):

    change1 = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Change1.objects.all(), read_only=False, allow_null=True)
    change2 = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Change2.objects.all(), read_only=False, allow_null=True)
    mailinglist = serializers.SlugRelatedField(slug_field="original_id", queryset=models.MailingList.objects.all(), read_only=False, allow_null=True)
    series = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Series.objects.all(), read_only=False, allow_null=True)
    newseries = serializers.SlugRelatedField(slug_field="original_id", queryset=models.NewSeries.objects.all(), read_only=False, allow_null=True)
    submitter_identity = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Identity.objects.all(), read_only=False)
    submitter_individual = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Individual.objects.all(), read_only=False, allow_null=True)
    project = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Project.objects.all(), read_only=False)


    class Meta:
        model = models.Patch
        fields = '__all__'
        list_serializer_class = PatchBulkCreateSerializer

    def to_internal_value(self, data):
        if type(data['in_reply_to']) == list:
            data['in_reply_to'] = json.dumps(data['in_reply_to'])

        data['msg_content'] = TextFile(data['msg_content'].encode(), name=f"{data['original_id']}-msg_content.txt")
        data['code_diff'] = TextFile(data['code_diff'].encode(), name=f"{data['original_id']}-code_diff.txt")
        return super().to_internal_value(data)


class PatchListSerializer(PatchStandardSerializer):
    change1 = serializers.SlugRelatedField(slug_field="original_id", read_only=True)
    change2 = serializers.SlugRelatedField(slug_field="original_id", read_only=True)
    mailinglist = serializers.SlugRelatedField(slug_field="original_id", read_only=True)
    series = serializers.SlugRelatedField(slug_field="original_id", read_only=True)
    newseries = serializers.SlugRelatedField(slug_field="original_id", read_only=True)
    submitter_identity = serializers.SlugRelatedField(slug_field="original_id", read_only=True)
    submitter_individual = serializers.SlugRelatedField(slug_field="original_id", read_only=True)
    project = serializers.SlugRelatedField(slug_field="original_id", read_only=True)


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


class NewSeriesListSerializer(serializers.ModelSerializer):
    project = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Project.objects.all(), read_only=False)
    patches = PatchListSerializer(many=True, read_only=True)

    class Meta:
        model = models.NewSeries
        fields = (
            'id',
            'original_id',
            'cover_letter_msg_id',
            'project',
            'patches',
            'inspection_needed',
        )

    def to_internal_value(self, data):
        if type(data['cover_letter_msg_id']) == list:
            data['cover_letter_msg_id'] = json.dumps(data['cover_letter_msg_id'])
        
        return super().to_internal_value(data)

    def to_representation(self, instance):
        data = super().to_representation(instance)

        try:
            data['cover_letter_msg_id'] = json.loads(data['cover_letter_msg_id'])
        except:
            return data
        
        return data


class CommentStandardSerializer(serializers.ModelSerializer):
    msg_content = serializers.CharField(allow_blank=True, allow_null=True)

    change1 = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Change1.objects.all(), read_only=False, allow_null=True)
    change2 = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Change2.objects.all(), read_only=False, allow_null=True)
    mailinglist = serializers.SlugRelatedField(slug_field="original_id", queryset=models.MailingList.objects.all(), read_only=False, allow_null=True)
    submitter_identity = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Identity.objects.all(), read_only=False)
    submitter_individual = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Individual.objects.all(), read_only=False, allow_null=True)
    project = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Project.objects.all(), read_only=False)


    class Meta:
        model = models.Comment
        fields = '__all__'
        list_serializer_class = CommentBulkCreateSerializer
    
    def to_internal_value(self, data):
        if type(data['in_reply_to']) == list:
            data['in_reply_to'] = json.dumps(data['in_reply_to'])

        return super().to_internal_value(data)


    def to_representation(self, instance):
        data = super().to_representation(instance)

        try:
            in_reply_to = json.loads(data['in_reply_to'])
        except:
            in_reply_to = data['in_reply_to']
        data['in_reply_to'] = in_reply_to
            
        return data


class CommentFileSerializer(serializers.ModelSerializer):

    change1 = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Change1.objects.all(), read_only=False, allow_null=True)
    change2 = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Change2.objects.all(), read_only=False, allow_null=True)
    mailinglist = serializers.SlugRelatedField(slug_field="original_id", queryset=models.MailingList.objects.all(), read_only=False, allow_null=True)
    submitter_identity = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Identity.objects.all(), read_only=False)
    submitter_individual = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Individual.objects.all(), read_only=False, allow_null=True)
    patch = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Patch.objects.all(), read_only=False)
    project = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Project.objects.all(), read_only=False)

    class Meta:
        model = models.Comment
        fields = '__all__'
        list_serializer_class = CommentBulkCreateSerializer

    def to_internal_value(self, data):
        if type(data['in_reply_to']) == list:
            data['in_reply_to'] = json.dumps(data['in_reply_to'])

        data['msg_content'] = TextFile(data['msg_content'].encode(), name=f"{data['original_id']}-msg_content.txt")
        return super().to_internal_value(data)


class CommentListSerializer(CommentStandardSerializer):

    change1 = serializers.SlugRelatedField(slug_field="original_id", read_only=True)
    change2 = serializers.SlugRelatedField(slug_field="original_id", read_only=True)
    mailinglist = serializers.SlugRelatedField(slug_field="original_id", read_only=True)
    submitter_identity = serializers.SlugRelatedField(slug_field="original_id", read_only=True)
    submitter_individual = serializers.SlugRelatedField(slug_field="original_id", read_only=True)
    patch = serializers.SlugRelatedField(slug_field="original_id", read_only=True)
    project = serializers.SlugRelatedField(slug_field="original_id", read_only=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)

        try:
            in_reply_to = json.loads(data['in_reply_to'])
        except:
            in_reply_to = data['in_reply_to']

        data['in_reply_to'] = in_reply_to

        if data['msg_content'] == f"comment_msg_content/{data['original_id']}-msg_content.txt":
            db = connections['default'].connection
            fs = GridFS(db, 'textfiles.comment_msg_content')
            file_content = fs.find_one({"filename": f"{data['original_id']}-msg_content.txt"}).read().decode()
            data['msg_content'] = file_content

        return data


class Change1CreateSerializer(serializers.ModelSerializer):
    project = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Project.objects.all(), read_only=False)
    patches = serializers.SlugRelatedField(slug_field="original_id", many=True, read_only=True)
    comments = serializers.SlugRelatedField(slug_field="original_id", many=True, read_only=True)
    
    # submitter_identity = serializers.PrimaryKeyRelatedField(many=True, queryset=models.Identity.objects.all(), read_only=False)
    # submitter_individual = serializers.PrimaryKeyRelatedField(many=True, queryset=models.Individual.objects.all(), read_only=False, allow_null=True)
    # series = serializers.PrimaryKeyRelatedField(many=True, queryset=models.Series.objects.all(), read_only=False, allow_null=True)
    # newseries = serializers.PrimaryKeyRelatedField(many=True, queryset=models.NewSeries.objects.all(), read_only=False, allow_null=True)

    class Meta:
        model = models.Change1
        fields = (
            'id',
            'original_id',
            'is_accepted',
            'parent_commit_id',
            'merged_commit_id',
            'commit_date',
            'project',
            'patches',
            'comments',
            'inspection_needed'
        )
        list_serializer_class = Change1BulkCreateSerializer

    def to_internal_value(self, data):
        if type(data['merged_commit_id']) == list:
            data['merged_commit_id'] = json.dumps(data['merged_commit_id'])
        
        return super().to_internal_value(data)


class Change2CreateSerializer(serializers.ModelSerializer):
    project = serializers.SlugRelatedField(slug_field="original_id", queryset=models.Project.objects.all(), read_only=False)
    patches = serializers.SlugRelatedField(slug_field="original_id", many=True, read_only=True)
    comments = serializers.SlugRelatedField(slug_field="original_id", many=True, read_only=True)

    # submitter_identity = serializers.PrimaryKeyRelatedField(many=True, queryset=models.Identity.objects.all(), read_only=False)
    # submitter_individual = serializers.PrimaryKeyRelatedField(many=True, queryset=models.Individual.objects.all(), read_only=False, allow_null=True)
    # series = serializers.PrimaryKeyRelatedField(many=True, queryset=models.Series.objects.all(), read_only=False, allow_null=True)
    # newseries = serializers.PrimaryKeyRelatedField(many=True, queryset=models.NewSeries.objects.all(), read_only=False, allow_null=True)

    class Meta:
        model = models.Change2
        fields = (
            'id',
            'original_id',
            'is_accepted',
            'parent_commit_id',
            'merged_commit_id',
            'commit_date',
            'project',
            'patches',
            'comments',
            'inspection_needed'
        )
        list_serializer_class = Change2BulkCreateSerializer

    def to_internal_value(self, data):
        if type(data['merged_commit_id']) == list:
            data['merged_commit_id'] = json.dumps(data['merged_commit_id'])
        
        return super().to_internal_value(data)


class Change1ListSerializer(serializers.ModelSerializer):

    project = serializers.SlugRelatedField(slug_field="original_id", read_only=True)

    patches = PatchListSerializer(many=True, read_only=True)
    comments = CommentListSerializer(many=True, read_only=True)

    class Meta:
        model = models.Change1
        fields = (
            'id',
            'original_id',
            'is_accepted',
            'parent_commit_id',
            'merged_commit_id',
            'commit_date',
            'project',
            'patches',
            'comments',
            'inspection_needed'
        )


    def to_representation(self, instance):
        data = super().to_representation(instance)

        try:
            merged_commit_id = json.loads(data['merged_commit_id'])
        except:
            merged_commit_id = data['merged_commit_id']
        data['merged_commit_id'] = merged_commit_id
            
        return data


class Change2ListSerializer(serializers.ModelSerializer):

    project = serializers.SlugRelatedField(slug_field="original_id", read_only=True)

    patches = PatchListSerializer(many=True, read_only=True)
    comments = CommentListSerializer(many=True, read_only=True)

    class Meta:
        model = models.Change2
        fields = (
            'id',
            'original_id',
            'is_accepted',
            'parent_commit_id',
            'merged_commit_id',
            'commit_date',
            'project',
            'patches',
            'comments',
            'inspection_needed'
        )


    def to_representation(self, instance):
        data = super().to_representation(instance)

        try:
            merged_commit_id = json.loads(data['merged_commit_id'])
        except:
            merged_commit_id = data['merged_commit_id']
        data['merged_commit_id'] = merged_commit_id
            
        return data


class MailingListsBulkCreateListSerializer(serializers.ListSerializer):
    
    def create(self, validated_data):
        result = [models.MailingList(**item) for item in validated_data]

        return models.MailingList.objects.bulk_create(result)


class MailingListSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.MailingList
        fields = '__all__'
        list_serializer_class = MailingListsBulkCreateListSerializer