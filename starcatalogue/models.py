from django.db import models


class Star(models.Model):
    superwasp_id = models.CharField(unique=True, max_length=26)


class FoldedLightcurve(models.Model):
    star = models.ForeignKey(to=Star, on_delete=models.CASCADE)


class ZooniverseSubject(models.Model):
    zooniverse_id = models.IntegerField(unique=True)
    lightcurve = models.OneToOneField(to=FoldedLightcurve, on_delete=models.CASCADE)