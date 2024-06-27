from django.db import models


class TourPlace_has_TourKeyword(models.Model):
    placekey_id = models.IntegerField(primary_key=True)
    tour_id = models.IntegerField()
    keyword_id = models.IntegerField()

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


# TourPlace 모델
class TourPlace(models.Model):
    tour_id = models.AutoField(primary_key=True)
    tour_name = models.CharField(max_length=100)
    tour_location = models.CharField(max_length=255)
    tour_x = models.FloatField()
    tour_y = models.FloatField()
    tour_info = models.TextField()
    tour_img = models.TextField()
    tour_viewcnt = models.IntegerField(default=0)
    tour_viewcnt_month = models.CharField(max_length=45, default="0")
    tour_summary = models.TextField()
    tour_tel = models.CharField(max_length=45, null=True, blank=True)
    tour_telname = models.CharField(max_length=45, null=True, blank=True)
    tour_title = models.CharField(max_length=45, null=True, blank=True)

    class Meta:
        db_table = "TourPlace"

    def __str__(self):
        return self.tour_name


# TourKeyword 모델
class TourKeyword(models.Model):
    keyword_id = models.AutoField(primary_key=True)
    keyword_name = models.CharField(max_length=45)

    class Meta:
        db_table = "TourKeyword"

    def __str__(self):
        return self.keyword_name


# User 모델
class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_login_id = models.CharField(max_length=45)
    user_login_pw = models.CharField(max_length=45)
    user_token = models.TextField()
    user_profilephoto = models.TextField(null=True, blank=True)
    user_nickname = models.CharField(max_length=45, null=True, blank=True)

    class Meta:
        db_table = "User"

    def __str__(self):
        return self.user_login_id


# Preference 모델
class Preference(models.Model):
    preference_id = models.AutoField(primary_key=True)
    preference_name = models.CharField(max_length=45)

    class Meta:
        db_table = "Preference"

    def __str__(self):
        return self.preference_name


# User_has_Preference 모델
class User_has_Preference(models.Model):
    userpre_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    preference_id = models.IntegerField()

    class Meta:
        db_table = "User_has_Preference"


# Likes 모델
class Likes(models.Model):
    likes_id = models.AutoField(primary_key=True)
    like_date = models.DateTimeField()
    tour_id = models.IntegerField()
    user_id = models.IntegerField()

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
    tour_id = models.IntegerField()
    user_id = models.IntegerField()
    post_view = models.IntegerField(default=0)
    last_modified = models.DateTimeField()

    class Meta:
        db_table = "Post"


# Notification 모델
class Notification(models.Model):
    noti_id = models.AutoField(primary_key=True)
    noti_title = models.TextField(null=True, blank=True)
    noti_text = models.TextField(null=True, blank=True)
    noti_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "Notification"


# Log 모델
class Log(models.Model):
    log_id = models.AutoField(primary_key=True)
    search_date = models.DateField()
    search_text = models.CharField(max_length=100)
    user_id = models.IntegerField()

    class Meta:
        db_table = "Log"
