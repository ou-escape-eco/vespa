import datetime
import logging
import urllib
import uuid

import numpy

from django.db import models
from django.utils import timezone

import astropy.io.fits as fits
from astropy import units
from astropy.coordinates import SkyCoord
from astropy.stats import sigma_clip
from astropy.timeseries import TimeSeries

from celery.result import AsyncResult
from humanize.time import naturaldelta
from humanize import naturalsize

from .fields import SPointField


OUTLIER_SIGMA_CLIP = 5
FLUX_MAX_CLIP = 2e5

logger = logging.getLogger(__name__)


def export_upload_to(instance, filename):
    return f'exports/{instance.id.hex[:3]}/{instance.id.hex}/{filename}'

def star_upload_to(instance, filename):
    return f'sources/{instance.superwasp_id}/v{instance.CURRENT_IMAGE_VERSION}_{filename}'

def lightcurve_upload_to(instance, filename):
    return f'sources/{instance.star.superwasp_id}/v{instance.CURRENT_IMAGE_VERSION}_{filename}'


class ImageGenerator(object):
    def get_or_generate_image(self, image_attr, generation_task, default=None):
        image_not_present = not image_attr or not self.image_version
        image_outdated = self.image_version and self.image_version < self.CURRENT_IMAGE_VERSION
        if image_not_present or image_outdated:
            if (
                not self.images_celery_task_id
                or AsyncResult(self.images_celery_task_id).ready()
                or not self.image_celery_started
                or self.image_celery_started < (timezone.now() - datetime.timedelta(minutes=5))
            ):
                self.images_celery_task_id = generation_task.delay(self.id).id
                self.image_celery_started = timezone.now()
                self.save()
            if image_not_present:
                return default
        elif self.images_celery_task_id:
            AsyncResult(self.images_celery_task_id).forget()
        return image_attr.url


