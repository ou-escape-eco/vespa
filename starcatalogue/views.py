from django.shortcuts import render

from starcatalogue.models import Star, FoldedLightcurve


def index(request):
    stars = Star.objects.all()
    return render(request, 'index.html', context={'stars': stars})