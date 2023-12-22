# Generated by Django 4.1.7 on 2023-12-19 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0043_rename_coporate_userprofile_corporate'),
    ]

    operations = [
        migrations.AddField(
            model_name='tempuserstatus',
            name='failed_reason',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='tempuserstatus',
            name='user_id',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='tempuserstatus',
            name='upload_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('failed', 'Failed'), ('completed', 'Completed')], default='pending', max_length=10),
        ),
    ]