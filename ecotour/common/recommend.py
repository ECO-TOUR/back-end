from community.models import *


def recommend(user_id):
    # Step 1: Get the user's highest-rated keywords
    user_keywords = KeywordRating.objects.filter(user_id=user_id).order_by("-rating").values_list("keyword", flat=True)

    if not user_keywords:
        print("No keywords found for this user.")
        return []

    tours = []

    # Step 2: Fetch all tour IDs that match the user's highest-rated keywords
    for keyword in user_keywords:
        matching_tours = TourPlace_TourKeyword.objects.filter(keyword_id=keyword).values_list("tour_id", flat=True).distinct()

        if matching_tours:
            # Fetch tour names for the matching tour IDs
            tours.extend(TourPlace.objects.filter(tour_id__in=matching_tours).order_by("-tour_viewcnt").values("tour_name", "tour_id"))

    # Step 3: Limit to 5 unique tours if less than 5 found
    unique_tours = {tour["tour_id"]: tour for tour in tours}.values()  # Using dictionary comprehension to ensure uniqueness
    if len(unique_tours) < 5:
        additional_tours = (
            TourPlace.objects.exclude(tour_id__in=[tour["tour_id"] for tour in unique_tours])
            .order_by("-tour_viewcnt")
            .values("tour_name", "tour_id")[: 5 - len(unique_tours)]
        )
        unique_tours = list(unique_tours) + list(additional_tours)

    return list(unique_tours)[:5]
