import random
from faker import Faker
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.trade.models import UltraDCASystem, Currency, Ticker, UltraDCAOrder, UltraDCAEngine, UltraDCAExchangeOrder

fake = Faker()
User = get_user_model()


class Command(BaseCommand):
    help = 'Generates fake UltraDCASystem data for testing'

    def handle(self, *args, **kwargs):
        # Ensure there are some users and currencies available
        if not User.objects.exists():
            self.stdout.write("No users found. Please create at least one user.")
            return

        if not Currency.objects.exists():
            for _ in range(3):
                ticker_from = Ticker.objects.create(name=fake.currency_code())
                ticker_to = Ticker.objects.create(name=fake.currency_code())
                Currency.objects.create(from_ticker=ticker_from, to_ticker=ticker_to,
                                        highest_price=fake.random_number(digits=5))

        creator = User.objects.first()
        currency = Currency.objects.first()

        for _ in range(10):  # Create 10 fake UltraDCASystem entries
            ultra_dca = UltraDCASystem.objects.create(
                market_type=random.choice([0, 1]),
                market_strategy=random.choice([0, 1]),
                creator=creator,
                system_name=fake.unique.word().capitalize() + "_System",
                currency=currency,
                leverage=random.randint(1, 100),
                system_fund_rate=fake.pyfloat(left_digits=3, right_digits=2, positive=True, min_value=0.1, max_value=10.0),
                system_balance=fake.pyfloat(left_digits=5, right_digits=2, positive=True, min_value=100.0, max_value=10000.0),
                status=random.choice([0, 1, 2]),
                buy_is_enabled=fake.boolean(),
                sell_is_enabled=fake.boolean(),
                start_time=timezone.make_aware(fake.date_time_this_year()),  # Make datetime timezone-aware
                err_msg=fake.sentence(),
                is_in_market_place=fake.boolean(),
                stop_loss_is_enabled=fake.boolean(),
                profit_amount=fake.pyfloat(left_digits=4, right_digits=2, min_value=0, max_value=500.0),
                profit_percentages=fake.pyfloat(left_digits=2, right_digits=2, min_value=0, max_value=100.0),
                engine_number=fake.random_int(min=1, max=10),
                order_number=fake.random_int(min=1, max=100),
                heavy_shedding_is_enabled=fake.boolean()
            )
            self.stdout.write(self.style.SUCCESS(f'Created UltraDCASystem: {ultra_dca.system_name}'))

            # Create related UltraDCAEngine and UltraDCAOrder instances for each UltraDCASystem
            for engine_count in range(ultra_dca.engine_number):
                engine = UltraDCAEngine.objects.create(
                    system=ultra_dca,
                    engine_name=f"{ultra_dca.system_name}_Engine_{engine_count + 1}",
                    order_number=fake.random_int(min=1, max=10),
                    next_engine_start_order=fake.random_int(min=1, max=10),
                    next_engine_start_condition=fake.pyfloat(left_digits=1, right_digits=2, positive=True, max_value=10.0),
                    fall_order_engine_condition=fake.pyfloat(left_digits=1, right_digits=2, positive=True, max_value=10.0),
                    fall_order_market_condition=fake.pyfloat(left_digits=1, right_digits=2, positive=True, max_value=10.0)
                )

                for order_count in range(engine.order_number):
                    ultra_order = UltraDCAOrder.objects.create(
                        engine=engine,
                        order_fund_rate=fake.pyfloat(left_digits=2, right_digits=2, positive=True, min_value=0.01, max_value=5.0),
                        order_take_profit=fake.pyfloat(left_digits=2, right_digits=2, min_value=0, max_value=20.0),
                        order_name=f"{engine.engine_name}_Order_{order_count + 1}",
                        next_order_start_condition=fake.pyfloat(left_digits=1, right_digits=2, positive=True, max_value=10.0),
                        next_order_start_time=fake.random_int(min=1, max=60),
                        jumped_order=fake.boolean()
                    )
                    self.stdout.write(self.style.SUCCESS(
                        f'Created UltraDCAOrder for {engine.engine_name}: Order {order_count + 1}'
                    ))

                    # Create UltraDCAExchangeOrder instances for each UltraDCAOrder
                    for _ in range(random.randint(1, 5)):  # 1 to 5 exchange orders per DCA order
                        exchange_order = UltraDCAExchangeOrder.objects.create(
                            engine=engine,
                            order=ultra_order,
                            iteration=fake.uuid4(),
                            type=random.choice([0, 1, 2]),
                            orderId=fake.uuid4(),
                            base_volume=fake.pydecimal(left_digits=3, right_digits=8, positive=True),
                            quote_volume=fake.pydecimal(left_digits=3, right_digits=8, positive=True),
                            line_price=fake.pydecimal(left_digits=3, right_digits=8, positive=True),
                            avg_price=fake.pydecimal(left_digits=3, right_digits=8, positive=True),
                            order_type=random.choice([0, 1]),  # OrderSide choices
                            place_type=random.choice([0, 1]),  # OrderPlaceType choices
                            order_details={
                                'description': fake.sentence(),
                                'timestamp': str(fake.date_time_this_year())
                            }
                        )
                        self.stdout.write(self.style.SUCCESS(
                            f'Created UltraDCAExchangeOrder for {ultra_order.order_name}: Exchange Order {exchange_order.orderId}'
                        ))
