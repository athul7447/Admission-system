from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import  (
    AuditLog, UserProfile, OfferLetter, OfferLetterDoument
)
from .serializers import OfferLetterSerializer, OfferLetterListSerializer
from django.contrib.auth.models import User
from .decorators import check_superadmin_and_roles
import ast
import os
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .langchain_agent import agent


class SendOfferLetterView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        page = request.query_params.get("page", 1)
        size = request.query_params.get("size", 10)
        
        offer_letters = OfferLetter.objects.all().order_by("-sent_at")
        paginator = Paginator(offer_letters, size)

        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        serializer = OfferLetterListSerializer(page_obj, many=True)
        return Response(
                {
                    "status": True,
                    "message": "Success",
                    "data": serializer.data, 
                    "total_pages": paginator.num_pages
                }
            )

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
                role = user.userprofile.role

                data = {
                    "document": document.id,
                    "user" : user.id
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
        
    
class LangChainQueryView(APIView):
    def get(self, request):
        """
        Run a query on the LangChain agent.

        Args:
            query (str): The query to run on the agent.

        Returns:
            Response: A response object containing the result of the query.

        Raises:
            400: If the query is not provided.
            500: If there is an internal server error.
        """
        
        query = request.GET.get("query")
        if not query:
            return Response({"error": "Query is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            result = agent.run(query)
            return Response({"response": result})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)