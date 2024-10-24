from django.db import models
from home.models import User


####################### Unions #######################
class OrderSide(models.IntegerChoices):
    BUY = 0,
    SELL = 1


class MarketStrategy(models.IntegerChoices):
    ISOLATED = 0,
    CROSS = 1


class OrderPlaceType(models.IntegerChoices):
    LIMIT = 0,
    MARKET = 1


class OrderStatus(models.IntegerChoices):
    FAILED = 0,
    PENDING = 1,
    PROCESSING = 2,
    SUCCESS = 3


class OrderTriggerType(models.IntegerChoices):
    ORDINARY = 0,
    TP = 1,
    SL = 2


class MarketType(models.IntegerChoices):
    FUTURES = 0,
    SPOT = 1


class SystemStatus(models.IntegerChoices):
    Running = 0, """در حال اجرا"""
    Busy = 1, """مشغول"""
    Stop = 2, """متوقف"""


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
    market_type = models.IntegerField(choices=MarketType.choices, default=MarketType.FUTURES)
    market_strategy = models.IntegerField(choices=MarketStrategy.choices, default=MarketStrategy.ISOLATED)
    creator = models.ForeignKey(User, on_delete=models.PROTECT)
    system_name = models.CharField(max_length=256, unique=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    system_fund_rate = models.FloatField(default=0)
    system_balance = models.FloatField(default=0, null=True, blank=True)
    status = models.IntegerField(choices=SystemStatus.choices, default=SystemStatus.Running)
    buy_is_enabled = models.BooleanField(default=True)
    sell_is_enabled = models.BooleanField(default=True)
    err_msg = models.TextField()

    class Meta:
        abstract = True


class Order(DataModel):
    order_fund_rate = models.FloatField()  # todo: total of orders_fund_rate must not be more than engine_fund_rate
    order_status = models.IntegerField(choices=OrderStatus.choices, default=OrderStatus.PENDING)
    tp_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    sl_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    err_msg = models.TextField()

    class Meta:
        abstract = True


class ExchangeOrder(DataModel):
    iteration = models.CharField(max_length=128)
    type = models.IntegerField(choices=OrderTriggerType.choices, default=OrderTriggerType.ORDINARY)
    orderId = models.CharField(max_length=128)
    base_volume = models.DecimalField(max_digits=20, decimal_places=8, blank=True, null=True)
    quote_volume = models.DecimalField(max_digits=20, decimal_places=8, blank=True, null=True)
    line_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    order_type = models.IntegerField(choices=OrderSide.choices, default=OrderSide.BUY)
    place_type = models.IntegerField(choices=OrderPlaceType.choices, default=OrderPlaceType.MARKET)
    order_details = models.JSONField(default=dict)

    class Meta:
        abstract = True


####################### UltraDCA #######################
class UltraDCASystem(System):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)  # todo: this must fill when hit stop button
    engine_number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.system_name}"


class UltraDCAEngine(DataModel):
    system = models.ForeignKey(UltraDCASystem, on_delete=models.CASCADE)
    engine_name = models.CharField(max_length=256, default='')
    order_number = models.PositiveIntegerField(default=0)
    next_engine_start_order = models.PositiveIntegerField(
        default=None, help_text='after_how_many_orders_of_current_engine_next_engine_start', null=True)
    next_engine_start_condition = models.FloatField(
        default=None, help_text='after_how_much_falls_of_current_engine_next_engine_start', null=True)
    fall_order_engine_condition = models.FloatField(
        default=None, help_text='after_how_much_falls_of_latest_order_in_current_engine_fall_order_starts',
        null=True)
    fall_order_market_condition = models.FloatField(
        default=None, help_text='after_how_much_falls_of_price_from_marketLine_fall_order_starts',
        null=True)

    def __str__(self):
        return f"sys:{self.system.system_name}/ en:{self.engine_name}"


class UltraDCAOrder(Order):
    engine = models.ForeignKey(UltraDCAEngine, on_delete=models.CASCADE)
    order_take_profit = models.FloatField(default=0)
    order_name = models.CharField(max_length=256, default='')
    next_order_start_condition = models.FloatField(
        default=None, help_text="after_how_much_falls_of_current_order_next_order_start", null=True)
    next_order_start_time = models.IntegerField(
        default=None, help_text="after_how_many_time_next_order_start", null=True)
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
    avg_price = models.DecimalField(max_digits=20, decimal_places=8, blank=True, null=True,
                                    help_text='my_line_price_after_average')  # قیمت سرخط خرید بعد از میانگین گیری

    def __str__(self):
        return f'sys:{self.order.engine.system.system_name}/ en:{self.order.engine.engine_name}/ or:{self.order.order_name}/ ex_or:{self.order_id}'


####################### UltraGrid #######################
class UltraGridSystem(System):
    order_number = models.PositiveIntegerField(default=0)
    part_number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.system_name}"


class UltraGridPart(DataModel):
    system = models.ForeignKey(UltraGridSystem, on_delete=models.CASCADE)
    part_name = models.CharField(max_length=256, default='')
    start_order_number = models.PositiveIntegerField(default=0)
    end_order_number = models.PositiveIntegerField(default=0)
    order_count = models.PositiveIntegerField(default=0)
    part_fund_rate = models.FloatField(default=0)
    next_order_condition = models.FloatField(default=0,
                                             help_text="after_how_much_falls_of_current_order_next_order_start")
    take_profit_condition = models.FloatField(default=0,
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
