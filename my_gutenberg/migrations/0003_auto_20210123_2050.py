# Generated by Django 3.1.5 on 2021-01-23 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_gutenberg', '0002_auto_20210123_1951'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ebook',
            name='authors',
            field=models.TextField(default=None, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='ebook',
            name='bookshelves',
            field=models.TextField(default=None, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='ebook',
            name='copyright',
            field=models.TextField(default=None, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='ebook',
            name='languages',
            field=models.TextField(default=None, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='ebook',
            name='subjects',
            field=models.TextField(default=None, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='ebook',
            name='title',
            field=models.CharField(default=None, max_length=200, null=True),
        ),
    ]