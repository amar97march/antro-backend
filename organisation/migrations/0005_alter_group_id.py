# Generated by Django 4.1.7 on 2023-09-10 07:27

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('organisation', '0004_remove_group_uuid_group_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True),
        ),
    ]
