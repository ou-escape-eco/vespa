from django.core.management.base import BaseCommand, CommandError

import csv
import json

from starcatalogue.models import ZooniverseSubject


IMPORT_LIMIT = 1000


class Command(BaseCommand):
    help = 'Imports Zooniverse subject metadata (superwasp-variable-stars-subjects.csv)'

    def add_arguments(self, parser):
        parser.add_argument('file', nargs=1, type=open)

    def handle(self, *args, **options):
        r = csv.DictReader(options['file'][0])
        imported_total = 0
        for row in r:
            try:
                zooniverse_subject = ZooniverseSubject.objects.get(zooniverse_id=int(row['subject_id']))
            except ZooniverseSubject.DoesNotExist:
                continue

            zooniverse_subject.subject_set_id = int(row['subject_set_id'])
            #TODO: zooniverse_subject.retired_at = 
            zooniverse_subject.image_location = json.loads(row['locations'])["0"]
            zooniverse_subject.save()

            imported_total += 1
            if imported_total >= IMPORT_LIMIT:
                break
        
        self.stdout.write("Total imported: {}".format(imported_total))