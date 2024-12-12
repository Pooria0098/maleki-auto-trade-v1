from django.db import models
from django.contrib.auth import get_user_model

from apps.users.models import API

User = get_user_model()


####################### Unions #######################
class OrderSide(models.IntegerChoices):
    Buy = 0,
    Sell = 1


class MarketStrategy(models.IntegerChoices):
    Isolated = 0,
    Cross = 1


class OrderPlaceType(models.IntegerChoices):
    Limit = 0,
    Market = 1


class OrderStatus(models.IntegerChoices):
    Failed = 0,
    Pending = 1,
    Processing = 2,
    Success = 3


class OrderTriggerType(models.IntegerChoices):
    Ordinary = 0,
    Tp = 1,
    Sl = 2


class MarketType(models.IntegerChoices):
    Futures = 0,
    Spot = 1


class SystemStatus(models.IntegerChoices):
    Running = 0,
    Busy = 1,
    Stop = 2,


####################### Utility #######################
class DataModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")
    is_active = models.BooleanField(default=True, verbose_name="Is active")

    # def delete(self, using=None, keep_parents=False):
    #     self.is_active = False
    #     self.save()

    # def hard_delete(self):
    #     super(DataModel, self).delete()

    class Meta:
        abstract = True


class Ticker(DataModel):
    name = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return self.name


class Currency(DataModel):
    from_ticker = models.ForeignKey(Ticker, on_delete=models.PROTECT, related_name='ticker_from')
    to_ticker = models.ForeignKey(Ticker, on_delete=models.PROTECT, related_name='ticker_to')
    highest_price = models.FloatField(default=0)

    def __str__(self):
        return f"{self.from_ticker.name.upper()}/{self.to_ticker.name.upper()}"


class System(DataModel):
    market_type = models.IntegerField(choices=MarketType.choices, default=MarketType.Futures)
    market_strategy = models.IntegerField(choices=MarketStrategy.choices, default=MarketStrategy.Isolated,null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.PROTECT)
    api = models.ForeignKey(API, on_delete=models.PROTECT)
    system_name = models.CharField(max_length=256, unique=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    leverage = models.IntegerField(blank=True, null=True, default=None)
    system_fund_rate = models.FloatField(default=0)
    system_balance = models.FloatField(default=0)
    status = models.IntegerField(choices=SystemStatus.choices, default=SystemStatus.Running)
    buy_is_enabled = models.BooleanField(default=False)
    sell_is_enabled = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True, blank=True, default=None)
    """
     اگه این فیلد خالی باشه فقط ی سیستم می سازه ولی اجراش نمی کنه 
     هرموقع خواست اجراش کنه این فیلد زمان همون لحظه می گیره.پس تو هسته معاملاتی سیستم هایی که Running هستند و 
     is_active اونا True و start_time دارند مورد بررسی قرار می گیرند 
    """
    err_msg = models.TextField()
    is_in_market_place = models.BooleanField(default=False)
    stop_loss_is_enabled = models.BooleanField(default=False)
    stop_loss_price = models.FloatField(null=True, blank=True, default=None)
    profit_amount = models.FloatField(default=0)
    profit_percentages = models.FloatField(default=0)
    is_limited_order = models.BooleanField(default=False)
    low_price_bound = models.FloatField(null=True, blank=True, default=None)
    high_price_bound = models.FloatField(null=True, blank=True, default=None)

    class Meta:
        abstract = True


class Order(DataModel):
    order_fund_rate = models.FloatField(default=0)
    order_status = models.IntegerField(choices=OrderStatus.choices, default=OrderStatus.Pending)
    tp_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True, default=None)
    sl_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True, default=None)
    err_msg = models.TextField()

    class Meta:
        abstract = True


class ExchangeOrder(DataModel):
    iteration = models.CharField(max_length=128)
    type = models.IntegerField(choices=OrderTriggerType.choices, default=OrderTriggerType.Ordinary)
    orderId = models.CharField(max_length=128)
    base_volume = models.DecimalField(max_digits=20, decimal_places=8, blank=True, null=True, default=None)
    quote_volume = models.DecimalField(max_digits=20, decimal_places=8, blank=True, null=True, default=None)
    line_price = models.DecimalField(max_digits=20, decimal_places=8, blank=True, null=True, default=None)
    order_type = models.IntegerField(choices=OrderSide.choices, default=OrderSide.Buy)
    place_type = models.IntegerField(choices=OrderPlaceType.choices, default=OrderPlaceType.Market)
    order_details = models.JSONField(default=dict)

    class Meta:
        abstract = True


