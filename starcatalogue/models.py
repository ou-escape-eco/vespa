import uuid

from django.db import models

from astropy.coordinates import SkyCoord
from astropy import units
from humanize.time import naturaldelta


class Star(models.Model):
    superwasp_id = models.CharField(unique=True, max_length=26)

    @property
    def coords(self):
        return SkyCoord(self.superwasp_id.replace('1SWASP', ''), unit=(units.hour, units.deg))

    @property
    def ra(self):
        return self.coords.ra.to_string(units.hour)
    
    @property
    def dec(self):
        return self.coords.dec


class FoldedLightcurve(models.Model):
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

    star = models.ForeignKey(to=Star, on_delete=models.CASCADE)

    period_number = models.IntegerField()
    period_length = models.FloatField(null=True)
    sigma = models.FloatField(null=True)
    chi_squared = models.FloatField(null=True)
    classification = models.IntegerField(choices=CLASSIFICATION_CHOICES, null=True)
    period_uncertainty = models.IntegerField(choices=PERIOD_UNCERTAINTY_CHOICES, null=True)
    classification_count = models.IntegerField(null=True)

    @property
    def natural_period(self):
        return naturaldelta(self.period_length)


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
    CHECKBOX_CHOICES = [
        (True, 'on'),
        (False, 'off'),
    ]
    CHECKBOX_CHOICES_DICT = dict([ (v, k) for (k, v) in CHECKBOX_CHOICES])

    ORDER_ASC = 0
    ORDER_DESC = 1
    ORDER_CHOICES = [
        (ORDER_ASC, 'asc'),
        (ORDER_DESC, 'desc')
    ]
    ORDER_CHOICES_DICT = dict([ (v, k) for (k, v) in ORDER_CHOICES])

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    min_period = models.FloatField(null=True)
    max_period = models.FloatField(null=True)
    type_pulsator = models.BooleanField(choices=CHECKBOX_CHOICES, default=True)
    type_rotator = models.BooleanField(choices=CHECKBOX_CHOICES, default=True)
    type_ew = models.BooleanField(choices=CHECKBOX_CHOICES, default=True)
    type_eaeb = models.BooleanField(choices=CHECKBOX_CHOICES, default=True)
    type_unknown = models.BooleanField(choices=CHECKBOX_CHOICES, default=True)
    search = models.TextField(null=True)
    sort = models.CharField(max_length=18, null=True)
    order = models.IntegerField(choices=ORDER_CHOICES, null=True)

    data_version = models.FloatField()

    created = models.DateTimeField(auto_now_add=True)

    @property
    def queryset_params(self):
        return {
            'min_period': self.min_period,
            'max_period': self.max_period,
            'type_pulsator': self.get_type_pulsator_display(),
            'type_rotator': self.get_type_rotator_display(),
            'type_ew': self.get_type_ew_display(),
            'type_eaeb': self.get_type_eaeb_display(),
            'type_unknown': self.get_type_unknown_display(),
            'search': self.search,
            'sort': self.sort,
            'order': self.get_order_display(),
        }
    
    @property
    def queryset(self):
        return StarListView().get_queryset(params=self.queryset_params)

from .tasks import generate_export
from .views import StarListView