from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone

from stats.models import ObjectStats
from vivacity_api.settings import AUTH_USER_MODEL as User


def deactivate(obj):
    if hasattr(obj, 'is_active'):
        obj.is_active = False
        if hasattr(obj, 'deactivated_on_date'):
            obj.deactivated_on_date = timezone.now()
        return True
    else:
        return False


class ItemCategory(models.Model):
    title = models.CharField(max_length=250, default="", blank=True)
    description = models.CharField(max_length=500, default="", blank=True)

    def total(self, *args):
        category_total = Item.objects.filter(category=self)
        items = {
            'all': category_total.count(),
            'activated': category_total.filter(is_active=True).count()
        }
        for arg in args:
            if arg in items.keys():
                return items[arg]
        return items['all']

    def __str__(self):
        return self.title


class Item(models.Model):
    CURRENCY = [
        (1, 'shinies'),
        (2, 'muns')
    ]

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    category = models.ForeignKey(
        ItemCategory,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    image = models.ImageField(
        upload_to='items/item_image/',
        blank=True,
        null=True
    )
    title = models.CharField(
        max_length=250,
        default="",
        blank=True,
        unique=True
    )
    description = models.TextField(
        max_length=1200,
        default="",
        blank=True
    )
    value = models.IntegerField(
        default=0,
        blank=True
    )
    currency = models.IntegerField(
        choices=CURRENCY,
        default=1
    )
    quantity_sold = models.IntegerField(default=0)

    is_active = models.BooleanField(default=False)
    created_on_date = models.DateTimeField(auto_now_add=True)
    activated_on_date = models.DateTimeField(blank=True, null=True)
    deactivated_on_date = models.DateTimeField(blank=True, null=True)

    create_stats = models.BooleanField(default=True)
    stats = models.ForeignKey(
        ObjectStats,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    @property
    def item_number(self):
        return f'{self.category.pk}-{self.pk}'

    def record_sale(self, quantity=None):
        if type(quantity) is int:
            self.stats.quantity_sold += quantity
        else:
            self.stats.quantity_sold += 1

        return self.stats.quantity_sold

    def activate(self):
        self.is_active = True
        self.activated_on_date = timezone.now()

    def set_stats(self):
        # Create the stats object for item if not exists
        object_type = f'{(type(self).__name__)}#{self.item_number}'
        print(object_type)
        try:
            item_stats = ObjectStats.objects.get(object_class=object_type)
        except ObjectDoesNotExist:
            item_stats = ObjectStats.objects.create(
                object_class=object_type
            )
        self.stats = item_stats

    def save(self, *args, **kwargs):

        super(Item, self).save(*args, **kwargs)
        #  If no stats are present but are needed to be created
        #  will generate a stats object using the objects item#
        if self.create_stats and self.stats is None:
            self.set_stats()