####################### UltraDCA #######################
class UltraDCASystem(System):
    engine_number = models.PositiveIntegerField(default=0)
    order_number = models.PositiveIntegerField(default=0)
    heavy_shedding_is_enabled = models.BooleanField(default=False)  # ریزش سنگین
    fall_order_engine_condition = models.FloatField(
        default=None, help_text='after_how_much_falls_of_latest_order_in_current_engine_fall_order_starts',
        null=True, blank=True)
    fall_order_market_condition = models.FloatField(
        default=None, help_text='after_how_much_falls_of_price_from_marketLine_fall_order_starts',
        null=True, blank=True)

    def __str__(self):
        return f"{self.system_name}"


class UltraDCAEngine(DataModel):
    system = models.ForeignKey(UltraDCASystem, on_delete=models.CASCADE)
    engine_name = models.CharField(max_length=256, default='')
    order_number = models.PositiveIntegerField(default=0)
    next_engine_start_order = models.PositiveIntegerField(
        default=None, blank=True, help_text='after_how_many_orders_of_current_engine_next_engine_start', null=True)
    next_engine_start_condition = models.FloatField(
        default=None, blank=True, help_text='after_how_much_falls_of_current_engine_next_engine_start', null=True)
    fall_order_engine_condition = models.FloatField(
        default=None, blank=True, help_text='after_how_much_falls_of_latest_order_in_current_engine_fall_order_starts',
        null=True)
    fall_order_market_condition = models.FloatField(
        default=None, blank=True, help_text='after_how_much_falls_of_price_from_marketLine_fall_order_starts',
        null=True)

    def __str__(self):
        return f"sys:{self.system.system_name}/ en:{self.engine_name}"


class UltraDCAOrder(Order):
    engine = models.ForeignKey(UltraDCAEngine, on_delete=models.CASCADE)
    order_take_profit = models.FloatField(default=0)
    order_name = models.CharField(max_length=256, default='')
    next_order_start_condition = models.FloatField(
        default=None, help_text="after_how_much_falls_of_current_order_next_order_start", null=True, blank=True)
    next_order_start_time = models.IntegerField(
        default=None, help_text="after_how_many_time_next_order_start", null=True, blank=True)
    jumped_order = models.BooleanField(default=False)

    def __str__(self):
        return f'sys:{self.engine.system.system_name}/ en:{self.engine.engine_name}/ or:{self.order_name}'

    def save(self, *args, **kwargs):
        if self.engine.next_engine_start_order and self.engine.ultradcaorder_set.count() == (
                self.engine.next_engine_start_order - 1):
            self.jumped_order = True
        super().save(*args, **kwargs)


class UltraDCAExchangeOrder(ExchangeOrder):
    engine = models.ForeignKey(UltraDCAEngine, on_delete=models.CASCADE)
    order = models.ForeignKey(UltraDCAOrder, on_delete=models.CASCADE)
    avg_price = models.DecimalField(max_digits=20, decimal_places=8, blank=True, default=None, null=True,
                                    help_text='my_line_price_after_average')  # قیمت سرخط خرید بعد از میانگین گیری

    def __str__(self):
        return f'sys:{self.order.engine.system.system_name}/ en:{self.order.engine.engine_name}/ or:{self.order.order_name}/ ex_or:{self.order_id}'


####################### UltraGrid #######################
class UltraGridSystem(System):
    part_number = models.PositiveIntegerField(default=0)
    order_number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.system_name}"


class UltraGridPart(DataModel):
    system = models.ForeignKey(UltraGridSystem, on_delete=models.CASCADE)
    part_name = models.CharField(max_length=256, default='')
    start_order_number = models.PositiveIntegerField(default=0)
    end_order_number = models.PositiveIntegerField(default=0)
    order_count = models.PositiveIntegerField(default=0)
    part_fund_rate = models.FloatField(default=0)
    next_order_condition = models.FloatField(null=True, blank=True, default=None,
                                             help_text="after_how_much_falls_of_current_order_next_order_start")
    take_profit_condition = models.FloatField(null=True, blank=True, default=None,
                                              help_text="after_how_much_jump_order_close")

    def __str__(self):
        return f"sys:{self.system.system_name}/ par:{self.part_name}"


class UltraGridOrder(Order):
    part = models.ForeignKey(UltraGridPart, on_delete=models.CASCADE)

    def __str__(self):
        return f'sys:{self.part.system.system_name}/ par:{self.part.part_name}/ or:{str(self.id)}'


class UltraGridExchangeOrder(ExchangeOrder):
    part = models.ForeignKey(UltraGridPart, on_delete=models.CASCADE)
    order = models.ForeignKey(UltraGridOrder, on_delete=models.CASCADE)

    def __str__(self):
        return f'sys:{self.part.system.system_name}/ par:{self.part.part_name}/ or:{str(self.order.id)}/ ex_or:{self.orderId}'
