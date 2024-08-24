# Create your models here.
from django.db import models

class TempTourData(models.Model):
    tour_location = models.CharField(max_length=255)
    areacode = models.IntegerField()
    tour_id = models.IntegerField(primary_key=True)  # primary key로 설정
    createdtime = models.DateTimeField(auto_now_add=True)
    tour_img = models.TextField()
    modifiedtime = models.DateTimeField(auto_now=True)
    sigungucode = models.IntegerField()
    subtitle = models.TextField()
    tour_info = models.TextField()
    tour_tel = models.CharField(max_length=45)
    tour_telname = models.CharField(max_length=45)
    tour_name = models.CharField(max_length=100)

    class Meta:
        db_table = 'temp_tour_data'  # 데이터베이스 테이블 이름 설정

    def __str__(self):
        return self.tour_name
