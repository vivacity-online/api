from django.test import TestCase

from items.models import Item, ItemCategory
from users.models import User


class StatsTestCase(TestCase):

    def setUp(self) -> None:
        self.author = User.objects.create_user(
            username="Username",
            email="email.email.com",
            date_of_birth="1909-04-20",
            password="Password123"
        )
        self.category = ItemCategory.objects.create(
            title="Category1",
            description="The first item category for testing"
        )
        self.item1 = Item.objects.create(
            author=self.author,
            category=self.category,
            title="Item One",
            value=10,
            currency=1,
        )

    def test_is_active(self):
        self.assertFalse(self.item1.is_active)

    def test_stats_setup(self):
        self.assertEqual(
            f'{type(self.item1).__name__}#{self.item1.item_number}',
            self.item1.stats.object_class
        )
