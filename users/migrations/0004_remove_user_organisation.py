# Generated by Django 4.1.7 on 2023-09-14 13:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_user_organisation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='organisation',
        ),
    ]