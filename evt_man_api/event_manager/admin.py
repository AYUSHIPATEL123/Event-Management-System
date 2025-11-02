from django.contrib import admin
from .models import UserProfile, Event, RSVP, Review
# Register your models here.

class UserprofileAdmin(admin.ModelAdmin):
    list_display = ('username', 'full_name', 'location')
admin.site.register(UserProfile, UserprofileAdmin)

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'start_time', 'end_time', 'is_public')
    search_fields = ('title', 'organizer__username', 'location')
    list_filter = ('is_public','title','location','organizer')
admin.site.register(Event, EventAdmin)    
class RSVPAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'status')
    search_fields = ('event__title', 'user__username', 'status')
    list_filter = ('status',)    
admin.site.register(RSVP, RSVPAdmin)
    
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'rating')
    search_fields = ('event__title', 'user__username')
    list_filter = ('rating',)
admin.site.register(Review, ReviewAdmin)    