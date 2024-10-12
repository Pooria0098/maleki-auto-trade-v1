# Generated by Django 4.2.9 on 2024-10-04 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0001_initial'),
        ('home', '0002_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='currencies',
            field=models.ManyToManyField(blank=True, to='trade.currency'),
        ),
        migrations.AddField(
            model_name='user',
            name='email_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='otp',
            field=models.CharField(blank=True, default=None, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='email address'),
        ),
    ]