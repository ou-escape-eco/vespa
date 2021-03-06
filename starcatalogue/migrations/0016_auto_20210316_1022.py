# Generated by Django 3.1.7 on 2021-03-16 10:22

from django.db import migrations, models
import starcatalogue.models


class Migration(migrations.Migration):

    dependencies = [
        ('starcatalogue', '0015_auto_20210315_1723'),
    ]

    operations = [
        migrations.AddField(
            model_name='star',
            name='image_file',
            field=models.ImageField(null=True, upload_to=starcatalogue.models.star_upload_to),
        ),
        migrations.AddField(
            model_name='star',
            name='image_version',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='star',
            name='images_celery_task_id',
            field=models.UUIDField(null=True),
        ),
    ]
