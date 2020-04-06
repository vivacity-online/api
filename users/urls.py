"""
    User urls
"""

from django.conf import settings
from django.urls import path
from rest_framework.generics import RetrieveAPIView, ListAPIView, UpdateAPIView

from . import views
from .models import User
from .serializers import QuickUserSerializer, OwnProfileSerializer
from .views import OwnProfileView

urlpatterns = [
    path(
        'login',
        views.Login.as_view(),
        name="login"
    ),
    path(
        'logout',
        views.Logout.as_view(),
        name="logout"
    ),
    path(
        'create',
        views.CreateUser.as_view(),
        name="create_user"
    ),
    path(
        'item/dailychance',
        views.DailyChance.as_view(),
        name="set_dailyChance"
    ),
    path(
        'profile/<str:username>',
        views.ProfileView.as_view(),
        name="profile_view"
    ),
    path(
        'profile/edit/<str:username>',
        OwnProfileView.as_view(),
        name="profile_edit_view"
    ),
    path('view/all', ListAPIView.as_view(
        authentication_classes=settings.AUTH_CLASSES,
        permission_classes=settings.PERM_CLASSES,
        serializer_class=QuickUserSerializer,
        queryset=User.objects.all(),
    )),

    path('view/<str:username>', RetrieveAPIView.as_view(
        authentication_classes=settings.AUTH_CLASSES,
        permission_classes=settings.PERM_CLASSES,
        serializer_class=QuickUserSerializer,
        lookup_field="username",
        queryset=User.objects.all(),
    )),

    path('validate', views.ValidateUserData.as_view(), name="validate_username"),
    path(
        'activate/<uidb64>/<token>',
        views.Activate.as_view(), name='activate'
    ),
    path('search', views.UserSearch.as_view(), name="user_search"),
    path('color/<str:username>', views.UserColorView.as_view(), name="user_colors"),
]
