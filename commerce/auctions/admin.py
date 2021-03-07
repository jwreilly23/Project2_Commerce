from django.contrib import admin

from .models import User, Category, Listing, Watchlist, Bid, Comment


# Register your models here.
class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "open_status", "category")


class BidAdmin(admin.ModelAdmin):
    list_display = ("listing", "bidder", "amount")


class CommentAdmin(admin.ModelAdmin):
    list_display = ("listing", "poster", "body", "post_date")


class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "date_joined", "is_superuser")


class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("user", "listing")


admin.site.register(User, UserAdmin)
admin.site.register(Category)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Watchlist, WatchlistAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
