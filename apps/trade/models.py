from django.db import models


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
