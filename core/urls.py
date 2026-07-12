from rest_framework.routers import DefaultRouter

from .views import (
    CompanyViewSet,
    ContactTagViewSet,
    ContactViewSet,
    EmailDraftViewSet,
    EmailTaskViewSet,
    KnowledgeTagViewSet,
    KnowledgeViewSet,
)

router = DefaultRouter()
router.register(r"companies", CompanyViewSet)
router.register(r"contact-tags", ContactTagViewSet)
router.register(r"contacts", ContactViewSet)
router.register(r"knowledge-tags", KnowledgeTagViewSet)
router.register(r"knowledge", KnowledgeViewSet)
router.register(r"email-tasks", EmailTaskViewSet)
router.register(r"email-drafts", EmailDraftViewSet)

urlpatterns = router.urls
