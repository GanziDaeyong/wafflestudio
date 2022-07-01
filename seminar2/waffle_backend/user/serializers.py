from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from seminar.profile_models import ParticipantsProfile, InstructorProfile
from seminar.relation_models import UserSeminar


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(allow_blank=False)
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    last_login = serializers.DateTimeField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    participant = serializers.SerializerMethodField()
    instructor = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'last_login',
            'date_joined',
            'participant',
            'instructor',
        )

    def validate_password(self, value):
        return make_password(value)

    def validate(self, data):  # 유저 생성을 위한 기본 정보들 validate

        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        role = data.get('role')
        username = data.get('username')
        if not username and not email and not role:
            raise serializers.ValidationError("Username/Email/Role are necessary fields.")

        email = str(email)
        if email.find("@") < 0:
            raise serializers.ValidationError("Email should include @")

        if bool(first_name) ^ bool(last_name):
            raise serializers.ValidationError("First name and last name should appear together.")
        if first_name and last_name and not (first_name.isalpha() and last_name.isalpha()):
            raise serializers.ValidationError("First name or last name should not have number.")

        return data

    def validate_for_profile(self, data, if_update):  # 유저의 참여자 / 진행자 프로필 생성을 위한 정보를 validate

        university = data.get('university')
        company = data.get('company')
        year = data.get('year')
        role = data.get('role')

        if if_update == 0 and role != 'participant' and role != 'instructor':  # API#4 회원가입 제한조건
            raise serializers.ValidationError("Role should be participant or instructor.")
        #if (university and not university.isalpha()) or (company and not (company.isalpha())):
        #    raise serializers.ValidationError("Name of institute should not include number.")
        if year and (int(year) < 0):
            raise serializers.ValidationError("Year should be greater than 0")

        return data

    def create(self, validated_data):

        user = super(UserSerializer, self).create(validated_data)

        for_profile_data = self.context['request'].data
        if for_profile_data.get('university'):
            university = for_profile_data.get('university')
        else:
            university = ""

        if for_profile_data.get('accepted'):
            if for_profile_data.get('accepted') == "false" or "False":
                accepted = False
        else:
            accepted = True

        if for_profile_data.get('company'):
            company = for_profile_data.get('company')
        else:
            company = ""
        if for_profile_data.get('year'):
            year = for_profile_data.get('year')
        else:
            year = None

        if for_profile_data.get('role') == ('participant'):
            ParticipantsProfile.objects.create(user=user, university=university, accepted=accepted)

        elif for_profile_data.get('role') == ('instructor'):
            InstructorProfile.objects.create(user=user, company=company, year=year)
        Token.objects.create(user=user)

        return user

    def get_participant(self, user):
        self.context['user'] = user
        from seminar.serializers import ParticipantsProfileSerializer
        if user.participants.all():
            serializer = ParticipantsProfileSerializer(user.participants.all(), context=self.context, many=True)
            return serializer.data[0]
        else:
            return None

        #return ParticipantsProfileSerializer(user.participants.all(), context=self.context, many=True #.all()
        #                                     ).data if user.participants.all() else None

    def get_instructor(self, user):
        self.context['user'] = user
        from seminar.serializers import InstructorProfileSerializer
        if user.instructor.all():
            serializer = InstructorProfileSerializer(user.instructor.all(), context=self.context, many=True)
            return serializer.data[0]
        else:
            return None
        #return InstructorProfileSerializer(user.instructor.all(), context=self.context,
        #                                   many=True).data if user.instructor.all() else None

    def update(self, data):  # 이미 validate 거친 data이다.

        # 유저의 기본 정보 업데이트
        user = self.context['request'].user
        if data.get('first_name'):
            user.first_name = data.get('first_name')
            user.last_name = data.get('last_name')
        if data.get('username'):
            user.username = data.get('username')
        if data.get('email'):
            user.email = data.get('email')

        # 유저와 관련된 참여자 / 진행자 프로필 받아오기.
        try:
            user.participants.get(user=user)
            user_role = user.participants.get(user=user)
        except:
            user_role = user.instructor.get(user=user)

        # 유저 프로필 업데이트
        for_profile_data = self.context['request'].data  # 이미 view에서 validation 과정 거치도록 설정해놓았다.

        if for_profile_data.get('university'):
            user_role.university = for_profile_data.get('university')
        if for_profile_data.get('company'):
            user_role.company = for_profile_data.get('company')
        if for_profile_data.get('year'):
            user_role.year = for_profile_data.get('year')

        user_role.save()
        user.save()

    def new_role(self, request):
        user = request.user
        data = request.data

        sw = 0
        try:
            if ParticipantsProfile.objects.get(user_id=user.id):
                sw = 1
        except:
            pass

        if sw == 1:
            raise serializers.ValidationError("You are already a participant")

        if data.get('university'):
            university = data.get('university')
        else:
            university = ""

        ParticipantsProfile.objects.create(user=user, university=university)

        return user
