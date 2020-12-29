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
GET /api/v1/user/me/
GET /api/v1/user/id/
"""


class GetUserMeCase(TestCase):
    client = Client()

    def setUp(self):
        response = self.client.post(
            '/api/v1/user/',
            json.dumps({
                "username": "ParticipantDaeyong",
                "password": "password",
                "first_name": "Daeyong",
                "last_name": "Jeong",
                "email": "JeongDaeyong@snu.ac.kr",
                "role": "participant",
                "university": "Kaist",
            }),
            content_type='application/json'
        )
        self.participant_token1 = 'Token ' + Token.objects.get(user__username='ParticipantDaeyong').key
        data = response.json()
        self.part_id = data["id"]

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

        response=self.client.post(
            '/api/v1/user/',
            json.dumps({
                "username": "InstructorDaeyongDaeyong",
                "password": "password",
                "first_name": "DaeyongThree",
                "last_name": "JeongThree",
                "email": "JeongDaeyong3@snu.ac.kr",
                "role": "instructor",
                "company": "waffleStudio",
                "year": "3",
            }),
            content_type='application/json'
        )
        self.instructor_token2 = 'Token ' + Token.objects.get(user__username='InstructorDaeyongDaeyong').key
        data = response.json()
        self.inst_id = data["id"]

        self.client.post(
            '/api/v1/user/participant/',
            json.dumps({
                "university": "Yonsei"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token2
        )

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

        response=self.client.post(
            '/api/v1/seminar/',
            json.dumps({
                "name": "frontend",
                "capacity": "10",
                "count": "5",
                "time": "15:30"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token2
        )
        data=response.json()
        self.frontend_id=data["id"]

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
            HTTP_AUTHORIZATION=self.participant_token1,
        )
        self.client.post(
            address,
            json.dumps({
                "role": "participant",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token2,
        )

        user_count = User.objects.count()
        self.assertEqual(user_count, 4)
        participant_count = ParticipantsProfile.objects.count()
        self.assertEqual(participant_count, 3)  # 진행자 한명이 참여자 프로필 만들어서 2+1
        instructor_count = InstructorProfile.objects.count()
        self.assertEqual(instructor_count, 2)
        seminar_count = Seminar.objects.count()
        self.assertEqual(seminar_count, 2)

        part_check = ParticipantsProfile.objects.get(user_id=self.part_id)
        self.assertEqual(part_check.university, "Kaist")
        profile_compare_to_above = User.objects.get(id=self.part_id)
        seminar_compare_to_above = UserSeminar.objects.filter(seminar_id=self.backend_seminar_id).get(
            user_id=self.part_id).user
        self.assertEqual(part_check.user, profile_compare_to_above)
        self.assertEqual(part_check.user, seminar_compare_to_above)
        inst_check = InstructorProfile.objects.get(user_id=self.inst_id)
        self.assertEqual(inst_check.company, "waffleStudio")

        profile_compare_to_above = User.objects.get(id=self.inst_id)
        seminar_compare_to_above = UserSeminar.objects.filter(seminar_id=self.frontend_id).get(
            user_id=self.inst_id).user
        self.assertEqual(inst_check.user, profile_compare_to_above)
        self.assertEqual(inst_check.user, seminar_compare_to_above)


    ##############################################################################

    def test_get_user_me_participant(self):
        address = '/api/v1/user/me/'
        response = self.client.get(
            address,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token1,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertIn("id", data)
        self.assertEqual(data["username"], "ParticipantDaeyong")
        self.assertEqual(data["email"], "JeongDaeyong@snu.ac.kr")
        self.assertEqual(data["first_name"], "Daeyong")
        self.assertEqual(data["last_name"], "Jeong")
        self.assertIn("last_login", data)
        self.assertIn("date_joined", data)

        participant = data["participant"]
        self.assertIsNotNone(participant)
        self.assertIn("id", participant)
        self.assertEqual(participant["university"], "Kaist")
        self.assertTrue(participant["accepted"])
        self.assertEqual(len(participant["seminars"]), 1)
        self.assertIsNone(data["instructor"])
        seminar = participant["seminars"][0]
        self.assertEqual(seminar["name"], "backend")
        self.assertFalse(seminar["is_active"])
        self.assertIn("id", seminar)
        self.assertIn("joined_at", seminar)
        self.assertIn("dropped_at", seminar)

    def test_get_user_me_instructor(self):
        address = '/api/v1/user/me/'
        response = self.client.get(
            address,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token2,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertIn("id", data)
        self.assertEqual(data["username"], "InstructorDaeyongDaeyong")
        self.assertEqual(data["email"], "JeongDaeyong3@snu.ac.kr")
        self.assertEqual(data["first_name"], "DaeyongThree")
        self.assertEqual(data["last_name"], "JeongThree")
        self.assertIn("last_login", data)
        self.assertIn("date_joined", data)

        participant = data["participant"]
        self.assertIsNotNone(participant)
        self.assertIn("id", participant)
        self.assertEqual(participant["university"], "Yonsei")
        self.assertTrue(participant["accepted"])
        self.assertEqual(len(participant["seminars"]), 1)

        seminar = participant["seminars"][0]
        self.assertIn("id", seminar)
        self.assertIn("joined_at", seminar)
        self.assertTrue(seminar["is_active"])
        self.assertIsNone(seminar["dropped_at"])
        self.assertEqual(seminar["name"], "backend")

        instructor = data["instructor"]
        self.assertIsNotNone(instructor)
        self.assertIn("id", instructor)
        self.assertEqual(instructor["company"], "waffleStudio")
        self.assertEqual(instructor["year"], 3)

        self.assertEqual(len(instructor["charge"]), 1)
        charge = instructor["charge"][0]
        self.assertIn("id", charge)
        self.assertIn("joined_at", charge)
        self.assertEqual(charge["name"], "frontend")


#######################################################################################
#######################################################################################

class GetUserIdCase(TestCase):
    client = Client()

    def setUp(self):
        response = self.client.post(
            '/api/v1/user/',
            json.dumps({
                "username": "ParticipantDaeyong",
                "password": "password",
                "first_name": "Daeyong",
                "last_name": "Jeong",
                "email": "JeongDaeyong@snu.ac.kr",
                "role": "participant",
                "university": "Kaist",
            }),
            content_type='application/json'
        )
        self.participant_token1 = 'Token ' + Token.objects.get(user__username='ParticipantDaeyong').key
        data = response.json()
        self.participant_id = data["id"]

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

        response = self.client.post(
            '/api/v1/user/',
            json.dumps({
                "username": "InstructorDaeyongDaeyong",
                "password": "password",
                "first_name": "DaeyongThree",
                "last_name": "JeongThree",
                "email": "JeongDaeyong3@snu.ac.kr",
                "role": "instructor",
                "company": "waffleStudio",
                "year": "3",
            }),
            content_type='application/json'
        )
        self.instructor_token2 = 'Token ' + Token.objects.get(user__username='InstructorDaeyongDaeyong').key
        data = response.json()
        self.instructor_id = data["id"]

        self.client.post(
            '/api/v1/user/participant/',
            json.dumps({
                "university": "Yonsei"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token2
        )

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

        response=self.client.post(
            '/api/v1/seminar/',
            json.dumps({
                "name": "frontend",
                "capacity": "10",
                "count": "5",
                "time": "15:30"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token2
        )
        data=response.json()
        self.frontend_id = data["id"]

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
            HTTP_AUTHORIZATION=self.participant_token1,
        )
        self.client.post(
            address,
            json.dumps({
                "role": "participant",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token2,
        )

        user_count = User.objects.count()
        self.assertEqual(user_count, 4)
        participant_count = ParticipantsProfile.objects.count()
        self.assertEqual(participant_count, 3)  # 진행자 한명이 참여자 프로필 만들어서 2+1
        instructor_count = InstructorProfile.objects.count()
        self.assertEqual(instructor_count, 2)
        seminar_count = Seminar.objects.count()
        self.assertEqual(seminar_count, 2)

        part_check = ParticipantsProfile.objects.get(user_id=self.participant_id)
        self.assertEqual(part_check.university, "Kaist")
        profile_compare_to_above = User.objects.get(id=self.participant_id)
        seminar_compare_to_above = UserSeminar.objects.filter(seminar_id=self.backend_seminar_id).get(
            user_id=self.participant_id).user
        self.assertEqual(part_check.user, profile_compare_to_above)
        self.assertEqual(part_check.user, seminar_compare_to_above)
        inst_check = InstructorProfile.objects.get(user_id=self.instructor_id)
        self.assertEqual(inst_check.company, "waffleStudio")

        profile_compare_to_above = User.objects.get(id=self.instructor_id)
        seminar_compare_to_above = UserSeminar.objects.filter(seminar_id=self.frontend_id).get(
            user_id=self.instructor_id).user
        self.assertEqual(inst_check.user, profile_compare_to_above)
        self.assertEqual(inst_check.user, seminar_compare_to_above)

    ##############################################################################

    def test_get_user_me_participant_id(self):
        id = self.participant_id
        address = '/api/v1/user/' + str(id) + "/"
        response = self.client.get(
            address,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token1,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertIn("id", data)
        self.assertEqual(data["username"], "ParticipantDaeyong")
        self.assertEqual(data["email"], "JeongDaeyong@snu.ac.kr")
        self.assertEqual(data["first_name"], "Daeyong")
        self.assertEqual(data["last_name"], "Jeong")
        self.assertIn("last_login", data)
        self.assertIn("date_joined", data)

        participant = data["participant"]
        self.assertIsNotNone(participant)
        self.assertIn("id", participant)
        self.assertEqual(participant["university"], "Kaist")
        self.assertTrue(participant["accepted"])
        self.assertEqual(len(participant["seminars"]), 1)
        self.assertIsNone(data["instructor"])
        seminar = participant["seminars"][0]
        self.assertEqual(seminar["name"], "backend")
        self.assertFalse(seminar["is_active"])
        self.assertIn("id", seminar)
        self.assertIn("joined_at", seminar)
        self.assertIn("dropped_at", seminar)

    def test_get_user_me_instructor_id(self):
        id = self.instructor_id
        address = '/api/v1/user/' + str(id) + "/"
        response = self.client.get(
            address,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token2,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertIn("id", data)
        self.assertEqual(data["username"], "InstructorDaeyongDaeyong")
        self.assertEqual(data["email"], "JeongDaeyong3@snu.ac.kr")
        self.assertEqual(data["first_name"], "DaeyongThree")
        self.assertEqual(data["last_name"], "JeongThree")
        self.assertIn("last_login", data)
        self.assertIn("date_joined", data)

        participant = data["participant"]
        self.assertIsNotNone(participant)
        self.assertIn("id", participant)
        self.assertEqual(participant["university"], "Yonsei")
        self.assertTrue(participant["accepted"])
        self.assertEqual(len(participant["seminars"]), 1)

        seminar = participant["seminars"][0]
        self.assertIn("id", seminar)
        self.assertIn("joined_at", seminar)
        self.assertTrue(seminar["is_active"])
        self.assertIsNone(seminar["dropped_at"])
        self.assertEqual(seminar["name"], "backend")

        instructor = data["instructor"]
        self.assertIsNotNone(instructor)
        self.assertIn("id", instructor)
        self.assertEqual(instructor["company"], "waffleStudio")
        self.assertEqual(instructor["year"], 3)

        self.assertEqual(len(instructor["charge"]), 1)
        charge = instructor["charge"][0]
        self.assertIn("id", charge)
        self.assertIn("joined_at", charge)
        self.assertEqual(charge["name"], "frontend")
