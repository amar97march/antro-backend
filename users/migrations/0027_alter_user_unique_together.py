# Generated by Django 4.1.7 on 2023-11-14 05:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0026_user_user_id_alter_user_email_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='user',
            unique_together=set(),
        ),
    ]