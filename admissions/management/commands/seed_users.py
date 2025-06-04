# admissions/management/commands/seed_users.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from admissions.models import UserProfile

class Command(BaseCommand):
    help = 'Seed test users with roles'

    def handle(self, *args, **kwargs):
        """
        Create test users with roles if they don't exist already.
        
        Seeds the following users:
        - student1
        - student2
        - consultant1
        - consultant2
        - teamlead1
        """

        users_data = [
            {"username": "student1", "email": "student1@example.com", "role": "student"},
            {"username": "student2", "email": "student2@example.com", "role": "student"},
            {"username": "consultant1", "email": "consultant1@example.com", "role": "consultant"},
            {"username": "consultant2", "email": "consultant2@example.com", "role": "consultant"},
            {"username": "teamlead1", "email": "teamlead1@example.com", "role": "team_lead"},
        ]

        for data in users_data:
            if not User.objects.filter(username=data["username"]).exists():
                user = User.objects.create_user(
                    username=data["username"],
                    email=data["email"],
                    password="Test@1234"
                )
                UserProfile.objects.create(user=user, role=data["role"])
                self.stdout.write(self.style.SUCCESS(f"Created {data['username']} with role {data['role']}"))
            else:
                self.stdout.write(f"{data['username']} already exists. Skipping.")

        self.stdout.write(self.style.SUCCESS("Test users seeded successfully"))