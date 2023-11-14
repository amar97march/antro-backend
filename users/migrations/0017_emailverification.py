# Generated by Django 4.1.7 on 2023-11-07 04:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_user_onboarding_complete_onboardinglink'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailVerification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('verification_time', models.DateTimeField(blank=True, null=True)),
                ('otp', models.IntegerField(blank=True, null=True)),
                ('verified', models.BooleanField(default=False)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='useremailverification', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]