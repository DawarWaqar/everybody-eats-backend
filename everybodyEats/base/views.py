from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import FoodListing, Restaurant, NGO, FoodClaim
from .serializers import (
    FoodListingSerializer,
    RestaurantSerializer,
    NGOSerializer,
    FoodClaimSerializer,
)
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.views import ObtainAuthToken


# View to list and create food listings (for restaurants)
class FoodListingView(generics.ListCreateAPIView):
    queryset = FoodListing.objects.all()
    serializer_class = FoodListingSerializer


# View to register a new restaurant
class RestaurantRegistrationView(generics.CreateAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer


# View to list all registered restaurants
class RestaurantListView(generics.ListAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer


class RestaurantDetailView(APIView):
    def get(self, request, pk):
        try:
            restaurant = Restaurant.objects.get(id=pk)  # Fetch restaurant by ID
        except Restaurant.DoesNotExist:
            return Response(
                {"detail": "Restaurant not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Serialize the restaurant and include food listings
        serializer = RestaurantSerializer(restaurant)
        return Response(serializer.data)


# View to register a new NGO
class NGORegistrationView(generics.CreateAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    queryset = NGO.objects.all()
    serializer_class = NGOSerializer


# View to list all registered NGOs
class NGOListView(generics.ListAPIView):
    queryset = NGO.objects.all()
    serializer_class = NGOSerializer


# View to allow an NGO to claim a portion of a food listing


class ClaimFoodView(generics.CreateAPIView):
    serializer_class = FoodClaimSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Automatically associate the authenticated NGO with the claim (done in the serializer)
        serializer.save()

    def post(self, request, *args, **kwargs):
        # Call the generic `CreateAPIView`'s post method to handle the claim creation
        return super().post(request, *args, **kwargs)


@api_view(["POST"])
def logout_view(request):
    """
    Logout the user by deleting their authentication token.
    """
    try:
        # Get the token from request headers
        token = request.headers.get("Authorization").split()[1]
        user_token = Token.objects.get(key=token)

        # Delete the token to log out
        user_token.delete()
        return Response(
            {"detail": "Successfully logged out."}, status=status.HTTP_200_OK
        )

    except Token.DoesNotExist:
        return Response(
            {"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST
        )
    except IndexError:
        return Response(
            {"detail": "Token not provided."}, status=status.HTTP_400_BAD_REQUEST
        )


class CustomObtainAuthToken(ObtainAuthToken):
    authentication_classes = []
    permission_classes = [AllowAny]
