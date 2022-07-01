from seminar.seminar_models import Seminar
from django.db import models
from django.contrib.auth.models import User

class UserSeminar(models.Model): # 맵핑테이블을 만들어 다대다 관계를 구현

    seminar = models.ForeignKey(Seminar, on_delete=models.CASCADE) # ForeignKey를 이용한 관계 구현. (+ .CASCADE() 이용)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True) # 생성 시점
    updated_at = models.DateTimeField(auto_now=True) # 수정 시점
    joined_at = models.DateTimeField(auto_now_add=True, null=True) # 유저가 세미나 등록하는 시점
    dropped_at = models.DateTimeField(null=True) # 유저가 포기하는 시점
    role = models.CharField(max_length=20, blank=True) # role을 따로 넣어주어 이후 쉽게 분류할 수 있도록 한다.
    is_active = models.BooleanField(default=True) # 유효한지 판단