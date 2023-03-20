# from django.db import models
from code_review_mining import settings
from djongo import models
from djongo.storage import GridFSStorage

grid_fs_storage = GridFSStorage(collection='textfiles', base_url=''.join([settings.BASE_URL, 'textfiles/']))


# Create your models here.
class Identity(models.Model):
    original_id = models.CharField(max_length=255, unique=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    api_url = models.CharField(max_length=255, blank=True, null=True)
    is_maintainer = models.BooleanField(default=False)


class Project(models.Model):
    original_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    repository_url = models.CharField(max_length=255, blank=True, null=True)
    api_url = models.CharField(max_length=255, blank=True, null=True)
    web_url = models.CharField(max_length=255, blank=True, null=True)
    list_id = models.CharField(max_length=255, blank=True, null=True)
    list_address = models.CharField(max_length=255, blank=True, null=True)
    maintainer_identity = models.ManyToManyField(Identity, through="ProjectIdentityRelation", blank=True, null=True)


class ProjectIdentityRelation(models.Model):
    project_original_id = models.ForeignKey(Project, on_delete=models.CASCADE, to_field="original_id", db_column="project_original_id")
    identity_original_id = models.ForeignKey(Identity, on_delete=models.CASCADE, to_field="original_id", db_column="identity_original_id")


class Individual(models.Model):
    original_id = models.CharField(max_length=255, unique=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, to_field="original_id", db_column="project", blank=True, null=True)
    identity = models.ManyToManyField(Identity, through="IndividualIdentityRelation", related_name="individuals", blank=True, null=True)


class IndividualIdentityRelation(models.Model):
    individual_original_id = models.ForeignKey(Individual, on_delete=models.CASCADE, to_field="original_id", db_column="individual_original_id")
    identity_original_id = models.ForeignKey(Identity, on_delete=models.CASCADE, to_field="original_id", db_column="identity_original_id")


class Series(models.Model):
    original_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    version = models.IntegerField(blank=True, null=True)
    total = models.IntegerField(blank=True, null=True)
    received_total = models.IntegerField(blank=True, null=True)
    cover_letter_msg_id = models.TextField(blank=True, null=True)
    cover_letter_content = models.FileField(blank=True, null=True, upload_to='series_cover_letter_content', storage=grid_fs_storage)
    api_url = models.CharField(max_length=255, blank=True, null=True)
    web_url = models.CharField(max_length=255, blank=True, null=True)
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=True, null=True, to_field="original_id", db_column="project")
    submitter_identity = models.ForeignKey(Identity, on_delete=models.RESTRICT, blank=True, null=True, to_field="original_id", db_column="submitter_identity")
    submitter_individual = models.ForeignKey(Individual, on_delete=models.RESTRICT, blank=True, null=True, to_field="original_id", db_column="submitter_individual")


class NewSeries(models.Model):
    original_id = models.CharField(max_length=255, unique=True)
    cover_letter_msg_id = models.TextField(blank=True, null=True)

    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=True, null=True, to_field="original_id", db_column="project")
    submitter_identity = models.ManyToManyField(Identity, through="NewSeriesIdentityRelation", blank=True)
    submitter_individual = models.ManyToManyField(Individual, through="NewSeriesIndividualRelation", blank=True)
    series = models.ManyToManyField(Series, through="NewSeriesSeriesRelation", blank=True)
    inspection_needed = models.BooleanField(default=False)


class NewSeriesIdentityRelation(models.Model):
    newseries_original_id = models.ForeignKey(NewSeries, on_delete=models.CASCADE, to_field="original_id", db_column="newseries_original_id")
    identity_original_id = models.ForeignKey(Identity, on_delete=models.CASCADE, to_field="original_id", db_column="identity_original_id")


class NewSeriesIndividualRelation(models.Model):
    newseries_original_id = models.ForeignKey(NewSeries, on_delete=models.CASCADE, to_field="original_id", db_column="newseries_original_id")
    individual_original_id = models.ForeignKey(Individual, on_delete=models.CASCADE, to_field="original_id", db_column="individual_original_id")


class NewSeriesSeriesRelation(models.Model):
    newseries_original_id = models.ForeignKey(NewSeries, on_delete=models.CASCADE, to_field="original_id", db_column="newseries_original_id")
    series_original_id = models.ForeignKey(Series, on_delete=models.CASCADE, to_field="original_id", db_column="series_original_id")

    
