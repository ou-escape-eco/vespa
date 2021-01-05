from django.shortcuts import render

from starcatalogue.models import Star, FoldedLightcurve


def index(request):
    stars = Star.objects.all()[:10]
    return render(request, 'index.html', context={'stars': stars})

def browse(request):
    stars = Star.objects.all()[:10]
    return render(request, 'browse.html', context={'stars': stars})

def download(request):
    return render(request, 'download.html')