class Star(models.Model, ImageGenerator):
    CURRENT_IMAGE_VERSION = 0.91
    CURRENT_STATS_VERSION = 0.2

    superwasp_id = models.CharField(unique=True, max_length=26)
    fits_file = models.FileField(null=True, upload_to=star_upload_to)
    fits_celery_task_id = models.UUIDField(null=True)
    fits_celery_started = models.DateTimeField(null=True)
    fits_error_count = models.IntegerField(default=0)

    image_file = models.ImageField(null=True, upload_to=star_upload_to)
    images_celery_task_id = models.UUIDField(null=True)
    image_version = models.FloatField(null=True)
    image_celery_started = models.DateTimeField(null=True)

    _min_magnitude = models.FloatField(null=True)
    _mean_magnitude = models.FloatField(null=True)
    _max_magnitude = models.FloatField(null=True)
    stats_version = models.FloatField(null=True)

    location = SPointField(null=True)

    @classmethod
    def outlier_clip(cls, flux):
        return sigma_clip(
            numpy.ma.masked_greater(
                numpy.ma.masked_less(
                    flux,
                    -FLUX_MAX_CLIP,
                ),
                FLUX_MAX_CLIP
            ),
            sigma=OUTLIER_SIGMA_CLIP
        )

    @property
    def coords_str(self):
        return self.superwasp_id.replace('1SWASP', '')

    @property
    def coords(self):
        return SkyCoord(self.coords_str, unit=(units.hour, units.deg))
    
    @property
    def coords_quoted(self):
        return urllib.parse.quote(self.coords_str)

    @property
    def ra(self):
        return self.coords.ra.to_string(units.hour)
    
    @property
    def dec(self):
        return self.coords.dec

    @property
    def ra_quoted(self):
        coords = self.coords_str
        return urllib.parse.quote(f'{coords[1:3]}:{coords[3:5]}:{coords[5:10]}')

    @property
    def dec_quoted(self):
        coords = self.coords_str
        return urllib.parse.quote(f'{coords[10:13]}:{coords[13:15]}:{coords[15:]}')

    def set_location(self):
        coords = self.coords
        self.location = (coords.ra.to_value(), coords.dec.to_value())
        self.save()

    @property
    def lightcurves(self):
        return self.foldedlightcurve_set.all().order_by('period_length')

    @property
    def fits(self):
        if (
            not self.fits_file
            and (
                not self.fits_celery_task_id
                or AsyncResult(self.fits_celery_task_id).ready()
                or not self.fits_celery_started
                or self.fits_celery_started < (timezone.now() - datetime.timedelta(minutes=5))
            )
        ):
            self.fits_celery_task_id = download_fits.apply_async(
                (self.id,),
                expires=300,
            ).id
            self.fits_celery_started = timezone.now()
            self.save()
            return None

        if self.fits_celery_task_id:
            AsyncResult(self.fits_celery_task_id).forget()

        return self.fits_file

    @property
    def fits_file_naturalsize(self):
        return naturalsize(self.fits_file.size)

    @property
    def timeseries(self):
        if not self.fits:
            return

        try:
            with fits.open(self.fits.path) as fits_file:
                hjd_col = fits.Column(name='HJD', format='D', array=fits_file[1].data['TMID']/86400 + 2453005.5)
                lc_data = fits.BinTableHDU.from_columns(fits_file[1].data.columns + fits.ColDefs([hjd_col]))
                return TimeSeries.read(lc_data, time_column='HJD', time_format='jd')
        except OSError as e:
            logger.warning(f'Could not read FITS file {self.fits.path} for star {self.id}')
            logger.warning(str(e))
            self.fits_file = None
            self.fits_error_count += 1
            self.save()

    @property
    def image_location(self):
        return self.get_image_location()

    def get_image_location(self):
        return self.get_or_generate_image(self.image_file, generate_star_images)

    @property
    def cerit_url(self):
        return f'https://wasp.cerit-sc.cz/search?objid={self.coords_quoted}&radius=1&radiusUnit=deg&limit=10'

    @property
    def simbad_url(self):
        return f'http://simbad.u-strasbg.fr/simbad/sim-coo?Coord={self.ra_quoted}+{self.dec_quoted}&Radius=2&Radius.unit=arcmin&submit=submit+query'
    
    @property
    def asassn_url(self):
        return f'https://asas-sn.osu.edu/photometry?ra={self.ra_quoted}&dec={self.dec_quoted}&radius=2'

    def get_magnitude(self, attr_name='_mean_magnitude', force=False):
        agg_funcs = {
            '_mean_magnitude': lambda x: x.mean(),
            '_min_magnitude': lambda x: x.min(),
            '_max_magnitude': lambda x: x.max(),
        }

        if (
            not force and 
            self.stats_version is not None and
            self.stats_version >= self.CURRENT_STATS_VERSION and 
            getattr(self, attr_name)
        ):
            return getattr(self, attr_name)

        timeseries = self.timeseries
        if not timeseries:
            return

        mag = 15 - 2.5 * numpy.log(
            agg_funcs[attr_name](Star.outlier_clip(timeseries['TAMFLUX2']))
        )
        setattr(self, attr_name, mag)
        self.stats_version = self.CURRENT_STATS_VERSION
        self.save()
        return mag

    def calculate_magnitudes(self, force=False):
        attrs = (
           '_mean_magnitude',
           '_min_magnitude',
           '_max_magnitude',
        )
        for attr_name in attrs:
            self.get_magnitude(attr_name, force=force)

    @property
    def mean_magnitude(self):
        return self.get_magnitude('_mean_magnitude')

    @property
    def max_magnitude(self):
        return self.get_magnitude('_max_magnitude')

    @property
    def min_magnitude(self):
        return self.get_magnitude('_min_magnitude')


class FoldedLightcurve(models.Model, ImageGenerator):
    PULSATOR = 1
    EA_EB = 2
    EW = 3
    ROTATOR = 4
    UNKNOWN = 5
    JUNK = 6
    CLASSIFICATION_CHOICES = [
        (PULSATOR, 'Pulsator'),
        (EA_EB, 'EA/EB'),
        (EW, 'EW'),
        (ROTATOR, 'Rotator'),
        (UNKNOWN, 'Unknown'),
        (JUNK, 'Junk'),
    ]

    CERTAIN = 0
    UNCERTAIN = 1
    PERIOD_UNCERTAINTY_CHOICES = [
        (CERTAIN, 'Certain'),
        (UNCERTAIN, 'Uncertain'),
    ]

    CURRENT_IMAGE_VERSION = 0.9

    star = models.ForeignKey(to=Star, on_delete=models.CASCADE)

    period_number = models.IntegerField()
    period_length = models.FloatField(null=True)
    sigma = models.FloatField(null=True)
    chi_squared = models.FloatField(null=True)
    classification = models.IntegerField(choices=CLASSIFICATION_CHOICES, null=True)
    period_uncertainty = models.IntegerField(choices=PERIOD_UNCERTAINTY_CHOICES, null=True)
    classification_count = models.IntegerField(null=True)

    image_file = models.ImageField(null=True, upload_to=lightcurve_upload_to)
    thumbnail_file = models.ImageField(null=True, upload_to=lightcurve_upload_to)
    images_celery_task_id = models.UUIDField(null=True)
    image_version = models.FloatField(null=True)
    image_celery_started = models.DateTimeField(null=True)

    @property
    def natural_period(self):
        return naturaldelta(self.period_length)

    @property
    def image_location(self):
        return self.get_image_location()

    def get_image_location(self):
        return self.get_or_generate_image(
            self.image_file,
            generate_lightcurve_images,
            self.zooniversesubject.image_location,
        )

    @property
    def thumbnail_location(self):
        return self.get_thumbnail_location()

    def get_thumbnail_location(self):
        return self.get_or_generate_image(
            self.thumbnail_file,
            generate_lightcurve_images,
            self.zooniversesubject.thumbnail_location,
        )

    @property
    def timeseries(self):
        if not self.star.timeseries:
            return
        return self.star.timeseries.fold(
            period=self.period_length * units.second,
        )


