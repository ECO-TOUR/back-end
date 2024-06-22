# Generated by Django 4.2.13 on 2024-06-22 07:05

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="TourKeyword",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50, unique=True)),
            ],
            options={
                "db_table": "TourKeyword",
            },
        ),
        migrations.CreateModel(
            name="TourPlace",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("tour_name", models.CharField(max_length=100)),
                ("tour_location", models.TextField()),
                ("tour_x", models.FloatField()),
                ("tour_y", models.FloatField()),
                ("tour_info", models.TextField()),
                ("tour_img", models.TextField()),
                ("tour_viewcnt", models.IntegerField(default=0)),
                ("tour_viewcnt_month", models.CharField(default="0", max_length=45)),
                ("tour_summary", models.TextField()),
                ("tour_tel", models.CharField(max_length=45, null=True)),
                ("tour_telname", models.CharField(max_length=45, null=True)),
                ("tour_title", models.CharField(max_length=45, null=True)),
            ],
            options={
                "db_table": "TourPlace",
            },
        ),
        migrations.CreateModel(
            name="TourPlace_has_TourKeyword",
            fields=[
                ("place_key", models.IntegerField(primary_key=True, serialize=False)),
                ("tour_id", models.IntegerField()),
                ("keyword", models.IntegerField()),
            ],
            options={
                "db_table": "TourPlace_has_TourKeyword",
            },
        ),
    ]
