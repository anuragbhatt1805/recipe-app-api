"""URL Mapping for the User API"""

from django.urls import path, include
from . import views

app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
]