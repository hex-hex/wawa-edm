from rest_framework.routers import DefaultRouter

from .views import (
    CompanyViewSet,
    ContactViewSet,
    EmailTaskViewSet,
    KnowledgeViewSet,
)

router = DefaultRouter()
router.register(r"companies", CompanyViewSet)
router.register(r"contacts", ContactViewSet)
router.register(r"knowledge", KnowledgeViewSet)
router.register(r"email-tasks", EmailTaskViewSet)

urlpatterns = router.urls
