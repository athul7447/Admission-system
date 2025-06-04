from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import  (
    AuditLog, UserProfile, OfferLetter, OfferLetterDoument
)
from .serializers import OfferLetterSerializer
from django.contrib.auth.models import User
from .decorators import check_superadmin_and_roles
import ast
import os
from django.db import transaction
from django.core.files.storage import default_storage



class SendOfferLetterView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user_ids = request.data.get("user_ids", [])
        print(user_ids, type(user_ids))
        file = request.FILES.get("file")
        
        if user_ids and isinstance(user_ids, str):
            user_ids = ast.literal_eval(user_ids)

        if not isinstance(user_ids, list) or not user_ids:
            return Response(
                {
                    "error": "user_ids must be a non-empty list."
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )
        if not file:
            return Response(
                {
                    "error": "File is required."
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )

        users = User.objects.filter(id__in=user_ids).select_related('userprofile')
        user_map = {user.id: user for user in users}

        invalid_users = []
        valid_users = []

        for uid in user_ids:
            user = user_map.get(uid)
            if not user:
                invalid_users.append({"id": uid, "error": "User not found"})
                continue
            try:
                profile = user.userprofile
                if profile.role not in ["student", "consultant"]:
                    invalid_users.append({"id": uid, "role": profile.role})
                else:
                    valid_users.append(user)
            except UserProfile.DoesNotExist:
                invalid_users.append({"id": uid, "error": "UserProfile not found"})

        if invalid_users:
            return Response({
                "error": "Some users have invalid roles or missing data.",
                "details": invalid_users
            }, status=status.HTTP_400_BAD_REQUEST)

        errors = []
        created_count = 0
        with transaction.atomic():
            
            document = OfferLetterDoument.objects.create(document=file)

            for user in valid_users:
                data = {
                    "student": user.id,
                    "consultant": request.user.id,
                    "document": document.id,
                }
                
                # Validate and save the offer letter
                serializer = OfferLetterSerializer(data=data)
                
                if serializer.is_valid():
                    serializer.save()
                    # Create audit log for each successful creation
                    AuditLog.objects.create(
                        user=request.user,
                        action="Sent Offer Letter",
                        offer_letter=serializer.instance
                    )
                    created_count += 1
                else:
                    # Add errors to the response
                    errors.append({"user_id": user.id, "errors": serializer.errors})
        if errors:
            return Response({
                "message": f"Offer letters sent to {created_count} users.",
                "errors": errors
            }, status=status.HTTP_207_MULTI_STATUS)  # Multi-status for partial success

        return Response({
            "message": f"Offer letters successfully sent to {created_count} users."
        }, status=status.HTTP_201_CREATED)