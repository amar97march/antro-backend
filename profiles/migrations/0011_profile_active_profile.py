# Generated by Django 4.1.7 on 2023-12-21 05:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0010_alter_profile_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='active_profile',
            field=models.BooleanField(default=False),
        ),
    ]
