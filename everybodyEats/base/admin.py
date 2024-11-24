from django.contrib import admin
from .models import FoodListing, Restaurant, NGO, FoodClaim

admin.site.register(FoodListing)
admin.site.register(Restaurant)
admin.site.register(NGO)
admin.site.register(FoodClaim)
