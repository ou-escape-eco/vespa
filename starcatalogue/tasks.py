import csv
import io
import yaml
import zipfile

from time import sleep

from celery import shared_task
from django.core.files.base import ContentFile
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import DataExport


EXPORT_DATA_DESCRIPTION = {
    'SuperWASP ID': '',
    'Period Length': 'The period length in seconds',
    'RA': '',
    'Dec': '',
    'Classification': 'The candidate variable star type',
}


@shared_task
def generate_export(export_id):
    export = DataExport.objects.get(id=export_id)
    if export.export_status in (export.STATUS_RUNNING, export.STATUS_COMPLETE):
        return

    export.export_status = export.STATUS_RUNNING
    export.save()

    try:
        export_csv = io.StringIO()
        w = csv.DictWriter(export_csv, fieldnames=EXPORT_DATA_DESCRIPTION.keys())
        w.writeheader()
        for record in export.queryset:
            w.writerow({
                'SuperWASP ID': record.star.superwasp_id,
                'Period Length': record.period_length,
                'RA': record.star.ra,
                'Dec': record.star.dec,
                'Classification': record.get_classification_display(), 
            })

        export_file = ContentFile(b'')
        with zipfile.ZipFile(export_file, 'w') as export_zip:
            export_zip.writestr('export.csv', export_csv.getvalue())
            export_zip.writestr('fields.yaml', yaml.dump(EXPORT_DATA_DESCRIPTION))
            export_zip.writestr('params.yaml', yaml.dump({
                'min_period': export.min_period,
                'max_period': export.max_period,
                'type_pulsator': export.type_pulsator,
                'type_rotator': export.type_rotator,
                'type_ew': export.type_ew,
                'type_eaeb': export.type_eaeb,
                'type_unknown': export.type_unknown,
                'search': export.search,
                'data_version': export.data_version,
            }))
        export.export_file.save(export.export_file_name, export_file)
    except:
        export.export_status = export.STATUS_FAILED
        export.save()
        raise

    export.export_status = export.STATUS_COMPLETE
    export.save()

@receiver(post_save, sender=DataExport)
def queue_export(sender, **kwargs):
    if kwargs['created']:
        kwargs['instance'].celery_task_id = generate_export.delay(kwargs['instance'].id).id
        kwargs['instance'].save()