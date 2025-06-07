from django.core.exceptions import ValidationError
from django.utils import timezone
import re

def validate_future_datetime(value):
    """Validate that datetime is in the future"""
    if value <= timezone.now():
        raise ValidationError("Date and time must be in the future")

def validate_email_format(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError("Invalid email format")

def validate_capacity(value):
    """Validate event capacity"""
    if value < 1:
        raise ValidationError("Capacity must be at least 1")
    if value > 10000:
        raise ValidationError("Capacity cannot exceed 10,000")

def validate_event_times(start_time, end_time):
    """Validate event start and end times"""
    if start_time >= end_time:
        raise ValidationError("Start time must be before end time")
    
    # Check if event duration is reasonable (not more than 7 days)
    duration = end_time - start_time
    if duration.days > 7:
        raise ValidationError("Event duration cannot exceed 7 days")
