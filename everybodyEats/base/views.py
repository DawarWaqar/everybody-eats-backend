from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import FoodListing, Restaurant, NGO, FoodClaim
from .serializers import FoodListingSerializer, RestaurantSerializer, NGOSerializer, FoodClaimSerializer, FoodClaimDonationSerializer
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.authtoken.views import ObtainAuthToken

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        # Determine user type (Restaurant or NGO)
        user_type = None
        if Restaurant.objects.filter(user=user).exists():
            user_type = "restaurant"
        elif NGO.objects.filter(user=user).exists():
            user_type = "ngo"

        return Response({
            'token': token.key,
            'role': user_type
        })

# View to list and create food listings (for restaurants)
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

class RestaurantDetailView(APIView):
    def get(self, request, pk):
        try:
            restaurant = Restaurant.objects.get(id=pk)  # Fetch restaurant by ID
        except Restaurant.DoesNotExist:
            return Response({"detail": "Restaurant not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize the restaurant and include food listings
        serializer = RestaurantSerializer(restaurant)
        return Response(serializer.data)

# View to register a new NGO
class NGORegistrationView(generics.CreateAPIView):
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



@api_view(['POST'])
def logout_view(request):
    """
    Logout the user by deleting their authentication token.
    """
    try:
        # Get the token from request headers
        token = request.headers.get('Authorization').split()[1]
        user_token = Token.objects.get(key=token)
        
        # Delete the token to log out
        user_token.delete()
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
    
    except Token.DoesNotExist:
        return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
    except IndexError:
        return Response({"detail": "Token not provided."}, status=status.HTTP_400_BAD_REQUEST)
    
# View to list claims linked to a restaurant
class RestaurantDonationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get the restaurant
            restaurant = Restaurant.objects.get(user=request.user)
        except Restaurant.DoesNotExist:
            return Response({"detail": "Restaurant not found."}, status=status.HTTP_404_NOT_FOUND)

        # Fetch claims linked to the restaurant's food listings
        claims = FoodClaim.objects.filter(food_listing__restaurant=restaurant)

        # Serialize the claims
        serializer = FoodClaimDonationSerializer(claims, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# View to list past claims by an NGO
class NGOClaimsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get the NGO
            ngo = NGO.objects.get(user=request.user)
        except NGO.DoesNotExist:
            return Response({"detail": "NGO not found."}, status=status.HTTP_404_NOT_FOUND)

        # Fetch all claims made by the NGO
        claims = FoodClaim.objects.filter(ngo=ngo)

        # Serialize the data
        serializer = FoodClaimDonationSerializer(claims, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)