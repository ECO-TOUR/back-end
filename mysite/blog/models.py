from django.db import models



class Banner(models.Model):
    banner_id = models.AutoField(primary_key=True)  # 자동 생성되는 기본 키 필드
    banner_img = models.CharField(max_length=200)
    startdate = models.DateField()
    enddate = models.DateField()
    banner_title = models.CharField(max_length=200)
    banner_url = models.CharField(max_length=200)

    class Meta:
        db_table = 'Banner'

    def __str__(self):
        return self.banner_title
