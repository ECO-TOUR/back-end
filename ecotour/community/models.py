from django.contrib.auth import get_user_model
from django.db import models

"""
class TourPlace_has_TourKeyword(models.Model):
    placekey_id = models.IntegerField(primary_key=True)
    tour_id = models.IntegerField()
    keyword_id = models.IntegerField()

    def __str__(self):
        return f"{self.tour_id} - {self.keyword}"

    class Meta:
        db_table = "TourPlace_has_TourKeyword"

"""


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


"""
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
"""
"""
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
"""
# accounts/models.py

# 충돌 코드
CustomUser = get_user_model()
# class CustomUser(models.Model):
#     user_id = models.AutoField(primary_key=True)
#     id = models.CharField(max_length=45)
#     password = models.CharField(max_length=45)
#     last_login = models.DateTimeField()
#     is_superuser = models.BooleanField()
#     username = models.CharField(max_length=150)
#     first_name = models.CharField(max_length=150)
#     last_name = models.CharField(max_length=150)
#     email = models.CharField(max_length=254)
#     is_staff = models.BooleanField()
#     is_active = models.BooleanField()
#     date_joined = models.DateTimeField()
#     profilephoto = models.TextField(null=True, blank=True)
#     nickname = models.CharField(max_length=45, null=True, blank=True)

#     class Meta:
#         db_table = "accounts_customuser"

#     def __str__(self):
#         return self.username


# accounts/models.py

RefreshTokenModel = get_user_model()
# class RefreshTokenModel(models.Model):
#     token_id = models.AutoField(primary_key=True)
#     token = models.CharField(max_length=255, unique=True)
#     jti = models.CharField(max_length=36, unique=True)  # JTI 필드 추가
#     created_at = models.DateTimeField(auto_now_add=True)
#     expires_at = models.DateTimeField()
#     blacklisted = models.BooleanField(default=False)
#     # user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='refreshuser')
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

#     class Meta:
#         db_table = "accounts_refreshtokenmodel"

#     def __str__(self):
#         return self.token

#     @staticmethod
#     def create_token(user):
#         refresh = RefreshToken.for_user(user)
#         token_instance = RefreshTokenModel.objects.create(
#             user=user, token=str(refresh), jti=refresh["jti"], expires_at=timezone.now() + refresh.lifetime
#         )
#         return token_instance

#     def blacklist(self):
#         self.blacklisted = True
#         self.save()


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
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user")
    preference = models.ForeignKey(Preference, on_delete=models.CASCADE, related_name="preference")

    class Meta:
        db_table = "User_has_Preference"


# Likes 모델
class Likes(models.Model):
    likes_id = models.AutoField(primary_key=True)
    like_date = models.DateTimeField()
    tour = models.ForeignKey(TourPlace, on_delete=models.CASCADE, related_name="tourplacelike")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="userlike")

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
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="userpost")
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


# tourLog 모델
class TourLog(models.Model):
    tourlog_id = models.AutoField(primary_key=True)
    tourlog_date = models.DateField()
    tourlog_text = models.CharField(max_length=100)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="usertourlog")

    class Meta:
        db_table = "TourLog"


# postlog
class PostLog(models.Model):
    postlog_id = models.AutoField(primary_key=True)
    postlog_date = models.DateField()
    postlog_text = models.CharField(max_length=100)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="userpostlog")

    class Meta:
        db_table = "PostLog"


# Comments 모델
class Comments(models.Model):
    comments_id = models.AutoField(primary_key=True)
    comments_date = models.DateTimeField()
    comments = models.TextField(null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="usercomment")
    post = models.ForeignKey(TourPlace, on_delete=models.CASCADE, related_name="tourplacecomment")

    class Meta:
        db_table = "Comments"
