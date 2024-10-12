from django.contrib.auth.hashers import make_password
from django.db import models
from django.contrib.auth.models import AbstractUser


class ApiModType(models.IntegerChoices):
  Hedge = 0
  OneWay = 1


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


class Exchange(DataModel):
  exchange_name = models.CharField(max_length=128, unique=True)

  def __str__(self):
    return f"{self.exchange_name.upper()}"


class API(DataModel):
  user = models.ForeignKey('User', on_delete=models.CASCADE)
  exchange = models.OneToOneField(Exchange, on_delete=models.CASCADE)
  api_name = models.CharField(max_length=128)
  api_key = models.CharField(max_length=512)
  secret_key = models.CharField(max_length=512)
  secret_key_hashed = models.CharField(max_length=512)
  api_mode = models.IntegerField(choices=ApiModType.choices, default=ApiModType.Hedge)

  class Meta:
    unique_together = ('api_name', 'api_key', 'secret_key')

  def save(self, *args, **kwargs):
    if self.secret_key_hashed is not None:
      self.secret_key = self.secret_key_hashed
      self.secret_key_hashed = make_password(self.secret_key_hashed)
    super().save(*args, **kwargs)

  def __str__(self):
    return f"{self.exchange.exchange_name.upper()} - {self.api_name.upper()}"


class User(AbstractUser):
  currencies = models.ManyToManyField('trade.Currency', blank=True)
  otp = models.CharField(max_length=128, null=True, blank=True, default=None)
  email_verified = models.BooleanField(default=False)
  email = models.EmailField(unique=True)
