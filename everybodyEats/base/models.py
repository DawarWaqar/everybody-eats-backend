from django.contrib.auth.models import User
from django.db import models


# Model to track claims by NGOs
class FoodClaim(models.Model):
    food_listing = models.ForeignKey('FoodListing', on_delete=models.CASCADE)
    ngo = models.ForeignKey('NGO', on_delete=models.CASCADE)
    claimed_quantity = models.PositiveIntegerField()  # How much of the food the NGO claimed
    claimed_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.ngo.name} claimed {self.claimed_quantity} of {self.food_listing.food_name}"

# Food Listing (what the restaurant is donating)
class FoodListing(models.Model):
    food_name = models.CharField(max_length=100)
    total_quantity = models.PositiveIntegerField()  # Total quantity of food available
    available_pickup_times = models.CharField(max_length=100)
    pickup_address = models.CharField(max_length=255)
    special_instructions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='available')  # Available, Partially Claimed, Claimed
    # restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, null=True)
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, null=True, related_name='food_listings')


    # Use a reverse relationship to access all claims (NGOs that have claimed portions of the food)
    claimed_by = models.ManyToManyField('NGO', through='FoodClaim', related_name='claimed_food')

    def __str__(self):
        return f"{self.food_name} - {self.total_quantity}"

    def claimed_quantity(self):
        # Calculate the total claimed quantity by all NGOs
        return sum(claim.claimed_quantity for claim in self.foodclaim_set.all())

    def remaining_quantity(self):
        # Return the remaining quantity of food available for claiming
        return self.total_quantity - self.claimed_quantity()

# Model for Restaurants
class Restaurant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Model for NGOs
class NGO(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
