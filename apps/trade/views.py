from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.trade.models import UltraDCASystem, UltraGridSystem, UltraDCAEngine, UltraDCAOrder, UltraDCAExchangeOrder, \
    UltraGridPart, UltraGridOrder, UltraGridExchangeOrder


######################################### UltraDCA #########################################
class UltraDCASmartCreateView(TemplateView):
    template_name = 'trade/bots/dca/ultra_dca_smart_create.html'


class UltraDCAAdvancedCreateView(TemplateView):
    template_name = 'trade/bots/dca/ultra_dca_advance_create.html'


class UltraDCAListView(LoginRequiredMixin, ListView):
    template_name = 'trade/bots/dca/ultra_dca_list.html'
    model = UltraDCASystem
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super(UltraDCAListView, self).get_context_data(**kwargs)
        context.update({
            'parent': 'UltraDCA',
            'segment': 'List',
        })
        return context


class UltraDCAEnginesView(LoginRequiredMixin, ListView):
    template_name = 'trade/bots/dca/ultra_dca_detail_engines.html'
    model = UltraDCAEngine
    fields = '__all__'

    def get_queryset(self):
        system_id = self.kwargs.get('system_id')
        system = get_object_or_404(UltraDCASystem, id=system_id)
        engines = system.ultradcaengine_set.all()
        return engines

    def get_context_data(self, **kwargs):
        context = super(UltraDCAEnginesView, self).get_context_data(**kwargs)
        context.update({
            'parent': 'UltraDCA',
            'parent_url': 'trades:ultra_dca_list',
            'segment': 'List',
        })
        return context


class UltraDCAOrdersView(LoginRequiredMixin, ListView):
    template_name = 'trade/bots/dca/ultra_dca_detail_orders.html'
    model = UltraDCAOrder
    fields = '__all__'

    def get_queryset(self):
        engine_id = self.kwargs.get('engine_id')
        engine = get_object_or_404(UltraDCAEngine, id=engine_id)
        orders = engine.ultradcaorder_set.all()
        return orders

    def get_context_data(self, **kwargs):
        context = super(UltraDCAOrdersView, self).get_context_data(**kwargs)
        context.update({
            'parent': 'UltraDCAEngine',
            'parent_url': 'trades:ultra_dca_engines',
            'parent_url_id': self.object_list.first().engine.system.id if self.object_list.first() else None,
            'segment': 'List',
        })
        return context


class UltraDCAExchangeOrdersView(LoginRequiredMixin, ListView):
    template_name = 'trade/bots/dca/ultra_dca_detail_exchange_orders.html'
    model = UltraDCAExchangeOrder
    fields = '__all__'

    def get_queryset(self):
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(UltraDCAOrder, id=order_id)
        exchangeorders = order.ultradcaexchangeorder_set.all()
        return exchangeorders

    def get_context_data(self, **kwargs):
        context = super(UltraDCAExchangeOrdersView, self).get_context_data(**kwargs)
        context.update({
            'parent': 'UltraDCAOrder',
            'segment': 'List',
        })
        if self.object_list.first():
            context.update({
                'parent_url': 'trades:ultra_dca_orders',
                'parent_url_id': self.object_list.first().order.engine.id,
            })
        return context


class UltraDCAUpdateView(TemplateView):
    template_name = 'trade/bots/dca/ultra_dca_detail_systems.html'


class UltraDCAToggleActivationView(TemplateView):
    pass


class UltraDCAToggleBuyView(TemplateView):
    pass


class UltraDCAToggleSellView(TemplateView):
    pass


class UltraDCADeactivateAllView(TemplateView):
    pass


######################################### UltraGrid #########################################
class UltraGridSmartCreateView(TemplateView):
    template_name = 'trade/bots/grid/ultra_grid_smart_create.html'


class UltraGridAdvancedCreateView(TemplateView):
    template_name = 'trade/bots/grid/ultra_grid_advance_create.html'


class UltraGridListView(LoginRequiredMixin, ListView):
    template_name = 'trade/bots/grid/ultra_grid_list.html'
    model = UltraGridSystem
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super(UltraGridListView, self).get_context_data(**kwargs)
        context.update({
            'parent': 'UltraGrid',
            'segment': 'List',
        })
        return context


class UltraGridPartsView(LoginRequiredMixin, ListView):
    template_name = 'trade/bots/grid/ultra_grid_detail_parts.html'
    model = UltraGridPart
    fields = '__all__'

    def get_queryset(self):
        system_id = self.kwargs.get('system_id')
        system = get_object_or_404(UltraGridSystem, id=system_id)
        parts = system.ultragridpart_set.all()
        return parts

    def get_context_data(self, **kwargs):
        context = super(UltraGridPartsView, self).get_context_data(**kwargs)
        context.update({
            'parent': 'UltraGrid',
            'parent_url': 'trades:ultra_grid_list',
            'segment': 'List',
        })
        return context


class UltraGridOrdersView(LoginRequiredMixin, ListView):
    template_name = 'trade/bots/grid/ultra_grid_detail_orders.html'
    model = UltraGridOrder
    fields = '__all__'

    def get_queryset(self):
        part_id = self.kwargs.get('part_id')
        parts = get_object_or_404(UltraGridPart, id=part_id)
        orders = parts.ultragridorder_set.all()
        return orders

    def get_context_data(self, **kwargs):
        context = super(UltraGridOrdersView, self).get_context_data(**kwargs)
        context.update({
            'parent': 'UltraGridPart',
            'parent_url': 'trades:ultra_grid_parts',
            'parent_url_id': self.object_list.first().part.system.id if self.object_list.first() else None,
            'segment': 'List',
        })
        return context


class UltraGridExchangeOrdersView(LoginRequiredMixin, ListView):
    template_name = 'trade/bots/grid/ultra_grid_detail_exchange_orders.html'
    model = UltraGridExchangeOrder
    fields = '__all__'

    def get_queryset(self):
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(UltraGridOrder, id=order_id)
        exchangeorders = order.ultragridexchangeorder_set.all()
        return exchangeorders

    def get_context_data(self, **kwargs):
        context = super(UltraGridExchangeOrdersView, self).get_context_data(**kwargs)
        context.update({
            'parent': 'UltraGridOrder',
            'segment': 'List',
        })
        if self.object_list.first():
            context.update({
                'parent_url': 'trades:ultra_grid_orders',
                'parent_url_id': self.object_list.first().order.part.id,
            })
        return context


class UltraGridUpdateView(TemplateView):
    template_name = 'trade/bots/grid/ultra_grid_detail_systems.html'


class UltraGridToggleActivationView(TemplateView):
    pass


class UltraGridToggleBuyView(TemplateView):
    pass


class UltraGridToggleSellView(TemplateView):
    pass


class UltraGridDeactivateAllView(TemplateView):
    pass
