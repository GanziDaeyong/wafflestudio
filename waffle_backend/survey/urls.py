from django.urls import include, path
from rest_framework.routers import SimpleRouter
from survey.views import SurveyResultViewSet, OperatingSystemViewSet

app_name = 'survey'
app_name = 'os'

router = SimpleRouter()
router.register('survey', SurveyResultViewSet, basename='survey')  # /api/v1/survey/
router.register('os', OperatingSystemViewSet, basename='os') # /api/v1/os/

urlpatterns = [
    path('', include((router.urls))),
]