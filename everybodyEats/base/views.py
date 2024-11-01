# Create your views here.
from rest_framework import generics
from .models import FoodListing
from .serializers import FoodListingSerializer

class FoodListingView(generics.ListCreateAPIView):
    queryset = FoodListing.objects.all()
    serializer_class = FoodListingSerializer