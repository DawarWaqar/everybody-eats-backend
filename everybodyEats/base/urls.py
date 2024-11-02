from django.contrib import admin
from django.urls import path
from .views import FoodListingView, RestaurantRegistrationView, RestaurantListView, NGORegistrationView, NGOListView

urlpatterns = [
    path("food-listings/", FoodListingView.as_view(), name='food_listings'),
    path("register-restaurant/", RestaurantRegistrationView.as_view(), name='register_restaurant'),
    path("restaurants/", RestaurantListView.as_view(), name='restaurants_list'),
    path("register-ngo/", NGORegistrationView.as_view(), name='register_ngo'),
    path("ngos/", NGOListView.as_view(), name='ngo_list'),
]
