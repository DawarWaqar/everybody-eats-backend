from rest_framework import serializers
from django.contrib.auth.models import User
from .models import FoodListing, Restaurant, NGO, FoodClaim

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Create the User object
        user = User.objects.create_user(**validated_data)
        return user

# Serializer for the FoodListing model
class FoodListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodListing
        fields = ['id', 'food_name', 'total_quantity', 'available_pickup_times', 'pickup_address', 'special_instructions', 'created_at', 'status', 'restaurant']

    def create(self, validated_data):
        # Get the currently authenticated user (which is the restaurant)
        user = self.context['request'].user  # Get the logged-in user from the request context
        
        # Fetch the restaurant associated with the logged-in user
        try:
            restaurant = Restaurant.objects.get(user=user)
        except Restaurant.DoesNotExist:
            raise serializers.ValidationError("Restaurant not found for this user.")
        
        # Create the FoodListing and assign the restaurant
        food_listing = FoodListing.objects.create(restaurant=restaurant, **validated_data)
        return food_listing

# Serializer for the Restaurant model
class RestaurantSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Restaurant
        fields = ['user', 'name', 'address', 'phone']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        restaurant = Restaurant.objects.create(user=user, **validated_data)
        restaurant.email = user.email
        restaurant.save()
        return restaurant

# Serializer for the NGO model
class NGOSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = NGO
        fields = ['user', 'name', 'address', 'phone']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        ngo = NGO.objects.create(user=user, **validated_data)
        ngo.email = user.email
        ngo.save()
        return ngo

# Serializer for the FoodClaim model (to handle claiming functionality)
class FoodClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodClaim
        fields = ['food_listing', 'claimed_quantity']

    def validate_claimed_quantity(self, value):
        # Ensure that claimed quantity is positive
        if value <= 0:
            raise serializers.ValidationError("Claimed quantity must be greater than zero.")
        return value

    def create(self, validated_data):
        # Get the logged-in user (NGO)
        user = self.context['request'].user
        try:
            ngo = NGO.objects.get(user=user)
        except NGO.DoesNotExist:
            raise serializers.ValidationError("The user is not associated with an NGO.")
        
        # Get the food listing from validated data
        food_listing = validated_data['food_listing']
        claimed_quantity = validated_data['claimed_quantity']

        # Check if enough food is available for claiming
        if claimed_quantity > food_listing.remaining_quantity():
            raise serializers.ValidationError(f"Not enough food remaining. Only {food_listing.remaining_quantity()} available.")
        
        # Check if the NGO has already claimed this food
        # if food_listing.claimed_by.filter(id=ngo.id).exists():
        #     raise serializers.ValidationError("This NGO has already claimed a portion of this food.")

        # Create the food claim
        food_claim = FoodClaim.objects.create(
            food_listing=food_listing,
            ngo=ngo,
            claimed_quantity=claimed_quantity
        )


        # Update the food listing's status based on the remaining quantity
        if food_listing.remaining_quantity() == 0:
            food_listing.status = 'claimed'  # All food claimed
        else:
            food_listing.status = 'partially claimed'  # Part of the food still available
        food_listing.save()

        return food_claim
