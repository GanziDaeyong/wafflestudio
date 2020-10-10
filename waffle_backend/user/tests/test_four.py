from django.contrib.auth.models import User
from django.test import Client, TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
import json

from seminar.serializers import InstructorProfile, ParticipantsProfile
from seminar.serializers import Seminar
import datetime
from seminar.relation_models import UserSeminar
"""
PUT /api/v1/seminar/{seminar_id}/
"""

class PUTSeminarSeminarIdCase(TestCase):
    client = Client()

    def setUp(self):
        self.client.post(
            '/api/v1/user/',
            json.dumps({
                "username": "ParticipantDaeyong",
                "password": "password",
                "first_name": "Daeyong",
                "last_name": "Jeong",
                "email": "JeongDaeyong@snu.ac.kr",
                "role": "participant",
            }),
            content_type='application/json'
        )
        self.participant_token1 = 'Token ' + Token.objects.get(user__username='ParticipantDaeyong').key

        self.client.post(
            '/api/v1/user/',
            json.dumps({
                "username": "ParticipantDaeyongDaeyong",
                "password": "password",
                "first_name": "Daeyong",
                "last_name": "Jeong",
                "email": "JeongDaeyong@snu.ac.kr",
                "role": "participant",
            }),
            content_type='application/json'
        )
        self.participant_token2 = 'Token ' + Token.objects.get(user__username='ParticipantDaeyongDaeyong').key

        self.client.post(
            '/api/v1/user/',
            json.dumps({
                "username": "InstructorDaeyong",
                "password": "password",
                "first_name": "Daeyong",
                "last_name": "Jeong",
                "email": "JeongDaeyong@snu.ac.kr",
                "role": "instructor",
            }),
            content_type='application/json'
        )
        self.instructor_token1 = 'Token ' + Token.objects.get(user__username='InstructorDaeyong').key

        self.client.post(
            '/api/v1/user/',
            json.dumps({
                "username": "InstructorDaeyongDaeyong",
                "password": "password",
                "first_name": "Daeyong",
                "last_name": "Jeong",
                "email": "JeongDaeyong@snu.ac.kr",
                "role": "instructor",
            }),
            content_type='application/json'
        )
        self.instructor_token2 = 'Token ' + Token.objects.get(user__username='InstructorDaeyongDaeyong').key

        response = self.client.post(
            '/api/v1/seminar/',
            json.dumps({
                "name": "backend",
                "capacity": "2",
                "count": "5",
                "time": "13:30"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token1
        )
        data = response.json()
        self.seminar_id = data["id"]

        seminar_id = self.seminar_id
        address = '/api/v1/seminar/' + str(seminar_id) + '/user/'
        self.client.post(
            address,
            json.dumps({
                "role": "participant",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token1,
        )
        self.client.post(
            address,
            json.dumps({
                "role": "participant",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token2,
        )
        # 기본 setup 체크
        user_count = User.objects.count()
        self.assertEqual(user_count, 4)
        participant_count = ParticipantsProfile.objects.count()
        self.assertEqual(participant_count, 2)
        instructor_count = InstructorProfile.objects.count()
        self.assertEqual(instructor_count, 2)
        seminar_count = Seminar.objects.count()
        self.assertEqual(seminar_count, 1)

    def test_put_seminar_seminarid_if_participant(self):  # 참여자가 바꾸려는 경우
        seminar_id = self.seminar_id
        address = '/api/v1/seminar/' + str(seminar_id) + '/'
        response = self.client.put(
            address,
            json.dumps({
                "name": "android",
                "capacity": "50",
                "count": "5",
                "time": "18:30",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token1,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_seminar_seminarid_if_not_charging(self):  # 담당이 아닌 진행자가 바꾸려는 경우
        seminar_id = self.seminar_id
        address = '/api/v1/seminar/' + str(seminar_id) + '/'
        response = self.client.put(
            address,
            json.dumps({
                "name": "android",
                "capacity": "50",
                "count": "5",
                "time": "18:30",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token2,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_seminar_seminarid_if_time_wrong(self):  # 바꾸려는 시간 양식이 잘못된 경우
        seminar_id = self.seminar_id
        address = '/api/v1/seminar/' + str(seminar_id) + '/'
        response = self.client.put(
            address,
            json.dumps({
                "name": "android",
                "capacity": "50",
                "count": "5",
                "time": "183:0",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token1,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_seminar_seminarid_if_name_wrong(self):  # 바꾸려는 이름이 잘못된 경우
        seminar_id = self.seminar_id
        address = '/api/v1/seminar/' + str(seminar_id) + '/'
        response = self.client.put(
            address,
            json.dumps({
                "name": "",
                "capacity": "50",
                "count": "5",
                "time": "18:30",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token1,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_seminar_seminarid_if_capacity_less_than_participants(self):  # 참여자 수보다 capacity가 적은 경우
        seminar_id = self.seminar_id
        address = '/api/v1/seminar/' + str(seminar_id) + '/'
        response = self.client.put(
            address,
            json.dumps({
                "name": "backend",
                "capacity": "1",
                "count": "5",
                "time": "18:30",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token1,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_seminar_seminarid_success(self):
        seminar_id = self.seminar_id
        address = '/api/v1/seminar/' + str(seminar_id) + '/'
        response = self.client.put(
            address,
            json.dumps({
                "name": "BackendIsFun",
                "capacity": "10",
                "count": "10",
                "time": "20:45",
                "online": "false",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token1,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        seminar_check = Seminar.objects.get(id=seminar_id)
        self.assertEqual(seminar_check.name, "BackendIsFun")
        self.assertEqual(seminar_check.capacity, 10)
        self.assertEqual(seminar_check.count, 10)
        self.assertEqual(seminar_check.time, datetime.time(20, 45))
        self.assertFalse(seminar_check.online)

        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["name"], "BackendIsFun")
        self.assertEqual(data["capacity"], 10)
        self.assertEqual(data["count"], 10)
        self.assertEqual(data["time"], "20:45:00")
        self.assertFalse(data["online"])
        self.assertGreaterEqual(len(data["participants"]), 2)  # setup에서 두명 가입했음

        instructor = data["instructors"][0]
        self.assertIsNotNone(instructor)
        self.assertIn("id", instructor)
        self.assertEqual(instructor["username"], "InstructorDaeyong")
        self.assertEqual(instructor["email"], "JeongDaeyong@snu.ac.kr")
        self.assertEqual(instructor["first_name"], "Daeyong")
        self.assertEqual(instructor["last_name"], "Jeong")
        self.assertIn("joined_at", instructor)
