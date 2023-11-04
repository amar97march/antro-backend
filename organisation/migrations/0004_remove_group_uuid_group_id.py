# Generated by Django 4.1.7 on 2023-09-10 07:21

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('organisation', '0003_remove_group_id_alter_group_uuid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='uuid',
        ),
        migrations.AddField(
            model_name='group',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True),
        ),
    ]