from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from .models import *
from .serializers import *
import json
from django.http import HttpResponse
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


def postlist(request):
    post_list = Post.objects.all()
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
@csrf_exempt
@api_view(['POST'])
def write(request):
    if request.method == "POST":
        text = request.data.get("text")
        img = request.data.get("img")
        date = request.data.get("date")
        likes = 0
        score = request.data.get("score", 0)
        hashtag = request.data.get("hashtag")
        tour_id = request.data.get("tour_id")
        user_id = request.data.get("user_id", 1)

        # Convert date string to datetime object
        
        post = Post.objects.create(
            post_text=text,
            post_img=img,
            post_date=date,
            post_likes=likes,
            post_score=score,
            post_hashtag=hashtag,
            post_view=0,
            last_modified=date,
            tour_id=tour_id,
            user_id=user_id,
        )

        serializer = PostSerializer(post)
        return JsonResponse("ok", safe=False, status=status.HTTP_200_OK)
    else:
        return JsonResponse({"error": "Only POST requests are allowed."}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def modify(request):
    if request.method == "POST":
        try:
            # JSON 데이터를 파싱합니다.
            data = json.loads(request.body)
            post_id = data.get("post_id")
            
            # post_id로 Post 객체를 가져오거나 404 오류를 반환합니다.
            post = get_object_or_404(Post, post_id=post_id)

            # 데이터를 업데이트합니다.
            post.post_text = data.get("text", post.post_text)
            post.post_img = data.get("img", post.post_img)
            #post.post_date = data.get("date", post.post_date)
            post.post_likes = data.get("likes", post.post_likes)
            post.post_score = data.get("score", post.post_score)
            post.post_hashtag = data.get("hashtag", post.post_hashtag)
            post.last_modified = timezone.now()
            post.tour_id = data.get("tour_id", post.tour_id)
            post.user_id = data.get("user_id", post.user_id)

            # 변경된 내용을 저장합니다.
            post.save()

            # 객체를 직렬화합니다.
            serializer = PostSerializer(post)
            
            # 직렬화된 데이터를 JSON 응답으로 반환합니다.
            return JsonResponse(serializer.data, safe=False, status=200)
        
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
        
        except KeyError as e:
            return JsonResponse({"error": f"Missing key: {str(e)}"}, status=400)
        
    else:
        return JsonResponse({"error": "modify: Only POST requests are allowed."}, status=404)


def delete(request, id):
    
    try:
            # 특정 포스트 객체를 가져옵니다. 없으면 404를 반환합니다.
        post = get_object_or_404(Post, post_id=id)  # 필드 이름이 'id'인지 'post_id'인지 확인하세요.
            
            # 객체를 삭제합니다.
        post.delete()

        return JsonResponse("ok", safe=False, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# 검색기능
def search_post(request, sorttype, text):
    print(sorttype, text)
    if not text.strip():  # 빈 문자열이나 공백만 있는 경우 처리
        return JsonResponse({"error": "No search text provided."}, status=status.HTTP_400_BAD_REQUEST)

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
    else:
        # sorttype이 예상치 못한 값일 경우 기본값 설정
        return JsonResponse({"error": "Invalid sort type provided."}, status=status.HTTP_400_BAD_REQUEST)

    # Remove duplicates
    post_queryset = post_queryset.distinct()

    # Serialize the result
    serializer = PostSerializer(post_queryset, many=True)

    return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)


def mypost(request, id):
    try:
        # 유저 ID로 포스트를 필터링
        print(f"Fetching posts for user ID: {id}")
        post = Post.objects.filter(user_id=id)
        print(f"Posts found: {post.count()}")

        # 시리얼라이저를 사용해 데이터를 직렬화
        serializer = PostSerializer(post, many=True)
        print("Serialization complete")

        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return JsonResponse({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 특정 포스트에 달린 댓글 모두 조회하기
def comment(request, id):
    comment = Comments.objects.filter(post_id=id)
    serializer = CommentSerializer(comment, many=True)
    return JsonResponse(serializer.data,  safe=False,status=status.HTTP_200_OK)

@csrf_exempt
def comment_write(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            # POST 데이터에서 필요한 정보 가져오기
            post_id = data.get("post_id")
            user_id = data.get("user_id")
            comments_date = timezone.now()
            comments = data.get("comments")

            # 데이터가 올바르게 제공되었는지 확인
            if not all([post_id, user_id, comments]):
                return JsonResponse({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

            # 댓글 생성
            com = Comments.objects.create(user_id=user_id, comments_date=comments_date, comments=comments, post_id=post_id)

            # 시리얼라이저 사용
            serializer = CommentSerializer(com)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            # 예외 처리 및 디버깅 정보 로그
            print(f"An error occurred: {str(e)}")
            return JsonResponse({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({"error": "Invalid HTTP method."}, status=status.HTTP_400_BAD_REQUEST)