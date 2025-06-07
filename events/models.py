from django.db import models
from django.core.validators import MinValueValidator, EmailValidator
from django.utils import timezone
from django.core.exceptions import ValidationError

class Event(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=300)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    max_capacity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'events'
        ordering = ['start_time']

    def __str__(self):
        return f"{self.name} - {self.location}"

    def clean(self):
        """Custom validation for model fields"""
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError("Start time must be before end time")
            
            if self.start_time <= timezone.now():
                raise ValidationError("Start time must be in the future")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_upcoming(self):
        """Check if event is upcoming"""
        return self.start_time > timezone.now()

    @property
    def attendee_count(self):
        """Get current number of registered attendees"""
        return self.attendees.count()

    @property
    def available_slots(self):
        """Get number of available slots"""
        return self.max_capacity - self.attendee_count

    @property
    def is_full(self):
        """Check if event is at max capacity"""
        return self.attendee_count >= self.max_capacity


class Attendee(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendees')
    name = models.CharField(max_length=100)
    email = models.EmailField(validators=[EmailValidator()])
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'attendees'
        unique_together = ('event', 'email')
        ordering = ['registered_at']

    def __str__(self):
        return f"{self.name} - {self.event.name}"

    def clean(self):
        """Custom validation for attendee registration"""
        if self.event and self.event.is_full:
            raise ValidationError("Event is at maximum capacity")