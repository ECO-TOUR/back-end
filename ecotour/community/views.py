import json

from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.db import IntegrityError

# 새로 추가
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view

from .models import *
from .serializers import *

User = get_user_model()

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


from django.http import JsonResponse

def postlist(request, id):
    # GET 요청만 처리
    if request.method == "GET":
        # 모든 게시물을 최근 수정된 순으로 가져오기
        post_list = Post.objects.all().order_by("-last_modified")

        # 게시물 리스트를 직렬화
        serializer = PostSerializer(post_list, many=True)

        # 해당 사용자가 좋아요를 누른 게시물의 ID 리스트 가져오기
        plike = PostLikes.objects.filter(user_id=id).values_list("post_id", flat=True)

        # 직렬화된 데이터를 리스트로 가져오기
        d = serializer.data

        # 각 게시물에 대해 좋아요 여부를 추가
        for x in d:
            # post_img가 있는 경우 처리
            if x["post_img"]:
                try:
                    # 이중 이스케이프된 JSON 문자열 처리
                    parsed_img = json.loads(x["post_img"])  # 첫 번째 파싱
                    if isinstance(parsed_img, str):
                        parsed_img = json.loads(parsed_img)  # 두 번째 파싱
                    
                    x["post_img"] = parsed_img
                except json.JSONDecodeError as e:
                    print(f"JSON 파싱 오류: {e}, 대상파일: {x['post_img']}")
                    x["post_img"] = []  # 파싱 실패 시 기본값 설정

            if x["post_id"] in plike:  # 게시물 ID가 plike 리스트에 있는지 확인
                x["like"] = "yes"
            else:
                x["like"] = "no"

        # 응답 데이터 생성
        response_data = {"statusCode": "OK", "message": "OK", "content": d}

        return JsonResponse(response_data, safe=False)

    # GET 이외의 요청이 들어왔을 때 405 Method Not Allowed 응답
    return JsonResponse({"statusCode": "ERROR", "message": "Invalid request method"}, status=405)


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

    # return JsonResponse(keyword_data, safe=False)
    response_data = {"statusCode": "OK", "message": "OK", "content": keyword_data}

    return JsonResponse(response_data, status=status.HTTP_200_OK, safe=False)


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

    # return JsonResponse(place_keyword_data, safe=False)
    response_data = {"statusCode": "OK", "message": "OK", "content": place_keyword_data}

    return JsonResponse(response_data, status=status.HTTP_200_OK, safe=False)


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

        # return JsonResponse(tour_place_data, safe=False)
        response_data = {"statusCode": "OK", "message": "OK", "content": tour_place_data}

        return JsonResponse(response_data, status=status.HTTP_200_OK, safe=False)

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
    # return JsonResponse(tour_data.data, safe=False)
    response_data = {"statusCode": "OK", "message": "OK", "content": tour_data.data}

    return JsonResponse(response_data, status=status.HTTP_200_OK, safe=False)


def userpre(request, id):
    likes = User_Preference.objects.filter(user=id)
    serializer = UserPreferenceSerializer(likes, many=True)

    # Return the serialized data as a JSON response
    # return JsonResponse(serializer.data, safe=False)

    # 직렬화된 데이터를 리스트로 가져오기
    d = serializer.data

    # 각 게시물에 대해 좋아요 여부를 추가
    for x in d:
        if x["post_img"]:
            x["post_img"] = json.loads(x["post_img"])
    response_data = {"statusCode": "OK", "message": "OK", "content": d}

    return JsonResponse(response_data, status=status.HTTP_200_OK, safe=False)


# 점수 높은 순 top3
def best(request):
    post_list = Post.objects.all().order_by("-post_likes")
    post_list = post_list[:4]
    serializer = PostSerializer(post_list, many=True)

    # Return the serialized data as a JSON response
    # return JsonResponse(serializer.data, safe=False)
    # 직렬화된 데이터를 리스트로 가져오기
    d = serializer.data

    # 각 게시물에 대해 좋아요 여부를 추가
    for x in d:
        if x["post_img"]:
            x["post_img"] = json.loads(x["post_img"])
    response_data = {"statusCode": "OK", "message": "OK", "content": d}

    return JsonResponse(response_data, status=status.HTTP_200_OK, safe=False)


