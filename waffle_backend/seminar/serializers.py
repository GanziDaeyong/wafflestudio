from rest_framework import serializers
from seminar.seminar_models import Seminar
from seminar.profile_models import ParticipantsProfile, InstructorProfile
from user.mini_serializers import MiniUserSerializer, MiniUserSerializerForParticipants
from seminar.relation_models import UserSeminar
import datetime
from django.core.exceptions import PermissionDenied


class ParticipantsProfileSerializer(serializers.ModelSerializer):
    seminars = serializers.SerializerMethodField()

    class Meta:
        model = ParticipantsProfile
        fields = (
            'id',
            'university',
            'accepted',
            'seminars',
        )

    def get_seminars(self, seminar):
        from seminar.mini_serializers import MiniSeminarSerializerForUser
        user = self.context['user']
        self.context['user'] = user
        sw = 0
        try:
            if UserSeminar.objects.filter(user_id=user.id).filter(role='participant'):
                # 만약 participant로 참가중인 세미나가 있다
                sw = 1
        except:
            pass
        if sw == 0:
            return None

        rstlist = []
        rst = UserSeminar.objects.filter(user_id=user.id)
        for query in rst:
            rstlist.append(query.seminar)
        return MiniSeminarSerializerForUser(rstlist, context=self.context, many=True).data


class InstructorProfileSerializer(serializers.ModelSerializer):
    charge = serializers.SerializerMethodField()

    class Meta:
        model = InstructorProfile
        fields = (
            'id',
            'company',
            'year',
            'charge',
        )

    def get_charge(self, instructor):
        from seminar.mini_serializers import MiniSeminarSerializerForUserForInstructor
        user = self.context['user']
        self.context['user'] = user
        rstlist = []
        rst = UserSeminar.objects.filter(user_id=user.id).filter(role='instructor')
        for query in rst:
            rstlist.append(query.seminar)
        return MiniSeminarSerializerForUserForInstructor(rstlist, context=self.context, many=True).data


class SeminarSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()
    instructor = serializers.SerializerMethodField()

    class Meta:
        model = Seminar
        fields = (
            'id',
            'name',
            'capacity',
            'count',
            'time',
            'online',
            'instructor',
            'participants',
        )

    def validate(self, data):

        name = data.get('name')
        capacity = data.get('capacity')
        count = data.get('count')
        time = data.get('time')

        if not (name and capacity and count and time):
            raise serializers.ValidationError("required data : name / capacity / count / time")
        if name == "":
            raise serializers.ValidationError("enter the name of seminar")
        if int(capacity) <= 0 or int(count) <= 0:
            raise serializers.ValidationError("capacity and count should be greater than 0.")
        # online의 경우 BooleanField가 허용하는 기본 값 사용하였다.
        time = str(time) # 시간의 경우도, TimeField가 허용하는 값에 글자수 제한을 두어 시:분 만 가능하도록 했다.
        if len(time) > 5:
            raise serializers.ValidationError("enter right form of time ex: 12:30 ")

        return data

    def create(self, validated_data):

        user = self.context['request'].user
        seminar = super(SeminarSerializer, self).create(validated_data)
        relation = UserSeminar.objects.create(seminar=seminar, user=user, role='instructor')
        relation.save()
        return seminar

    def update(self, pk, data):
        seminar = Seminar.objects.get(id=pk)
        if data.get('name'):
            seminar.name = data['name']
        if data.get('count'):
            seminar.count = data['count']
        if data.get('capacity'):
            num = UserSeminar.objects.filter(seminar_id=pk).filter(role='participant').filter(is_active=True).count()
            if int(data['capacity']) < num:
                raise serializers.ValidationError(
                    "Capacity should be greater than the number of participants at this moment.")
            seminar.capacity = data['capacity']
        if data.get('time'):
            seminar.time = data['time']
        if data.get('online'):
            seminar.online = data['online']

        seminar.save()

        return seminar

    def add(self, pk, seminar):  ##role따라.

        user = self.context['request'].user
        role = self.context['request'].data.get('role')

        sw = 0
        try:
            profile = UserSeminar.objects.filter(seminar_id=pk).get(user_id=user.id)
            sw = 1
        except:
            pass

        if sw == 1 and profile.is_active == False:
            raise serializers.ValidationError("you dropped from this seminar")

        if sw == 1 and profile.is_active:  # UserSeminar.objects.filter(seminar_id=pk).filter(user_id=user.id):
            raise serializers.ValidationError("you are already participating in this seminar")

        if role == 'participant':
            if UserSeminar.objects.filter(seminar_id=pk).filter(role='participant').count() >= seminar.capacity:
                raise serializers.ValidationError("this seminar is full already.")
            try:
                ParticipantsProfile.objects.get(user_id=user.id)
                if ParticipantsProfile.objects.get(user_id=user.id).accepted == False:
                    raise PermissionDenied()
            except:
                raise PermissionDenied()

        elif role == 'instructor':
            if UserSeminar.objects.filter(user_id=user.id).filter(role='instructor'):
                raise serializers.ValidationError("You are already engaging as an instructor from another seminar")
            try:
                InstructorProfile.objects.get(user_id=user.id)
            except:
                raise PermissionDenied()

        seminar = Seminar.objects.get(id=pk)

        relation = UserSeminar.objects.create(seminar=seminar, user=user, role=role)
        relation.save()

    def delete(self, seminar, user):
        try:
            profile = UserSeminar.objects.filter(seminar_id=seminar.id).get(user_id=user.id)
            if profile.role == 'instructor':
                raise PermissionDenied()
        except:
            pass

        profile.is_active = False
        profile.dropped_at = datetime.datetime.now()
        profile.save()

    def get_instructor(self, seminar):
        try:
            seminar.id  # (처음생성하는 경우. )
        except:
            user = self.context['request'].user
            return MiniUserSerializer(user).data

        self.context['seminar_id'] = seminar.id
        rst = UserSeminar.objects.filter(seminar_id=seminar.id).filter(role='instructor')
        rstlist = []
        for query in rst:
            rstlist.append(query.user)
        return MiniUserSerializer(rstlist, many=True, context=self.context).data

    def get_participants(self, seminar):
        try:
            seminar.id  # (처음생성하는 경우. )
        except:
            return None
        self.context['seminar_id'] = seminar.id
        rst = UserSeminar.objects.filter(seminar_id=seminar.id).filter(role='participant')
        rstlist = []
        for query in rst:
            rstlist.append(query.user)
        return MiniUserSerializerForParticipants(rstlist, many=True, context=self.context).data

    def get_participant_count(self, pk):
        return UserSeminar.objects.filter(seminar_id=pk).filter(role='participant').filter(is_active=True).count()
