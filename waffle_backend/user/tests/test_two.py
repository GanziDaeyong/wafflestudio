from django.test import Client, TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
import json

"""
PUT /api/v1/user/login/
POST /api/v1/user/participant/
POST /api/v1/seminar/
"""

########################################################################################################################
########################################################################################################################
# PUT /api/v1/user/login/

class PutUserLoginCase(TestCase):
    # 조건: 아이디 / 비밀번호
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
                "university": "서울대학교"
            }),
            content_type='application/json'
        )

    def test_put_user_login(self):
        response = self.client.put(
            '/api/v1/user/login/',
            json.dumps({
                "username": "ParticipantDaeyong",
                "password": "password"
            }),
            content_type='application/json'  # authorization 필요없는 동작.
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_user_login_incorrect(self):
        response = self.client.put(
            '/api/v1/user/login/',
            json.dumps({
                "username": "ParticipantDaeyong",
                "password": "wrongpassword"
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


###################################################################################################
###################################################################################################
# post /api/v1/user/participant/


class PostUserParticipantCase(TestCase):
    # 조건: 아이디 / 비밀번호
    client = Client()

    def setUp(self):
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
        self.instructor_token = 'Token ' + Token.objects.get(user__username='InstructorDaeyong').key

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
        self.participant_token = 'Token ' + Token.objects.get(user__username='ParticipantDaeyong').key

    def test_post_user_participant_incorrect(self):  # 이미 participant는 participant를 신청할 수 없다. (400)

        response = self.client.post(
            '/api/v1/user/participant/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_user_participant_with_univ(self):
        response = self.client.post(
            '/api/v1/user/participant/',
            json.dumps({
                "university": "Korea University"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["username"], "InstructorDaeyong")
        self.assertEqual(data["email"], "JeongDaeyong@snu.ac.kr")
        self.assertEqual(data["first_name"], "Daeyong")
        self.assertEqual(data["last_name"], "Jeong")
        self.assertIn("last_login", data)
        self.assertIn("date_joined", data)
        self.assertNotIn("token", data)
        self.assertIsNotNone(data["participant"])

        participant = data["participant"]
        self.assertEqual(participant["university"], "Korea University")
        self.assertIn("id", participant)
        self.assertEqual(participant["accepted"], True)
        self.assertEqual(participant["seminars"], [])

        instructor = data["instructor"]
        self.assertIsNotNone(instructor)
        self.assertIn("id", instructor)
        self.assertIsNone(instructor["charge"])

    def test_post_user_participant_without_univ(self):
        response = self.client.post(
            '/api/v1/user/participant/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["username"], "InstructorDaeyong")
        self.assertEqual(data["email"], "JeongDaeyong@snu.ac.kr")
        self.assertEqual(data["first_name"], "Daeyong")
        self.assertEqual(data["last_name"], "Jeong")
        self.assertIn("last_login", data)
        self.assertIn("date_joined", data)
        self.assertNotIn("token", data)
        self.assertIsNotNone(data["participant"])

        participant = data["participant"]
        self.assertEqual(participant["university"], "")
        self.assertIn("id", participant)
        self.assertEqual(participant["accepted"], True)
        self.assertEqual(participant["seminars"], [])

        instructor = data["instructor"]
        self.assertIsNotNone(instructor)
        self.assertIn("id", instructor)
        self.assertIsNone(instructor["charge"])


###################################################################################################
###################################################################################################
# Post seminar

class PostSeminarCase(TestCase):
    # 조건: 아이디 / 비밀번호
    client = Client()

    def setUp(self):
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
        self.instructor_token = 'Token ' + Token.objects.get(user__username='InstructorDaeyong').key

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
        self.participant_token = 'Token ' + Token.objects.get(user__username='ParticipantDaeyong').key

    def test_post_seminar_if_participant_makes_it(self):  # 참여자가 만드는 경우
        response = self.client.post(
            '/api/v1/seminar/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_seminar_if_necessary_info_missed(self):  # time 없는경우
        response = self.client.post(
            '/api/v1/seminar/',
            json.dumps({
                "name": "backend",
                "capacity": "25",
                # time /
                "count" : "3",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_seminar_if_necessary_info_missed2(self):  # capacity 없는 경우
        response = self.client.post(
            '/api/v1/seminar/',
            json.dumps({
                "name": "backend",
                "count": "25",
                "time": "13:30"
                # capacity missing
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_seminar_if_necessary_info_wrong_type(self):  # 이름에 0글자, 즉 이름이 빈칸인 경우
        response = self.client.post(
            '/api/v1/seminar/',
            json.dumps({
                "name": "",
                "capacity": "30",
                "count": "25",
                "time": "13:30"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_seminar_if_necessary_info_wrong_type2(self):  # capacity가 양의 정수가 아닌 경우
        response = self.client.post(
            '/api/v1/seminar/',
            json.dumps({
                "name": "backend",
                "capacity": "-3",
                "count": "25",
                "time": "13:30"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_seminar_if_necessary_info_wrong_type3(self):  # count가 양의 정수가 아닌 경우
        response = self.client.post(
            '/api/v1/seminar/',
            json.dumps({
                "name": "backend",
                "capacity": "30",
                "count": "-3",
                "time": "13:30"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_seminar_if_necessary_info_wrong_type4(self):  # time 형식이 잘못된 경우
        response = self.client.post(
            '/api/v1/seminar/',
            json.dumps({
                "name": "backend",
                "capacity": "30",
                "count": "5",
                "time": "1:230"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_seminar_if_necessary_info_wrong_type5(self):  # online이 True False가 아닌 경우
        response = self.client.post(
            '/api/v1/seminar/',
            json.dumps({
                "name": "backend",
                "capacity": "30",
                "count": "5",
                "time": "13:30",
                "online": "truE"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_seminar_success(self):
        response = self.client.post(
            '/api/v1/seminar/',
            json.dumps({
                "name": "backend",
                "capacity": "30",
                "count": "5",
                "time": "13:30"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["name"], "backend")
        self.assertEqual(data["capacity"], 30)
        self.assertEqual(data["count"], 5)
        self.assertEqual(data["time"], "13:30:00")
        self.assertEqual(data["online"], True)
        self.assertEqual(data["participants"], [])

        instructor = data["instructor"][0]
        self.assertIsNotNone(instructor)
        self.assertIn("id", instructor)
        self.assertEqual(instructor["username"], "InstructorDaeyong")
        self.assertEqual(instructor["email"], "JeongDaeyong@snu.ac.kr")
        self.assertEqual(instructor["first_name"], "Daeyong")
        self.assertEqual(instructor["last_name"], "Jeong")
        self.assertIn("joined_at", instructor)

