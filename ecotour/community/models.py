# accounts/models.py
from django.conf import settings
from django.db import models


class TourPlace(models.Model):
    tour_id = models.AutoField(primary_key=True)
    tour_name = models.CharField(max_length=100)
    tour_location = models.CharField(max_length=255)
    tour_x = models.FloatField()
    tour_y = models.FloatField()
    tour_info = models.TextField()
    tour_img = models.TextField()
    tour_viewcnt = models.IntegerField(default=0)
    tour_viewcnt_month = models.IntegerField(default=0)
    tour_summary = models.TextField()
    tour_tel = models.CharField(max_length=45, null=True, blank=True)
    tour_telname = models.CharField(max_length=45, null=True, blank=True)
    tour_title = models.CharField(max_length=45, null=True, blank=True)

    # 새로운 필드 추가
    areacode = models.IntegerField(null=True, blank=True)  # 'int'에 맞음
    createdtime = models.DateTimeField(null=True, blank=True)  # 'datetime'에 맞음
    sigungucode = models.IntegerField(null=True, blank=True)  # 'int'에 맞음
    opening_hours = models.CharField(max_length=255, null=True, blank=True)  # 'varchar(255)'에 맞음
    tour_hours = models.CharField(max_length=255, null=True, blank=True)  # 'varchar(255)'에 맞음
    website = models.CharField(max_length=255, null=True, blank=True)  # 'varchar(255)'에 맞음
    fees = models.CharField(max_length=255, null=True, blank=True)  # 'varchar(255)'에 맞음
    restrooms = models.CharField(max_length=255, null=True, blank=True)  # 'varchar(255)'에 맞음
    accessibility = models.CharField(max_length=255, null=True, blank=True)  # 'varchar(255)'에 맞음
    parking = models.CharField(max_length=255, null=True, blank=True)  # 'varchar(255)'에 맞음
    search_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "TourPlace"

    def __str__(self):
        return self.tour_name


# TourKeyword 모델
class TourKeyword(models.Model):
    keyword_id = models.AutoField(primary_key=True)
    keyword_name = models.CharField(max_length=45)
    search_count = models.IntegerField(default=0)  # 가윤 검색 횟수 추가

    class Meta:
        db_table = "TourKeyword"

    def __str__(self):
        return self.keyword_name


class TourPlace_TourKeyword(models.Model):
    placekey_id = models.IntegerField(primary_key=True)
    # tour_id = models.IntegerField()
    # keyword_id = models.IntegerField()
    tour = models.ForeignKey(TourPlace, on_delete=models.CASCADE, related_name="tourplace")
    keyword = models.ForeignKey(TourKeyword, on_delete=models.CASCADE, related_name="tourkeyword")

    def __str__(self):
        return f"{self.tour_id} - {self.keyword}"

    class Meta:
        db_table = "TourPlace_has_TourKeyword"


# Banner 모델
class Banner(models.Model):
    banner_id = models.AutoField(primary_key=True)
    banner_img = models.CharField(max_length=255)
    startdate = models.DateField()
    enddate = models.DateField()
    banner_title = models.CharField(max_length=200)
    banner_url = models.URLField()

    class Meta:
        db_table = "Banner"

    def __str__(self):
        return self.banner_title


# Preference 모델
class Preference(models.Model):
    preference_id = models.AutoField(primary_key=True)
    preference_name = models.CharField(max_length=45)

    class Meta:
        db_table = "Preference"

    def __str__(self):
        return self.preference_name


# User_has_Preference 모델
class User_Preference(models.Model):
    userpre_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user")
    preference = models.ForeignKey(Preference, on_delete=models.CASCADE, related_name="preference")

    class Meta:
        db_table = "User_has_Preference"


# Likes 모델
class Likes(models.Model):
    likes_id = models.AutoField(primary_key=True)
    like_date = models.DateTimeField(auto_now_add=True)
    tour = models.ForeignKey(TourPlace, on_delete=models.CASCADE, related_name="tourplacelike")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="userlike")

    class Meta:
        db_table = "Likes"


# Post 모델
class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    post_text = models.TextField(null=True, blank=True)
    post_img = models.TextField(null=True, blank=True)
    post_date = models.DateTimeField()
    post_likes = models.IntegerField(default=0)
    post_score = models.IntegerField(null=True, default=0)
    post_hashtag = models.CharField(max_length=100, null=True, blank=True)
    tour = models.ForeignKey(TourPlace, on_delete=models.CASCADE, related_name="tourplacepost")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="userpost")
    post_view = models.IntegerField(default=0)
    last_modified = models.DateTimeField()
    comm_cnt = models.IntegerField(default=0)



    class Meta:
        db_table = "Post"


# PostLikes 모델
class PostLikes(models.Model):
    plikes_id = models.AutoField(primary_key=True)
    like_date = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="postlike")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="userlikepost")

    class Meta:
        db_table = "PostLikes"


# Notification 모델
class Notification(models.Model):
    noti_id = models.AutoField(primary_key=True)
    noti_title = models.TextField(null=True, blank=True)
    noti_text = models.TextField(null=True, blank=True)
    noti_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "Notification"


# tourLog 모델
class TourLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    search_date = models.DateTimeField(auto_now_add=True)
    search_text = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,blank=True,on_delete=models.CASCADE, related_name="usertourlog")
 
    class Meta:
        db_table = "TourLog"


# postlog
class PostLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    search_date = models.DateField()
    search_text = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="userpostlog")

    class Meta:
        db_table = "PostLog"


# Comments 모델
class Comments(models.Model):
    comments_id = models.AutoField(primary_key=True)
    comments_date = models.DateTimeField()
    comments = models.TextField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="usercomment")
    post = models.ForeignKey(TourPlace, on_delete=models.CASCADE, related_name="tourplacecomment")

    class Meta:
        db_table = "Comments"
