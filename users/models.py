"""Users are of CustomUser type. Models include all user profile and bio
info as well as user Role and currency tracking/transacting.
Login/Authorization information available here as well"""
import datetime
import os

from django.conf import settings
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from rest_framework.authtoken.models import Token

from boards.models import Board, Comment, BoardLike, CommentLike
# from main.models import FullSizeNPC
from wallet.models import Wallet


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


def get_auth_token(sender):
    if Token.objects.filter(user=sender).exists():
        token = Token.objects.get(user=sender)
        if not token:
            raise ValueError("No token found")
        return token
    else:
        raise ValueError("No user found")


class Role(models.Model):
    title = models.CharField(max_length=250, blank=True, null=True)
    desc = models.TextField(max_length=2500, blank=True, null=True)
    clearance = models.IntegerField(default=1)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs) -> None:
        self.title = self.title.lower()
        super(Role, self).save(*args, **kwargs)


class MyUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, date_of_birth=None, age_verified=None) -> object:
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            password=password,
            date_of_birth=date_of_birth,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, date_of_birth=None, password=None) -> object:
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email=email,
            username=username,
            password=password,
            date_of_birth=date_of_birth,
        )
        #  If user is_admin and no role has been assigned
        # the role of staff will be assigned. There is no further
        # authorizations for this role but to be a placeholder
        role_exists = Role.objects.filter(title="staff").exists()
        if not role_exists:
            Role.objects.create(
                title="staff",
                desc="Basic staff role. No extended authorizations granted",
                clearance=1
            )
        user_role = Role.objects.get(title="staff")
        user.role = user_role
        user.is_admin = True
        user.save(using=self._db)
        return user


class Interest(models.Model):
    title = models.CharField(
        max_length=50,
        blank=False,
        default="",
        null=False,
        unique=True
    )

    def __str__(self):
        return self.title


