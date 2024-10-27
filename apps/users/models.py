import json
from django_quill.fields import QuillField

from django.contrib.auth.hashers import make_password
from django.db import models
from django.contrib.auth.models import AbstractUser


class ApiModType(models.IntegerChoices):
    Hedge = 0
    Oneway = 1


class MarketType(models.IntegerChoices):
    Futures = 0,
    Spot = 1


class ApiStatus(models.IntegerChoices):
    Active = 0,
    Deactive = 1,


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
    market_type = models.IntegerField(choices=MarketType.choices, default=MarketType.Futures)
    api_name = models.CharField(max_length=128)
    api_key = models.CharField(max_length=512)
    secret_key = models.CharField(max_length=512)
    secret_key_hashed = models.CharField(max_length=512)
    api_mode = models.IntegerField(choices=ApiModType.choices, default=ApiModType.Hedge)
    expire_date = models.DateTimeField(blank=True, null=True)
    balance = models.FloatField(default=0)
    status = models.IntegerField(choices=ApiStatus.choices, default=ApiStatus.Deactive)

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


#############################################################################################################
# Create your models here.

ROLE_CHOICES = (
    ('admin', 'Admin'),
    ('user', 'User'),
)


def avatar_with_id(instance, filename):
    return "{}/avatar/{}".format(f"{instance.user.id}", filename)


def convert_to_quill():
    converted_data = {
        "delta": "",
        "html": "Write something #cool about you.",
    }
    return json.dumps(converted_data)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    full_name = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    zip_code = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    avatar = models.ImageField(upload_to=avatar_with_id, null=True, blank=True)
    dark_mode = models.BooleanField(default=False)
    bio = QuillField(default=convert_to_quill())

    def __str__(self):
        return self.user.username
