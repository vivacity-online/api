from django.test import TestCase
from django.utils import timezone

from users.models import User
from .models import Item, ItemCategory, deactivate


class CategoryTestCase(TestCase):
    def setUp(self) -> None:
        self.category = ItemCategory.objects.create(
            title="Category1",
            description="The first item category for testing"
        )
        self.item1 = Item.objects.create(
            category=self.category,
            title="Item One",
            value=10,
            currency=1,
        )

    def test_category_total(self):
        self.assertEqual(self.category.total(), 1)
        self.assertEqual(self.category.total('activated'), 0)
        self.assertEqual(str(self.category), "Category1")

    def test_deactivate_category(self):
        #  Category has no attribute of is_active so False
        self.assertFalse(deactivate(self.category))


class ItemTestCase(TestCase):
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

    def test_record_sale(self):
        item1 = self.item1
        self.assertEqual(item1.quantity_sold, 0)
        item1.record_sale()
        self.assertEqual(item1.stats.quantity_sold, 1)
        item1.record_sale(5)
        self.assertEqual(item1.stats.quantity_sold, 6)

    def test_deactivate_item(self):
        item1 = self.item1
        self.assertFalse(item1.is_active)
        item1.activate()
        self.assertTrue(item1.is_active)
        self.assertTrue(deactivate(item1))
        item1.save()
        self.assertFalse(item1.is_active)
        self.assertEqual(
            item1.deactivated_on_date.date(),
            timezone.now().date()
        )
