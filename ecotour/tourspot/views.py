from django.http import JsonResponse
from community.models import TourPlace, TourLog, TourKeyword
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db.models import F
from django.views.decorators.csrf import csrf_exempt

# 검색
# @login_required  로그인이 필요한 경우 사용
def search_tour_places(request):
    if request.method == "GET":
        search_term = request.GET.get('search', '')  # 쿼리 파라미터로 검색어를 받음
        
        # 검색 기록 저장
        if search_term and request.user.is_authenticated:
            TourLog.objects.create(user=request.user, tourlog_text=search_term)
        
        # 검색어 처리: TourKeyword의 search_count 업데이트
        for keyword in TourKeyword.objects.all():
            if len(set(keyword.keyword_name) & set(search_term)) >= 2:  # 두 글자 이상 겹치는지 확인
                keyword.search_count = F('search_count') + 1  # search_count 증가
                keyword.save()
        
        # 관광지 검색
        results = TourPlace.objects.filter(tour_name__icontains=search_term)
        
        # 검색 결과 반환
        search_results = [
            {
                "tour_id": place.tour_id,
                "tour_name": place.tour_name,
                "tour_location": place.tour_location,
                "tour_info": place.tour_info,
                "tour_img": place.tour_img,
            }
            for place in results
        ]
        
        return JsonResponse({"statusCode": 200, "search_results": search_results})
    
    return JsonResponse({"statusCode": 400, "message": "잘못된 요청입니다.", "error": "요청 메소드는 GET이어야 합니다."}, status=400)

# 사용자별 검색 기록 조회
# @login_required  
def get_search_history(request, user_id):
    if request.method == "GET":
        # 특정 사용자의 검색 기록을 최신순으로 가져옴
        search_history = TourLog.objects.filter(user_id=user_id).order_by('-search_date')
        history = [log.search_text for log in search_history]
        
        return JsonResponse({"statusCode": 200, "search_history": history})

    return JsonResponse({"statusCode": 400, "message": "잘못된 요청입니다.", "error": "요청 메소드는 GET이어야 합니다."}, status=400)


# 검색 기록 삭제
# @login_required  
@csrf_exempt
def delete_search_history(request, user_id, log_id):
    if request.method == "DELETE":
        # 해당 사용자와 일치하는 특정 검색 기록 삭제
        log = get_object_or_404(TourLog, log_id=log_id, user_id=user_id)
        log.delete()
        return JsonResponse({"statusCode": 200, "message": "검색 기록이 삭제되었습니다."})
    
    return JsonResponse({"statusCode": 400, "message": "잘못된 요청입니다.", "error": "요청 메소드는 DELETE여야 합니다."}, status=400)


# 검색어 순위
def get_top_search_terms(request):
    if request.method == "GET":
        # 상위 10개의 검색어 순위 조회
        top_terms = TourKeyword.objects.order_by('-search_count')[:10]
        top_searches = [
            {
                "term": term.keyword_name,
                "search_count": term.search_count,
            }
            for term in top_terms
        ]
        
        return JsonResponse({"statusCode": 200, "top_search_terms": top_searches})
    
    return JsonResponse({"statusCode": 400, "message": "잘못된 요청입니다.", "error": "요청 메소드는 GET이어야 합니다."}, status=400)

# 검색어 자동완성
def autocomplete_search(request):
    if request.method == "GET":
        query = request.GET.get('query', '')
        if query:
            autocomplete_results = TourPlace.objects.filter(tour_name__icontains=query).values_list('tour_name', flat=True)
            return JsonResponse({"statusCode": 200, "autocompleteResults": list(autocomplete_results)})
        else:
            return JsonResponse({"statusCode": 200, "autocompleteResults": []})
    
    return JsonResponse({"statusCode": 400, "message": "잘못된 요청입니다.", "error": "요청 메소드는 GET이어야 합니다."}, status=400)
