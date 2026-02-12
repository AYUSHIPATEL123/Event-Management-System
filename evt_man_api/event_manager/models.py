from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
# Create your models here.

class UserProfile(AbstractUser):
    full_name = models.CharField("person's full name : ",max_length=100)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.full_name


class Event(models.Model):
    organizer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='organized_events')
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class RSVP(models.Model):

    GOING = 'going'
    MAYBE = 'maybe'
    NOT_GOING = 'not going'

    STATUS_CHOICES = [
        (GOING, 'Going'),
        (MAYBE, 'Maybe'),
        (NOT_GOING, 'Not Going'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvps')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='rsvps')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
   

    class Meta:
        unique_together = ('event', 'user')  # prevent duplicate RSVPs

    def __str__(self):
        return f"{self.user.username} - {self.event.title} ({self.status})"



class Review(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()  # e.g., 1–5 stars
    comment = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('event', 'user')  # one review per event per user


    def __str__(self):
        return f"Review by {self.user.username} for {self.event.title}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.rating < 1 or self.rating > 5:
            raise ValidationError('Rating must be between 1 and 5.'
                                  )
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
class Post(models.Model):
    mapping = models.ForeignKey(Event,on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title   

class blog(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class comment(models.Model):
   
    name = models.CharField(max_length=50)
    comment = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    project_id = models.PositiveIntegerField()

    content_object =GenericForeignKey('content_type','project_id')
    
    def __str__(self):
        return self.name        

class Topping(models.Model):
    name = models.CharField(max_length=100)
    class Meta:
        ordering = ['-name']
        verbose_name_plural = 'toppig'
        
    def __str__(self):
        return self.name
    
class Souse(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name 

# class Souse_Manager(models.Manager):
#     def get_queryset(self):
#         return super().get_queryset().filter(souse__name ="veg souce")

class PizzaQuerySet(models.QuerySet):
    def veg(self):
        return self.filter(souse__name = "veg souce")
    
    def simple(self):
        return self.filter(souse__name = "simple souse")
    
    def indi(self):
        return self.filter(souse__name = "indi_tund_souce")

    def thin_crust(self):
        return self.filter(souse__name = "thin crust souce") 

class PizzaManager(models.Manager):
    def get_queryset(self):
        return PizzaQuerySet(self.model,using=self._db)

    def veg_pizzas(self):
        return self.get_queryset().veg()
    
    def simple_pizzas(self):
        return self.get_queryset().simple()

    def indi_pizzas(self):
        return self.get_queryset().indi()

    def thin_crust_pizzas(self):
        return self.get_queryset().thin_crust()
           
class Pizza(models.Model):
    name = models.CharField(max_length=100)
    toppings = models.ManyToManyField(Topping)
    blog = models.ForeignKey(blog,on_delete=models.CASCADE,null=True,blank=True)
    souse = models.OneToOneField(Souse,on_delete=models.CASCADE,null=True,blank=True)
    date = models.DateField(auto_now_add=True,blank=True)
    regular_price = models.DecimalField(max_digits=5, decimal_places=2,blank=True,null=True)
    special_price = models.DecimalField(max_digits=5, decimal_places=2, blank=True , null=True)
    
    # objects = models.Manager()
    # souse_objects = Souse_Manager()
    piz = PizzaManager()
    class Meta:
    #     order_with_respect_to = 'souse'
    #     get_latest_by = 'name'
    #     default_permissions = ('change','view')
    #     default_manager_name = 'objects'
        abstract = True
    #     verbose_name = 'Pizza_'
    #     verbose_name_plural = 'pizzas__'
    #     db_table = 'pizzas****'
    def __str__(self):
        return self.name

class SpecialPizza(Pizza):
    objects = PizzaManager()

    