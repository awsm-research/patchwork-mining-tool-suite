# from django.db import models
from djongo import models

# Create your models here.
class Accounts(models.Model):
    original_id = models.CharField(max_length=255, unique=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    api_url = models.CharField(max_length=255, blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    
class Users(models.Model):
    account_original_id = models.JSONField(blank=True, null=True)
    
class Projects(models.Model):
    original_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    repo_url = models.CharField(max_length=255, blank=True, null=True)
    api_url = models.CharField(max_length=255, blank=True, null=True)
    web_url = models.CharField(max_length=255, blank=True, null=True)
    list_id = models.CharField(max_length=255, blank=True, null=True)
    list_address = models.CharField(max_length=255, blank=True, null=True)
    
    maintainer_account_original_id = models.JSONField(blank=True, null=True)
    maintainer_user_id = models.JSONField(blank=True, null=True)
    
    
class Series(models.Model):
    original_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    created_date = models.DateTimeField(blank=True, null=True)
    version = models.IntegerField(blank=True, null=True)
    total = models.IntegerField(blank=True, null=True)
    received_total = models.IntegerField(blank=True, null=True)
    cover_letter_content = models.TextField(blank=True, null=True)
    api_url = models.CharField(max_length=255, blank=True, null=True)
    web_url = models.CharField(max_length=255, blank=True, null=True)
    
    project_original_id = models.CharField(max_length=255, blank=True, null=True)
    submitter_account_original_id = models.CharField(max_length=255, blank=True, null=True)
    submitter_user_id = models.IntegerField(blank=True, null=True)

    
class Changes(models.Model):
    status = models.BooleanField(default=False)
    parent_commit_id = models.CharField(max_length=255, blank=True, null=True)
    merged_commit_id = models.CharField(max_length=255, blank=True, null=True)
    commit_date = models.DateTimeField(blank=True, null=True)
    
    project_original_id = models.CharField(max_length=255, blank=True, null=True)
    series_original_id = models.JSONField(blank=True, null=True)

    
class MailingLists(models.Model):
    web_url = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    sender_email = models.CharField(max_length=255, blank=True, null=True)
    subject = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    
    project_original_id = models.CharField(max_length=255, blank=True, null=True)

    
class Patches(models.Model):
    original_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    msg_id = models.TextField(blank=True, null=True)
    msg_content = models.TextField(blank=True, null=True)
    code_diff = models.TextField(blank=True, null=True)
    api_url = models.CharField(max_length=255, blank=True, null=True)
    web_url = models.CharField(max_length=255, blank=True, null=True)
    commit_ref = models.TextField(blank=True, null=True)
    
    change_id1 = models.IntegerField(blank=True, null=True)
    change_id2 = models.IntegerField(blank=True, null=True)
    mailing_list_id = models.IntegerField(blank=True, null=True)
    series_original_id = models.CharField(max_length=255, blank=True, null=True)
    submitter_account_original_id = models.CharField(max_length=255, blank=True, null=True)
    submitter_user_id = models.IntegerField(blank=True, null=True)
    project_original_id = models.CharField(max_length=255, blank=True, null=True)

    
class Comments(models.Model):
    original_id = models.CharField(max_length=255, unique=True)
    msg_id = models.TextField(blank=True, null=True)
    msg_content = models.TextField(blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    subject = models.TextField(blank=True, null=True)
    reply_to_msg_id = models.TextField(blank=True, null=True)
    web_url = models.CharField(max_length=255, blank=True, null=True)
    
    change_id1 = models.IntegerField(blank=True, null=True)
    change_id2 = models.IntegerField(blank=True, null=True)
    mailing_list_id = models.IntegerField(blank=True, null=True)
    submitter_account_original_id = models.CharField(max_length=255, blank=True, null=True)
    submitter_user_id = models.IntegerField(blank=True, null=True)
    patch_original_id = models.CharField(max_length=255, blank=True, null=True)
    project_original_id = models.CharField(max_length=255, blank=True, null=True)