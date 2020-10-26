from django.core.management.base import BaseCommand, CommandError

import csv

from starcatalogue.models import Star, FoldedLightcurve


IMPORT_LIMIT = 10


class Command(BaseCommand):
    help = 'Imports folded lightcurve data (results_total.dat)'

    def add_arguments(self, parser):
        parser.add_argument('file', nargs=1, type=open)

    def handle(self, *args, **options):
        r = csv.reader(options['file'][0], delimiter=' ', skipinitialspace=True)
        imported_total = 0
        for row in r:
            if row[7] != '0':
                continue
            superwasp_id = " ".join(row[1:3])
            period_number = int(row[3])
            period_length = float(row[4])
            sigma = float(row[5])
            chi_squared = float(row[6])


            star, created = Star.objects.get_or_create(superwasp_id=superwasp_id)
            lightcurve, created = FoldedLightcurve.objects.get_or_create(
                star=star,
                period_number=period_number,
                defaults={
                    'period_length': period_length,
                    'sigma': sigma,
                    'chi_squared': chi_squared,
                }
            )

            if created:
                imported_total += 1
                if imported_total >= IMPORT_LIMIT:
                    break
        
        self.stdout.write("Total imported: {}".format(imported_total))