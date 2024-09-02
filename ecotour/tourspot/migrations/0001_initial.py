# Generated by Django 4.2.13 on 2024-08-27 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="TempTourData",
            fields=[
                ("tour_location", models.CharField(max_length=255)),
                ("areacode", models.IntegerField()),
                ("tour_id", models.IntegerField(primary_key=True, serialize=False)),
                ("createdtime", models.DateTimeField(auto_now_add=True)),
                ("tour_img", models.TextField()),
                ("modifiedtime", models.DateTimeField(auto_now=True)),
                ("sigungucode", models.IntegerField()),
                ("subtitle", models.TextField()),
                ("tour_info", models.TextField()),
                ("tour_tel", models.CharField(max_length=45)),
                ("tour_telname", models.CharField(max_length=45)),
                ("tour_name", models.CharField(max_length=100)),
            ],
            options={"db_table": "temp_tour_data"},
        )
    ]