# Generated by Django 4.2.9 on 2024-10-06 19:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_api_api_mode_api_secret_key_hashed_alter_user_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='api',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
