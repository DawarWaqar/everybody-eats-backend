from django.urls import path
from .views import FoodListingView, RestaurantRegistrationView, RestaurantListView, NGORegistrationView, NGOListView, ClaimFoodView, logout_view, RestaurantDetailView, RestaurantDonationsView, NGOClaimsView, CustomAuthToken, CustomObtainAuthToken, DonationStatisticsView, MonthlyDonationStatsView
from rest_framework.authtoken.views import obtain_auth_token

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
    path('claim-food/', ClaimFoodView.as_view(), name='claim_food_listing'),
    
    path('login/', CustomAuthToken.as_view(), name='custom_auth_token'),  # Login to get the token
    path('logout/', logout_view, name='logout'),  # Logout to delete token
    
    # Get past donations by a restaurant
    path('donations/', RestaurantDonationsView.as_view(), name='restaurant_donations'),

    # Get past claims by an NGO
    path('claims/', NGOClaimsView.as_view(), name='ngo_claims'),
    
    # Get statistics
    path('donation-statistics/', DonationStatisticsView.as_view(), name='donation_statistics'),
    path('monthly-donations/', MonthlyDonationStatsView.as_view(), name='monthly_donations'),
]