# 커뮤니티 글 작성
def update_or_create_rating(user_id, tour_id):
    try:
        keyword_ids = TourPlace_TourKeyword.objects.filter(tour_id=tour_id).values_list("keyword_id", flat=True)

        for keyword_id in keyword_ids:
            # Step 1: 특정 user_id와 keyword_id의 존재 여부 확인
            obj, created = KeywordRating.objects.get_or_create(
                user_id=user_id, keyword_id=keyword_id, defaults={"rating": 1}  # 존재하지 않으면 rating을 1로 초기화
            )

            # Step 2: 존재할 경우, rating 값을 +1
            if not created:
                obj.rating += 1
                obj.save()

    except IntegrityError as e:
        print(f"Error occurred: {e}")


# from django.utils.dateparse import parse_datetime
@csrf_exempt
@api_view(["POST"])
def write(request):
    if request.method == "POST":
        text = request.data.get("text")
        img_files = request.FILES.getlist("img")
        # date = parse_datetime(request.data.get("date"))
        date = request.data.get("date")
        likes = 0
        score = request.data.get("score", 0)
        hashtag = request.data.get("hashtag")
        tour_id = request.data.get("tour_id")
        user_id = request.data.get("user_id", 1)

        # Convert date string to datetime object

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

        img_paths = []
        # Handle the image file upload and store its path
        if img_files:
            for i, img_file in enumerate(img_files):
                # Define the path where you want to save the image
                path = f"uploads/{post.post_id}/{img_file.name}"
                # Save the image file to the storage system (e.g., S3)
                full_path = default_storage.save(path, img_file)
                # Store the file path in the post_img field
                img_paths.append(settings.MEDIA_URL.replace("media/", "") + full_path)
                # Save the post again with the image path
            # print(img_paths)
            post.post_img = json.dumps(img_paths)
            post.save()

        PostSerializer(post)
        update_or_create_rating(user_id, tour_id)
        # return JsonResponse("ok", safe=False, status=status.HTTP_200_OK)
        response_data = {"statusCode": "OK", "message": "OK", "content": "OK"}

        return JsonResponse(response_data, status=status.HTTP_200_OK, safe=False)

    else:
        return JsonResponse({"error": "Only POST requests are allowed."}, status=status.HTTP_400_BAD_REQUEST)


def update_or_create_rating2(user_id, origin_tour_id, tour_id):
    try:
        keyword_ids = TourPlace_TourKeyword.objects.filter(tour_id=origin_tour_id).values_list("keyword_id", flat=True)

        for keyword_id in keyword_ids:
            # Step 1: 특정 user_id와 keyword_id의 존재 여부 확인
            obj, created = KeywordRating.objects.get_or_create(
                user_id=user_id, keyword_id=keyword_id, defaults={"rating": 0}  # 존재하지 않으면 rating을 1로 초기화
            )

            # Step 2: 존재할 경우, rating 값을 -1
            if not created:
                obj.rating = max(0, obj.rating - 1)
                obj.save()

        update_or_create_rating(user_id, tour_id)
    except IntegrityError as e:
        print(f"Error occurred: {e}")


@csrf_exempt
def modify(request):
    if request.method == "POST":
        try:
            # Content-Type 확인: multipart/form-data 인 경우 request.POST 사용
            if request.content_type == "application/json":
                data = json.loads(request.body)
            else:
                data = request.POST

            if not data:
                raise json.JSONDecodeError("Empty JSON body", "", 0)

            post_id = data.get("post_id")
            if not post_id:
                raise KeyError("post_id")

            # post_id로 Post 객체 가져오기
            post = get_object_or_404(Post, pk=post_id)

            # 데이터 업데이트
            post.post_text = data.get("text", post.post_text)
            post.post_likes = data.get("likes", post.post_likes)
            post.post_score = data.get("score", post.post_score)
            post.post_hashtag = data.get("hashtag", post.post_hashtag)
            post.last_modified = timezone.now()
            post.user_id = data.get("user_id", post.user_id)
            post.tour_id = data.get("tour_id", post.tour_id)

            # 기존 이미지 배열을 로드 (없을 경우 빈 배열로 처리)
            try:
                existing_imgs = json.loads(post.post_img) if post.post_img else []
            except (TypeError, json.JSONDecodeError):
                existing_imgs = []  # JSON 파싱 오류 시 빈 배열로 초기화

            # 이미지 파일 처리
            img_files = request.FILES.getlist("img")
            img_paths = []

            # 새로 업로드된 이미지를 처리하여 경로를 저장
            if img_files:
                for i, img_file in enumerate(img_files):
                    # Define the path where you want to save the image
                    path = f"uploads/{post.post_id}/{img_file.name}"
                    # Save the image file to the storage system (e.g., S3)
                    full_path = default_storage.save(path, img_file)
                    # Store the file path in the img_paths list
                    img_paths.append(settings.MEDIA_URL.replace("media/", "") + full_path)

            # 기존 이미지와 새 이미지 배열을 결합
            combined_imgs = existing_imgs + img_paths

            # 배열을 JSON으로 직렬화하여 저장
            post.post_img = json.dumps(combined_imgs)
            post.save()

            # 직렬화 및 응답
            serializer = PostSerializer(post)
            post_data = serializer.data
            if post_data.get("post_img"):
                try:
                    post_data["post_img"] = json.loads(post_data["post_img"])
                except (TypeError, json.JSONDecodeError):
                    pass

            response_data = {"statusCode": "OK", "message": "OK", "content": post_data}
            return JsonResponse(response_data, status=status.HTTP_200_OK, safe=False)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)

        except KeyError:
            return JsonResponse({"error": "Missing key: "}, status=400)

        except Exception:
            return JsonResponse({"error": "An error occurred."}, status=500)

    else:
        return JsonResponse({"error": "Only POST requests are allowed."}, status=404)

