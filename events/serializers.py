from rest_framework import serializers
from django.utils import timezone
from .models import Event, Attendee

class EventSerializer(serializers.ModelSerializer):
    attendee_count = serializers.ReadOnlyField()
    available_slots = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = [
            'id', 'name', 'location', 'start_time', 'end_time',
            'max_capacity', 'attendee_count', 'available_slots',
            'is_full', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_start_time(self, value):
        """Validate that start time is in the future"""
        if value <= timezone.now():
            raise serializers.ValidationError("Start time must be in the future")
        return value

    def validate(self, data):
        """Cross-field validation"""
        if data.get('start_time') and data.get('end_time'):
            if data['start_time'] >= data['end_time']:
                raise serializers.ValidationError("Start time must be before end time")
        return data


class AttendeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendee
        fields = ['id', 'name', 'email', 'registered_at']
        read_only_fields = ['id', 'registered_at']

    def validate_email(self, value):
        """Validate email format and uniqueness for the event"""
        event_id = self.context.get('event_id')
        if event_id:
            if Attendee.objects.filter(event_id=event_id, email=value).exists():
                raise serializers.ValidationError("This email is already registered for this event")
        return value


class AttendeeRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendee
        fields = ['name', 'email']

    def validate_email(self, value):
        """Validate email format"""
        return value

    def create(self, validated_data):
        """Create attendee with event from context"""
        event = self.context['event']
        return Attendee.objects.create(event=event, **validated_data)


class EventListSerializer(serializers.ModelSerializer):
    """Simplified serializer for event listing"""
    attendee_count = serializers.ReadOnlyField()
    available_slots = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = [
            'id', 'name', 'location', 'start_time', 'end_time',
            'max_capacity', 'attendee_count', 'available_slots'
        ]