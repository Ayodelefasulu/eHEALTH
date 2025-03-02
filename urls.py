from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(title="eHealth API", default_version='v1'),
    public=True,
    permission_classes=[permissions.AllowAny],
    authentication_classes=[TokenAuthentication],
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('health_management.urls')),
    path('api/swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    #path('api/rate-practitioner/', PractitionerRatingView.as_view(), name='rate_practitioner'),
    path('accounts/', include('django.contrib.auth.urls')),
]
