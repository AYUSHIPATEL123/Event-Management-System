from django.shortcuts import render ,redirect
from .serializers import RegisterSerializer, LoginSerializer,EventSerializer,ReviewSerializer,RSVPSerializer
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import AllowAny , IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile, Event, Review, RSVP,blog,Pizza, Souse, Topping , SpecialPizza
from .permissions import IsOwner, IsPublicEvent
from .forms import UserForm, BlogForm
from django.contrib.auth.decorators import login_required
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
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
class BlogListView(LoginRequiredMixin,UserPassesTestMixin,ListView):
    def test_func(self):
        return self.request.user.email.endswith('@gmail.com')
    # model = blog
    # queryset = blog.objects.filter(title="3")
    # queryset = blog.objects.order_by('-id')
    # queryset = blog.objects.raw('SELECT * FROM event_manager_blog where id = 10')
    # queryset = blog.objects.filter(id=3)|blog.objects.filter(id=10)
    # queryset = blog.objects.filter(id__in=[3,17])
    l = [3,17,18,19]
    queryset = blog.objects.in_bulk([3,17,18])
    # queryset = blog.objects.filter(id__in=l)
    # queryset = blog.objects.exclude(id__in=l)
    # queryset = blog.objects.bulk_create([blog(title="#",description="########"),blog(title = "@",description="@@@"),blog(title="$",description="$$$$"),blog(title="%",description="%%%%%%%%")])
    # queryset = blog.objects.bulk_update([blog(id =19 ,title="#",description="#___#####"),blog(id=20,title = "@",description="@______@@")],fields=['title','description'])
    
    template_name = 'blog_list.html'
    context_object_name = 'blog_list'
    

class BlogDetailsView(DetailView):
    # model = blog
    # queryset = blog.objects.all()
    template_name = 'blog_detail.html'
    # context_object_name = 'data'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blog_list'] = blog.objects.get(id=self.kwargs['pk'])
        return context
    def get_object(self, queryset=None):
        return blog.objects.get(id=self.kwargs['pk'])

class BlogCreateView(CreateView):
    model = blog
    template_name = 'blog_post.html'
    fields = ['title', 'description']
    success_url = reverse_lazy('blog_list')

    

class BlogUpdateView(UpdateView):
    # model = blog
    template_name = 'blog_update.html'
    fields = '__all__'
    def get_success_url(self):
        return reverse_lazy('blog_update', kwargs={'pk': self.object.pk}) 
    def get_queryset(self):
        return blog.objects.all() 
    

class BlogDeleteView(DeleteView):
    model = blog
    template_name ='blog_delete.html'

    def get_success_url(self):
        return reverse_lazy('blog_list')
from django.db.models import F
import math
from django.db.models import Count

@login_required
def pizza(request):
    if not request.user.has_perm('event_manager.view_pizza'):
        raise PermissionError("you don't have the permission to view this pizzas")
    # pizza = Pizza.objects.get(name="Veg Pizz")
    # print(pizza.name)
    # print(Pizza.objects.all().values_list('name',flat=True))

    # all
    # q = Pizza.objects.all()
    # Souse(name="thin crust pizz").save(using='backup')
    # s = Souse.objects.get(id = 1)
    # Pizza(name="thin crust pizza",souse=s).save(using='backup')
    # q= Pizza.objects.using('backup').get(id=12)
    # filter
    # q = Pizza.objects.filter(souse__name = "veg souce").dates('date', 'month')

    # exclude
    # q = Pizza.objects.exclude(date__year__lt=2025).exclude(souse__name="veg souce")
    # q = Pizza.objects.annotate(totle_price=F('regular_price')+F('special_price'),loss=F('regular_price')-F('special_price'),loss_percent=((F('regular_price')-F('special_price'))/F('regular_price')*100)).order_by('-loss_percent')
    # print(q.values_list('totle_price',flat=True))
    # print(q.values_list('name',flat=True))
    # print(q.values('name','totle_price'))
    # q= Pizza.objects.annotate(count= Count('toppings')).filter(count__gt=5)
    # print(q.values('toppings__name','count'))
    # q= Pizza.objects.order_by('-regular_price').reverse()
    # q1 = Pizza.objects.values('toppings__name').filter(name="veg pizza")
    # q2 = Topping.objects.values('name')
    # q= q1.union(q2)
    # q = q1.intersection(q2)
    # q= q1.difference(q2)
    # q = Pizza.objects.select_related('blog').get(id=5)
    # q = q.blog.description
    # q  = Pizza.objects.prefetch_related('toppings')
    # q = q.all()[0:2]
    # q = Pizza.objects.extra(select={'totle_price': 'regular_price+special_price'},order_by=['-totle_price'])
    # q = Pizza.objects.extra(where=['special_price < regular_price'])
    # q = Pizza.objects.prefetch_related().filter(name="veg pizza").defer('toppings')
    # print(q.values_list('totle_price',flat=True))
    # q= Pizza.objects.raw
    # q  = Pizza.objects.earliest('date')
    # q = Pizza.objects.filter(souse__name = "veg souce") & Pizza.objects.filter(souse__name = "simple souse")
    # q = Pizza.objects.filter(souse__name = "veg souce") ^ Pizza.objects.filter(souse__name = "simple souse")
    
    # q = Pizza.souse_objects.all()
    # q = Pizza.souse_objects.filter(name="veg pizza")
    # q = Pizza.souse_objects.get(name="veg pizza")

    # q = Pizza.piz.veg_pizzas()
    # q = Pizza.piz.simple_pizzas().filter(regular_price__gt=100,special_price__lt=299)
    # q = Pizza.piz.thin_crust_pizzas().order_by('-regular_price')[:2]
    # q = Pizza.piz.indi_pizzas()
    q = SpecialPizza.objects.veg_pizzas()
    q = SpecialPizza.objects.simple_pizzas()
    return render(request,'pizza.html',{'pizza': q})       
@login_required(redirect_field_name = 'pizza')
def form_prc(request):
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            # print(form.cleaned_data['password'])
            # print(form.cleaned_data['first_name'])
            # print(form.cleaned_data['last_name'])
            # print(form.cleaned_data['username'])
            print(form.cleaned_data.get('title'))
            print(form.cleaned_data.get('description'))
            print("your form is valid.....")
            redirect('blog_list')
        else:
            print("your form is not valid.....")      
    else:
        form = BlogForm()
    context = {'form':form }                 
    return render(request,'forms.html',context)