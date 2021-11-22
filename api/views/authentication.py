from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from api.serializers import LoginSerializer, UserSerializer, TokenSerializer


class AuthenticationViewSet(viewsets.ViewSet):

    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            token, is_created = Token.objects.get_or_create(user=serializer.save())
            serializer = TokenSerializer(instance=token)
            return Response(
                data={
                    'message': 'Login successful',
                    'data': serializer.data,
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
