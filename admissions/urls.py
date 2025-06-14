from django.urls import path
from .views import *

app_name = 'admissions_'

urlpatterns = [
    path('send-offer-letter', SendOfferLetterView.as_view(), name= app_name + 'login'),
    path('langchain-query', LangChainQueryView.as_view(), name='langchain_query'),
    path('users', FetchStudents.as_view(), name='users'),
    path('lagchain/user/data', FetchDataFromDocument.as_view(), name='users'),
]