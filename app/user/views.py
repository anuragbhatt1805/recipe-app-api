"""Views for the User interface"""

from rest_framework import generics

from .serializers import UserSerializers


class CreateUserView(generics.CreateAPIView):
    """View for creating a new User"""
    serializer_class = UserSerializers