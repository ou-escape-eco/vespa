from time import sleep

from celery import shared_task
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import DataExport


@shared_task
def generate_export(export_id):
    export = DataExport.objects.get(id=export_id)
    print(export.queryset.count())
    print(export.queryset_params)

@receiver(post_save, sender=DataExport)
def queue_export(sender, **kwargs):
    if kwargs['created']:
        generate_export.delay(kwargs['instance'].id)