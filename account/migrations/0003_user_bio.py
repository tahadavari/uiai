# Generated by Django 4.0.2 on 2022-02-26 22:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_user_groups_user_user_permissions'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='bio',
            field=models.CharField(blank=True, max_length=300, null=True, verbose_name='bio'),
        ),
    ]
