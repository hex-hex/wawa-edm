from rest_framework.routers import DefaultRouter

from .views import CompanyViewSet, ContactViewSet

router = DefaultRouter()
router.register(r"companies", CompanyViewSet)
router.register(r"contacts", ContactViewSet)

urlpatterns = router.urls
