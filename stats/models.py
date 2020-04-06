from django.db import models


class ObjectStats(models.Model):
    object_class = models.CharField(
        default="",
        max_length=50,
        blank=False,
        null=False
    )
    quantity_sold = models.IntegerField(default=0, blank=True)

    @property
    def is_active(self):
        if hasattr(self.objects, 'is_active'):
            return self.objects.is_active
        else:
            return False

    def __str__(self):
        return self.object_class
