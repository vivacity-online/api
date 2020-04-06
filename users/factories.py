from faker import Faker
import factory
from .models import User
import factory
from faker import Faker

from .models import User

faker = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',)

    email = faker.ascii_safe_email()
    username = email.split('@')[0]
    password = faker.word(ext_word_list=None)
    first_name = faker.first_name()
    last_name = faker.last_name()
    date_of_birth = faker.date_of_birth(
        tzinfo=None,
        minimum_age=18,
        maximum_age=115
    )
    location = faker.state()
    occupation = faker.job()
    tag = faker.paragraph(nb_sentences=1, variable_nb_sentences=True, ext_word_list=None)
    bio = faker.paragraph(nb_sentences=4, variable_nb_sentences=True, ext_word_list=None)
    display_full_name = faker.pybool()
    display_date_of_birth = faker.pybool()
    display_location = faker.pybool()
    display_occupation = faker.pybool()
