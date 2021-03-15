import csv
import io
import urllib
import yaml
import zipfile

import seaborn

from astropy.stats import sigma_clip
from astropy.table import vstack

from celery import shared_task

from django.core.files.base import ContentFile
from django.db.models.signals import post_save
from django.dispatch import receiver

from matplotlib import pyplot

from PIL import Image

from .models import DataExport, Star, FoldedLightcurve


EXPORT_DATA_DESCRIPTION = {
    'SuperWASP ID': 'The unique identifier for the source',
    'Period Length': 'The period length in seconds',
    'RA': 'Right ascension in hours',
    'Dec': 'Declination in degrees',
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
                'object_count': export.queryset.count(),
            }))
        export.export_file.save(export.EXPORT_FILE_NAME, export_file)
    except:
        export.export_status = export.STATUS_FAILED
        export.save()
        raise

    export.export_status = export.STATUS_COMPLETE
    export.save()


@shared_task
def download_fits(star_id):
    star = Star.objects.get(id=star_id)
    encoded_params = urllib.parse.urlencode(
        {'objid': star.superwasp_id.replace('1SWASP', '1SWASP ')},
        quote_via=urllib.parse.quote,
    )
    fits_url = f'http://wasp.warwick.ac.uk/lcextract?{encoded_params}'
    fits_data = urllib.request.urlopen(fits_url, timeout=30)
    star.fits_file.save(f'{star.superwasp_id}.fits', fits_data)
    star.save()

    for lightcurve in star.foldedlightcurve_set.all():
        lightcurve.image_location


@shared_task
def generate_images(lightcurve_id):
    lightcurve = FoldedLightcurve.objects.get(id=lightcurve_id)

    if not lightcurve.star.fits:
        return
    
    ts = lightcurve.timeseries
    if not ts:
        return
    epoch_length = ts['time'].max() - ts['time'].min()
    ts_extend = ts.copy()
    ts_extend['time'] = ts_extend['time'] + epoch_length
    ts = vstack([ts, ts_extend])
    ts_flux = sigma_clip(ts['TAMFLUX2'], sigma=4)
    ts_data = {
        'time': ts.time.jd,
        'flux': ts_flux,
    }
    fig = pyplot.figure()
    plot = seaborn.scatterplot(
        data=ts_data,
        x='time',
        y='flux',
        alpha=0.5,
        s=1,
    )
    plot.set_title(
        f'{lightcurve.star.superwasp_id} Period {lightcurve.period_length}s ({lightcurve.get_classification_display()})'
    )
    image_data = ContentFile(b'')
    fig.savefig(image_data)
    lightcurve.image_file.save(f'lightcurve-{lightcurve.id}.png', image_data)

    thumbnail_data = ContentFile(b'')
    thumbmail_image = Image.open(image_data)
    thumbmail_image.thumbnail((100, 60))
    thumbmail_image.save(thumbnail_data, format='png')
    lightcurve.thumbnail_file.save(f'lightcurve-{lightcurve.id}-small.png', thumbnail_data)

    lightcurve.image_version = lightcurve.CURRENT_IMAGE_VERSION
    lightcurve.save()