# Generated by Django 4.1.7 on 2023-11-14 10:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0028_alter_user_phone_number_alter_userprofile_phone'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='user_id',
            new_name='username',
        ),
    ]
