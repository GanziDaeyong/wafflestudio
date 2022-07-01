from seminar.seminar_models import Seminar
from rest_framework import serializers
from seminar.serializers import SeminarSerializer
from seminar.relation_models import UserSeminar
from user.mini_serializers import MiniUserSerializerForParticipants

class MiniSeminarSerializer(SeminarSerializer): # For seminar search

    participant_count = serializers.SerializerMethodField()

    class Meta:
        model = Seminar
        fields = (
            'id',
            'name',
            'instructors',
            'participant_count'
        )



class MiniSeminarSerializerForUser(MiniUserSerializerForParticipants): # For user search (participant)

    class Meta:
        model = Seminar
        fields = (
            'id',
            'name',
            'joined_at',
            'is_active',
            'dropped_at',
        )

    def get_joined_at(self, seminar): # 상속받았어도 context 정보가 다르기때문에 오버라이딩 필요하다.
        user = self.context['user']
        userseminarProfile = UserSeminar.objects.filter(seminar_id=seminar.id).get(user_id=user.id)
        return userseminarProfile.joined_at

    def get_dropped_at(self, seminar):
        user = self.context['user']
        userseminarProfile = UserSeminar.objects.filter(seminar_id=seminar.id).get(user_id=user.id)
        return userseminarProfile.dropped_at

    def get_is_active(self, seminar):
        user = self.context['user']
        userseminarProfile = UserSeminar.objects.filter(seminar_id=seminar.id).get(user_id=user.id)
        return userseminarProfile.is_active

class MiniSeminarSerializerForUserForInstructor(MiniSeminarSerializerForUser): # For user search (instructor)

    class Meta:
        model = Seminar
        fields = (
            'id',
            'name',
            'joined_at',
        )

    def get_joined_at(self, seminar):
        user = self.context['user']
        userseminarProfile = UserSeminar.objects.filter(seminar_id=seminar.id).get(user_id=user.id)
        return userseminarProfile.joined_at

