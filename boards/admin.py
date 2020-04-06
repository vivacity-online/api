from django.contrib import admin

from .models import Board, Comment, Topic, BoardLike, CommentLike


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('author', 'title', 'published_on_date', 'views', )


@admin.register(Comment, Topic, BoardLike, CommentLike)
class BoardItemsAdmin(admin.ModelAdmin):
    pass
