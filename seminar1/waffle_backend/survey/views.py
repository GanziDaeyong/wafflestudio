from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response
from django.contrib.auth.models import User
from survey.serializers import OperatingSystemSerializer, SurveyResultSerializer
from survey.models import OperatingSystem, SurveyResult


class SurveyResultViewSet(viewsets.GenericViewSet):
    queryset = SurveyResult.objects.all()
    serializer_class = SurveyResultSerializer

    def list(self, request):
        surveys = self.get_queryset().select_related('os')
        return Response(self.get_serializer(surveys, many=True).data)

    def retrieve(self, request, pk=None):
        survey = get_object_or_404(SurveyResult, pk=pk)
        return Response(self.get_serializer(survey).data)

    #@action(detail=False, methods=['POST']) # 이거 체크
    def create(self, request):

        # 로그인하지 않았다면 바로 403을 리턴
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_403_FORBIDDEN)


        # 필요한 항목 가져오기
        python = request.data.get('python')
        rdb = request.data.get('rdb')
        programming = request.data.get('programming')
        os = request.data.get('os')

        # 조건 1 : 꼭 있어야 되는 항목들
        if not python or not rdb or not programming or not os:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 조건 2 : 해당 항목들의 타입
        if not python.isdigit() or not rdb.isdigit() or not programming.isdigit(): #or not os.isalpha():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 조건 3 : 해당 항목들의 범위
        if (1>int(python) and int(python)>5) or (1>int(rdb) and int(rdb)>5) or (1>int(programming) and int(programming)>5):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # os의 경우 survey_operatingsystem을 통해 대응하는 os_id를 얻어 survey_surveyresult에 삽입
        OperatingSystem.objects.get_or_create(name=os)
        query = OperatingSystem.objects.get(name=os) # .get은 row (==쿼리)를 리턴. / .filter는 조건에 부합하는 쿼리셋을 리턴
        os_id = query

        # 로그인했다면 user_id 가져오기
        user_id = request.user.id
        user_query = User.objects.get(id=user_id)

        # 조건을 만족한 항목들을 최종적으로 쿼리로 형성
        SurveyResult.objects.create(python=python, rdb=rdb, programming=programming, os=os_id, user=user_query)
        survey = SurveyResult.objects.last()

        return Response(self.get_serializer(survey).data, status=status.HTTP_201_CREATED)


class OperatingSystemViewSet(viewsets.GenericViewSet):
    queryset = OperatingSystem.objects.all()
    serializer_class = OperatingSystemSerializer

    def list(self, request):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    def retrieve(self, request, pk=None):
        try:
            os = OperatingSystem.objects.get(id=pk)
        except OperatingSystem.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(self.get_serializer(os).data)








