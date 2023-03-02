# Generated by Django 4.1.7 on 2023-03-02 06:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='parent_user',
            field=models.ForeignKey(blank=True, default='', help_text='Parent User for this model', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to=settings.AUTH_USER_MODEL, verbose_name='Parent User'),
        ),
    ]