class User(AbstractBaseUser):

    def upload_to_avatar_dir(self, file):
        """Uploads to avatars directory"""
        uploadTo = os.path.join(f'avatars/{self.username}', file)
        return uploadTo

    def upload_to_thumbnail_dir(self, file):
        """Uploads to thumbnail directory"""
        uploadTo = os.path.join(f'avatars/{self.username}/thumbnail', file)
        return uploadTo

    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    username = models.CharField(
        max_length=250,
        unique=True,
        blank=True,
        null=True,
        default=""
    )
    first_name = models.CharField(max_length=250, default="", blank=True, null=True)
    last_name = models.CharField(max_length=250, default="", blank=True, null=True)
    role = models.ForeignKey(Role, null=True, blank=True, on_delete=models.SET_NULL)
    date_of_birth = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(blank=True, default=False)
    isAuthenticated = models.BooleanField(default=True)
    joined_on = models.DateField(default=timezone.now)
    online = models.BooleanField(default=False)
    email_confirmed = models.BooleanField(default=False)
    primary_color = models.CharField(
        max_length=10,
        default="#8115C4"
    )
    secondary_color = models.CharField(
        max_length=10,
        default="#e67a63"
    )
    wallet = models.ForeignKey(
        Wallet,
        related_name="wallet",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    # PROFILE
    location = models.CharField(
        max_length=250,
        default="",
        null=True,
        blank=True
    )
    occupation = models.CharField(
        max_length=250,
        default="",
        null=True,
        blank=True
    )
    tag = models.CharField(
        max_length=1200,
        default="",
        null=True,
        blank=True
    )
    bio = models.TextField(
        max_length=2400,
        default="",
        null=True,
        blank=True
    )
    interests = models.ManyToManyField(
        Interest,
        blank=True
    )
    friends = models.ManyToManyField(
        'self',
        blank=True
    )

    # For usage once Avatar Builder is operational
    # TODO avatar builder model
    avatar = models.ImageField(
        null=True,
        blank=True,
        upload_to=upload_to_avatar_dir,
        default="avatars/DEFAULT/dressedAvatar-300x516.png"
    )
    avatar_thumbnail = models.ImageField(
        null=True,
        blank=True,
        upload_to=upload_to_thumbnail_dir,
        default="avatars/DEFAULT/thumbnail/avatar-120x120.png"
    )

    # For use before avatar Builder becomes active
    # Uses an NPC character as avatar for now
    # npc_avatar = models.ForeignKey(
    #     FullSizeNPC,
    #     on_delete=models.CASCADE,
    #     blank=True,
    #     null=True
    # )

    # Settings
    display_profile_snackbar = models.BooleanField(default=True)
    display_full_name = models.BooleanField(default=False)
    display_date_of_birth = models.BooleanField(default=False)
    display_location = models.BooleanField(default=False)
    display_occupation = models.BooleanField(default=False)
    IS_ANONYMOUS = models.BooleanField(default=False)  # User is anonymous and cannot interact, but is invisible
    dailyChance = models.BooleanField(default=True)
    dailyChanceDate = models.DateTimeField(default=timezone.now)

    #  Data
    #  Gathered data about user usage and stats
    #  Board Count, Comment Count, Has Liked Count
    @property
    def board_count(self) -> int:
        """Returns the amount of boards the user has"""
        user_boards = Board.objects.filter(author=self)
        if user_boards.count() > 0:
            return user_boards.count()
        else:
            return 0

    @property
    def comment_count(self, show=None) -> int:
        user_comments = Comment.objects.filter(author=self)
        if show:
            return user_comments.all()
        return user_comments.count()

    @property
    def has_liked_count(self) -> int:
        # TODO Add AvatarLikes once Avatar component is up
        user_has_liked_boards = BoardLike.objects.filter(author=self).count()
        user_has_liked_comments = CommentLike.objects.filter(author=self).count()
        return user_has_liked_boards + user_has_liked_comments

    @property
    def shinies(self):
        shinies = self.wallet.shinies
        return shinies

    @property
    def muns(self):
        muns = self.wallet.muns
        return muns

    objects = MyUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'date_of_birth']

    def has_perm(self, perm, obj=None):
        # Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        # "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        # "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    def set_dailyChance(self, state=None):
        if state is None:
            self.dailyChance = False
            self.dailyChanceDate = timezone.now()
            if self.dailyChance is False:
                return True

        if state == "reset":
            now = datetime.datetime.now()
            last_picked = datetime.datetime(
                self.dailyChanceDate.year,
                self.dailyChanceDate.month,
                self.dailyChanceDate.day,
                self.dailyChanceDate.hour,
                self.dailyChanceDate.minute
            )
            # Add day to last_picked to find next available date
            t = last_picked + datetime.timedelta(hours=24)
            # If 24hrs has passed since the last item pick, will reset
            if t <= now:
                self.dailyChance = True
            else:
                self.dailyChance = False
            return True

        if type(state) == bool:
            self.dailyChance = state
            return True

    def add_friend(self, friend):
        try:
            new_friend = User.objects.get(username=friend.username)
            self.friends.add(new_friend)
            return True
        except ObjectDoesNotExist:
            return False

    def get_clearance(self, req=None):
        #  Checks clearance leveled required vs clearance
        #  of user
        if req is not None and type(req) is int:
            # If required clearance is within bounds
            if 10 >= req >= 0:
                return self.role.clearance >= req
            else:
                raise ValueError("Clearance level out of range")
        else:
            return self.role.clearance

    def get_friends(self):
        #  Returns full list of friends from the ManyToMany
        return self.friends.all()

    def check_username(self) -> str:
        #  If username includes "@" wil split on @ and
        #  return the string before @
        if '@' in self.username:
            email = self.username
            user = email.split('@')[0]
            return user
        else:
            return self.username

    def __str__(self):
        return self.username

    def create_wallet(self):
        try:
            wallet = Wallet.objects.get(owner=self.username)
        except ObjectDoesNotExist:
            wallet = Wallet.objects.create(owner=self.username)
        self.wallet = wallet

    def save(self, *args, **kwargs):
        if user := self.check_username():
            #  Format username before saving
            self.username = user

        if not self.role:
            if not self.is_admin:
                #  If user is not admin and no role is assigned
                # the role of 'user' will be used- Role will be
                # created if not existent
                role_exists = Role.objects.filter(title="user").exists()
                if not role_exists:
                    Role.objects.create(
                        title="user",
                        desc="User",
                        clearance=0
                    )
                user_role = Role.objects.get(title="user")

                self.role = user_role
        super(User, self).save(*args, **kwargs)
        if self.wallet is None:
            self.create_wallet()
            self.save()
