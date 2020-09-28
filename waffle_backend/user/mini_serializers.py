from django.contrib.auth.models import User
from rest_framework import serializers
from user.serializers import UserSerializer
from seminar.relation_models import UserSeminar

class MiniUserSerializerForParticipants(UserSerializer):

    joined_at = serializers.SerializerMethodField()
    dropped_at = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'joined_at',
            'is_active',
            'dropped_at'
        )

    def get_joined_at(self, user):
        #처음세미만드는 경우.
        try:
            id = self.context['seminar_id']
        except:
            return None
        id = self.context['seminar_id']
        userseminarProfile = UserSeminar.objects.filter(seminar_id=id).get(user_id=user.id)
        return userseminarProfile.joined_at

    def get_dropped_at(self, user):
        id = self.context['seminar_id']
        userseminarProfile = UserSeminar.objects.filter(seminar_id=id).get(user_id=user.id)
        return userseminarProfile.dropped_at

    def get_is_active(self, user):
        id = self.context['seminar_id']
        userseminarProfile = UserSeminar.objects.filter(seminar_id=id).get(user_id=user.id)
        return userseminarProfile.is_active


class MiniUserSerializer(MiniUserSerializerForParticipants): # 상속 너무좋

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'joined_at',
        )

