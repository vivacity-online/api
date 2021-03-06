# Generated by Django 3.0.4 on 2020-04-04 19:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='items/item_image/')),
                ('title', models.CharField(blank=True, default='', max_length=250, unique=True)),
                ('description', models.TextField(blank=True, default='', max_length=1200)),
                ('value', models.IntegerField(blank=True, default=0)),
                ('currency', models.IntegerField(choices=[(1, 'shinies'), (2, 'muns')], default=1)),
                ('quantity_sold', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=False)),
                ('created_on_date', models.DateTimeField(auto_now_add=True)),
                ('activated_on_date', models.DateTimeField(blank=True, null=True)),
                ('deactivated_on_date', models.DateTimeField(blank=True, null=True)),
                ('create_stats', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='ItemCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, default='', max_length=250)),
                ('description', models.CharField(blank=True, default='', max_length=500)),
            ],
        ),
    ]
