from django.db import models

class FoodListing(models.Model):
    food_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    available_pickup_times = models.CharField(max_length=100)
    pickup_address = models.CharField(max_length=255)
    special_instructions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.food_name} - {self.quantity}"