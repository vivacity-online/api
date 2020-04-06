"""Models from the main application API,
including Images, Non playable Characters, Stats
"""
from django.db import models
from django.utils import timezone

from vivacity_api.settings import AUTH_USER_MODEL as User


class StaticImage(models.Model):
    """Base Image class, all other static images used throughout
    the site will be derived from this class
    """

    class Meta:
        abstract = True

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    image = models.ImageField(upload_to="main/images")
    title = models.CharField(max_length=250, blank=True, default="")
    alt = models.CharField(max_length=250, blank=True, default="")
    created_on_date = models.DateTimeField(default=timezone.now)
    activated_on_date = models.DateTimeField(default=timezone.now)
    deactivated_on_date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Dialogue(models.Model):
    """Dialogue used for NPC"""
    content = models.CharField(max_length=250)

    def __str__(self):
        return self.content


class FullSizeNPC(StaticImage):
    """Full sized NPC images as displayed on the header and
    anywhere else that a NPC will be valuable
    """
    image = models.ImageField(upload_to="main/images/NPC")
    dialogue = models.ManyToManyField(Dialogue, blank=True)


class HeaderImage(StaticImage):
    """The main header background image. Not expected to change
    but better to have the option now
    """
    image = models.ImageField(upload_to="main/images/header")


MONTHS = (
    (1, 'January'),
    (2, 'February'),
    (3, 'March'),
    (4, 'April'),
    (5, 'May'),
    (6, 'June'),
    (7, 'July'),
    (8, 'August'),
    (9, 'September'),
    (10, 'October'),
    (11, 'November'),
    (12, 'December')
)