class Change1(models.Model):
    original_id = models.CharField(max_length=255, unique=True)
    is_accepted = models.BooleanField(default=False)
    parent_commit_id = models.TextField(blank=True, null=True)
    merged_commit_id = models.TextField(blank=True, null=True)
    commit_date = models.DateTimeField(blank=True, null=True)
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=True, null=True, to_field="original_id", db_column="project")
    submitter_identity = models.ManyToManyField(Identity, through="Change1IdentityRelation", blank=True, null=True)
    submitter_individual = models.ManyToManyField(Individual, through="Change1IndividualRelation", blank=True, null=True)
    series = models.ManyToManyField(Series, through="Change1SeriesRelation", blank=True, null=True)
    newseries = models.ManyToManyField(NewSeries, through="Change1NewSeriesRelation", blank=True, null=True)
    inspection_needed = models.BooleanField(default=False)


class Change1IdentityRelation(models.Model):
    change1_original_id = models.ForeignKey(Change1, on_delete=models.CASCADE, to_field="original_id", db_column="change1_original_id")
    identity_original_id = models.ForeignKey(Identity, on_delete=models.CASCADE, to_field="original_id", db_column="identity_original_id")


class Change1IndividualRelation(models.Model):
    change1_original_id = models.ForeignKey(Change1, on_delete=models.CASCADE, to_field="original_id", db_column="change1_original_id")
    individual_original_id = models.ForeignKey(Individual, on_delete=models.CASCADE, to_field="original_id", db_column="individual_original_id")


class Change1SeriesRelation(models.Model):
    change1_original_id = models.ForeignKey(Change1, on_delete=models.CASCADE, to_field="original_id", db_column="change1_original_id")
    series_original_id = models.ForeignKey(Series, on_delete=models.CASCADE, to_field="original_id", db_column="series_original_id")


class Change1NewSeriesRelation(models.Model):
    change1_original_id = models.ForeignKey(Change1, on_delete=models.CASCADE, to_field="original_id", db_column="change1_original_id")
    newseries_original_id = models.ForeignKey(NewSeries, on_delete=models.CASCADE, to_field="original_id", db_column="newseries_original_id")


class Change2(models.Model):
    original_id = models.CharField(max_length=255, unique=True)
    is_accepted = models.BooleanField(default=False)
    parent_commit_id = models.TextField(blank=True, null=True)
    merged_commit_id = models.TextField(blank=True, null=True)
    commit_date = models.DateTimeField(blank=True, null=True)
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=True, null=True, to_field="original_id", db_column="project")
    submitter_identity = models.ManyToManyField(Identity, through="Change2IdentityRelation", blank=True, null=True)
    submitter_individual = models.ManyToManyField(Individual, through="Change2IndividualRelation", blank=True, null=True)
    series = models.ManyToManyField(Series, through="Change2SeriesRelation", blank=True, null=True)
    newseries = models.ManyToManyField(NewSeries, through="Change2NewSeriesRelation", blank=True, null=True)
    inspection_needed = models.BooleanField(default=False)


class Change2IdentityRelation(models.Model):
    change2_original_id = models.ForeignKey(Change2, on_delete=models.CASCADE, to_field="original_id", db_column="change2_original_id")
    identity_original_id = models.ForeignKey(Identity, on_delete=models.CASCADE, to_field="original_id", db_column="identity_original_id")


class Change2IndividualRelation(models.Model):
    change2_original_id = models.ForeignKey(Change2, on_delete=models.CASCADE, to_field="original_id", db_column="change2_original_id")
    individual_original_id = models.ForeignKey(Individual, on_delete=models.CASCADE, to_field="original_id", db_column="individual_original_id")


class Change2SeriesRelation(models.Model):
    change2_original_id = models.ForeignKey(Change2, on_delete=models.CASCADE, to_field="original_id", db_column="change2_original_id")
    series_original_id = models.ForeignKey(Series, on_delete=models.CASCADE, to_field="original_id", db_column="series_original_id")


