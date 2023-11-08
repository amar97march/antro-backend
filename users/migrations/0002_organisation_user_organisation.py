# Generated by Django 4.1.7 on 2023-09-14 13:32

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Company Name')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='company_logos/', verbose_name='Company Logo')),
                ('website', models.URLField(blank=True, max_length=255, verbose_name='Website')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('founded_year', models.PositiveIntegerField(blank=True, null=True, verbose_name='Founded Year')),
                ('headquarters', models.CharField(blank=True, max_length=255, verbose_name='Headquarters')),
                ('industry', models.CharField(blank=True, max_length=255, verbose_name='Industry')),
                ('employee_count', models.PositiveIntegerField(blank=True, null=True, verbose_name='Employee Count')),
                ('contact_email', models.EmailField(blank=True, max_length=255, verbose_name='Contact Email')),
                ('phone_number', models.CharField(blank=True, max_length=20, verbose_name='Phone Number')),
                ('social_media_links', models.JSONField(blank=True, verbose_name='Social Media Links')),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='organisation',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='users.organisation'),
            preserve_default=False,
        ),
    ]
