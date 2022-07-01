from django.contrib.auth.models import User
from django.db import models
from seminar.seminar_models import Seminar

class ParticipantsProfile(models.Model):
    user = models.ForeignKey(User, related_name='participants', unique=True, null=True, on_delete=models.CASCADE)
    #참여자 프로필과 일대일 관계를 unique=True를 통해 구현
    university = models.CharField(max_length=20, blank=True)
    accepted = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    seminar = models.ForeignKey(Seminar, related_name='participants_seminar', null=True, on_delete=models.CASCADE)

class InstructorProfile(models.Model):
    user = models.ForeignKey(User, related_name='instructor', unique=True, null=True, on_delete=models.CASCADE)
    company = models.CharField(max_length=20, blank=True)
    year = models.PositiveIntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    seminar = models.ForeignKey(Seminar, related_name='instructor_seminar', null=True, on_delete=models.CASCADE)

