from django.contrib import admin
from .models import Event, Attendee

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'start_time', 'end_time', 'max_capacity', 'attendee_count']
    list_filter = ['start_time', 'location']
    search_fields = ['name', 'location']
    readonly_fields = ['created_at', 'updated_at', 'attendee_count']
    
    def attendee_count(self, obj):
        return obj.attendees.count()
    attendee_count.short_description = 'Registered Attendees'

@admin.register(Attendee)
class AttendeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'event', 'registered_at']
    list_filter = ['registered_at', 'event']
    search_fields = ['name', 'email', 'event__name']
    readonly_fields = ['registered_at']
