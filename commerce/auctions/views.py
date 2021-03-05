from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.db.models import Max
from django.utils.translation import gettext_lazy as _

from .models import User, Category, Listing, Watchlist, Bid


# class ListingForm(forms.Form):
#     title = forms.CharField(label="Title", max_length=30)
#     description = forms.CharField(label="Description", max_length=200)
#     image = forms.URLField(label="Image (optional)", required=False)
#     temp = forms.DecimalField()
    # create tuple for category choices
    # choices = []
    # for category in Category.objects.all():
    #     choices = choices + [category.id, category.name]
    # category = forms.ChoiceField(choices=choices)

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ("title", "description", "image", "category")


class BidForm(forms.Form):
    starting_bid = forms.DecimalField(label="Starting Bid:", max_value=9999.99, min_value=1.00, decimal_places=2)
    

def index(request):
    # get all active listings
    active_listings = Listing.objects.filter(open_status=True)

    # get bids for active listings
    current_max_bids = []
    for listing in active_listings:
        # add the maximum bid to the list for each listing
        current_max_bids.append( "%.2f" % Bid.objects.filter(listing_id = listing.id).aggregate(Max('amount'))['amount__max'] )

    # combine lists to iterate concurrently; https://stackoverflow.com/questions/2415865/iterating-through-two-lists-in-django-templates
    listings_and_bids = zip(active_listings, current_max_bids)

    return render(request, "auctions/index.html", {
        "listings_and_bids": listings_and_bids
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def new_listing(request):
    if request.method == "POST":
        # take the posted data and save as form
        listing_form = ListingForm(request.POST)
        bid_form = BidForm(request.POST)

        # confirm form data is valid
        if listing_form.is_valid() and bid_form.is_valid():
            title = listing_form.cleaned_data["title"]
            description = listing_form.cleaned_data["description"]
            image = listing_form.cleaned_data["image"]
            category = listing_form.cleaned_data["category"]
            starting_bid = bid_form.cleaned_data["starting_bid"]
        
        # if form data was not valid, re-render page
        else: 
            return render(request, "auctions/new_listing.html", {
            "listing_form": ListingForm(),
            "bid_form": BidForm(),
            "message": "Invalid inputs"
        })

        # check valid category
        # category = request.POST["category"]
        # try:
        #     test_object = Category.objects.get(id=int(category))
        # except Category.DoesNotExist:
        #     return render(request, "auctions/new_listing.html", {
        #     "form": ListingForm(),
        #     "categories": Category.objects.all(),
        #     "message": "Invalid Category"
        # })

        # insert new listing data into Listing
        current_user = User.objects.get(id=request.user.id)
        new_listing = Listing(title=title, description=description, image=image, category=category, owner=current_user)
        new_listing.save()
        # insert starting bid
        starting_bid = Bid(listing_id=new_listing, bidder_id=current_user, amount=starting_bid)
        starting_bid.save()

        # TEMP - RETURN FORM INFO        
        return render(request, "auctions/temp.html", {
            "title": title,
            "description": description,
            "image": image,
            "category": category,
            "request.user.id": request.user.id
        })

    else:
        return render(request, "auctions/new_listing.html", {
            "listing_form": ListingForm(),
            "bid_form": BidForm()
        })


def listing_page(request, listing_title, listing_id):
    
    listing = Listing.objects.get(id=listing_id)

    context = {
        "listing": listing
    }
    return render(request, "auctions/listing_page.html", context)


def watchlist(request, username):
    current_user = User.objects.get(id=request.user.id)
    watchlist = Watchlist.objects.filter(user_id=current_user)