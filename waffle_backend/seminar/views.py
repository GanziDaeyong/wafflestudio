from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from seminar.serializers import SeminarSerializer
from seminar.mini_serializers import MiniSeminarSerializer
from seminar.seminar_models import Seminar
from seminar.relation_models import UserSeminar


class SeminarViewSet(viewsets.GenericViewSet):
    queryset = Seminar.objects.all()
    serializer_class = SeminarSerializer
    permission_classes = (IsAuthenticated(),)

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return (AllowAny(),)
        return self.permission_classes

    def create(self, request):

        user = request.user
        try:
            user.instructor.get(user=user)
        except:
            return Response({"error": "Only authorized instructors can create a seminar."},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=id):
        user = request.user
        data = request.data
        try:
            seminar = Seminar.objects.get(id=pk)
        except:
            return Response({"error": "Can't find the proper seminar."}, status=status.HTTP_404_NOT_FOUND)
        try:
            profile = UserSeminar.objects.filter(seminar_id=pk).get(user_id=user.id)
            if profile.role != 'instructor':
                return Response({"error": "only authorized seminar instructors can access."},
                                status=status.HTTP_403_FORBIDDEN)  ##메세지 추가.
        except:
            return Response({"error": "only authorized seminar instructors can access."},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(user, data=data, partial=True)
        # get_serializer는 데이터를 받아서 serializer해준다.
        serializer.is_valid(raise_exception=True)
        seminar = serializer.update(pk, data)

        return Response(SeminarSerializer(seminar).data)

    def retrieve(self, request, pk=id):
        try:
            seminar = Seminar.objects.get(id=pk)
        except:
            return Response({"error": "Can't find the proper seminar."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SeminarSerializer()
        serializer.get_participant_count(pk)

        return Response(SeminarSerializer(seminar).data)

    def list(self, request, pk=None):
        queryset = self.queryset.order_by('-created_at')
        if request.GET.get('name', ''):
            queryset = self.queryset.filter(name__contains=request.GET.get('name')).order_by('-created_at')
        if request.GET.get('order', '') == 'earlist':
            queryset = self.queryset.order_by('created_at')

        return Response(MiniSeminarSerializer(queryset, many=True).data)

    # DELETE / api / v1 / seminar / {seminar_id} / user /
    def delete(self, request, pk=id):
        try:
            seminar = Seminar.objects.get(id=pk)
        except:
            return Response({"error": "Can't find the proper seminar."}, status=status.HTTP_404_NOT_FOUND)
        user = request.user
        data = request.data
        serializer = self.get_serializer(user, data=data, partial=True)
        serializer.delete(seminar, user)

        return Response(SeminarSerializer(seminar).data)

    # POST / api / v1 / seminar / {seminar_id} / user /
    @action(detail=True, methods=['post'])
    def user(self, request, pk=id):
        user = request.user
        data = request.data
        try:
            seminar = Seminar.objects.get(id=pk)
        except:
            return Response({"error": "Can't find the proper seminar."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(user, data=data, partial=True)
        serializer.add(pk, seminar)
        return Response(SeminarSerializer(seminar).data)