class Change2NewSeriesRelation(models.Model):
    change2_original_id = models.ForeignKey(Change2, on_delete=models.CASCADE, to_field="original_id", db_column="change2_original_id")
    newseries_original_id = models.ForeignKey(NewSeries, on_delete=models.CASCADE, to_field="original_id", db_column="newseries_original_id")

    
class MailingList(models.Model):
    original_id = models.CharField(max_length=255, unique=True)
    msg_id = models.TextField(unique=True, blank=True, null=True)
    subject = models.TextField(blank=True, null=True)
    content = models.FileField(blank=True, null=True, upload_to='mailing_list_email_content', storage=grid_fs_storage)
    date = models.DateTimeField(blank=True, null=True)
    sender_name = models.CharField(max_length=255, blank=True, null=True)
    web_url = models.CharField(max_length=255, blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=True, null=True, to_field="original_id", db_column="project")

    
class Patch(models.Model):
    original_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    msg_id = models.TextField(blank=True, null=True)
    msg_content = models.FileField(blank=True, null=True, upload_to='patch_msg_content', storage=grid_fs_storage)
    code_diff = models.FileField(blank=True, null=True, upload_to='patch_code_diff', storage=grid_fs_storage)
    api_url = models.CharField(max_length=255, blank=True, null=True)
    web_url = models.CharField(max_length=255, blank=True, null=True)
    commit_ref = models.TextField(blank=True, null=True)
    in_reply_to = models.TextField(blank=True, null=True)
    
    change1 = models.ForeignKey(Change1, related_name='patches', on_delete=models.RESTRICT, blank=True, null=True, to_field="original_id", db_column="change1")
    change2 = models.ForeignKey(Change2, related_name='patches', on_delete=models.RESTRICT, blank=True, null=True, to_field="original_id", db_column="change2")
    mailinglist = models.ForeignKey(MailingList, related_name='patches', on_delete=models.RESTRICT, blank=True, null=True, to_field="original_id", db_column="mailinglist")
    series = models.ForeignKey(Series, related_name='patches', on_delete=models.RESTRICT, blank=True, null=True, to_field="original_id", db_column="series")
    newseries = models.ForeignKey(NewSeries, related_name='patches', on_delete=models.RESTRICT, blank=True, null=True, to_field="original_id", db_column="newseries")
    submitter_identity = models.ForeignKey(Identity, on_delete=models.RESTRICT, blank=True, null=True, to_field="original_id", db_column="submitter_identity")
    submitter_individual = models.ForeignKey(Individual, on_delete=models.RESTRICT, blank=True, null=True, to_field="original_id", db_column="submitter_individual")
    project = models.ForeignKey(Project, on_delete=models.RESTRICT, blank=True, null=True, to_field="original_id", db_column="project")

    
class Comment(models.Model):
    original_id = models.CharField(max_length=255, unique=True)
    msg_id = models.TextField(blank=True, null=True)
    msg_content = models.FileField(blank=True, null=True, upload_to='comment_msg_content', storage=grid_fs_storage)
    date = models.DateTimeField(blank=True, null=True)
    subject = models.TextField(blank=True, null=True)
    in_reply_to = models.TextField(blank=True, null=True)
    web_url = models.CharField(max_length=255, blank=True, null=True)
    
    change1 = models.ForeignKey(Change1, related_name='comments', on_delete=models.RESTRICT, blank=True, null=True, to_field="original_id", db_column="change1")
    change2 = models.ForeignKey(Change2, related_name='comments', on_delete=models.RESTRICT, blank=True, null=True, to_field="original_id", db_column="change2")
    mailinglist = models.ForeignKey(MailingList, related_name='comments', on_delete=models.DO_NOTHING, blank=True, null=True, to_field="original_id", db_column="mailinglist")
    submitter_identity = models.ForeignKey(Identity, on_delete=models.RESTRICT, blank=True, null=True, to_field="original_id", db_column="submitter_identity")
    submitter_individual = models.ForeignKey(Individual, on_delete=models.RESTRICT, blank=True, null=True, to_field="original_id", db_column="submitter_individual")
    patch = models.ForeignKey(Patch, related_name='comments', on_delete=models.CASCADE, blank=True, null=True, to_field="original_id", db_column="patch")
    project = models.ForeignKey(Project, on_delete=models.RESTRICT, blank=True, null=True, to_field="original_id", db_column="project")