def update_or_create_rating3(user_id, tour_id):
    try:
        keyword_ids = TourPlace_TourKeyword.objects.filter(tour_id=tour_id).values_list("keyword_id", flat=True)

        for keyword_id in keyword_ids:
            # Step 1: 특정 user_id와 keyword_id의 존재 여부 확인
            obj, created = KeywordRating.objects.get_or_create(
                user_id=user_id, keyword_id=keyword_id, defaults={"rating": 0}  # 존재하지 않으면 rating을 1로 초기화
            )

            # Step 2: 존재할 경우, rating 값을 +1
            if not created:
                obj.rating = max(0, obj.rating - 1)
                obj.save()

    except IntegrityError as e:
        print(f"Error occurred: {e}")


@csrf_exempt
def delete(request, id):
    if request.method == "DELETE":
        try:
            # 특정 포스트 객체를 가져옵니다. 없으면 404를 반환합니다.
            post = get_object_or_404(Post, post_id=id)  # 필드 이름이 'id'인지 'post_id'인지 확인하세요.
            user_id = post.user_id
            tour_id = post.tour_id
            # 객체를 삭제합니다.
            post.delete()

            # return JsonResponse("ok", safe=False, status=status.HTTP_200_OK)
            response_data = {"statusCode": "OK", "message": "OK", "content": "OK"}
            update_or_create_rating3(user_id, tour_id)
            return JsonResponse(response_data, status=status.HTTP_200_OK, safe=False)

        except Exception as e:
            return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
def savelog(text, id):
    postlog = PostLog.objects.create(search_date=timezone.now(), search_text=text, user_id=id)
    postlog.save()
    # response_data = {"statusCode": "OK", "message": "OK", "content": "OK"}

    # return JsonResponse(response_data, status=status.HTTP_200_OK, safe=False)


# 검색기능
def search_post(request, sorttype, text, id):
    savelog(text, id)
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

    # return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
    # 직렬화된 데이터를 리스트로 가져오기
    d = serializer.data

    response_data = {"statusCode": "OK", "message": "OK", "content": d}

    return JsonResponse(response_data, status=status.HTTP_200_OK, safe=False)


