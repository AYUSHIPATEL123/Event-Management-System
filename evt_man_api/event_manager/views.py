from django.shortcuts import render ,redirect
from .serializers import RegisterSerializer, LoginSerializer,EventSerializer,ReviewSerializer,RSVPSerializer
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import AllowAny , IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile, Event, Review, RSVP,blog
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
        
from django.views.generic import ListView , CreateView , UpdateView, DeleteView ,DetailView
from django.urls import reverse_lazy
# class BlogListView(ListView):
#     model = blog
#     template_name = 'blog.html'
#     success_url = reverse_lazy('blog_list')
#     feilds = '__all__'

# class BlogCreateView(CreateView):
#     model = blog
#     template_name = 'blog_create.html'
#     fields = ['title', 'description']
#     success_url = reverse_lazy('blog_create')

from django.views import View

class BlogListView(View):
    def get(self,request,id=None):
        if id:
            data = blog.objects.get(id=id)
        else:
            data = blog.objects.all()
        return render(request, 'blog.html', {'data': data})
        return render(request,'blog.html',{'data':data})
    
    def post(self,request,id=None):
        method = request.POST.get("_method", "").upper()
        if method == 'PUT':
            id = int(request.POST.get('id'))
            print(id)
            title = request.POST.get('title')
            description = request.POST.get('description')
            blog.objects.filter(id=id).update(title=title,description=description)
            return redirect('blog')
        elif method =='PATCH':
            id = int(request.POST.get('id'))
            feilds={}
            if request.POST.get('title'):
                title = request.POST.get('title')
                feilds['title'] = title
            if request.POST.get('description'):
                description = request.POST.get('description')
                feilds['description'] = description
            blog.objects.filter(id=id).update(**feilds)
            return redirect('blog')
        elif method == 'DELETE':
            id = int(request.POST.get('id'))
            blog.objects.filter(id=id).delete()
            return redirect('blog')
        title = request.POST.get('title')
        description = request.POST.get('description')
        blog.objects.create(title=title,description=description)
        return redirect('blog')
        

from django.views.generic import ListView , UpdateView ,DeleteView , DetailView

class BlogListView(ListView):
    model = blog
    template_name = 'blog_list.html'
    context_object_name = 'blog_list'

class BlogDetailsView(DetailView):
    model = blog
    template_name = 'blog_detail.html'
    context_object_name = 'data'

class BlogCreateView(CreateView):
    model = blog
    template_name = 'blog_post.html'
    fields = ['title', 'description']
    success_url = reverse_lazy('blog_list')
        