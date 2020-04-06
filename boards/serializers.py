from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from boards.models import Board, Topic, Comment


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = "__all__"


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = "__all__"

    published_on_date = serializers.DateTimeField(format='%B.%d.%Y')
    author = serializers.SerializerMethodField()
    liked_by = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    pk = serializers.SerializerMethodField()

    def get_pk(self, board):
        return board.pk

    def get_likes(self, board):
        return board.likes

    def get_liked_by(self, board):
        liked_by = board.liked_by
        users = [user.username for user in liked_by]
        return users

    def get_author(self, board):
        return {
            'username': board.author.username,
            'online': board.author.online,
            'thumbnail': board.author.avatar_thumbnail.url
        }


class ForumWidgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = [
            'pk',
            'author',
            'topic',
            'title',
            'desc',
            'published_on_date',
            'likes',
            'liked_by',
            'slug',
        ]

    published_on_date = serializers.DateTimeField(format='%B.%d.%Y')
    author = serializers.SerializerMethodField()
    liked_by = serializers.SerializerMethodField()

    def get_author(self, board):
        return {
            'username': board.author.username,
            'online': board.author.online,
            'thumbnail': board.author.avatar_thumbnail.url
        }

    def get_liked_by(self, board):
        liked_by = board.liked_by
        users = [user.username for user in liked_by]
        return users


class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"

    published_on_date = serializers.DateTimeField(format='%B.%d.%Y')
    author = serializers.SerializerMethodField()

    def get_author(self, board):
        return {
            'username': board.author.username,
            'online': board.author.online,
            'thumbnail': board.author.avatar_thumbnail.url
        }