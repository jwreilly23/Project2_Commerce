from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Category, Listing, Watchlist


class ListingForm(forms.Form):
    title = forms.CharField(label="Title", max_length=30)
    description = forms.CharField(label="Description", max_length=200)
    image = forms.URLField(label="Image (optional)", required=False)

    # create tuple for category choices
    choices = ()
    for category in Category.objects.all():
        choices = choices + (category, category.name)
    category = forms.ChoiceField(choices=choices)

    


def index(request):
    return render(request, "auctions/index.html")


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
        form = ListingForm(request.POST)

        # confirm form data is valid
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            image = form.cleaned_data["image"]
        
        # if form data was not valid, re-render page with existing information
        else: 
            return render(request, "auctions/new_listing.html", {
            "form": form
        })

        # log the new listing in Listing model
        # new_listing = Listing(title=title, description=description, image=image, category=category)
        # new_listing.save()


        # TEMP - RETURN FORM INFO
        return render(request, "auctions/temp.html", {
            "title": title,
            "description": description,
            "image": image,
            "category": category
        })

    else:
        return render(request, "auctions/new_listing.html", {
            "form": ListingForm(),
            "categories": Category.objects.all()
        })