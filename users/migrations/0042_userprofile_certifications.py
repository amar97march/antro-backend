# Generated by Django 4.1.7 on 2023-12-18 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0041_rename_certifications_tempuserprofile_certifications_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='certifications',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