class ZooniverseSubject(models.Model):
    zooniverse_id = models.IntegerField(unique=True)
    lightcurve = models.OneToOneField(to=FoldedLightcurve, on_delete=models.CASCADE)

    subject_set_id = models.IntegerField(null=True)
    retired_at = models.DateTimeField(null=True)
    image_location = models.URLField(null=True)

    @property
    def thumbnail_location(self):
        return 'https://thumbnails.zooniverse.org/100x80/{}'.format(
            self.image_location.replace('https://', ''),
        )


class DataExport(models.Model):
    EXPORT_FILE_NAME = 'superwasp-vespa-export.zip'

    CHECKBOX_CHOICES = [
        (True, 'on'),
        (False, 'off'),
    ]
    CHECKBOX_CHOICES_DICT = dict([ (v, k) for (k, v) in CHECKBOX_CHOICES])

    STATUS_PENDING = 0
    STATUS_RUNNING = 1
    STATUS_COMPLETE = 2
    STATUS_FAILED = 3
    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_RUNNING, 'Running'),
        (STATUS_COMPLETE, 'Complete'),
        (STATUS_FAILED, 'Failed'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    min_period = models.FloatField(null=True)
    max_period = models.FloatField(null=True)
    min_magnitude = models.FloatField(null=True)
    max_magnitude = models.FloatField(null=True)
    certain_period = models.BooleanField(choices=CHECKBOX_CHOICES, default=True)
    uncertain_period = models.BooleanField(choices=CHECKBOX_CHOICES, default=True)
    type_pulsator = models.BooleanField(choices=CHECKBOX_CHOICES, default=True)
    type_rotator = models.BooleanField(choices=CHECKBOX_CHOICES, default=True)
    type_ew = models.BooleanField(choices=CHECKBOX_CHOICES, default=True)
    type_eaeb = models.BooleanField(choices=CHECKBOX_CHOICES, default=True)
    type_unknown = models.BooleanField(choices=CHECKBOX_CHOICES, default=True)
    search = models.TextField(null=True)
    search_radius = models.FloatField(null=True)

    data_version = models.FloatField()

    celery_task_id = models.UUIDField(null=True)
    export_status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_PENDING)
    export_file = models.FileField(
        upload_to=export_upload_to,
        null=True,
    )

    progress = models.FloatField(default=0.0)

    created = models.DateTimeField(auto_now_add=True)

    @property
    def queryset_params(self):
        return {
            'min_period': self.min_period,
            'max_period': self.max_period,
            'min_magnitude': self.min_magnitude,
            'max_magnitude': self.max_magnitude,
            'certain_period': self.get_certain_period_display(),
            'uncertain_period': self.get_uncertain_period_display(),
            'type_pulsator': self.get_type_pulsator_display(),
            'type_rotator': self.get_type_rotator_display(),
            'type_ew': self.get_type_ew_display(),
            'type_eaeb': self.get_type_eaeb_display(),
            'type_unknown': self.get_type_unknown_display(),
            'search': self.search,
            'search_radius': self.search_radius,
        }
    
    @property
    def queryset(self):
        return StarListView().get_queryset(params=self.queryset_params)

    @property
    def export_file_naturalsize(self):
        return naturalsize(self.export_file.size)


from .tasks import download_fits, generate_lightcurve_images, generate_star_images
from .views import StarListView