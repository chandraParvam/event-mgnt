from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Event, Attendee
from .serializers import (
    EventSerializer, AttendeeSerializer, 
    AttendeeRegistrationSerializer, EventListSerializer
)
from .services import EventService, TimezoneService
from .exceptions import EventCapacityExceeded, DuplicateRegistration, EventNotFound

@extend_schema_view(
    post=extend_schema(
        summary="Create a new event",
        description="Create a new event with name, location, start_time, end_time, and max_capacity",
        tags=["Events"]
    ),
    get=extend_schema(
        summary="List all upcoming events",
        description="Get a list of all upcoming events",
        tags=["Events"]
    )
)
class EventListCreateView(generics.ListCreateAPIView):
    """
    List all upcoming events or create a new event
    """
    serializer_class = EventSerializer
    
    def get_queryset(self):
        return EventService.get_upcoming_events()
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return EventListSerializer
        return EventSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                event = EventService.create_event(serializer.validated_data)
                response_serializer = EventSerializer(event)
                return Response(
                    response_serializer.data, 
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {'error': str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Register attendee for event",
    description="Register a new attendee for a specific event",
    tags=["Attendees"]
)
@api_view(['POST'])
def register_attendee(request, event_id):
    """
    Register an attendee for a specific event
    """
    serializer = AttendeeRegistrationSerializer(
        data=request.data,
        context={'event_id': event_id}
    )
    
    if serializer.is_valid():
        try:
            attendee = EventService.register_attendee(
                event_id, 
                serializer.validated_data
            )
            response_serializer = AttendeeSerializer(attendee)
            return Response(
                {
                    'message': 'Registration successful',
                    'attendee': response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        except EventNotFound:
            return Response(
                {'error': 'Event not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except EventCapacityExceeded:
            return Response(
                {'error': 'Event is at maximum capacity'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except DuplicateRegistration:
            return Response(
                {'error': 'This email is already registered for this event'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Get event attendees",
    description="Get all registered attendees for a specific event with pagination",
    tags=["Attendees"]
)
@api_view(['GET'])
def event_attendees(request, event_id):
    """
    Get all attendees for a specific event with pagination
    """
    try:
        page_size = int(request.GET.get('page_size', 20))
        page_number = int(request.GET.get('page', 1))
        
        result = EventService.get_event_attendees(
            event_id, 
            page_size=page_size, 
            page_number=page_number
        )
        
        serializer = AttendeeSerializer(result['attendees'], many=True)
        
        return Response({
            'attendees': serializer.data,
            'pagination': {
                'current_page': result['page'],
                'page_size': result['page_size'],
                'total_pages': result['total_pages'],
                'total_count': result['total_count']
            }
        })
        
    except EventNotFound:
        return Response(
            {'error': 'Event not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(
    summary="Get event with timezone conversion",
    description="Get event details with times converted to specified timezone",
    tags=["Events"]
)
@api_view(['GET'])
def event_with_timezone(request, event_id):
    """
    Get event with timezone conversion
    """
    try:
        event = EventService.get_event_by_id(event_id)
        timezone_param = request.GET.get('timezone', 'Asia/Kolkata')
        
        converted_times = TimezoneService.convert_event_times(
            event, 
            timezone_param
        )
        
        serializer = EventSerializer(event)
        data = serializer.data
        data.update(converted_times)
        
        return Response(data)
        
    except EventNotFound:
        return Response(
            {'error': 'Event not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
