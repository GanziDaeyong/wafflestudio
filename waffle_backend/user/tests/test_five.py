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
GET /api/v1/seminar/{seminar_id}/
GET /api/v1/seminar/ 
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
                "first_name": "DaeyongTwo",
                "last_name": "JeongTwo",
                "email": "JeongDaeyong2@snu.ac.kr",
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
                "first_name": "DaeyongThree",
                "last_name": "JeongThree",
                "email": "JeongDaeyong3@snu.ac.kr",
                "role": "instructor",
            }),
            content_type='application/json'
        )
        self.instructor_token2 = 'Token ' + Token.objects.get(user__username='InstructorDaeyongDaeyong').key

        response = self.client.post(
            '/api/v1/seminar/',
            json.dumps({
                "name": "backend",
                "capacity": "10",
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
        self.client.delete(
            address,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token2,
        )
        self.client.post(
            address,
            json.dumps({
                "role": "instructor",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token2,
        )

        user_count = User.objects.count()
        self.assertEqual(user_count, 4)
        participant_count = ParticipantsProfile.objects.count()
        self.assertEqual(participant_count, 2)
        instructor_count = InstructorProfile.objects.count()
        self.assertEqual(instructor_count, 2)
        seminar_count = Seminar.objects.count()
        self.assertEqual(seminar_count, 1)
        seminar_check = Seminar.objects.get(id=seminar_id)
        self.assertEqual(seminar_check.name, "backend")
        self.assertEqual(seminar_check.capacity, 10)
        self.assertEqual(seminar_check.count, 5)
        self.assertEqual(seminar_check.time, datetime.time(13, 30))
        self.assertTrue(seminar_check.online)
        seminar_participant_count = UserSeminar.objects.filter(seminar_id=seminar_id).filter(role="participant").count()
        self.assertEqual(seminar_participant_count, 2)
        seminar_instructor_count = UserSeminar.objects.filter(seminar_id=seminar_id).filter(role="instructor").count()
        self.assertEqual(seminar_instructor_count, 2)

    def test_get_seminar_seminarid(self):
        seminar_id = self.seminar_id
        address = '/api/v1/seminar/' + str(seminar_id) + '/'
        response = self.client.get(
            address,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["name"], "backend")
        self.assertEqual(data["capacity"], 10)
        self.assertEqual(data["count"], 5)
        self.assertEqual(data["time"], "13:30:00")
        self.assertEqual(data["online"], True)
        self.assertIsNotNone("participants", data)

        participant = data["participants"][0]
        self.assertEqual(participant["username"], "ParticipantDaeyong")
        self.assertEqual(participant["email"], "JeongDaeyong@snu.ac.kr")
        self.assertEqual(participant["first_name"], "Daeyong")
        self.assertEqual(participant["last_name"], "Jeong")
        self.assertIn("joined_at", participant)
        self.assertEqual(participant["is_active"], True)
        self.assertEqual(participant["dropped_at"], None)

        participant = data["participants"][1]
        self.assertEqual(participant["username"], "ParticipantDaeyongDaeyong")
        self.assertEqual(participant["email"], "JeongDaeyong2@snu.ac.kr")
        self.assertEqual(participant["first_name"], "DaeyongTwo")
        self.assertEqual(participant["last_name"], "JeongTwo")
        self.assertIn("joined_at", participant)
        self.assertEqual(participant["is_active"], False)
        self.assertIsNotNone("dropped_at", participant)

        instructor = data["instructors"][0]
        self.assertIn("id", instructor)
        self.assertEqual(instructor["username"], "InstructorDaeyong")
        self.assertEqual(instructor["email"], "JeongDaeyong@snu.ac.kr")
        self.assertEqual(instructor["first_name"], "Daeyong")
        self.assertEqual(instructor["last_name"], "Jeong")
        self.assertIn("joined_at", instructor)

        instructor = data["instructors"][1]
        self.assertIn("id", instructor)
        self.assertEqual(instructor["username"], "InstructorDaeyongDaeyong")
        self.assertEqual(instructor["email"], "JeongDaeyong3@snu.ac.kr")
        self.assertEqual(instructor["first_name"], "DaeyongThree")
        self.assertEqual(instructor["last_name"], "JeongThree")
        self.assertIn("joined_at", instructor)


##############################################################################################
##############################################################################################
class GetSeminarCase(TestCase):
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
                "first_name": "DaeyongTwo",
                "last_name": "JeongTwo",
                "email": "JeongDaeyong2@snu.ac.kr",
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
                "first_name": "DaeyongThree",
                "last_name": "JeongThree",
                "email": "JeongDaeyong3@snu.ac.kr",
                "role": "instructor",
            }),
            content_type='application/json'
        )
        self.instructor_token2 = 'Token ' + Token.objects.get(user__username='InstructorDaeyongDaeyong').key

        self.client.post(
            '/api/v1/user/',
            json.dumps({
                "username": "InstructorDaeyongDaeyongDaeyong",
                "password": "password",
                "first_name": "DaeyongFour",
                "last_name": "JeongFour",
                "email": "JeongDaeyong4@snu.ac.kr",
                "role": "instructor",
            }),
            content_type='application/json'
        )
        self.instructor_token3 = 'Token ' + Token.objects.get(user__username='InstructorDaeyongDaeyongDaeyong').key

        response = self.client.post(
            '/api/v1/seminar/',
            json.dumps({
                "name": "backend",
                "capacity": "10",
                "count": "5",
                "time": "13:30"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token1
        )
        data = response.json()
        self.backend_seminar_id = data["id"]

        response = self.client.post(
            '/api/v1/seminar/',
            json.dumps({
                "name": "frontend",
                "capacity": "5",
                "count": "7",
                "time": "10:30"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token1
        )
        data = response.json()
        self.frontend_seminar_id = data["id"]

        response = self.client.post(
            '/api/v1/seminar/',
            json.dumps({
                "name": "android",
                "capacity": "15",
                "count": "5",
                "time": "15:30"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token2
        )
        data = response.json()
        self.android_seminar_id = data["id"]

        id = self.backend_seminar_id
        address = '/api/v1/seminar/' + str(id) + '/user/'
        self.client.post(
            address,
            json.dumps({
                "role": "participant",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token1,
        )
        self.client.delete(
            address,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token1
        )
        self.client.post(
            address,
            json.dumps({
                "role": "participant",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token2,
        )
        self.client.post(
            address,
            json.dumps({
                "role": "instructor",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token3,
        )

        id = self.frontend_seminar_id
        address = '/api/v1/seminar/' + str(id) + '/user/'
        self.client.post(
            address,
            json.dumps({
                "role": "participant",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token1,
        )
        id = self.android_seminar_id
        address = '/api/v1/seminar/' + str(id) + '/user/'
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

        user_count = User.objects.count()
        self.assertEqual(user_count, 5)
        participant_count = ParticipantsProfile.objects.count()
        self.assertEqual(participant_count, 2)
        instructor_count = InstructorProfile.objects.count()
        self.assertEqual(instructor_count, 3)
        seminar_count = Seminar.objects.count()
        self.assertEqual(seminar_count, 3)
        backend_seminar_check = Seminar.objects.get(id=self.backend_seminar_id)
        self.assertEqual(backend_seminar_check.name, "backend")
        backend_seminar_user_count = UserSeminar.objects.filter(seminar_id=self.backend_seminar_id).count()
        self.assertEqual(backend_seminar_user_count, 4)
        frontend_seminar_check = Seminar.objects.get(id=self.frontend_seminar_id)
        self.assertEqual(frontend_seminar_check.name, "frontend")
        frontend_seminar_user_count = UserSeminar.objects.filter(seminar_id=self.frontend_seminar_id).count()
        self.assertEqual(frontend_seminar_user_count, 2)
        android_seminar_check = Seminar.objects.get(id=self.android_seminar_id)
        self.assertEqual(android_seminar_check.name, "android")
        android_seminar_user_count = UserSeminar.objects.filter(seminar_id=self.android_seminar_id).count()
        self.assertEqual(android_seminar_user_count, 3)

        # 백엔드(진행자 2 참여자 1(원래 2였다가 하나 드랍))
        # 프론트엔드(진행자 1 참여자 1)
        # 안드로이드(진행자 1 참여자 2)

    def test_get_seminar(self):
        address = '/api/v1/seminar/'
        response = self.client.get(
            address,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(len(data), 3)  # 세미나 다 들어있는지 수 확인

        for seminar in data:
            if seminar["name"] == "android":
                android = seminar
            if seminar["name"] == "frontend":
                frontend = seminar
            if seminar["name"] == "backend":
                backend = seminar

        # backend
        self.assertIn("id", backend)
        self.assertEqual(backend["name"], "backend")
        self.assertEqual(backend["participant_count"], 1)  # 드랍자 한명 미포함
        instructor = backend["instructors"]
        self.assertEqual(len(instructor), 2)  # 다 들어있는지 수 확인
        for user in instructor:
            if user["username"] == "InstructorDaeyong":
                instructor1 = user
            if user["username"] == "InstructorDaeyongDaeyongDaeyong":
                instructor2 = user
        self.assertIn("id", instructor1)
        self.assertEqual(instructor1["username"], "InstructorDaeyong")
        self.assertEqual(instructor1["email"], "JeongDaeyong@snu.ac.kr")
        self.assertEqual(instructor1["first_name"], "Daeyong")
        self.assertEqual(instructor1["last_name"], "Jeong")
        self.assertIn("joined_at", instructor1)

        self.assertIn("id", instructor2)
        self.assertEqual(instructor2["username"], "InstructorDaeyongDaeyongDaeyong")
        self.assertEqual(instructor2["email"], "JeongDaeyong4@snu.ac.kr")
        self.assertEqual(instructor2["first_name"], "DaeyongFour")
        self.assertEqual(instructor2["last_name"], "JeongFour")
        self.assertIn("joined_at", instructor2)

        # frontend
        self.assertIn("id", frontend)
        self.assertEqual(frontend["name"], "frontend")
        self.assertEqual(frontend["participant_count"], 1)
        instructor = frontend["instructors"]
        self.assertEqual(len(instructor), 1)  # 다 들어있는지 수 확인
        instructor = instructor[0]  # 한명이니까 바로 인덱스로 호출
        self.assertIn("id", instructor)
        self.assertEqual(instructor["username"], "InstructorDaeyong")
        self.assertEqual(instructor["email"], "JeongDaeyong@snu.ac.kr")
        self.assertEqual(instructor["first_name"], "Daeyong")
        self.assertEqual(instructor["last_name"], "Jeong")
        self.assertIn("joined_at", instructor)

        # android
        self.assertIn("id", android)
        self.assertEqual(android["name"], "android")
        self.assertEqual(android["participant_count"], 2)
        instructor = android["instructors"]
        self.assertEqual(len(instructor), 1)  # 다 들어있는지 수 확인
        instructor = instructor[0]  # 한명이니까 바로 인덱스로 호출
        self.assertIn("id", instructor)
        self.assertEqual(instructor["username"], "InstructorDaeyongDaeyong")
        self.assertEqual(instructor["email"], "JeongDaeyong3@snu.ac.kr")
        self.assertEqual(instructor["first_name"], "DaeyongThree")
        self.assertEqual(instructor["last_name"], "JeongThree")
        self.assertIn("joined_at", instructor)
