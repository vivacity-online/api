import json

from django.conf import settings
from django.contrib.auth import authenticate, logout
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, Interest
from .serializers import NewUserSerializer, LoginSerializer, ProfileSerializer, OwnProfileSerializer, \
    InterestSerializer, QuickUserSerializer, ColorSerializer


class Login(APIView):

    def post(self, request):
        username = request.data['username']
        password = request.data['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            user.online = True
            user.set_dailyChance(state="reset")  # Checks and sets dailyChance item bool
            user.save()
            loggedUser = LoginSerializer(user, context={"request": request})
            loggedIn = loggedUser.data
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        return Response(loggedIn, status=status.HTTP_200_OK)


class Logout(APIView):
    authentication_classes = settings.AUTH_CLASSES
    permission_classes = settings.PERM_CLASSES

    def get(self, request):
        request.user.online = False
        print("User should be offline NOW")
        request.user.save()
        logout(request)
        return Response({"loggedOut": True}, status=status.HTTP_200_OK)


class CreateUser(APIView):

    def send_activation_email(self, request, user):
        mail_subject = 'Activate your Vivacity account.'
        message = render_to_string('acc_activate_email.html', {
            'user': user,
            'domain': get_current_site(request),
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': user.auth_token,
        })
        to_email = ['jsyme222@gmail.com', ]
        email = EmailMessage(
            mail_subject, message, to=to_email
        )
        email.send()
        print("Sent Mail")

    def post(self, request):
        data = request.data
        serialized = NewUserSerializer(data=data)
        if serialized.is_valid():
            user = User.objects.create_user(
                serialized.validated_data['email'],
                serialized.validated_data['username'],
                serialized.initial_data['password'],
                serialized.validated_data['date_of_birth']
            )
            self.send_activation_email(request, user)
            response_data = LoginSerializer(user, context={"request": request})
            return Response(response_data.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)


class Activate(APIView):

    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
            return Response({'Error': 'No user to activate'}, status=status.HTTP_400_BAD_REQUEST)

        if user is not None:
            print("Found user")
            userToken = user.auth_token
            if str(userToken) == str(token):
                print("Tokens match")
                user.email_confirmed = True
                user.save()
            return redirect('http://localhost:3000')


class ProfileView(RetrieveAPIView):
    authentication_classes = settings.AUTH_CLASSES
    permission_classes = settings.PERM_CLASSES

    lookup_field = "username"
    queryset = User.objects.all()
    serializer_class = ProfileSerializer


class OwnProfileView(UpdateAPIView):
    authentication_classes = settings.AUTH_CLASSES
    permission_classes = settings.PERM_CLASSES
    lookup_field = "username"
    queryset = User.objects.all()

    def token_from_string(self, token_string):
        """Token is in Authorization: Token <TOKEN> - format
        so must this pulls just the TOKEN from string
        """
        token = token_string.split()[1]
        return token

    def authorized(self, username, token_string):
        token = self.token_from_string(token_string)
        try:
            user = User.objects.get(username=username)
            requesting_token = user.auth_token
        except ObjectDoesNotExist:
            return False
        return str(token) == str(requesting_token)

    def patch(self, request, *args, **kwargs):
        token_string = request.headers['Authorization']
        if self.authorized(kwargs['username'], token_string):
            # User is owner of profile
            data = request.data
            profile_user = User.objects.get(username=kwargs['username'])
            if not data:
                # No patch data sent so return is full user profile data
                serialized_profile = OwnProfileSerializer(profile_user)
                user_data = serialized_profile.data
                return Response(
                    user_data,
                    status=status.HTTP_200_OK
                )
            else:
                # Check for interest and create/add interests
                if 'interests' in data.keys():
                    interests = data['interests']
                    interests = json.loads(interests)
                    profile_user.interests.set([])
                    for interest in interests:
                        try:
                            obj = Interest.objects.get(title=interest['title'])
                        except ObjectDoesNotExist:
                            serialized_interest = InterestSerializer(data=interest)
                            if serialized_interest.is_valid():
                                serialized_interest.save()
                                obj = Interest.objects.get(title=serialized_interest.data['title'])
                            else:
                                return Response(
                                    {"Value Error": "Value error in data"},
                                    status=status.HTTP_400_BAD_REQUEST
                                )
                        profile_user.interests.add(obj)  # Add interest to profile
                        profile_user.save()

                serialized_profile_data = OwnProfileSerializer(
                    profile_user,
                    data=data,
                    partial=True
                )
                if serialized_profile_data.is_valid():
                    serialized_profile_data.save()
                    serialized_return_data = LoginSerializer(profile_user, context={'request': request})
                    return Response(
                        serialized_return_data.data,
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {"Value Error": "Value error in data"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        else:
            # User is not profile owner and patch access is denied
            return Response(
                {"Unauthorized": "Unauthorized edit requested"},
                status=status.HTTP_401_UNAUTHORIZED
            )

    def get_serializer_class(self):
        return OwnProfileSerializer


class DailyChance(APIView):
    authentication_classes = settings.AUTH_CLASSES
    permission_classes = settings.PERM_CLASSES

    def put(self, request):
        user = User.objects.get(username=request.user.username)
        if user.set_dailyChance():
            user.save()
            response = {
                'dailyChance': user.dailyChance
            }
            if not user.dailyChance:
                return Response(response, status=status.HTTP_202_ACCEPTED)
        else:
            response = {"400": "No change sent"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class ValidateUserData(APIView):

    def get(self, request):
        if 'username' in request.GET.keys():
            username = request.GET['username']
            try:
                user = User.objects.get(username=username)
                if user:
                    return Response({}, status.HTTP_226_IM_USED)
            except ObjectDoesNotExist:
                return Response({}, status=status.HTTP_200_OK)
        if 'email' in request.GET.keys():
            email = request.GET['email']
            try:
                user = User.objects.get(email=email)
                if user:
                    return Response({}, status.HTTP_226_IM_USED)
            except ObjectDoesNotExist:
                return Response({}, status=status.HTTP_200_OK)


class UserSearch(APIView):
    authentication_classes = settings.AUTH_CLASSES
    permission_classes = settings.PERM_CLASSES

    def search(self, term, user=None):
        users = User.objects.all()
        if user:
            users = user.get_friends()

        matches = []
        names = users.filter(display_full_name=True)\
            .filter(first_name__icontains=term)
        matches += [name for name in names]

        usernames = users.filter(username__icontains=term)
        matches += [user for user in usernames]

        cleaned_matches = []
        for match in matches:
            if match not in cleaned_matches:
                cleaned_matches.append(match)

        cleaned_matches = [user for user in cleaned_matches]

        return cleaned_matches

    def get(self, *args, **kwargs):
        payload = []
        user = None
        get = self.request.GET
        if 'search_terms' in get.keys():
            terms = get['search_terms'].split('_')
            if 'friends' in get.keys():
                user = self.request.user
            for term in terms:
                matches = self.search(term, user)
                payload += matches

            if len(payload) >= 2:
                cleaned_payload = []
                for user in payload:
                    if user not in cleaned_payload:
                        cleaned_payload.append(user)
                payload = cleaned_payload

            payload = [QuickUserSerializer(user).data for user in payload]

        return Response(payload, status=status.HTTP_200_OK)


class UserColorView(APIView):
    def get(self, username, request):
        print(username)
        try:
            user = User.objects.get(username=username)
            colors = {
                'primary_color': user.primary_color,
                'secondary_color': user.secondary_color
            }
            serialized_colors = ColorSerializer(colors)
            if serialized_colors.is_valid():
                return Response(serialized_colors.data, status=status.HTTP_200_OK)
            else:
                return Response({"Error": serialized_colors.errors}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({"100": "no-user"}, status=status.HTTP_100_CONTINUE)
