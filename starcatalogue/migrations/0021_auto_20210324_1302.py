# Generated by Django 3.1.7 on 2021-03-24 13:02

from django.db import migrations
from django.contrib.postgres.operations import CreateExtension


class Migration(migrations.Migration):

    dependencies = [
        ('starcatalogue', '0020_auto_20210317_1154'),
    ]

    operations = [
        CreateExtension('pg_sphere')
    ]
