from django.contrib import admin
from django.urls import path
from .views import FoodListingView

urlpatterns = [
    path("food-listings/", FoodListingView.as_view(), name='food_listings')
]
