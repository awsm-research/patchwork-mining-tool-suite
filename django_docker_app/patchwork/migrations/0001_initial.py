# Generated by Django 3.2.15 on 2022-09-19 04:32

from django.db import migrations, models
import djongo.models.fields
import djongo.storage


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Accounts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_id', models.CharField(max_length=255, unique=True)),
                ('email', models.CharField(blank=True, max_length=255, null=True)),
                ('username', models.CharField(blank=True, max_length=255, null=True)),
                ('api_url', models.CharField(blank=True, max_length=255, null=True)),
                ('user_id', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Changes1',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(default=False)),
                ('parent_commit_id', models.CharField(blank=True, max_length=255, null=True)),
                ('merged_commit_id', models.CharField(blank=True, max_length=255, null=True)),
                ('commit_date', models.DateTimeField(blank=True, null=True)),
                ('project_original_id', models.CharField(blank=True, max_length=255, null=True)),
                ('series_original_id', djongo.models.fields.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Changes2',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(default=False)),
                ('parent_commit_id', models.CharField(blank=True, max_length=255, null=True)),
                ('merged_commit_id', models.CharField(blank=True, max_length=255, null=True)),
                ('commit_date', models.DateTimeField(blank=True, null=True)),
                ('project_original_id', models.CharField(blank=True, max_length=255, null=True)),
                ('series_original_id', djongo.models.fields.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_id', models.CharField(max_length=255, unique=True)),
                ('msg_id', models.TextField(blank=True, null=True)),
                ('msg_content', models.FileField(blank=True, null=True, storage=djongo.storage.GridFSStorage(base_url='https://127.0.0.1:8000/textfiles/', collection='textfiles'), upload_to='comment_msg_content')),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('subject', models.TextField(blank=True, null=True)),
                ('reply_to_msg_id', models.TextField(blank=True, null=True)),
                ('web_url', models.CharField(blank=True, max_length=255, null=True)),
                ('change_id1', models.IntegerField(blank=True, null=True)),
                ('change_id2', models.IntegerField(blank=True, null=True)),
                ('mailing_list_id', models.IntegerField(blank=True, null=True)),
                ('submitter_account_original_id', models.CharField(blank=True, max_length=255, null=True)),
                ('submitter_user_id', models.IntegerField(blank=True, null=True)),
                ('patch_original_id', models.CharField(blank=True, max_length=255, null=True)),
                ('project_original_id', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MailingLists',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('web_url', models.CharField(blank=True, max_length=255, null=True)),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('sender_email', models.CharField(blank=True, max_length=255, null=True)),
                ('subject', models.TextField(blank=True, null=True)),
                ('content', models.FileField(blank=True, null=True, storage=djongo.storage.GridFSStorage(base_url='https://127.0.0.1:8000/textfiles/', collection='textfiles'), upload_to='mailing_list_email_content')),
                ('project_original_id', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Patches',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_id', models.CharField(max_length=255, unique=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('state', models.CharField(blank=True, max_length=255, null=True)),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('msg_id', models.TextField(blank=True, null=True)),
                ('msg_content', models.FileField(blank=True, null=True, storage=djongo.storage.GridFSStorage(base_url='https://127.0.0.1:8000/textfiles/', collection='textfiles'), upload_to='patch_msg_content')),
                ('code_diff', models.FileField(blank=True, null=True, storage=djongo.storage.GridFSStorage(base_url='https://127.0.0.1:8000/textfiles/', collection='textfiles'), upload_to='patch_code_diff')),
                ('api_url', models.CharField(blank=True, max_length=255, null=True)),
                ('web_url', models.CharField(blank=True, max_length=255, null=True)),
                ('commit_ref', models.TextField(blank=True, null=True)),
                ('change_id1', models.IntegerField(blank=True, null=True)),
                ('change_id2', models.IntegerField(blank=True, null=True)),
                ('mailing_list_id', models.IntegerField(blank=True, null=True)),
                ('series_original_id', models.CharField(blank=True, max_length=255, null=True)),
                ('submitter_account_original_id', models.CharField(blank=True, max_length=255, null=True)),
                ('submitter_user_id', models.IntegerField(blank=True, null=True)),
                ('project_original_id', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Projects',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_id', models.CharField(max_length=255, unique=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('repo_url', models.CharField(blank=True, max_length=255, null=True)),
                ('api_url', models.CharField(blank=True, max_length=255, null=True)),
                ('web_url', models.CharField(blank=True, max_length=255, null=True)),
                ('list_id', models.CharField(blank=True, max_length=255, null=True)),
                ('list_address', models.CharField(blank=True, max_length=255, null=True)),
                ('maintainer_account_original_id', djongo.models.fields.JSONField(blank=True, null=True)),
                ('maintainer_user_id', djongo.models.fields.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Series',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_id', models.CharField(max_length=255, unique=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('created_date', models.DateTimeField(blank=True, null=True)),
                ('version', models.IntegerField(blank=True, null=True)),
                ('total', models.IntegerField(blank=True, null=True)),
                ('received_total', models.IntegerField(blank=True, null=True)),
                ('cover_letter_content', models.FileField(blank=True, null=True, storage=djongo.storage.GridFSStorage(base_url='https://127.0.0.1:8000/textfiles/', collection='textfiles'), upload_to='series_cover_letter_content')),
                ('api_url', models.CharField(blank=True, max_length=255, null=True)),
                ('web_url', models.CharField(blank=True, max_length=255, null=True)),
                ('project_original_id', models.CharField(blank=True, max_length=255, null=True)),
                ('submitter_account_original_id', models.CharField(blank=True, max_length=255, null=True)),
                ('submitter_user_id', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_original_id', djongo.models.fields.JSONField(blank=True, null=True)),
            ],
        ),
    ]
