# Generated by Django 4.1.7 on 2023-03-06 04:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_date_of_birth_user_is_admin_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.CharField(blank=True, default='', max_length=200)),
                ('phone', models.IntegerField(blank=True, default=0)),
                ('image', models.ImageField(blank=True, upload_to='profile_image')),
                ('gender', models.CharField(blank=True, default='', max_length=20)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='userprofile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
