from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Default Django User model"""

class Category(models.Model):
    """Category options for listings"""
    name = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.name}"

    # make plural categories instead of categorys
    class Meta:
        verbose_name_plural = "categories"


class Listing(models.Model):
    """Listing model. References User and Category models."""
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    open_status = models.BooleanField(default=True)
    starting_bid = models.DecimalField(max_digits=5, decimal_places=2)
    # optional inputs
    image = models.URLField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="listings", null=True, blank=True)    
    
    def __str__(self):
        return f"Title: {self.title}---Owner: {self.owner.username}---Open:{self.open_status}"


class Watchlist(models.Model):
    """Watchlist model. References User and Listing models."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlists")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watchlists")

    def __str__(self):
        return f"User {self.user} is watching listing '{self.listing.title}'"


class Bid(models.Model):
    """Bid model. References User and Listing models."""
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"User {self.bidder} bid {self.amount} on listing '{self.listing.title}'"


class Comment(models.Model):
    """Comment model. References User and Listing models."""
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    body = models.CharField(max_length=100)
    post_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User {self.poster.username} commented on listing '{self.listing.title}' at {self.post_date}"