# Generated by Django 4.1.7 on 2023-09-25 07:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organisation', '0015_remove_location_members_branch'),
    ]

    operations = [
        migrations.AlterField(
            model_name='branch',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organisation.location'),
        ),
        migrations.AlterField(
            model_name='group',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organisation.group'),
        ),
        migrations.AlterField(
            model_name='location',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organisation.location'),
        ),
    ]
