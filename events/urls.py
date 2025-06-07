from django.urls import path
from .views import (
    EventListCreateView, 
    register_attendee, 
    event_attendees,
    event_with_timezone
)

app_name = 'events'

urlpatterns = [
    path('events/', EventListCreateView.as_view(), name='event-list-create'),
    path('events/<int:event_id>/register/', register_attendee, name='register-attendee'),
    path('events/<int:event_id>/attendees/', event_attendees, name='event-attendees'),
    path('events/<int:event_id>/timezone/', event_with_timezone, name='event-timezone'),
]
