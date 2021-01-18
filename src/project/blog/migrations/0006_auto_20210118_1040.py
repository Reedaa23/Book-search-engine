# Generated by Django 3.1.5 on 2021-01-18 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_auto_20210118_1036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='authors',
            field=models.TextField(default='EMPTY', max_length=500),
        ),
        migrations.AlterField(
            model_name='post',
            name='bookshelves',
            field=models.TextField(default='EMPTY', max_length=500),
        ),
        migrations.AlterField(
            model_name='post',
            name='content_url',
            field=models.URLField(null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='copyright',
            field=models.TextField(default='EMPTY', max_length=500),
        ),
        migrations.AlterField(
            model_name='post',
            name='languages',
            field=models.TextField(default='EMPTY', max_length=500),
        ),
        migrations.AlterField(
            model_name='post',
            name='subjects',
            field=models.TextField(default='EMPTY', max_length=500),
        ),
        migrations.AlterField(
            model_name='post',
            name='title',
            field=models.CharField(default='EMPTY', max_length=200),
        ),
    ]