from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import  (
    AuditLog, OfferLetter, OfferLetterDoument
)
from .serializers import (
    OfferLetterSerializer, OfferLetterListSerializer,UserSerializer
)
from django.contrib.auth.models import User
from .decorators import consultant_only
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .langchain_agent import agent_executor
from utility.queue_jobs import send_offer_letter_email
from langchain.document_loaders import PyPDFLoader
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import HuggingFaceHub
import json
from django.conf import settings    
import fitz


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

    @consultant_only
    def post(self, request):
        user_id = request.data.get("user_id")
        file = request.FILES.get("file")
        

        if not user_id:
            return Response(
                {
                    "error": "user_id is required."
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

        user = User.objects.filter(id=user_id).first()
        
        if not user:
            return Response(
                {
                    "error": "User does not exist."
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )

        role = user.userprofile.role
        if role != 'student':
            return Response({
                "status" : False,
                "message": "Only students can receive an offer letter.",
            }, status=status.HTTP_400_BAD_REQUEST)



        errors = []
        created_count = 0
        with transaction.atomic():
            
            document = OfferLetterDoument.objects.create(document=file)
            
            attachment_path = document.document.path 

            data = {
                "document": document.id,
                "user" : request.user.id,
                "student": user.id
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
                
                # Send offer letter email
                subject = "Offer Letter from Our Institution"
                message = "Please find your offer letter attached."
                
                #CELERY is not working on my system
                send_offer_letter_email(
                    student_email=user.email,
                    subject=subject,
                    message=message,
                    attachment_path=attachment_path
                )
                
                created_count += 1
            else:
                return Response(
                    {
                        "status": False, 
                        "message": serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "status": True,
            "message": f"Offer letters created successfully."
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
            result = agent_executor.run(input=query)
            return Response({"response": result})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FetchStudents(APIView):
    
    # permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        
        users = User.objects.filter(userprofile__role='student').select_related('userprofile')
        serializer = UserSerializer(users, many=True)
        return Response(
            {
                "status": True,
                "message": "Success",
                "data": serializer.data
            }
        )
        
    
class FetchDataFromDocument(APIView):

    def get(self, request):
        document_id = request.GET.get("document_id")
        document = OfferLetterDoument.objects.filter(id=document_id).first()

        if not document:
            return Response({
                "status": False,
                "message": "Document not found",
            })

        # Step 1: Extract form fields from first page using PyMuPDF
        try:
            doc = fitz.open(document.document.path)
            first_page = doc[0]
            field_data = {}

            for widget in first_page.widgets():
                if widget.field_name and widget.field_value:
                    field_data[widget.field_name.strip()] = widget.field_value.strip()

            doc.close()

            # Convert form fields to plain text for LLM
            formatted_text = "\n".join([f"{key}: {value}" for key, value in field_data.items()])
        except Exception as e:
            return Response({
                "status": False,
                "message": f"Failed to read PDF form fields: {str(e)}"
            })

        # Step 2: Set up LangChain
        llm = HuggingFaceHub(
            repo_id="HuggingFaceH4/zephyr-7b-beta",
            huggingfacehub_api_token=settings.HUGGING_FACE_TOKENS,
            model_kwargs={"temperature": 0.3, "max_length": 256}
        )

        prompt_template = PromptTemplate(
            input_variables=["text"],
            template="""
            You are a helpful assistant. Extract the following details from the form data:

            - Student Name (from "Your Name")
            - Course Name (from "Program Name 2")
            - Offer Date (from "Text Field 5", format should be YYYY-MM-DD)

            Text:
            {text}

            Return the result strictly in JSON format:
            {{
            "student_name": "John Doe",
            "course": "BBA",
            "offer_date": "2023-09-01"
            }}
            give me this json only and nothing else
            """
        )

        chain = LLMChain(llm=llm, prompt=prompt_template)

        # Step 3: Run LLM and respond
        try:
            response = chain.run(text=formatted_text)
            data = json.loads(response)
            return Response({
                "status": True,
                "data": data
            })
        except Exception as e:
            return Response({
                "status": False,
                "message": f"LLM parsing failed: {str(e)}",
                "raw_response": response if 'response' in locals() else None
            })