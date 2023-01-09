# from django.db import models
from code_review_mining import settings
from djongo import models
from djongo.storage import GridFSStorage

grid_fs_storage = GridFSStorage(collection='textfiles', base_url=''.join([settings.BASE_URL, 'textfiles/']))

# Create your models here.
class Accounts(models.Model):
    original_id = models.CharField(max_length=255, unique=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    api_url = models.CharField(max_length=255, blank=True, null=True)
    user_original_id = models.CharField(max_length=255, blank=True, null=True)
    
    
class Users(models.Model):
    original_id = models.CharField(max_length=255, unique=True)
    account_original_id = models.JSONField(blank=True, null=True)
    

class Projects(models.Model):
    original_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    repository_url = models.CharField(max_length=255, blank=True, null=True)
    api_url = models.CharField(max_length=255, blank=True, null=True)
    web_url = models.CharField(max_length=255, blank=True, null=True)
    list_id = models.CharField(max_length=255, blank=True, null=True)
    list_address = models.CharField(max_length=255, blank=True, null=True)
    
    maintainer_account_original_id = models.JSONField(blank=True, null=True)
    maintainer_user_original_id = models.JSONField(blank=True, null=True)
    
    
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
    
    project_original_id = models.CharField(max_length=255, blank=True, null=True)
    submitter_account_original_id = models.CharField(max_length=255, blank=True, null=True)
    submitter_user_original_id = models.CharField(max_length=255, blank=True, null=True)


class NewSeries(models.Model):
    original_id = models.CharField(max_length=255, unique=True)
    cover_letter_msg_id = models.TextField(blank=True, null=True)

    project_original_id = models.CharField(max_length=255, blank=True, null=True)
    submitter_account_original_id = models.JSONField(blank=True, null=True)
    submitter_user_original_id = models.JSONField(blank=True, null=True)
    series_original_id = models.JSONField(blank=True, null=True)
    inspection_needed = models.BooleanField(default=False)

    
class Changes1(models.Model):
    original_id = models.CharField(max_length=255, unique=True)
    is_accepted = models.BooleanField(default=False)
    parent_commit_id = models.TextField(blank=True, null=True)
    merged_commit_id = models.TextField(blank=True, null=True)
    commit_date = models.DateTimeField(blank=True, null=True)
    
    project_original_id = models.CharField(max_length=255, blank=True, null=True)
    submitter_account_original_id = models.JSONField(blank=True, null=True)
    submitter_user_original_id = models.JSONField(blank=True, null=True)
    series_original_id = models.JSONField(blank=True, null=True)
    new_series_original_id = models.JSONField(blank=True, null=True)
    patch_original_id = models.JSONField(blank=True, null=True)
    inspection_needed = models.BooleanField(default=False)


class Changes2(models.Model):
    original_id = models.CharField(max_length=255, unique=True)
    is_accepted = models.BooleanField(default=False)
    parent_commit_id = models.TextField(blank=True, null=True)
    merged_commit_id = models.TextField(blank=True, null=True)
    commit_date = models.DateTimeField(blank=True, null=True)
    
    project_original_id = models.CharField(max_length=255, blank=True, null=True)
    submitter_account_original_id = models.JSONField(blank=True, null=True)
    submitter_user_original_id = models.JSONField(blank=True, null=True)
    series_original_id = models.JSONField(blank=True, null=True)
    new_series_original_id = models.JSONField(blank=True, null=True)
    patch_original_id = models.JSONField(blank=True, null=True)
    inspection_needed = models.BooleanField(default=False)

    
class MailingLists(models.Model):
    original_id = models.CharField(max_length=255, unique=True)
    msg_id = models.TextField(unique=True, blank=True, null=True)
    subject = models.TextField(blank=True, null=True)
    content = models.FileField(blank=True, null=True, upload_to='mailing_list_email_content', storage=grid_fs_storage)
    date = models.DateTimeField(blank=True, null=True)
    sender_name = models.CharField(max_length=255, blank=True, null=True)
    web_url = models.CharField(max_length=255, blank=True, null=True)
    project_original_id = models.CharField(max_length=255, blank=True, null=True)

    
class Patches(models.Model):
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
    reply_to_msg_id = models.TextField(blank=True, null=True)
    
    change1_original_id = models.CharField(max_length=255, blank=True, null=True)
    change2_original_id = models.CharField(max_length=255, blank=True, null=True)
    mailing_list_original_id = models.CharField(max_length=255, blank=True, null=True)
    series_original_id = models.CharField(max_length=255, blank=True, null=True)
    new_series_original_id = models.CharField(max_length=255, blank=True, null=True)
    submitter_account_original_id = models.CharField(max_length=255, blank=True, null=True)
    submitter_user_original_id = models.CharField(max_length=255, blank=True, null=True)
    project_original_id = models.CharField(max_length=255, blank=True, null=True)

    
class Comments(models.Model):
    original_id = models.CharField(max_length=255, unique=True)
    msg_id = models.TextField(blank=True, null=True)
    msg_content = models.FileField(blank=True, null=True, upload_to='comment_msg_content', storage=grid_fs_storage)
    date = models.DateTimeField(blank=True, null=True)
    subject = models.TextField(blank=True, null=True)
    reply_to_msg_id = models.TextField(blank=True, null=True)
    web_url = models.CharField(max_length=255, blank=True, null=True)
    
    change1_original_id = models.CharField(max_length=255, blank=True, null=True)
    change2_original_id = models.CharField(max_length=255, blank=True, null=True)
    mailing_list_original_id = models.CharField(max_length=255, blank=True, null=True)
    submitter_account_original_id = models.CharField(max_length=255, blank=True, null=True)
    submitter_user_original_id = models.CharField(max_length=255, blank=True, null=True)
    patch_original_id = models.CharField(max_length=255, blank=True, null=True)
    project_original_id = models.CharField(max_length=255, blank=True, null=True)