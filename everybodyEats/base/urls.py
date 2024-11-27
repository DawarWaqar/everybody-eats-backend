from django.urls import path
from .views import (
    FoodListingView,
    RestaurantRegistrationView,
    RestaurantListView,
    NGORegistrationView,
    NGOListView,
    ClaimFoodView,
    logout_view,
    RestaurantDetailView,
    CustomObtainAuthToken,
)

urlpatterns = [
    # Food Listings (for restaurants)
    path("food-listings/", FoodListingView.as_view(), name="food_listings"),
    # Restaurant Routes
    path(
        "register-restaurant/",
        RestaurantRegistrationView.as_view(),
        name="register_restaurant",
    ),
    path("restaurants/", RestaurantListView.as_view(), name="restaurants_list"),
    path(
        "restaurants/<int:pk>/",
        RestaurantDetailView.as_view(),
        name="restaurant_detail",
    ),
    # NGO Routes
    path("register-ngo/", NGORegistrationView.as_view(), name="register_ngo"),
    path("ngos/", NGOListView.as_view(), name="ngo_list"),
    # Claim and Update Donation Routes
    path("claim-food/", ClaimFoodView.as_view(), name="claim_food_listing"),
    path(
        "login/", CustomObtainAuthToken.as_view(), name="api_token_auth"
    ),  # Login to get the token
    path("logout/", logout_view, name="logout"),  # Logout to delete token
]
