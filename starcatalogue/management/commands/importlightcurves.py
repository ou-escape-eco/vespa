from django.core.management.base import BaseCommand, CommandError

import csv

from starcatalogue.models import Star, FoldedLightcurve


class Command(BaseCommand):
    help = 'Imports folded lightcurve data (results_total.dat)'

    def add_arguments(self, parser):
        parser.add_argument('file', nargs=1, type=open)

    def handle(self, *args, **options):
        r = csv.reader(options['file'][0], delimiter=' ', skipinitialspace=True)
        imported_total = 0
        for count, row in enumerate(r):
            try:
                if row[7] != '0':
                    continue
                superwasp_id = "".join(row[1:3])
                period_number = int(row[3])
                period_length = float(row[4])
                sigma = float(row[5])
                chi_squared = float(row[6])
            except IndexError:
                print('Warning: Skipping row {} due to IndexError'.format(count))
                continue

            try:
                star = Star.objects.get(superwasp_id=superwasp_id)
                lightcurve = FoldedLightcurve.objects.get(
                    star=star,
                    period_number=period_number,
                )
            except (Star.DoesNotExist, FoldedLightcurve.DoesNotExist):
                continue

            lightcurve.period_length = period_length
            lightcurve.sigma = sigma
            lightcurve.chi_squared = chi_squared
            lightcurve.save()

            imported_total += 1
        
        self.stdout.write("Total imported: {}".format(imported_total))
