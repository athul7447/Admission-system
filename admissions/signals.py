from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal receiver that creates a corresponding UserProfile instance
    whenever a new User is created. If the created User is a superuser,
    assigns the role 'admin' to the UserProfile.
    """

    if created:
        if  instance.is_superuser:
            UserProfile.objects.create(user=instance, role='admin')
