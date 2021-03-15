# Generated by Django 3.1.7 on 2021-03-09 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('starcatalogue', '0006_dataexport_export_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataexport',
            name='celery_task_id',
            field=models.UUIDField(null=True),
        ),
        migrations.AddField(
            model_name='dataexport',
            name='export_status',
            field=models.IntegerField(choices=[(0, 'Pending'), (1, 'Running'), (2, 'Complete'), (3, 'Failed')], default=0),
        ),
    ]