"""links_organizer_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


admin.site.site_header = "Links Organizer"
admin.site.site_title = "Links Organizer"

api_info = openapi.Info(
    title="Links Organizer API",
    default_version="v1",
    description="API for Links Organizer",
    terms_of_service="",
    contact=openapi.Contact(email=""),
    license=openapi.License(name=""),
)

schema_view = get_schema_view(
    api_info,
    public=True,
    permission_classes=(permissions.AllowAny,),
)

api_v1_urlpatterns = [
    path("accounts/", include("accounts.urls"), name="accounts"),
]

urlpatterns = [
    path("api/v1/", include(api_v1_urlpatterns), name="api_v1"),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.extend(
        [
            path("api-auth", include("rest_framework.urls")),
            # debug_toolbar
            path("__debug__/", include(debug_toolbar.urls), name="debug_toolbar"),
            path(
                "swagger",
                schema_view.with_ui("swagger", cache_timeout=0),
                name="schema-swagger-ui",
            ),
            path(
                "redoc",
                schema_view.with_ui("redoc", cache_timeout=0),
                name="schema-redoc",
            ),
        ]
    )
