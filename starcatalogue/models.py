from django.db import models


class Star(models.Model):
    superwasp_id = models.CharField(unique=True, max_length=26)


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
    period_length = models.FloatField()
    sigma = models.FloatField()
    chi_squared = models.FloatField()
    classification = models.IntegerField(choices=CLASSIFICATION_CHOICES)
    period_uncertainty = models.IntegerField(choices=PERIOD_UNCERTAINTY_CHOICES)
    classification_count = models.IntegerField()


class ZooniverseSubject(models.Model):
    zooniverse_id = models.IntegerField(unique=True)
    lightcurve = models.OneToOneField(to=FoldedLightcurve, on_delete=models.CASCADE)

    subject_set_id = models.IntegerField()
    retired_at = models.DateTimeField()
    image_location = models.URLField()