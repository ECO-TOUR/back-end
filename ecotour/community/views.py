from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from .serializers import *

# 모든 유저가 쓴 post를 별명과 함께 출력하기
# <내가 쓴 글>
# def test2(request):
#     user_list=User.objects.all()
#     response_content = ""
#     for u in user_list:
#         response_content+=u.user_nickname+" "

#     post=Post.objects.filter(user_id=user_list.first().user_id)
#     for p in post:
#         response_content+=p.post_text
#     return HttpResponse(response_content)


def postbyid(request, id):
    post_list = Post.objects.filter(user_id=id)
    serializer = PostSerializer(post_list, many=True)
    return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)


def tourkeyword(request):
    # Retrieve all TourPlace objects
    t_list = TourPlace.objects.all()

    # Extract tour_ids from t_list
    tour_ids = [tour.tour_id for tour in t_list]

    # Filter TourPlace_has_TourKeyword based on tour_ids
    place_keyword_list = TourPlace_TourKeyword.objects.filter(tour_id__in=tour_ids)

    # Extract keyword_ids from place_keyword_list
    keyword_ids = [pk.keyword_id for pk in place_keyword_list]

    # Filter TourKeyword based on keyword_ids
    keyword_list = TourKeyword.objects.filter(keyword_id__in=keyword_ids)

    # Prepare data to return as JSON
    keyword_data = {k.keyword_id: k.keyword_name for k in keyword_list}

    return JsonResponse(keyword_data, safe=False)


def findkeyword(id):
    result = TourKeyword.objects.get(keyword_id=id)
    return result.keyword_name


def place2keyword(request, id):
    # Query all instances of TourPlace_TourKeyword
    tour_keywords = TourPlace_TourKeyword.objects.filter(tour_id=id)

    # Prepare data to return as JSON
    place_keyword_data = []
    for t in tour_keywords:
        place_keyword_data.append(
            {"placekey_id": t.placekey_id, "tour_id": t.tour_id, "keyword_id": t.keyword_id, "keyword": findkeyword(t.keyword_id)}
        )

    return JsonResponse(place_keyword_data, safe=False)


# 커뮤니티에서 장소 조회하면, 관련 포스트 출력


def search(request):
    place_name = request.GET.get("place", None)

    if place_name:
        # Filter TourPlace objects based on the 'place' parameter
        tour_place = get_object_or_404(TourPlace, tour_name__icontains=place_name)

        # Get posts related to the filtered tour place
        posts = Post.objects.filter(tour_id=tour_place.tour_id)

        # Extract tour_ids from the filtered tour place
        tour_ids = [tour_place.tour_id]

        # Filter TourPlace_TourKeyword based on tour_ids
        place_keyword_list = TourPlace_TourKeyword.objects.filter(tour_id__in=tour_ids)

        # Extract keyword_ids from place_keyword_list
        keyword_ids = [pk.keyword_id for pk in place_keyword_list]

        # Filter TourKeyword based on keyword_ids
        keyword_list = TourKeyword.objects.filter(keyword_id__in=keyword_ids)

        # Prepare data to return as JSON
        tour_place_data = {
            "tour_place": {"tour_id": tour_place.tour_id, "tour_name": tour_place.tour_name},
            "posts": list(posts.values("post_id", "post_text", "post_date")),  # Adjust fields as needed
            "keywords": list(keyword_list.values("keyword_id", "keyword_name")),  # Adjust fields as needed
        }

        return JsonResponse(tour_place_data, safe=False)

    return JsonResponse({"error": "Place not found"}, status=404)


# 키워드에 해당하는 tour 찾기
def search2(request, id):
    # Filter TourPlace_TourKeyword objects based on placekey_id
    tour_keywords = TourPlace_TourKeyword.objects.filter(placekey_id=id)

    # Extract tour_id values from the filtered TourPlace_TourKeyword objects
    tour_ids = [tk.tour_id for tk in tour_keywords]

    # Filter TourPlace objects based on the collected tour_id values
    result = TourPlace.objects.filter(tour_id__in=tour_ids)

    # Serialize the queryset to JSON format
    tour_data = TourPlaceSerializer(result, many=True)

    # Return the serialized data as a JSON response
    return JsonResponse(tour_data.data, safe=False)


def userpre(request, id):
    likes = User_Preference.objects.filter(user=id)
    serializer = UserPreferenceSerializer(likes, many=True)

    # Return the serialized data as a JSON response
    return JsonResponse(serializer.data, safe=False)


# 점수 높은 순 top3
def best(request):
    post_list = Post.objects.all().order_by("-post_score")
    post_list = post_list[:3]
    serializer = PostSerializer(post_list, many=True)

    # Return the serialized data as a JSON response
    return JsonResponse(serializer.data, safe=False)


