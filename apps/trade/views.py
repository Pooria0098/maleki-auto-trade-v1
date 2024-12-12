from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from loguru import logger
from apps.trade.forms import UltraDCASmartSystemForm, UltraDCAAdvancedSystemForm, UltraDCAEngineForm, UltraDCAOrderForm
from apps.trade.models import UltraDCASystem, UltraGridSystem, UltraDCAEngine, UltraDCAOrder, UltraDCAExchangeOrder, \
    UltraGridPart, UltraGridOrder, UltraGridExchangeOrder, MarketType
from django.contrib import messages
from apps.trade.utils import get_user_robots_status, get_user_apis
from rest_framework.reverse import reverse_lazy
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from apps.users.models import ApiStatus
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect, Http404, JsonResponse


@login_required
@csrf_exempt
def get_balance(request, api):
    if request.method == 'GET':
        try:
            # bingx = BingX(request.user)
            # spot_balance = bingx.get_balance(type='spot')
            # swap_balance = bingx.get_balance(type='swap')
            return JsonResponse({
                'spot_balance': 100,
                'swap_balance': 100,
                'message': 'Balance Updated Successfully'
            })
        except:
            return JsonResponse({
                'spot_balance': 0,
                'swap_balance': 0,
                'message': 'Error Updating Balance'
            })


######################################### UltraDCA #########################################


class UltraDCASmartCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'trade/bots/dca/ultra_dca_smart_create.html'
    model = UltraDCASystem
    form_class = UltraDCASmartSystemForm
    success_message = 'Successfully Created'

    def get_success_url(self):
        return reverse_lazy('trades:ultra_dca_list')

    def form_invalid(self, form):
        messages.warning(self.request, form.errors)
        return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super(UltraDCASmartCreateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(UltraDCASmartCreateView, self).get_context_data(**kwargs)
        context.update({
            'parent': 'UltraDCA',
            'parent_url': 'trades:ultra_dca_list',
            'segment': 'Create',
        })
        return context


class UltraDCAAdvancedCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'trade/bots/dca/ultra_dca_advance_create.html'
    model = UltraDCASystem
    form_class = UltraDCAAdvancedSystemForm
    success_message = 'Successfully Created'

    def get_success_url(self):
        return reverse_lazy('trades:ultra_dca_list')

    def form_invalid(self, form):
        messages.warning(self.request, form.errors)
        return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super(UltraDCAAdvancedCreateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def find_engine_order_numbers(self):
        from collections import defaultdict
        # Initialize sets to store unique engine and order numbers
        engine_numbers = set()
        order_numbers_per_engine = defaultdict(set)

        # Loop through the keys to identify engines and orders
        for key in self.request.POST.keys():
            if key.startswith("engine-"):
                # Extract the engine number, e.g., "engine-1-engine_name" -> 1
                engine_number = key.split("-")[1]
                engine_numbers.add(engine_number)

            elif key.startswith("order-"):
                # Extract both order and engine numbers, e.g., "order-1-engine-1-order_name" -> (1, 1)
                order_number = key.split("-")[1]
                engine_number = key.split("-")[3]

                # Add the order number to the specific engine's set of orders
                order_numbers_per_engine[engine_number].add(order_number)

        return engine_numbers, order_numbers_per_engine

    def form_valid(self, form):
        try:
            with transaction.atomic():
                forms = []

                # Validate system form
                if form.is_valid():
                    system_instance = form.save(commit=False)
                    system_instance.creator = self.request.user

                    if form.cleaned_data.get('fall_order_engine_condition') is not None or form.cleaned_data.get(
                            'fall_order_market_condition') is not None:
                        system_instance.heavy_shedding_is_enabled = True

                    if 'spot' in form.cleaned_data.get('api').__str__().lower():
                        system_instance.market_type = MarketType.Spot
                    else:
                        system_instance.market_type = MarketType.Futures

                    if form.cleaned_data.get('stop_loss_price') is not None:
                        system_instance.stop_loss_is_enabled = True

                    if form.cleaned_data.get('low_price_bound') is not None or form.cleaned_data.get(
                            'high_price_bound') is not None:
                        system_instance.is_limited_order = True

                    action = self.request.GET.get('action')
                    if action == 'submit':
                        system_instance.start_time = timezone.now()

                    system_instance.save()

                    engine_numbers, order_numbers_per_engine = self.find_engine_order_numbers()
                    sorted_engine_numbers = sorted(engine_numbers)
                    order_numbers = 0
                    for i in sorted_engine_numbers:
                        engine_form = UltraDCAEngineForm(self.request.POST, prefix=f'engine-{i}')
                        forms.append({
                            'engine_form': engine_form,
                            'order_forms': []
                        })

                        # Validate engine form
                        if not engine_form.is_valid():
                            return self.form_invalid(form)

                        sorted_order_numbers = sorted(order_numbers_per_engine.get(i))
                        order_numbers += len(sorted_order_numbers)
                        for j in sorted_order_numbers:
                            order_form = UltraDCAOrderForm(self.request.POST, prefix=f'order-{j}-engine-{i}')
                            forms[-1]['order_forms'].append(order_form)  # Append to the last item in forms

                            # Validate order form
                            if not order_form.is_valid():
                                return self.form_invalid(form)

                    for _form in forms:
                        engine_instance = _form['engine_form'].save(commit=False)
                        engine_instance.system = system_instance
                        engine_instance.fall_order_engine_condition = system_instance.fall_order_engine_condition
                        engine_instance.fall_order_market_condition = system_instance.fall_order_market_condition
                        engine_instance.order_number = len(sorted_order_numbers)
                        engine_instance.save()

                        for order_form in _form['order_forms']:
                            order_instance = order_form.save(commit=False)
                            order_instance.engine = engine_instance
                            order_instance.save()

                    system_instance.engine_number = len(engine_numbers)
                    system_instance.order_number = order_numbers
                    system_instance.save()
                    return super().form_valid(form)
                else:
                    return self.form_invalid(form)
        except Exception as _e:
            logger.warning(f'UltraDCAAdvancedCreateView Error: {_e}')
            transaction.rollback()
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(UltraDCAAdvancedCreateView, self).get_context_data(**kwargs)
        context.update({
            'parent': 'UltraDCA',
            'parent_url': 'trades:ultra_dca_list',
            'segment': 'Create',
        })
        context.update({
            'spot_balance': 0,
            'swap_balance': 0,
        })
        # user = self.request.user
        # apis = user.api_set.filter(status=ApiStatus.Active)
        # for api in apis:
        #     if api.market_type == MarketType.Futures:
        #         context.update({
        #             f'{api.exchange.exchange_name.lower()}_future_balance': 0,
        #         })
        #     else:
        #         context.update({
        #             f'{api.exchange.exchange_name.lower()}_spot_balance': 0,
        #         })
        return context


class UltraDCAListView(LoginRequiredMixin, ListView):
    template_name = 'trade/bots/dca/ultra_dca_list.html'
    model = UltraDCASystem
    fields = '__all__'

    def get_queryset(self):
        queryset = super().get_queryset()
        api = self.kwargs.get('api')
        if api:
            queryset = queryset.filter(api=api)
        return queryset

    def get_context_data(self, **kwargs):
        bots_status = get_user_robots_status(self, 'DCA')
        apis = get_user_apis(self)
        context = super(UltraDCAListView, self).get_context_data(**kwargs)
        context.update({
            'parent': 'UltraDCA',
            'segment': 'List',
            'bot': bots_status,
            'apis': apis
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

    def get_queryset(self):
        queryset = super().get_queryset()
        api = self.kwargs.get('api')
        if api:
            queryset = queryset.filter(api=api)
        return queryset

    def get_context_data(self, **kwargs):
        bots_status = get_user_robots_status(self, 'Grid')
        apis = get_user_apis(self)
        context = super(UltraGridListView, self).get_context_data(**kwargs)
        context.update({
            'parent': 'UltraGrid',
            'segment': 'List',
            'bot': bots_status,
            'apis': apis
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
