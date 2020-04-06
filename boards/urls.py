from django.urls import path

from . import views

urlpatterns = [
    path('view', views.BoardViewAll.as_view(), name="board_view_all"),
    path('view/<str:slug>', views.BoardView.as_view(), name="board_view"),
    path('topic/view', views.TopicView.as_view(), name="topic_view"),
    path('forum/widget', views.ForumWidgetView.as_view(), name="forum_widget"),
    path('comment/create', views.BoardCommentCreateView.as_view(), name="board_comment_create"),
    path('like/create/<int:object_pk>/<str:username>', views.BoardLikeCreateView.as_view(), name="board_like_create"),
    path('like/delete/<int:object_pk>/<str:username>', views.BoardLikeDeleteView.as_view(), name="board_like_delete"),
]
