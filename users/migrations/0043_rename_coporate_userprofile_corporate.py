# Generated by Django 4.1.7 on 2023-12-18 12:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0042_userprofile_certifications'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='coporate',
            new_name='corporate',
        ),
    ]
