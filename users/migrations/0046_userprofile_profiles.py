# Generated by Django 4.1.7 on 2023-12-21 05:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0011_profile_active_profile'),
        ('users', '0045_alter_tempuserstatus_upload_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='profiles',
            field=models.ManyToManyField(related_name='user_profiles', to='profiles.profile'),
        ),
    ]
