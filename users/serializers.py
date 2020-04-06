from rest_framework import serializers

from .models import User, Interest

INFO = [
    'email',
    'username',
    'is_active',
    'is_admin',
    'date_of_birth',
    'role',
    'first_name',
    'last_name',
    'joined_on',
    'last_login',
]
DISPLAY_SETTINGS = [
    'display_occupation_to',
    'display_occupation',
    'display_location_to',
    'display_location',
    'display_date_of_birth_to',
    'display_date_of_birth',
    'display_full_name_to',
    'display_full_name',
]
PROFILE = [
    'location',
    'tag',
    'bio',
    'friends',
    'occupation',
    'interests',
    'board_count',
    'avatar',
    'avatar_thumbnail',
    'primary_color',
    'secondary_color',
]


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = '__all__'


class QuickUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'avatar_thumbnail',
            'primary_color',
            'secondary_color'
        ]


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'isAuthenticated',
            'online',
            'avatar',
            'avatar_thumbnail',
            'dailyChance',
            'is_staff',
            'auth_token',
            'primary_color',
            'secondary_color',
            'shinies',
            'muns'
        ]


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'primary_color',
            'secondary_color',
        ]


class NewUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'date_of_birth',
            'password'
        ]


class ProfileSerializer(serializers.ModelSerializer):

    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    date_of_birth = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    occupation = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = INFO + PROFILE

    def get_first_name(self, user):
        display = user.display_full_name
        return None if not display else user.first_name

    def get_last_name(self, user):
        display = user.display_full_name
        return None if not display else user.last_name

    def get_date_of_birth(self, user):
        display = user.display_date_of_birth
        return None if not display else user.date_of_birth

    def get_location(self, user):
        display = user.display_location
        return None if not display else user.location

    def get_occupation(self, user):
        display = user.display_occupation
        return None if not display else user.occupation


class OwnProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = '__all__'
        exclude = ['password', ]

    interests = InterestSerializer(read_only=True, many=True)
    board_count = serializers.SerializerMethodField()
    friends = QuickUserSerializer(many=True)

    def get_board_count(self, user):
        return user.board_count
    

class DailyChanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['dailyChance', 'dailyChanceDate']
