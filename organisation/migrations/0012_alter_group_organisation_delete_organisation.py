# Generated by Django 4.1.7 on 2023-09-14 13:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_organisation_user_organisation'),
        ('organisation', '0011_group_messages_group_participants'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='organisation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.organisation'),
        ),
        migrations.DeleteModel(
            name='Organisation',
        ),
    ]
