import random
from faker import Faker
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.trade.models import UltraGridSystem, Currency, Ticker, UltraGridPart, UltraGridOrder, UltraGridExchangeOrder

fake = Faker()
User = get_user_model()


class Command(BaseCommand):
  help = 'Generates fake UltraGridSystem data for testing'

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

    for _ in range(10):  # Create 10 fake UltraGridSystem entries
      ultra_grid = UltraGridSystem.objects.create(
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
        start_time=timezone.make_aware(fake.date_time_this_year()),
        err_msg=fake.sentence(),
        is_in_market_place=fake.boolean(),
        stop_loss_is_enabled=fake.boolean(),
        profit_amount=fake.pyfloat(left_digits=4, right_digits=2, min_value=0, max_value=500.0),
        profit_percentages=fake.pyfloat(left_digits=2, right_digits=2, min_value=0, max_value=100.0),
        part_number=fake.random_int(min=1, max=10),
        order_number=fake.random_int(min=1, max=100),
      )
      self.stdout.write(self.style.SUCCESS(f'Created UltraGridSystem: {ultra_grid.system_name}'))

      # Create related UltraGridPart instances for each UltraGridSystem
      for part_count in range(ultra_grid.part_number):
        part = UltraGridPart.objects.create(
          system=ultra_grid,
          part_name=f"{ultra_grid.system_name}_Part_{part_count + 1}",
          start_order_number=fake.random_int(min=1, max=10),
          end_order_number=fake.random_int(min=11, max=20),
          order_count=fake.random_int(min=1, max=10),
          part_fund_rate=fake.pyfloat(left_digits=3, right_digits=2, positive=True, min_value=0.1, max_value=5.0),
          next_order_condition=fake.pyfloat(left_digits=1, right_digits=2, positive=True, max_value=10.0),
          take_profit_condition=fake.pyfloat(left_digits=1, right_digits=2, positive=True, max_value=10.0)
        )
        self.stdout.write(
          self.style.SUCCESS(f'Created UltraGridPart for {ultra_grid.system_name}: Part {part.part_name}'))

        # Create UltraGridOrder instances for each UltraGridPart
        for order_count in range(part.order_count):
          ultra_order = UltraGridOrder.objects.create(
            part=part,
            order_fund_rate=fake.pyfloat(left_digits=2, right_digits=2, positive=True, min_value=0.01, max_value=5.0),
            order_status=random.choice([0, 1, 2, 3]),
            tp_price=fake.pydecimal(left_digits=4, right_digits=8, positive=True),
            sl_price=fake.pydecimal(left_digits=4, right_digits=8, positive=True),
            err_msg=fake.sentence()
          )
          self.stdout.write(self.style.SUCCESS(
            f'Created UltraGridOrder for {part.part_name}: Order {order_count + 1}'
          ))

          # Create UltraGridExchangeOrder instances for each UltraGridOrder
          for _ in range(random.randint(1, 5)):  # 1 to 5 exchange orders per Grid order
            exchange_order = UltraGridExchangeOrder.objects.create(
              part=part,
              order=ultra_order,
              iteration=fake.uuid4(),
              type=random.choice([0, 1, 2]),
              orderId=fake.uuid4(),
              base_volume=fake.pydecimal(left_digits=3, right_digits=8, positive=True),
              quote_volume=fake.pydecimal(left_digits=3, right_digits=8, positive=True),
              line_price=fake.pydecimal(left_digits=3, right_digits=8, positive=True),
              order_type=random.choice([0, 1]),  # OrderSide choices
              place_type=random.choice([0, 1]),  # OrderPlaceType choices
              order_details={
                'description': fake.sentence(),
                'timestamp': str(fake.date_time_this_year())
              }
            )
            self.stdout.write(self.style.SUCCESS(
              f'Created UltraGridExchangeOrder for {ultra_order.id}: Exchange Order {exchange_order.orderId}'
            ))
