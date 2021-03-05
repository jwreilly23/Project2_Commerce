from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.name}"

    # make plural categories instead of categorys
    class Meta:
        verbose_name_plural = "categories"

        
class Listing(models.Model):
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    open_status = models.BooleanField(default=True)
    # optional inputs 
    image = models.URLField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="listings", null=True, blank=True)
    
    if open_status:
        status = "OPEN"
    else:
        status = "CLOSED"
    def __str__(self):
        return f"Title: {self.title}---Owner: {self.owner.username}---{self.status}"


class Watchlist(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlists")
    listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watchlists")

    def __str__(self):
        return f"User {self.user_id} is watching listing {self.listing_id}"


class Bid(models.Model):
    bidder_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"User {self.bidder_id} bid {self.amount} on listing {self.listing_id.title}"