from django.shortcuts import render
from .serializers import RegisterSerializer, LoginSerializer,EventSerializer,ReviewSerializer,RSVPSerializer
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import AllowAny , IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile, Event, Review, RSVP
from .permissions import IsOwner, IsPublicEvent

# Create your views here.

class RegisterView(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    queryset = UserProfile.objects.all()

class LoginView(APIView):
    permission_classes = [AllowAny]
    # serializer_class = LoginSerializer
    
    def post(self, request):
        data = request.data
        # serializer = self.serializer_class(data=data)
        serializer = LoginSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
        if user:
            token = RefreshToken.for_user(user)
            Refresh_Token = str(token)
            Access_Token = str(token.access_token)
            return Response({
                'data': serializer.data,
                'refresh': Refresh_Token,
                'access': Access_Token
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)    
            
class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.all()
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        if self.action == 'list':
            return Event.objects.filter(is_public=True)
        return Event.objects.filter(organizer=self.request.user)

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        if event_id:
            return Review.objects.filter(event__id=event_id)
        return Review.objects.all()
    
    def create(self, request, *args, **kwargs):
        event_id = self.kwargs.get('event_id', None)
        data = request.data.copy()
        data['user'] = request.user.id
        data['event'] = event_id
        if Review.objects.filter(event_id=event_id, user=data['user']).exists():
            return Response(
                {"error": "You have already reviewed this event."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
class RSVPViewSet(viewsets.ModelViewSet):
    serializer_class = RSVPSerializer
    queryset = RSVP.objects.all()
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        event_id = self.kwargs.get('event_id')
        data = request.data.copy()
        data['user'] = request.user.id
        data['event'] = event_id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def partial_update(self, request, *args, **kwargs):
        event_id = self.kwargs.get('event_id')
        user_id = self.kwargs.get('user_id')
        try:
            rsvp = RSVP.objects.get(event_id=event_id, user_id=user_id)
        except RSVP.DoesNotExist:
            return Response({"error": "RSVP not found"}, status=status.HTTP_404_NOT_FOUND)
        if request.user.id != user_id:
            return Response({"error": "You can only update your own RSVP."}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(rsvp, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)   
        
