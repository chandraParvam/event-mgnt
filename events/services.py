from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Event, Attendee
from .exceptions import EventCapacityExceeded, DuplicateRegistration, EventNotFound

class EventService:
    """Service class for event-related business logic"""

    @staticmethod
    def create_event(event_data):
        """Create a new event with validation"""
        try:
            with transaction.atomic():
                event = Event.objects.create(**event_data)
                return event
        except ValidationError as e:
            raise ValidationError(f"Event creation failed: {str(e)}")

    @staticmethod
    def get_upcoming_events():
        """Get all upcoming events"""
        return Event.objects.filter(start_time__gt=timezone.now())

    @staticmethod
    def get_event_by_id(event_id):
        """Get event by ID or raise exception"""
        try:
            return Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            raise EventNotFound(f"Event with ID {event_id} not found")

    @staticmethod
    def register_attendee(event_id, attendee_data):
        """Register an attendee for an event"""
        try:
            with transaction.atomic():
                event = EventService.get_event_by_id(event_id)
                
                # Check if event is at capacity
                if event.is_full:
                    raise EventCapacityExceeded("Event is at maximum capacity")
                
                # Check for duplicate registration
                email = attendee_data.get('email')
                if Attendee.objects.filter(event=event, email=email).exists():
                    raise DuplicateRegistration("This email is already registered for this event")
                
                # Create attendee
                attendee = Attendee.objects.create(event=event, **attendee_data)
                return attendee
                
        except (EventCapacityExceeded, DuplicateRegistration):
            raise
        except Exception as e:
            raise ValidationError(f"Registration failed: {str(e)}")

    @staticmethod
    def get_event_attendees(event_id, page_size=20, page_number=1):
        """Get paginated list of attendees for an event"""
        event = EventService.get_event_by_id(event_id)
        attendees = event.attendees.all()
        
        # Simple pagination
        start_index = (page_number - 1) * page_size
        end_index = start_index + page_size
        
        return {
            'attendees': attendees[start_index:end_index],
            'total_count': attendees.count(),
            'page': page_number,
            'page_size': page_size,
            'total_pages': (attendees.count() + page_size - 1) // page_size
        }


class TimezoneService:
    """Service for handling timezone conversions"""
    
    @staticmethod
    def convert_event_times(event, target_timezone):
        """Convert event times to target timezone"""
        import pytz
        
        target_tz = pytz.timezone(target_timezone)
        
        return {
            'start_time': event.start_time.astimezone(target_tz),
            'end_time': event.end_time.astimezone(target_tz)
        }