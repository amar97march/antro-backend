# Generated by Django 4.1.7 on 2023-11-21 17:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0031_alter_user_email_accountmergerequest'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='phone',
            new_name='phone_number',
        ),
    ]