def mypost(request, id):
    try:
        # 유저 ID로 포스트를 필터링
        print(f"Fetching posts for user ID: {id}")
        post = Post.objects.filter(user_id=id).order_by("-post_date")
        print(f"Posts found: {post.count()}")

        # 시리얼라이저를 사용해 데이터를 직렬화
        serializer = PostSerializer(post, many=True)
        print("Serialization complete")

        #
        # return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)

        # 직렬화된 데이터를 리스트로 가져오기
        d = serializer.data

        # 각 게시물에 대해 좋아요 여부를 추가
        for x in d:
            if x["post_img"]:
                x["post_img"] = json.loads(x["post_img"])
        response_data = {"statusCode": "OK", "message": "OK", "content": d}

        return JsonResponse(response_data, status=status.HTTP_200_OK, safe=False)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return JsonResponse({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 특정 포스트에 달린 댓글 모두 조회하기
def comment(request, id):
    comment = Comments.objects.filter(post_id=id)
    serializer = CommentSerializer(comment, many=True)
    # return JsonResponse(serializer.data,  safe=False,status=status.HTTP_200_OK)

    # 직렬화된 데이터를 리스트로 가져오기
    d = serializer.data

    # 각 게시물에 대해 좋아요 여부를 추가

    response_data = {"statusCode": "OK", "message": "OK", "content": d}

    return JsonResponse(response_data, status=status.HTTP_200_OK, safe=False)


def addcommcnt(post_id):
    po = Post.objects.get(post_id=post_id)
    cnt = int(po.comm_cnt)
    po.comm_cnt = cnt + 1
    po.save()
    return


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
            # return JsonResponse(serializer.data, status=status.HTTP_200_OK)

            # 직렬화된 데이터를 리스트로 가져오기
            d = serializer.data

            response_data = {"statusCode": "OK", "message": "OK", "content": d}
            addcommcnt(post_id)
            return JsonResponse(response_data, status=status.HTTP_200_OK, safe=False)

        except Exception as e:
            # 예외 처리 및 디버깅 정보 로그
            print(f"An error occurred: {str(e)}")
            return JsonResponse({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({"error": "Invalid HTTP method."}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def deletepostlog(request, id):
    if request.method == "DELETE":
        # 특정 포스트 객체를 가져옵니다. 없으면 404를 반환합니다.
        postlog = get_object_or_404(PostLog, log_id=id)

        # 객체를 삭제합니다.
        postlog.delete()

        # return JsonResponse("ok", safe=False, status=status.HTTP_200_OK)
        response_data = {"statusCode": "OK", "message": "OK", "content": "OK"}

        return JsonResponse(response_data, status=status.HTTP_200_OK, safe=False)


def mypostlog(request, id):
    postlog_list = PostLog.objects.filter(user_id=id)
    serializer = PostLogSerializer(postlog_list, many=True)

    # 직렬화된 데이터를 리스트로 가져오기
    d = serializer.data

    # 각 게시물에 대해 좋아요 여부를 추가
    for x in d:
        if x["post_img"]:
            x["post_img"] = json.loads(x["post_img"])
    response_data = {"statusCode": "OK", "message": "OK", "content": d}

    return JsonResponse(response_data, status=status.HTTP_200_OK, safe=False)


# 게시글 좋아요


@csrf_exempt
def toggle_post_like(request, user_id):
    if request.method == "POST":
        data = json.loads(request.body)
        post_id = data.get("post_id")
        post = get_object_or_404(Post, post_id=post_id)
        user = get_object_or_404(User, user_id=user_id)

        # 좋아요 추가/삭제 로직
        like, created = PostLikes.objects.get_or_create(user=user, post=post)

        # 관련 키워드 가져오기
        tour_place = post.tour
        tour_keywords = TourPlace_TourKeyword.objects.filter(tour=tour_place)

        if not created:
            # 이미 좋아요를 누른 경우, 좋아요 취소 및 post_likes 감소
            like.delete()
            post.post_likes = F("post_likes") - 1
            post.save(update_fields=["post_likes"])

            # 모든 관련 keyword_id에 대해 rating -1
            for tour_keyword in tour_keywords:
                keyword_rating, _ = KeywordRating.objects.get_or_create(user=user, keyword=tour_keyword.keyword)
                keyword_rating.rating = max(keyword_rating.rating - 1, 0)  # rating이 1보다 작아지지 않도록 설정
                keyword_rating.save()

            post.refresh_from_db()  # 데이터베이스에서 최신 값을 다시 가져옴
            return JsonResponse(
                {
                    "statusCode": 200,
                    "message": "게시글에서 좋아요가 취소되었습니다.",
                    "status": "unliked",
                    "post_id": post_id,
                    "post_likes": post.post_likes,
                }
            )

        # 좋아요 추가 및 post_likes 증가
        post.post_likes = F("post_likes") + 1
        post.save(update_fields=["post_likes"])

        # 모든 관련 keyword_id에 대해 rating +1
        for tour_keyword in tour_keywords:
            keyword_rating, _ = KeywordRating.objects.get_or_create(user=user, keyword=tour_keyword.keyword)
            keyword_rating.rating += 1
            keyword_rating.save()

        post.refresh_from_db()  # 데이터베이스에서 최신 값을 다시 가져옴
        return JsonResponse(
            {"statusCode": 200, "message": "게시글에 좋아요가 추가되었습니다.", "status": "liked", "post_id": post_id, "post_likes": post.post_likes}
        )

    return JsonResponse({"statusCode": 400, "message": "잘못된 요청입니다.", "error": "요청 메소드는 POST여야 합니다."}, status=400)
