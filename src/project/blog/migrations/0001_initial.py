# Generated by Django 3.1.5 on 2021-01-18 01:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('authors', models.TextField(default='EMPTY AUTHORS', max_length=500)),
                ('subjects', models.TextField(default='EMPTY SUBJECTS', max_length=500)),
                ('bookshelves', models.TextField(default='EMPTY BOOKSHELVES', max_length=500)),
                ('languages', models.TextField(default='EMPTY LANGUAGES', max_length=500)),
                ('copyright', models.TextField(default='EMPTY COPYRIGHT', max_length=500)),
                ('content_url', models.URLField(default='https://www.example.com/')),
                ('download_count', models.IntegerField(default=0, max_length=500)),
            ],
        ),
    ]
