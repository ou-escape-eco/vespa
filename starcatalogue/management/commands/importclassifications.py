from django.core.management.base import BaseCommand, CommandError

import csv

from starcatalogue.models import Star, FoldedLightcurve, ZooniverseSubject



class Command(BaseCommand):
    help = ('Creates records for stars, lightcurves, and Zooniverse subjects. '
            'Imports classifications (class_top.csv) . Run this first.')

    def add_arguments(self, parser):
        parser.add_argument('file', nargs=1, type=open)

    def handle(self, *args, **options):
        r = csv.reader(options['file'][0], delimiter=' ', skipinitialspace=True)
        imported_total = 0
        for row in r:
            subject_id = row[0]
            superwasp_id = row[1]
            period_number = int(row[2])
            period_length = float(row[3])
            classification = int(row[4])
            period_uncertainty = float(row[5])
            classification_count = int(row[6])

            if classification == FoldedLightcurve.JUNK:
                continue

            star, created = Star.objects.get_or_create(superwasp_id=superwasp_id)
            lightcurve, created = FoldedLightcurve.objects.get_or_create(
                star=star,
                period_number=period_number,
            )
            
            lightcurve.period_length = period_length
            lightcurve.classification = classification
            lightcurve.period_uncertainty = period_uncertainty
            lightcurve.classification_count = classification_count
            lightcurve.save()

            zooniverse_subject, created = ZooniverseSubject.objects.get_or_create(
                zooniverse_id=subject_id, 
                lightcurve=lightcurve,
            )

            if created:
                imported_total += 1
        
        self.stdout.write("Total imported: {}".format(imported_total))
