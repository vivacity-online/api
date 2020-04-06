"""vivacity_api URL Configuration

"""
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('api/main/', include('main.urls')),
                  path('api/board/', include('boards.urls')),
                  path('api/user/', include('users.urls')),
                  path('api/auth/', include('djoser.urls.authtoken')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
