from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

from starcatalogue.models import Star, FoldedLightcurve


class StarListView(ListView):
    paginate_by = 20

    def get_queryset(self):
        qs = FoldedLightcurve.objects.all()

        self.min_period = self.request.GET.get('min_period', None)
        if self.min_period:
            qs = qs.filter(period_length__gte=self.min_period)
        
        self.max_period = self.request.GET.get('max_period', None)
        if self.max_period:
            qs = qs.filter(period_length__lte=self.max_period)

        self.type_pulsator = self.request.GET.get('type_pulsator', None)
        self.type_rotator = self.request.GET.get('type_rotator', None)
        self.type_ew = self.request.GET.get('type_ew', None)
        self.type_eaeb = self.request.GET.get('type_eaeb', None)
        self.type_unknown = self.request.GET.get('type_unknown', None)

        type_map = {
            FoldedLightcurve.PULSATOR: self.type_pulsator,
            FoldedLightcurve.EA_EB: self.type_eaeb,
            FoldedLightcurve.EW: self.type_ew,
            FoldedLightcurve.ROTATOR: self.type_rotator,
            FoldedLightcurve.UNKNOWN: self.type_unknown,
        }

        enabled_types = [ k for k, v in type_map.items() if v == 'on']

        # If nothing is enabled, enable everything
        # This works as a default, because why would anyone actually want to exclude all types?
        if not enabled_types:
            enabled_types = type_map.keys()
            self.type_pulsator = 'on'
            self.type_rotator = 'on'
            self.type_ew = 'on'
            self.type_eaeb = 'on'
            self.type_unknown = 'on'

        qs = qs.filter(classification__in=enabled_types)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['min_period'] = self.min_period
        context['max_period'] = self.max_period
        context['type_pulsator'] = self.type_pulsator
        context['type_eaeb'] = self.type_eaeb
        context['type_ew'] = self.type_ew
        context['type_rotator'] = self.type_rotator
        context['type_unknown'] = self.type_unknown
        return context


class IndexListView(StarListView):
    template_name = 'index.html'


class DownloadView(TemplateView):
    template_name = 'starcatalogue/download.html'