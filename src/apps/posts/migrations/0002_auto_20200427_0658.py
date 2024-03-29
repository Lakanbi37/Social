# Generated by Django 3.0.5 on 2020-04-27 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='photos',
            field=models.ManyToManyField(blank=True, related_name='albums', to='posts.Media'),
        ),
        migrations.AlterField(
            model_name='post',
            name='media',
            field=models.ManyToManyField(blank=True, related_name='posts', to='posts.Media'),
        ),
        migrations.AlterField(
            model_name='story',
            name='media',
            field=models.ManyToManyField(blank=True, related_name='stories', to='posts.Media'),
        ),
    ]
