from django.conf import settings
from django.db.models import Q
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

from starcatalogue.models import Star, FoldedLightcurve, DataExport


class StarListView(ListView):
    paginate_by = 20

    def get_queryset(self, params=None):
        if params is None:
            params = self.request.GET

        qs = FoldedLightcurve.objects.all()

        self.min_period = params.get('min_period', None)
        if self.min_period:
            qs = qs.filter(period_length__gte=self.min_period)
        else:
            # To ensure it's None rather than ''
            self.min_period = None
        
        self.max_period = params.get('max_period', None)
        if self.max_period:
            qs = qs.filter(period_length__lte=self.max_period)
        else:
            # To ensure it's None rather than ''
            self.max_period = None

        self.type_pulsator = params.get('type_pulsator', 'off')
        self.type_rotator = params.get('type_rotator', 'off')
        self.type_ew = params.get('type_ew', 'off')
        self.type_eaeb = params.get('type_eaeb', 'off')
        self.type_unknown = params.get('type_unknown', 'off')

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

        self.search = params.get('search', None)
        if self.search:
            search_filter = Q(star__superwasp_id=self.search)

            try:
                search_filter = search_filter | Q(zooniversesubject__zooniverse_id=int(self.search))
            except ValueError:
                pass
            
            qs = qs.filter(search_filter)

        sort_fields = (
            'star__superwasp_id',
            'period_length',
            'classification',
        )

        self.sort = params.get('sort', None)
        if self.sort not in sort_fields:
            self.sort = 'star__superwasp_id'

        self.order = params.get('order', None)
        if self.order == 'desc':
            order_prefix = '-'
        else:
            order_prefix = ''
            self.order = 'asc' # To ditch any invalid values
        
        qs = qs.order_by('{}{}'.format(order_prefix, self.sort))

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
        context['search'] = self.search
        context['sort'] = self.sort
        context['order'] = self.order

        DataExport.objects.create(
            data_version=settings.DATA_VERSION,
            min_period = self.min_period,
            max_period = self.max_period,
            type_pulsator = DataExport.CHECKBOX_CHOICES_DICT[self.type_pulsator],
            type_eaeb = DataExport.CHECKBOX_CHOICES_DICT[self.type_eaeb],
            type_ew = DataExport.CHECKBOX_CHOICES_DICT[self.type_ew],
            type_rotator = DataExport.CHECKBOX_CHOICES_DICT[self.type_rotator],
            type_unknown = DataExport.CHECKBOX_CHOICES_DICT[self.type_unknown],
            search = self.search,
        )
        return context


class IndexListView(StarListView):
    template_name = 'starcatalogue/index.html'


class DownloadView(TemplateView):
    template_name = 'starcatalogue/download.html'