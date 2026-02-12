from django.contrib import admin
from django.urls import path , include
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'register', views.RegisterView, basename='register')
router.register(r'events', views.EventViewSet, basename='events')
# router.register(r'reviews', views.ReviewViewSet, basename='reviews')
# router.register(r'rsvps', views.RSVPViewSet, basename='rsvps')
# router.register(r'login', views.LoginView, basename='login')

urlpatterns = [
    # path('', views.register, name='register'),
    path('', include(router.urls)),
    path('login/', views.LoginView.as_view(), name='login'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('events/<int:event_id>/rsvp/', views.RSVPViewSet.as_view({'post': 'create'}), name='event-rsvp'),
    path('events/<int:event_id>/rsvp/<int:user_id>/', views.RSVPViewSet.as_view({'patch': 'partial_update'}), name='update-rsvp'),
    path('events/<int:event_id>/reviews/', views.ReviewViewSet.as_view({'get': 'list', 'post': 'create'}), name='event-reviews'),
    path('blog/',views.BlogListView.as_view(),name='blog'),
    path('blog/<int:pk>/',views.BlogListView.as_view(),name='blog_detail'),
    path('blog_list/',views.BlogListView.as_view(),name='blog_list'),
    path('blog_detail/<int:pk>/',views.BlogDetailsView.as_view(),name='blog_detail'),
    path('blog_create/',views.BlogCreateView.as_view(),name='blog_create'),
    path('blog_update/<int:pk>/',views.BlogUpdateView.as_view(),name='blog_update'),
    path('blog_delete/<int:pk>/',views.BlogDeleteView.as_view(),name='blog_delete'),
    path('pizza/',views.pizza,name='pizza'),
    path('user/',views.form_prc,name='user'),
]