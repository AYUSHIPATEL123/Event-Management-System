from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile


@receiver(post_save,sender = UserProfile)
def create_user_profile(sender,created,instance,**kwargs):
    if created:
        print("new user has been created.........")
    else:
        print("user has been updated.........")    