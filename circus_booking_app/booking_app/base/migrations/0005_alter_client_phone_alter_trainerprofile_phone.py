# Generated by Django 5.2.3 on 2025-07-24 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_client_address_client_email_client_name_client_phone_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='phone',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='trainerprofile',
            name='phone',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
