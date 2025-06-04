from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("consultant", "Consultant"),
        ("team_lead", "Team Lead"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
class OfferLetterDoument(models.Model):
    document = models.FileField(upload_to='offer_letters/')

class OfferLetter(models.Model):
    STATUS_CHOICES = [
        ("sent", "Sent"),
        ("signed", "Signed"),
        ("escalated", "Escalated"),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offer_letters')
    consultant = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_offers')
    document = models.ForeignKey(OfferLetterDoument, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    sent_at = models.DateTimeField(auto_now_add=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    escalated = models.BooleanField(default=False)

    def __str__(self):
        return f"Offer for {self.student.username}"

class AuditLog(models.Model):
    offer_letter = models.ForeignKey(OfferLetter, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.action} at {self.timestamp}"
