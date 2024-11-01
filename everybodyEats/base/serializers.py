from rest_framework import serializers
from .models import FoodListing

class FoodListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodListing
        fields = "__all__"


    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value
