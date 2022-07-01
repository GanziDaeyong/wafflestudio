from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from user.serializers import UserSerializer


class UserViewSet(viewsets.GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    # POST /api/v1/user/
    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('firstName')
        last_name = request.data.get('lastName')
        print(first_name)
        print(last_name)

        if not username or not email or not password:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if (first_name and not last_name) or (not first_name and last_name):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # 위에서 둘 중 하나만 입력된 경우를 걸렀으니, if문의 else는 자연스레 둘 다 입력되지 않은 경우이다.
        if first_name and last_name:
            if not first_name.isalpha() or not last_name.isalpha():
                return Response(status=status.HTTP_400_BAD_REQUEST)

        else:
            first_name = ""
            last_name = ""

        try:
            # Django 내부에 기본으로 정의된 User에 대해서는 create가 아닌 create_user를 사용
            # password가 자동으로 암호화되어 저장됨. database를 직접 조회해도 알 수 없는 형태로 저장됨.
            user = User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name)

        except IntegrityError:  # 중복된 username
            return Response(status=status.HTTP_409_CONFLICT)

        # 가입했으니 바로 로그인 시켜주기
        login(request, user)
        # login을 하면 Response의 Cookies에 csrftoken이 발급됨
        # 이후 요청을 보낼 때 이 csrftoken을 Headers의 X-CSRFToken의 값으로 사용해야 POST, PUT 등의 method 사용 가능
        return Response(self.get_serializer(user).data, status=status.HTTP_201_CREATED)

    # PUT /api/v1/user/login/
    @action(detail=False, methods=['PUT'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # authenticate라는 함수는 username, password가 올바르면 해당 user를, 그렇지 않으면 None을 return
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            # login을 하면 Response의 Cookies에 csrftoken이 발급됨 (반복 로그인 시 매번 값이 달라짐)
            # 이후 요청을 보낼 때 이 csrftoken을 Headers의 X-CSRFToken의 값으로 사용해야 POST, PUT 등의 method 사용 가능
            return Response(self.get_serializer(user).data)
        # 존재하지 않는 사용자이거나 비밀번호가 틀린 경우
        return Response(status=status.HTTP_403_FORBIDDEN)

    # PUT /api/v1/user/

    def put(self, request):
        #로그인하지 않았으면 403
        if not(request.user.is_authenticated):
            return Response(status=status.HTTP_403_FORBIDDEN)

        user = request.user

        newusername = request.data.get('newusername')
        newfirstname = request.data.get('newfirstname')
        newlastname = request.data.get('newlastname')

        # 변경 안되는 경우 2) 성, 이름 중에 하나만 입력한 경우.
        if (newfirstname and not newlastname) or (not newfirstname and newlastname):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # 변경 안되는 경우 3) 성, 이름에 숫자가 포함된 경우
        # 문제 없으면 갱신.
        if newfirstname and newlastname:
            if not newfirstname.isalpha() or not newlastname.isalpha():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            user.first_name = newfirstname
            user.last_name = newlastname

        # username 변경하기
        if newusername:
            # 아래 정의한 is_it_overlap 함수 이용해서 중복체크하기

            if self.is_it_overlap(newusername):
                # 중복이면 409 리스폰스를 리턴
                return Response(status=status.HTTP_409_CONFLICT)
            # 아니면 username 변경.
            user.username = newusername

        # 최종 저장 - lazy evaluation 개념 살펴보기.
        user.save()

        return Response(self.get_serializer(user).data, status=status.HTTP_200_OK)

    # 중복이면 True, 아니면 False를 리턴하는 함수
    # (위에서처럼 Integrity error 을 예외처리하는 게 더 옳겠지만(세미나 장 님께서 그렇게 하셨으니..) 공부 겸 새로운 함수를 만들어보았습니다.)
    def is_it_overlap(request, newusername):
        try:
            # newusername인자가 username으로 쓰이는 객체가 User.objects에 있는지 찾는다.
            user = User.objects.get(username=newusername)
        except:
            # User.objects에서 그러한 user가 없을 경우 except으로 빠진다.
            user = None
        if user:
            return True

        return False

    # 로그아웃 만들기
    @action(detail=False, methods=['GET'])
    def logout(self, request):
        if request.user.is_authenticated:
            logout(request)
            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_403_FORBIDDEN)

    # 유저 정보 확인하기 - 함수명은 디폴트로 존재하는 list를 사용했습니다.
    def list(self, request):
        if request.user.is_authenticated:
            user = request.user
            return Response(self.get_serializer(user).data)

        return Response(status=status.HTTP_403_FORBIDDEN)