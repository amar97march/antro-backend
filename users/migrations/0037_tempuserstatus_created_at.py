# Generated by Django 4.1.7 on 2023-12-11 16:19

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0036_alter_tempuser_email_tempuserstatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='tempuserstatus',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
