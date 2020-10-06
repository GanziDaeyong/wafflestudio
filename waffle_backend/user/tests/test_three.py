from django.test import Client, TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
import json

"""
POST /api/v1/seminar/{seminar_id}/user/
DELETE /api/v1/seminar/{seminar_id}/user/
"""


class POSTSeminarSeminarIdUserCase(TestCase):
    client = Client()

    def setUp(self):
        response=self.client.post(
            '/api/v1/user/',
            json.dumps({
                "username": "ParticipantDaeyong",
                "password": "password",
                "first_name": "Daeyong",
                "last_name": "Jeong",
                "email": "JeongDaeyong@snu.ac.kr",
                "role": "participant",
                "university": "서울대학교"
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
                "first_name": "Daeyong",
                "last_name": "Jeong",
                "email": "JeongDaeyong@snu.ac.kr",
                "role": "participant",
                "university": "서울대학교",
                "accepted": "False",
            }),
            content_type='application/json'
        )

        self.participant_token2 = 'Token ' + Token.objects.get(user__username='ParticipantDaeyongDaeyong').key


        self.client.post(
            '/api/v1/user/',
            json.dumps({
                "username": "ParticipantDaeyongDaeyongDaeyong",
                "password": "password",
                "first_name": "Daeyong",
                "last_name": "Jeong",
                "email": "JeongDaeyong@snu.ac.kr",
                "role": "participant",
                "university": "서울대학교",
            }),
            content_type='application/json'
        )

        self.participant_token3 = 'Token ' + Token.objects.get(user__username='ParticipantDaeyongDaeyongDaeyong').key

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
            '/api/v1/user/',
            json.dumps({
                "username": "InstructorDaeyongDaeyongDaeyong",
                "password": "password",
                "first_name": "Daeyong",
                "last_name": "Jeong",
                "email": "JeongDaeyong@snu.ac.kr",
                "role": "instructor",
            }),
            content_type='application/json'
        )
        self.instructor_token3 = 'Token ' + Token.objects.get(user__username='InstructorDaeyongDaeyongDaeyong').key
        data = response.json()
        self.inst_id = data["id"]

        response = self.client.post(
            '/api/v1/seminar/',
            json.dumps({
                "name": "backend",
                "capacity": "30",
                "count": "5",
                "time": "13:30"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token1
        )
        data = response.json()
        self.seminar_id = data["id"]

        response = self.client.post(
            '/api/v1/seminar/',
            json.dumps({
                "name": "frontend",
                "capacity": "1",
                "count": "5",
                "time": "13:30"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token2
        )
        data = response.json()
        self.frontend_seminar_id = data["id"]

    def test_post_seminar_seminarid_user_if_wrong_seminarid(self):  # 세미나 번호 틀리면
        response = self.client.post(
            '/api/v1/seminar/5000/user/',
            json.dumps({
                "role": "participant"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token1
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_seminar_seminarid_user_if_user_unaccepted(self):  # accepted되지 않은 참여자가 신청하면
        seminar_id = self.seminar_id
        address = '/api/v1/seminar/' + str(seminar_id) + '/user/'
        response = self.client.post(
            address,
            json.dumps({
                "role": "participant"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token2
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_seminar_seminarid_user_if_wrong_role(self):  # 올바르지 않은 role로 신청하면
        seminar_id = self.seminar_id
        address = '/api/v1/seminar/' + str(seminar_id) + '/user/'
        response = self.client.post(
            address,
            json.dumps({
                "role": "instructor"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token1
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_seminar_seminarid_user_if_instructor_already_charges(self):  # 이미 차징중인 세미나가 있는 진행자가 신청하면
        seminar_id = self.seminar_id
        address = '/api/v1/seminar/' + str(seminar_id) + '/user/'
        response = self.client.post(
            address,
            json.dumps({
                "role": "instructor"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token2
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_seminar_seminarid_user_if_participant_already(self):  # 이미 참여자인데 또 신청하면
        seminar_id = self.seminar_id
        address = '/api/v1/seminar/' + str(seminar_id) + '/user/'
        response = self.client.post(
            address,
            json.dumps({
                "role": "participant"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token1
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response2 = self.client.post(
            address,
            json.dumps({
                "role": "participant"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token1
        )
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_seminar_seminarid_user_if_seminar_full(self):  # 세미나 가득 찬 경우

        seminar_id = self.frontend_seminar_id
        address = '/api/v1/seminar/' + str(seminar_id) + '/user/'

        self.client.post(
            address,
            json.dumps({
                "role": "participant"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token1
        )
        response = self.client.post(
            address,
            json.dumps({
                "role": "participant"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token3
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_seminar_seminarid_user_if_seminar_full(self):  # 드랍한 사람이 신청하는 경우
        seminar_id = self.seminar_id
        address = '/api/v1/seminar/' + str(seminar_id) + '/user/'

        self.client.post(
            address,
            json.dumps({
                "role": "participant"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token1
        )
        self.client.delete(
            address,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token1
        )
        response = self.client.post(
            address,
            json.dumps({
                "role": "participant"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token1
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_seminar_seminarid_user_success_instructor(self):  # 진행자 성공적인 경우
        seminar_id = self.seminar_id
        address = '/api/v1/seminar/' + str(seminar_id) + '/user/'
        response = self.client.post(
            address,
            json.dumps({
                "role": "instructor"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token3
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertGreater(len(data["instructor"]), 1)  # 이미 진행자가 있으니 두명 이상이어야 한다.
        for dicts in data["instructor"]:  # 그중 방금 신청한 진행자 프로필이 제대로 들어갔는지 확인
            if dicts["id"] == self.inst_id:
                dict = dicts
        self.assertIn("id", dict)
        self.assertEqual(dict["username"], "InstructorDaeyongDaeyongDaeyong")
        self.assertEqual(dict["email"], "JeongDaeyong@snu.ac.kr")
        self.assertEqual(dict["first_name"], "Daeyong")
        self.assertEqual(dict["last_name"], "Jeong")
        self.assertIn("joined_at", dict)

    def test_post_seminar_seminarid_user_success_instructor(self):  # 참가자 성공적인 경우
        seminar_id = self.seminar_id
        address = '/api/v1/seminar/' + str(seminar_id) + '/user/'
        response = self.client.post(
            address,
            json.dumps({
                "role": "participant"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token1
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        for dicts in data["participants"]:
            if dicts["id"] == self.part_id:
                dict = dicts
        self.assertIn("id", dict)
        self.assertEqual(dict["username"], "ParticipantDaeyong")
        self.assertEqual(dict["email"], "JeongDaeyong@snu.ac.kr")
        self.assertEqual(dict["first_name"], "Daeyong")
        self.assertEqual(dict["last_name"], "Jeong")
        self.assertIn("joined_at", dict)
        self.assertEqual(dict["is_active"], True)
        self.assertEqual(dict["dropped_at"], None)

#################################################################################################
#################################################################################################


class DeleteSeminarSeminarIdUserCase(TestCase):
    client = Client()

    def setUp(self):
        response=self.client.post(
            '/api/v1/user/',
            json.dumps({
                "username": "ParticipantDaeyong",
                "password": "password",
                "first_name": "Daeyong",
                "last_name": "Jeong",
                "email": "JeongDaeyong@snu.ac.kr",
                "role": "participant",
                "university": "서울대학교"
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
                "first_name": "Daeyong",
                "last_name": "Jeong",
                "email": "JeongDaeyong@snu.ac.kr",
                "role": "participant",
                "university": "서울대학교",
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
            '/api/v1/seminar/',
            json.dumps({
                "name": "backend",
                "capacity": "30",
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
                "role": "participant"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token1
        )

    def test_delete_seminar_seminarid_user_if_stranger(self): # 가입하지 않은 사람이 드랍요청하는 경우
        seminar_id = self.seminar_id
        address = '/api/v1/seminar/' + str(seminar_id) + '/user/'
        response=self.client.delete(
            address,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token2,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_delete_seminar_seminarid_user_if_stranger(self): # 진행자가 드랍하는 경우
        seminar_id = self.seminar_id
        address = '/api/v1/seminar/' + str(seminar_id) + '/user/'
        response=self.client.delete(
            address,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token1,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_seminar_seminarid_user_if_already_deleted(self): # 드랍한 사람이 또 드랍하는 경우
        seminar_id = self.seminar_id
        address = '/api/v1/seminar/' + str(seminar_id) + '/user/'
        self.client.delete(
            address,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token1,
        )
        response=self.client.delete(
            address,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token1,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_seminar_seminarid_user_success(self):
        seminar_id = self.seminar_id
        address = '/api/v1/seminar/' + str(seminar_id) + '/user/'
        response=self.client.delete(
            address,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token1,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data=response.json()
        for dicts in data["participants"]:
            if dicts["id"] == self.part_id:
                dict = dicts
        self.assertIn("id", dict)
        self.assertEqual(dict["username"], "ParticipantDaeyong")
        self.assertEqual(dict["email"], "JeongDaeyong@snu.ac.kr")
        self.assertEqual(dict["first_name"], "Daeyong")
        self.assertEqual(dict["last_name"], "Jeong")
        self.assertIn("joined_at", dict)
        self.assertEqual(dict["is_active"], False)
        self.assertIn("dropped_at", dict)

