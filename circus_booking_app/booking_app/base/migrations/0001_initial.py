# Generated by Django 5.2.3 on 2025-07-21 16:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('date', models.DateTimeField()),
                ('max_clients', models.PositiveIntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=7)),
                ('session_type', models.CharField(choices=[('Private', 'Private'), ('Group', 'Group'), ('Workshop', 'Workshop'), ('Performance', 'Performance')], max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('can_self_book', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('booked', 'Booked'), ('invoice_generated', 'Invoice Generated'), ('invoice_sent', 'Invoice Sent'), ('invoice_paid', 'Invoice Paid'), ('special', 'Special')], default='booked', max_length=20)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.client')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='base.session')),
            ],
            options={
                'unique_together': {('session', 'client')},
            },
        ),
        migrations.CreateModel(
            name='TrainerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('business_name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='session',
            name='trainer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.trainerprofile'),
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('sent', models.BooleanField(default=False)),
                ('paid', models.BooleanField(default=False)),
                ('special', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('bookings', models.ManyToManyField(to='base.booking')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.client')),
                ('trainer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.trainerprofile')),
            ],
        ),
        migrations.AddField(
            model_name='client',
            name='trainer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.trainerprofile'),
        ),
    ]
