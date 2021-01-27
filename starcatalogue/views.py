from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

from starcatalogue.models import Star, FoldedLightcurve


class StarListView(ListView):
    model = Star
    paginate_by = 20


class IndexListView(StarListView):
    template_name = 'index.html'


class DownloadView(TemplateView):
    template_name = 'starcatalogue/download.html'