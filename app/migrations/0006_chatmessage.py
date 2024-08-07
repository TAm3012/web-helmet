# Generated by Django 5.0.6 on 2024-07-14 04:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_product_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=255)),
                ('response', models.CharField(max_length=255)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
