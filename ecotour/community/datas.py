from community.models import TourKeyword, TourPlace

# Assuming you have already created instances of TourKeyword for 'Nature' and 'History'
# Create a TourPlace instance and associate it with TourKeyword instances

# Example:
tour_place = TourPlace.objects.create(
    tour_name="보영이집333",
    tour_location="제주특별자치도 제주시 조천읍 동백로 77",
    tour_x=0,
    tour_y=0,
    tour_info="null",
    tour_img="http://tong.visitkorea.or.kr/cms/resource/40/2549040_image2_1.jpg",
    tour_viewcnt=0,
    tour_viewcnt_month="0",
    tour_summary="info",
    tour_tel="064-784-9445",
    tour_telname="동백동산 탐방안내소",
    tour_title="동백동산 습지센터",
)

# Add keywords to the TourPlace instance
nature_keyword = TourKeyword.objects.get(name="Nature")
tour_place.keyword.add(nature_keyword)

# Similarly, add other TourPlace instances and associate with appropriate TourKeyword instances as needed
