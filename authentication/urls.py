from django.urls import path
from .views import *

app_name = 'authentication_'

urlpatterns = [
    path('login', LoginView.as_view(), name= app_name + 'login')
]