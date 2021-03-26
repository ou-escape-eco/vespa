import os

from celery import Celery
from django.db.models import Q


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vespa.settings')

app = Celery('vespa')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(120.0, queue_image_generations.s())
    sender.add_periodic_task(300, calculate_magnitudes.s())
    sender.add_periodic_task(60, set_locations.s())

@app.task
def queue_image_generations():
    from starcatalogue.models import Star, FoldedLightcurve
    for star in Star.objects.filter(fits_error_count__lt=5).filter(
        Q(image_version=None) 
        | Q(image_version__lt=Star.CURRENT_IMAGE_VERSION)
    )[:10]:
        star.get_image_location()

    for lightcurve in FoldedLightcurve.objects.filter(star__fits_error_count__lt=5).filter(
        Q(image_version=None) 
        | Q(image_version__lt=FoldedLightcurve.CURRENT_IMAGE_VERSION)
    )[:10]:
        lightcurve.get_image_location()

@app.task
def calculate_magnitudes():
    from starcatalogue.models import Star
    for star in Star.objects.filter(
        Q(fits_file__isnull=False)
        & (
            Q(_min_magnitude__isnull=True)
            | Q(_max_magnitude__isnull=True)
            | Q(_mean_magnitude__isnull=True)
        )
    )[:100]:
        star.calculate_magnitudes()

@app.task
def set_locations():
    from starcatalogue.models import Star
    for star in Star.objects.filter(location=None)[:1000]:
        star.set_location()