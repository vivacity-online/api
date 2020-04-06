from django.contrib import admin

from .models import FullSizeNPC, HeaderImage, Dialogue


@admin.register(FullSizeNPC, HeaderImage, Dialogue)
class MainAdmin(admin.ModelAdmin):
    pass
