from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from api.serializers import LoginSerializer, UserSerializer, TokenSerializer, OrganizationSerializer


class AuthenticationViewSet(viewsets.ViewSet):

    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, is_created = Token.objects.get_or_create(user=user)
            serializer = TokenSerializer(instance=token)
            organization_data = None
            if user.organization:
                organization_data = OrganizationSerializer(instance=user.organization).data
            return Response(
                data={
                    'message': 'Login successful',
                    'data': serializer.data,
                    'organization': organization_data,
                    'success': True
                }
            )
        return Response(
            status=400,
            data={
                'message': 'Login Failed',
                'success': False,
                'data': serializer.errors
            }
        )

    def user(self, request):
        if not request.user.is_authenticated:
            return Response(
                data={
                    'mess age': 'User not authenticated',
                    'success': False,
                    'data': None
                },
                status=403
            )
        serializer = UserSerializer(request.user)
        return Response(
            data={
                'message': 'User fetch successful',
                'success': True,
                'data': serializer.data
            }
        )


login = AuthenticationViewSet.as_view({'post': 'login'})
user = AuthenticationViewSet.as_view({'get': 'user'})
