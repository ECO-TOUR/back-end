from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *


class Test1View(APIView):
    def get(self, request, format=None):
        banner_list = Banner.objects.all()
        serializer = BannerSerializer(banner_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
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

class Test2View(APIView):
    def get(self, request, id, format=None):
        post_list = Post.objects.filter(user_id=id)
        serializer = PostSerializer(post_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



from django.http import JsonResponse
from .models import TourPlace, TourPlace_has_TourKeyword, TourKeyword

#관광지에 연결된 키워드 출력
def test3(request):
    # Retrieve all TourPlace objects
    t_list = TourPlace.objects.all()

    # Extract tour_ids from t_list
    tour_ids = [tour.tour_id for tour in t_list]
    
    # Filter TourPlace_has_TourKeyword based on tour_ids
    place_keyword_list = TourPlace_has_TourKeyword.objects.filter(tour_id__in=tour_ids)
    
    # Extract keyword_ids from place_keyword_list
    keyword_ids = [pk.keyword_id for pk in place_keyword_list]

    # Filter TourKeyword based on keyword_ids
    keyword_list = TourKeyword.objects.filter(keyword_id__in=keyword_ids)
    
    a=""
    # Prepare data to return as JSON
    for k in keyword_list:
        a+=str(k.keyword_id)+" : "
        a+=k.keyword_name
    # keyword_data = list(keyword_list.values())

    return HttpResponse(a)




def test4(request):
    # Query all instances of TourPlace_has_TourKeyword
    tour_keywords = TourPlace_has_TourKeyword.objects.all()

    # Pass data to the template context
    context = {
        'tour_keywords': tour_keywords
    }

    a=""
    for t in tour_keywords:
        a+=str(t.placekey_id)
    # Render the template with context data
    return HttpResponse(a)


# 커뮤니티에서 장소 조회하면, 관련 포스트 출력
def search(request):
    place_name = request.GET.get('place', None)

    if place_name:
        # Filter TourPlace objects based on the 'place' parameter
        tour_place = get_object_or_404(TourPlace, tour_name__icontains=place_name)
        
        # Get posts related to the filtered tour place
        posts = Post.objects.filter(tour_id=tour_place.tour_id)

        # Extract tour_ids from t_list
        tour_ids = [tour_place.tour_id]
    
        # Filter TourPlace_has_TourKeyword based on tour_ids
        place_keyword_list = TourPlace_has_TourKeyword.objects.filter(tour_id__in=tour_ids)
    
        # Extract keyword_ids from place_keyword_list
        keyword_ids = [pk.keyword_id for pk in place_keyword_list]

        # Filter TourKeyword based on keyword_ids
        keyword_list = TourKeyword.objects.filter(keyword_id__in=keyword_ids)

        # Prepare data to return as JSON
        posts_data = list(posts.values())
        keyword_data = list(keyword_list.values())

        return HttpResponse(tour_place)
        return HttpResponse(posts_data+keyword_data)
   
    
#점수 높은 순 top3
def best(request):
    post_list=Post.objects.all().order_by('-post_score')
    post_list=post_list[:3]
    context=""
    for p in post_list:
        context+="socre: " +str(p.post_score)+"text: "+p.post_text+" \n"
        
    return HttpResponse(context)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ExampleSerializer

class ExampleView(APIView):
    def get(self, request, format=None):
        data = {"id": 1, "name": "Example"}
        return Response(data)

    def post(self, request, format=None):
        serializer = ExampleSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
