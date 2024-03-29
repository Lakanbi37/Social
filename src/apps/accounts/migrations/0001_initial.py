# Generated by Django 3.0.5 on 2020-04-27 13:04

import core.utils.utils
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Favourite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Recommendation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('slug', models.SlugField(blank=True, null=True)),
                ('bio', models.TextField(blank=True, null=True)),
                ('group_type', models.CharField(choices=[('public', 'Public'), ('private', 'Private')], default=(('public', 'Public'), ('private', 'Private')), max_length=30)),
                ('avatar', models.ImageField(upload_to=core.utils.utils.upload_location)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'permissions': [('group_admin', 'Admin'), ('group_member', 'Group Member')],
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_type', models.CharField(choices=[('public', 'Public'), ('private', 'Private'), ('company', 'Company')], default='public', max_length=30)),
                ('avatar', models.ImageField(blank=True, null=True, upload_to=core.utils.utils.avatar_upload_location)),
                ('bookmarked_accounts', models.ManyToManyField(blank=True, related_name='bookmarked', through='accounts.Bookmark', to=settings.AUTH_USER_MODEL)),
                ('bookmarked_groups', models.ManyToManyField(blank=True, related_name='bookmarked', to='accounts.UserGroup')),
                ('following', models.ManyToManyField(blank=True, related_name='followed_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': [('user_profile', 'Profile')],
            },
        ),
    ]
