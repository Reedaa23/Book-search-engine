# Generated by Django 3.1.5 on 2021-01-27 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_gutenberg', '0006_auto_20210127_1155'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebook',
            name='rank',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
