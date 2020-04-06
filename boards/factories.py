import random

import factory
from faker import Factory

from users.models import User
from .models import Board, Topic

faker = Factory.create()


class TopicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Topic

    title = faker.text(20)
    desc = faker.text()


AUTHORS = User.objects.all()
BOARD_AUTHOR = AUTHORS[random.randint(0, len(AUTHORS) - 1)]


class BoardFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Board
        django_get_or_create = ('title',)

    author = BOARD_AUTHOR
    topic = factory.Iterator(Topic.objects.all())
    title = faker.text(50)
    desc = faker.text()
    content = faker.paragraphs(5)
