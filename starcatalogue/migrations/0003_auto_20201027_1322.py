# Generated by Django 3.1.2 on 2020-10-27 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('starcatalogue', '0002_auto_20201026_1432'),
    ]

    operations = [
        migrations.AlterField(
            model_name='foldedlightcurve',
            name='chi_squared',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='foldedlightcurve',
            name='sigma',
            field=models.FloatField(null=True),
        ),
    ]
