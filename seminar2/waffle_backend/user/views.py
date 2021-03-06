from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from user.serializers import UserSerializer


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated(),)

    def get_permissions(self):
        if self.action in ('create', 'login'):
            return (AllowAny(),)
        return self.permission_classes

    def create(self, request):

        serializer_profile = UserSerializer
        serializer_profile.validate_for_profile(request.user, request.data, if_update=0)  # 프로필 생성을 위한 데이터들이 validate한지 체크

        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            user = serializer.save()
        except IntegrityError:
            return Response({"error": "A user with that username already exists."}, status=status.HTTP_400_BAD_REQUEST)

        login(request, user)

        data = serializer.data
        data['token'] = user.auth_token.key
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
            return Response(data)

        return Response({"error": "Wrong username or wrong password"}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=False, methods=['POST'])
    def logout(self, request):
        logout(request)
        return Response()

    def retrieve(self, request, pk=None):
        user = request.user if pk == 'me' else self.get_object()
        return Response(self.get_serializer(user).data)

    def update(self, request, pk=None):
        if pk != 'me':
            return Response({"error": "Can't update other Users information"}, status=status.HTTP_403_FORBIDDEN)

        user = request.user

        serializer_profile = UserSerializer
        serializer_profile.validate_for_profile(request.user, request.data, if_update=1)  # 유저의 프로필정보 변경을 위한 validation check

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)  # 유저의 기본정보 변경을 위한 validation check
        serializer.update(serializer.validated_data)
        return Response(serializer.data)


#POST /api/v1/user/participant/
    @action(detail=False, methods=['POST'])
    def participant(self, request):
        user = request.user
        serializer = UserSerializer
        serializer.validate_for_profile(user, request.data, if_update=1)
        serializer.new_role(user, request)
        return Response(self.get_serializer(user).data, status=status.HTTP_201_CREATED)