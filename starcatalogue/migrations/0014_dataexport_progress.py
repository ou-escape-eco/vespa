# Generated by Django 3.1.7 on 2021-03-15 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('starcatalogue', '0013_star_fits_celery_started'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataexport',
            name='progress',
            field=models.FloatField(null=True),
        ),
    ]
