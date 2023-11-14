# Generated by Django 4.1.7 on 2023-11-14 05:21

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0025_alter_user_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_id',
            field=models.CharField(default=users.models.generate_user_id, editable=False, max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='user',
            unique_together={('email', 'email_verified'), ('phone_number', 'phone_verified')},
        ),
    ]
