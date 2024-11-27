from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import FoodListing, Restaurant, NGO, FoodClaim
from .serializers import FoodListingSerializer, RestaurantSerializer, NGOSerializer, FoodClaimSerializer, FoodClaimDonationSerializer
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from django.db.models import Sum, Count, Max
from datetime import datetime, timedelta
from django.db.models.functions import TruncMonth


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

class CustomObtainAuthToken(ObtainAuthToken):
    authentication_classes = []
    permission_classes = [AllowAny]
    
class DonationStatisticsView(APIView):

    def get(self, request):
        # Current date and time
        now = datetime.now()
        
        # Calculate total donations
        total_stats = FoodClaim.objects.aggregate(
            total_claims=Count('id'),
            total_quantity=Sum('claimed_quantity')
        )

        # Calculate current month's donations
        current_month_stats = FoodClaim.objects.filter(
            food_listing__created_at__year=now.year,
            food_listing__created_at__month=now.month
        ).aggregate(
            total_claims=Count('id'),
            total_quantity=Sum('claimed_quantity')
        )

        # Calculate last month's donations
        last_month = (now.replace(day=1) - timedelta(days=1))  # Last month's last day
        last_month_stats = FoodClaim.objects.filter(
            food_listing__created_at__year=last_month.year,
            food_listing__created_at__month=last_month.month
        ).aggregate(
            total_claims=Count('id'),
            total_quantity=Sum('claimed_quantity')
        )
        
        # Fetch recent donations (last 5 restaurants with their most recent donation)
        recent_donations = (
            FoodClaim.objects.select_related('food_listing', 'food_listing__restaurant')
            .filter(food_listing__restaurant__isnull=False)  # Ensure restaurant exists
            .values('food_listing__restaurant__id', 'food_listing__restaurant__name')
            .annotate(
                most_recent_claim=Max('claimed_at'),  # Get the most recent claim per restaurant
                most_recent_claim_quantity=Max('claimed_quantity')  # Get the most recent claimed quantity
            )
            .order_by('-most_recent_claim')  # Order by the most recent claim date
        )[:5]

        # Format the response for recent donations
        recent_donations_data = []
        for donation in recent_donations:
            # Get the most recent food claim and associated food listing for the restaurant
            recent_claim = FoodClaim.objects.filter(
                food_listing__restaurant_id=donation['food_listing__restaurant__id'],
                claimed_at=donation['most_recent_claim']
            ).first()

            if recent_claim:
                recent_donations_data.append({
                    'restaurant_name': donation['food_listing__restaurant__name'],
                    'most_recent_donation': {
                        'food_name': recent_claim.food_listing.food_name,
                        'claimed_quantity': recent_claim.claimed_quantity,
                        'pickup_address': recent_claim.food_listing.pickup_address,
                        'donation_date': recent_claim.claimed_at.strftime('%Y-%m-%d %H:%M:%S')
                    }
                })

        # Format the response
        response_data = {
            "total_donations": {
                "total_donations": total_stats['total_claims'] or 0,
                "total_quantity": total_stats['total_quantity'] or 0,
            },
            "current_month_donations": {
                "total_donations": current_month_stats['total_claims'] or 0,
                "total_quantity": current_month_stats['total_quantity'] or 0,
            },
            "last_month_donations": {
                "total_donations": last_month_stats['total_claims'] or 0,
                "total_quantity": last_month_stats['total_quantity'] or 0,
            },
            "recent_donations": recent_donations_data 
        }

        return Response(response_data, status=200)


class MonthlyDonationStatsView(APIView):

    def get(self, request):
        # Current date to get this year
        current_year = datetime.now().year
        
        # Query to get number of donations and total quantity for each month in the current year
        donations_per_month = FoodClaim.objects.filter(
            claimed_at__year=current_year  # Filter claims from this year
        ).annotate(month=TruncMonth('claimed_at')).values('month').annotate(
            donations_count=Count('id'),  # Count the number of donations
            total_claimed_quantity=Sum('claimed_quantity')  # Sum the claimed quantity
        ).order_by('month')  # Order by month
        
        # Format the data into a list of dictionaries
        monthly_donations = []
        for donation in donations_per_month:
            monthly_donations.append({
                'month': donation['month'].strftime('%B'),  # Month name (e.g. January, February)
                'year': donation['month'].year,
                'donations_count': donation['donations_count'],
                'total_claimed_quantity': donation['total_claimed_quantity'],  # Total claimed quantity
            })
        
        return Response({
            'monthly_donations': monthly_donations
        }, status=200)