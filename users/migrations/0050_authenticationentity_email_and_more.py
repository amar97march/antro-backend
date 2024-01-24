# Generated by Django 4.1.7 on 2024-01-24 05:33

from django.db import migrations, models
import phonenumber_field.modelfields
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0049_handgesture'),
    ]

    operations = [
        migrations.AddField(
            model_name='authenticationentity',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='authenticationentity',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None),
        ),
        migrations.AddField(
            model_name='authenticationentity',
            name='user_id_string',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='tempuserstatus',
            name='user_id',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_id',
            field=models.CharField(default=users.models.generate_user_id, editable=False, max_length=15, unique=True),
        ),
    ]