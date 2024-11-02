# Create your views here.
from rest_framework import generics
from .models import FoodListing, Restaurant, NGO
from .serializers import FoodListingSerializer, RestaurantSerializer, NGOSerializer

class FoodListingView(generics.ListCreateAPIView):
    queryset = FoodListing.objects.all()
    serializer_class = FoodListingSerializer

# View to register a new restaurant
class RestaurantRegistrationView(generics.CreateAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

# View to list all registered restaurants
class RestaurantListView(generics.ListAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

# View to register a new NGO
class NGORegistrationView(generics.CreateAPIView):
    queryset = NGO.objects.all()
    serializer_class = NGOSerializer

# View to list all registered NGOs
class NGOListView(generics.ListAPIView):
    queryset = NGO.objects.all()
    serializer_class = NGOSerializer