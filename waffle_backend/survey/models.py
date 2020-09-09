from django.db import models
from django.contrib.auth.models import User

class OperatingSystem(models.Model):
    name = models.CharField(max_length=50, db_index=True)
    description = models.CharField(max_length=200, blank=True)
    price = models.PositiveIntegerField(null=True)


class SurveyResult(models.Model):
    EXPERIENCE_DEGREE = (
        (1, 'very low'),
        (2, 'low'),
        (3, 'middle'),
        (4, 'high'),
        (5, 'very_high'),
    )
    # 정수 값들은 null=True로, 문자 값들은 blank=True로 설정한다.
    os = models.ForeignKey(OperatingSystem, null=True, related_name='surveys', on_delete=models.SET_NULL)
    #user을 외래키를 이용하여 User과 연결해준다.
    user = models.ForeignKey(User, null=True, related_name='surveys', on_delete=models.SET_NULL)
    python = models.PositiveSmallIntegerField(choices=EXPERIENCE_DEGREE)
    rdb = models.PositiveSmallIntegerField(choices=EXPERIENCE_DEGREE)
    programming = models.PositiveSmallIntegerField(choices=EXPERIENCE_DEGREE)
    major = models.CharField(max_length=100, blank=True)
    grade = models.CharField(max_length=20, blank=True)
    backend_reason = models.CharField(max_length=500, blank=True)
    waffle_reason = models.CharField(max_length=500, blank=True)
    say_something = models.CharField(max_length=500, blank=True)
    # 추가되는 시점의 시간을 삽입한다.
    timestamp = models.DateTimeField(auto_now_add=True)
