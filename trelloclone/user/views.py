from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from user.models import UserProfile
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from django.db import IntegrityError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from user.serializers import UserSerializer

class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ('create', 'login'):
            return (AllowAny(),)
        return super(UserViewSet, self).get_permissions()

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.save()
        except IntegrityError:
            return Response({"error": "A user with that username already exists."}, status=status.HTTP_400_BAD_REQUEST)

        login(request, user)
        data = serializer.data
        data['token'] = user.auth_token.key
        type = request.data.get('access_type')
        UserProfile.objects.create(user=user, access_type=type)

        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['PUT'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            data = self.get_serializer(user).data
            token, created = Token.objects.get_or_create(user=user)
            data['token'] = token.key
            print(user.is_authenticated)
            return Response(data)

        return Response({"error": "Wrong username or wrong password"}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=False, methods=['PUT'])
    def logout(self, request):
        logout(request)
        return Response()

    def retrieve(self, request, pk=None):
        user = request.user
        return Response(self.get_serializer(user).data)

    def update(self, request, pk=None):
        if pk != 'me':
            return Response({"error": "No permission to other's info"}, status=status.HTTP_403_FORBIDDEN)

        user = request.user
        data = request.data
        serializer = self.get_serializer(user, data=data, partial=True)
        serializer.update(user, serializer.date)
        return Response(serializer.data)
