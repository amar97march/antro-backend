# Generated by Django 4.1.7 on 2023-09-10 09:31

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('organisation', '0006_alter_group_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisation',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
