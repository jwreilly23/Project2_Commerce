from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import User, Category, Listing, Watchlist, Bid, Comment


class ListingForm(forms.ModelForm):
    """Listing form generated fomr Listing model"""
    class Meta:
        model = Listing
        fields = ("title", "description", "image", "category", "starting_bid")
        error_messages = {
            'starting_bid': {
                'max_digits': _("Max starting bid is 999.99")
            }
        }


def index(request):
    # get all active listings
    active_listings = Listing.objects.filter(open_status=True)

    # get bids for active listings
    current_max_bids = []
    for listing in active_listings:
        # add the maximum or starting bid to the list for each listing
        try:
            current_max_bids.append("%.2f" % Bid.objects.filter(listing=listing).latest('amount').amount)
        except Bid.DoesNotExist:
            current_max_bids.append("%.2f" % listing.starting_bid)

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

        # confirm form data is valid
        if listing_form.is_valid():
            title = listing_form.cleaned_data["title"]
            description = listing_form.cleaned_data["description"]
            image = listing_form.cleaned_data["image"]
            category = listing_form.cleaned_data["category"]
            starting_bid = listing_form.cleaned_data["starting_bid"]
        
        # if form data was not valid, re-render page
        else:
            return render(request, "auctions/new_listing.html", {
                "listing_form": listing_form,
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
        listing = Listing(title=title, description=description, image=image, category=category, owner=current_user, starting_bid=starting_bid)
        listing.save()

        # redirect to new listing page
        listing_title = listing.title
        listing_id = listing.id
        return HttpResponseRedirect(reverse("listing_page", args=(listing_title, listing_id)))
        

    else:
        return render(request, "auctions/new_listing.html", {
            "listing_form": ListingForm(),
        })


def listing_page(request, listing_title, listing_id):
    # user, listing, bid, comments needed regardless of method
    listing = Listing.objects.get(id=listing_id)
    # check if signed in
    if request.user.id:
        current_user = User.objects.get(id=request.user.id)
    else:
        current_user = None
    
    # check if current user is listing owner
    if listing.owner == current_user:
        listing_owner = True
    else:
        listing_owner = False

    try: # check if listing has been bid on
        current_bid = Bid.objects.filter(listing=listing).latest('amount').amount
    except Bid.DoesNotExist: # listing has not been bid on, set bid to starting bid
        current_bid = listing.starting_bid

    

    # check if closed and if latest bid by current user
    if (not listing.open_status) and (Bid.objects.filter(listing=listing).latest('amount').bidder == current_user):
        winner = True
    else:
        winner = False

    # get all comments for listing
    comments = Comment.objects.filter(listing=listing)


    if request.method == "POST":
        # if watchlist added
        try:
            watchlist_action = request.POST["watchlist_action"]
            if watchlist_action == "Remove from Watchlist":
                Watchlist.objects.get(listing=listing, user=current_user).delete()
                watchlist_check = False
            elif watchlist_action == "Add to Watchlist":
                Watchlist(user=current_user, listing=listing).save()
                watchlist_check = True
        except KeyError: # watchlist_action not submitted
            try: # already on watchlist
                watchlist_check = Watchlist.objects.get(listing=listing, user=current_user)
            except Watchlist.DoesNotExist: # not on watchlist
                watchlist_check = False
            # except UnboundLocalError:
            #     watchlist_check = None

        # if bid on
        try:
            new_bid = float(request.POST["bid_amount"])
            if new_bid <= current_bid:
                return render(request, "auctions/listing_page.html", {
                    "message": "Bid must be greater than current bid",
                    "listing": listing,
                    "watchlist_check": watchlist_check,
                    "current_bid": current_bid,
                    "listing_owner": listing_owner,
                    "comments": comments
                })

            Bid(listing=listing, bidder=current_user, amount=new_bid).save()
            current_bid = Bid.objects.filter(listing=listing).latest('amount').amount
        except KeyError: # was not bid on
            pass

        # if closed by owner
        try:
            request.POST["close_listing"]
            Listing.objects.filter(id=listing_id).update(open_status=False)
            # reload listing so status correctly shows as closed
            listing = Listing.objects.get(id=listing_id)
        except KeyError: # was not closed
            pass

        # if comment added
        try:
            new_comment = request.POST["new_comment"]
            Comment(listing=listing, poster=current_user, body=new_comment).save()

        except KeyError: # no new comment
            pass

        return HttpResponseRedirect(reverse("listing_page", args=(listing_title, listing_id)))

    else: # not via POST
        try:
            watchlist_check = Watchlist.objects.get(listing=listing, user=current_user)
        except Watchlist.DoesNotExist:
            watchlist_check = False
        except UnboundLocalError: # not logged in
            watchlist_check = None

        return render(request, "auctions/listing_page.html", {
            "listing": listing,
            "watchlist_check": watchlist_check,
            "current_bid": current_bid,
            "listing_owner": listing_owner,
            "winner": winner,
            "comments": comments
        })


def watchlist(request, username):
    current_user = User.objects.get(id=request.user.id)
    user_watchlist = Watchlist.objects.filter(user=current_user)

    # get listings, bids from watchlist
    listings_and_bids = []
    for item in user_watchlist:
        listing = item.listing
        bid = "%.2f" % Bid.objects.filter(listing=item.listing).latest('amount').amount
        listings_and_bids.append((listing, bid))

    return render(request, "auctions/watchlist.html", {
        "listings_and_bids": listings_and_bids
    })


def categories(request):
    # get categories list
    categories_list = Category.objects.all()
    
    # get listings
    # listings = []
    # for category in categories:
    #     listings.append( Listing.objects.filter(category=category) )

    return render(request, "auctions/categories.html", {
        "categories": categories_list,
        # "listings": listingsS
    })


def category_listing(request, category_name):
    category = Category.objects.get(name=category_name)

    # get listings, bids from watchlist
    listings = Listing.objects.filter(category=category)
    bids = []
    for listing in listings:
        bids.append("%.2f" % Bid.objects.filter(listing=listing).latest('amount').amount)

    # combine lists to iterate concurrently; https://stackoverflow.com/questions/2415865/iterating-through-two-lists-in-django-templates
    listings_and_bids = zip(listings, bids)

    return render(request, "auctions/category_listings.html", {
        "category": category,
        "listings_and_bids": listings_and_bids
    })