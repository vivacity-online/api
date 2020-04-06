from django.contrib import admin

from .models import ItemCategory, Item


@admin.register(ItemCategory, Item)
class ItemAdmin(admin.ModelAdmin):
    pass
