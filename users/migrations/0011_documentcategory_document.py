# Generated by Django 4.1.7 on 2023-11-04 06:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_user_verified_by_antro_user_verified_by_organisation_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('verified_by_antro', models.BooleanField(default=False)),
                ('verified_by_user', models.BooleanField(default=False)),
                ('verified_by_organisation', models.BooleanField(default=False)),
                ('file', models.FileField(upload_to='documents/')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.documentcategory')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]