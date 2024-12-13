from django import forms
from apps.trade.models import API, UltraDCASystem, UltraDCAEngine, UltraDCAOrder, UltraGridPart, UltraGridSystem

####################### UltraDCA #######################
from apps.users.models import ApiStatus


class UltraDCAAdvancedSystemForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        try:
            user = kwargs.pop('user')
            self.user = user
        except:
            self.user = None
        super().__init__(*args, **kwargs)

        self.fields['currency'].queryset = self.user.currencies.all()
        self.fields['api'].queryset = self.user.api_set.filter(status=ApiStatus.Active)

        # self.fields['engine_number'].widget.attrs.update({'class': "form-control"})
        # self.fields['order_number'].widget.attrs.update({'class': "form-control"})
        self.fields['heavy_shedding_is_enabled'].widget.attrs.update({'class': "form-control"})
        self.fields['fall_order_engine_condition'].widget.attrs.update({'class': "form-control"})
        self.fields['fall_order_market_condition'].widget.attrs.update({'class': "form-control"})
        self.fields['market_strategy'].widget.attrs.update({'class': "form-control"})
        self.fields['system_name'].widget.attrs.update({'class': "form-control"})
        self.fields['currency'].widget.attrs.update({'class': "form-control"})
        self.fields['api'].widget.attrs.update({'class': "form-control"})
        self.fields['leverage'].widget.attrs.update({'class': "form-control"})
        self.fields['system_fund_rate'].widget.attrs.update({'class': "form-control"})
        self.fields['stop_loss_is_enabled'].widget.attrs.update({'class': "form-control"})
        self.fields['stop_loss_price'].widget.attrs.update({'class': "form-control"})
        self.fields['is_limited_order'].widget.attrs.update({'class': "form-control"})
        self.fields['low_price_bound'].widget.attrs.update({'class': "form-control"})
        self.fields['high_price_bound'].widget.attrs.update({'class': "form-control"})

    class Meta:
        model = UltraDCASystem
        fields = [
            # 'engine_number',
            # 'order_number',
            'heavy_shedding_is_enabled',  #
            'fall_order_engine_condition',  #
            'fall_order_market_condition',  #
            'market_strategy',  #
            'system_name',
            'currency',
            'api',
            'leverage',  #
            'system_fund_rate',  #
            'stop_loss_is_enabled',  #
            'stop_loss_price',  #
            'is_limited_order',  #
            'low_price_bound',  #
            'high_price_bound',  #
        ]


class UltraDCAEngineForm(forms.ModelForm):
    class Meta:
        model = UltraDCAEngine
        fields = [
            'engine_name',
            # 'order_number',
            'next_engine_start_order',  # optional
            'next_engine_start_condition',  # optional
            # 'fall_order_engine_condition',
            # 'fall_order_market_condition',
        ]


class UltraDCAOrderForm(forms.ModelForm):
    class Meta:
        model = UltraDCAOrder
        fields = [
            'order_name',
            'order_take_profit',
            'order_fund_rate',
            'next_order_start_condition',  # optional
            'next_order_start_time',  # optional
        ]


class UltraDCASmartSystemForm(forms.ModelForm):
    class Meta:
        model = UltraDCASystem
        fields = '__all__'


####################### UltraGrid #######################
class UltraGridAdvancedSystemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        try:
            user = kwargs.pop('user')
            self.user = user
        except:
            self.user = None
        super().__init__(*args, **kwargs)

        self.fields['currency'].queryset = self.user.currencies.all()
        self.fields['api'].queryset = self.user.api_set.filter(status=ApiStatus.Active)

        self.fields['market_strategy'].widget.attrs.update({'class': "form-control"})
        self.fields['system_name'].widget.attrs.update({'class': "form-control"})
        self.fields['currency'].widget.attrs.update({'class': "form-control"})
        self.fields['api'].widget.attrs.update({'class': "form-control"})
        self.fields['leverage'].widget.attrs.update({'class': "form-control"})
        self.fields['system_fund_rate'].widget.attrs.update({'class': "form-control"})
        self.fields['stop_loss_is_enabled'].widget.attrs.update({'class': "form-control"})
        self.fields['stop_loss_price'].widget.attrs.update({'class': "form-control"})
        self.fields['is_limited_order'].widget.attrs.update({'class': "form-control"})
        self.fields['low_price_bound'].widget.attrs.update({'class': "form-control"})
        self.fields['high_price_bound'].widget.attrs.update({'class': "form-control"})

    class Meta:
        model = UltraGridSystem
        fields = [
            'system_name',
            'market_strategy',
            'currency',
            'api',
            'leverage',
            'system_fund_rate',
            'stop_loss_is_enabled',
            'stop_loss_price',
            'is_limited_order',
            'low_price_bound',
            'high_price_bound',
        ]


class UltraGridPartForm(forms.ModelForm):
    class Meta:
        model = UltraGridPart
        fields = [
            'part_name',
            'start_order_number',
            'end_order_number',
            'part_fund_rate',
            'next_order_condition',
            'take_profit_condition',
        ]


class UltraGridSmartSystemForm(forms.ModelForm):
    class Meta:
        model = UltraGridSystem
        fields = '__all__'
