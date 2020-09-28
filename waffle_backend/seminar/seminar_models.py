from django.contrib.auth.models import User
from django.db import models

class Seminar(models.Model):
    name = models.CharField(max_length=20, blank=True)
    capacity = models.PositiveIntegerField(null=True)
    count = models.PositiveIntegerField(null=True)
    time = models.TimeField(null=True)
    online = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True) # 생성 시점 저장하는 created_at 필드 생성.
    updated_at = models.DateTimeField(auto_now=True)  # 업데이트 시점 저장하는 updated_at 필드생성.
    user = models.ForeignKey(User, related_name='seminar_user', null=True, on_delete=models.CASCADE)


