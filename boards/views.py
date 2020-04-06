from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from vivacity_api import settings
from .models import Topic, Board, Comment, BoardLike
from .serializers import TopicSerializer, BoardSerializer, ForumWidgetSerializer, CommentSerializer, \
    CreateCommentSerializer


class TopicView(ListAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer


class BoardViewAll(ListAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer


class BoardView(APIView):

    def get(self, request, *args, **kwargs):
        payload = {}
        slug = kwargs["slug"]
        board = Board.objects.get(slug=slug)
        board.is_viewed()
        board.last_viewed_date = timezone.now()
        board.save()
        serialized_board = BoardSerializer(board)
        payload['board'] = serialized_board.data

        #  Get comments
        comments = Comment.objects.filter(board=board).order_by('-published_on_date')
        serialized_comments = [CommentSerializer(comment).data for comment in comments]
        payload['comments'] = serialized_comments

        return Response(payload, status=status.HTTP_200_OK)


class ForumWidgetView(ListAPIView):

    def get(self, request, *args, **kwargs):
        boards = Board.objects.filter(type=1)\
            .filter(is_active=True)\
            .order_by('published_on_date')
        for board in boards:
            if board.expires_on_date and (board.expires_on_date < timezone.now()):
                board.is_active = False
                board.removed_on_date = timezone.now()
                board.save()
                boards.pop(board)
        serialized_boards = [ForumWidgetSerializer(board, context={'request': request}).data for board in boards]

        return Response(serialized_boards, status=status.HTTP_200_OK)


class BoardCommentCreateView(APIView):
    authentication_classes = settings.AUTH_CLASSES
    permission_classes = settings.PERM_CLASSES

    def post(self, request, *args, **kwargs):
        comment = request.data
        board_pk = comment['board']
        comment['board'] = Board.objects.get(pk=board_pk).pk
        comment['author'] = User.objects.get(username=comment['author']).pk
        comment['published_on_date'] = timezone.now()
        comment_serialized = CreateCommentSerializer(data=comment)

        if comment_serialized.is_valid():
            comment_serialized.save()
            comment = comment_serialized.data
            new_comment = Comment.objects.get(pk=comment['id'])
            serialized_comment = CommentSerializer(new_comment)
            return Response(serialized_comment.data, status=status.HTTP_200_OK)
        else:
            print(comment_serialized.errors)

        return Response({'ERROR': "Data not valid"}, status=status.HTTP_400_BAD_REQUEST)


class BoardLikeCreateView(APIView):

    def put(self, request, object_pk, username):
        board = Board.objects.get(pk=object_pk)
        user = User.objects.get(username=username)
        try:
            like = BoardLike.objects.get(board=board, author=user)
        except ObjectDoesNotExist:
            like = BoardLike.objects.create(board=board, author=user)

        return Response({"Liked": True}, status=status.HTTP_200_OK)


class BoardLikeDeleteView(APIView):

    def put(self, request, object_pk, username):
        board = Board.objects.get(pk=object_pk)
        user = User.objects.get(username=username)
        try:
            BoardLike.objects.get(board=board, author=user).delete()
            return Response({"Success": "Removed like"}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"Error": "Couldn't remove like"}, status=status.HTTP_400_BAD_REQUEST)
