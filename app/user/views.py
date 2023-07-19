"""Views for the User interface"""

from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from .serializers import (
    UserSerializers,
    AuthTokenSerializer,
)


class CreateUserView(generics.CreateAPIView):
    """View for creating a new User"""
    serializer_class = UserSerializers


class CreateTokenView(ObtainAuthToken):
    """View for creating a new Auth Token"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """View for managing the authenticated user"""
    serializer_class = UserSerializers
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrieve and return the authenticated user"""
        return self.request.user
