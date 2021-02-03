from django.db import models

from astropy.coordinates import SkyCoord
from astropy import units


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