# 커뮤니티 글 작성

# from django.utils.dateparse import parse_datetime


class WriteView(APIView):
    def post(self, request, format=None):
        text = request.data.get("text")
        img_file = request.FILES.get("img")
        # date = parse_datetime(request.data.get("date"))
        date = request.data.get("date")
        likes = request.data.get("likes", 0)
        score = request.data.get("score", 0)  # 5점만점.12345.★★★★☆
        hashtag = request.data.get("hashtag")
        tour_id = request.data.get("tour_id")
        user_id = request.data.get("user_id", 1)  # Change this to the actual user ID handling logic

        post = Post.objects.create(
            post_text=text,
            post_date=date,
            post_likes=likes,
            post_score=score,
            post_hashtag=hashtag,
            post_view=0,
            last_modified=date,
            tour_id=tour_id,
            user_id=user_id,
        )

        # Handle the image file upload and store its path
        if img_file:
            # Define the path where you want to save the image
            path = f"uploads/{post.post_id}/{img_file.name}"
            # Save the image file to the storage system (e.g., S3)
            full_path = default_storage.save(path, img_file)
            # Store the file path in the post_img field
            post.post_img = full_path
            # Save the post again with the image path
            post.save()

        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# post_id를 입력받으면, 해당하는 커뮤니티 글 수정
# 일단 전체 post 내용을 전달해주고, 다시 받아와야 할 듯.
class ModifyView(APIView):
    def post(self, request, format=None):
        post_id = request.data.get("post_id")

        # Fetch the post object or return a 404 error if not found
        post = get_object_or_404(Post, post_id=post_id)

        # Update the fields with the provided data
        post.post_text = request.data.get("text", post.post_text)
        post.post_img = request.data.get("img", post.post_img)
        post.post_date = request.data.get("date", post.post_date)
        post.post_likes = request.data.get("likes", post.post_likes)
        post.post_score = request.data.get("score", post.post_score)
        post.post_hashtag = request.data.get("hashtag", post.post_hashtag)
        post.last_modified = timezone.now()
        post.tour_id = request.data.get("tour_id", post.tour_id)
        post.user_id = request.data.get("user_id", post.user_id)  # Ensure to handle user ID appropriately

        # Save the updated post object
        post.save()

        # Serialize the updated post object
        serializer = PostSerializer(post)

        # Return the serialized data as a response
        return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteView(APIView):
    def get(self, request, id, format=None):
        post = Post.objects.filter(post_id=id)
        post.delete()
        return Response(status=status.HTTP_200_OK)


# 검색기능
class SearchView(APIView):
    def get(self, request, sorttype, text, format=None):
        # sorttype = 최신순(1) or 좋아요순(2)

        if not text:
            return Response({"error": "No search text provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Initialize an empty queryset
        post_queryset = Post.objects.none()

        # Search posts by text in post_text
        post_queryset |= Post.objects.filter(post_text__icontains=text)

        # Search keywords by text
        key_list = TourKeyword.objects.filter(keyword_name__icontains=text)

        if key_list.exists():
            # Get tour places related to found keywords
            temp_list = TourPlace_TourKeyword.objects.filter(keyword_id__in=key_list)

            if temp_list.exists():
                # Get all related tour ids
                tour_ids = [t.tour_id for t in temp_list]

                # Search posts by related tour ids
                post_queryset |= Post.objects.filter(tour_id__in=tour_ids)

        # Sort posts based on sorttype
        if sorttype == 1:  # 최신순
            post_queryset = post_queryset.order_by("-post_date")
        elif sorttype == 2:  # 좋아요순
            post_queryset = post_queryset.order_by("-post_likes")

        # Remove duplicates
        post_queryset = post_queryset.distinct()

        # Serialize the result
        serializer = PostSerializer(post_queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class MyPostView(APIView):
    def get(self, request, id, format=None):
        post = Post.objects.filter(user_id=id)
        serializer = PostSerializer(post, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 특정 포스트에 달린 댓글 모두 조회하기
class CommentsView(APIView):
    def get(self, request, post_id, format=None):
        comment = Comments.objects.filter(post_id=post_id)
        serializer = CommentSerializer(comment, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentsWriteView(APIView):
    def post(self, request, format=None):
        post_id = request.data.get("post_id")
        user_id = request.data.get("user_id")
        comments_date = timezone.now()
        comments = request.data.get("comments")
        com = Comments.objects.create(user_id=user_id, comments_date=comments_date, comments=comments, post_id=post_id)

        serializer = CommentSerializer(com)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
