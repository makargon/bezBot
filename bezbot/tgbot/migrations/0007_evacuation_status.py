# Generated by Django 4.2.1 on 2023-05-07 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0006_evacuation_before_evacuation_missing_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='evacuation',
            name='status',
            field=models.CharField(choices=[('1', 'эвакуированны'), ('2', 'забарикодированны'), ('0', 'нет данных')], default=0, max_length=2),
        ),
    ]
