from community.models import *


def recommend(user_id):
    # Step 1: Get the user's highest-rated keyword
    user_keyword = KeywordRating.objects.filter(user_id=user_id).order_by("-rating").values_list("keyword", flat=True).first()

    if not user_keyword:
        print("No keywords found for this user.")

    # Step 2: Fetch all tour IDs that match the user's highest-rated keyword
    matching_tours = TourPlace_TourKeyword.objects.filter(keyword_id=user_keyword).values_list("tour_id", flat=True).distinct()

    if not matching_tours:
        print("No matching tours found.")

    # Step 3: Get the tour names corresponding to the matching tour IDs
    tours = TourPlace.objects.filter(tour_id__in=matching_tours).order_by("-tour_viewcnt").values("tour_name", "tour_id")

    if not tours:
        print("No tours found.")
    else:
        return tours
