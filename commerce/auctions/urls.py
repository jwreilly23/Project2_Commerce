from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new-listing", views.new_listing, name="new_listing"),
    path("listing-<str:listing_title>-<int:listing_id>", views.listing_page, name="listing_page"),
    path("watchlist-<str:username>", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("category-<str:category_name>", views.category_listing, name="category_listing")
]
