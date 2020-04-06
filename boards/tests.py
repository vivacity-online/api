from django.test import TestCase, Client
from django.utils import timezone

from boards.models import Board, Comment, Topic, deactivate, BoardLike, CommentLike
from users.models import User


class BoardTestCase(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(
            email="boardUser@email.com",
            date_of_birth="1980-03-20",
            username="UserUnAuth",
            password="nonAuthPassword"
        )
        self.board = Board.objects.create(
            author=self.user,
            title="This is the test title",
            desc="Obviously it is a test, it is only a test",
            content="This could go on and on, so i won't let it."
        )

    def test_slug_onSave(self):
        board_with_improper_slug = Board.objects.create(
            author=self.user,
            slug="the slug is here but wrong",
            title="This is the test title",
            desc="Obviously it is a test, it is only a test",
            content="This could go on and on, so i won't let it."
        )
        self.assertEqual(
            board_with_improper_slug.slug,
            "the-slug-is-here-but-wrong"
        )

    def test_activate(self):

        #  Activate boards, is_active=True,
        #  published_on_date-now
        self.board.activate()
        self.assertTrue(self.board.is_active)
        self.assertEqual(self.board.published_on_date.date(), timezone.now().date())

    def test_deactivate(self):
        #  Activate boards initially
        self.board.activate()

        #  Deactivate boards
        deactivated = deactivate(self.board)
        self.assertTrue(deactivated)
        self.assertEqual(self.board.removed_on_date, timezone.now().date())

        #  Board is reactivated
        # initial_pub_date = self.board.published_on_date
        # self.board.activate()
        # self.assertTrue(self.board.is_active)
        # self.assertTrue(self.board.republished)
        # self.assertEqual(initial_pub_date.date(), self.board.published_on_date.date())

    def test_board_count(self):
        self.assertEqual(self.user.board_count, 1)
        Board.objects.create(
            author=self.user,
            slug="the slug but wrong",
            title="This is the te actual st title",
            desc="Obviously it is a test, it is only a test",
            content="This could go on and on, so i won't let it."
        )
        self.assertEqual(self.user.board_count, 2)
        all_boards = Board.objects.all()
        all_boards.delete()
        self.assertEqual(self.user.board_count, 0)

    def test_likes_count(self):
        newerUser = User.objects.create(
            email="newerUser@email.com",
            date_of_birth="1980-03-20",
            username="newAuth",
            password="nonAuthPassword"
        )
        evenNewerUser = User.objects.create(
            email="NewestUser@email.com",
            date_of_birth="1980-03-20",
            username="NewestUserUnAuth",
            password="nonAuthPassword"
        )
        self.assertEqual(self.board.likes, 0)
        BoardLike.objects.create(
            board=self.board,
            author=newerUser
        )
        self.assertEqual(self.board.likes, 1)
        BoardLike.objects.create(
            board=self.board,
            author=evenNewerUser
        )
        self.assertEqual(self.board.likes, 2)
        evenNewerUser.delete()
        self.assertEqual(self.board.likes, 1)

    def test_stats_views(self):
        self.assertEqual(self.board.views, 0)
        self.board.is_viewed()
        self.assertEqual(self.board.views, 1)
        self.board.is_viewed(10)
        self.assertEqual(self.board.views, 11)
        # If value other than int is sent will increase by 1
        self.board.is_viewed("wrong")
        self.assertEqual(self.board.views, 12)

    def test_set_date_if_active(self):
        self.assertFalse(self.board.is_active)
        self.board.is_active = True
        self.board.save()
        self.assertTrue(self.board.published_on_date is not None)
        deactivate(self.board)
        self.assertFalse(self.board.is_active)


class CommentTestCase(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(
            email="boardUser@email.com",
            date_of_birth="1980-03-20",
            username="UserUnAuth",
            password="nonAuthPassword"
        )
        self.board = Board.objects.create(
            author=self.user,
            title="This is the test title",
            desc="Obviously it is a test, it is only a test",
            content="This could go on and on, so i won't let it."
        )
        self.comment = Comment.objects.create(
            board=self.board,
            author=self.user,
            content="This comment is here because I am grateful for this test!"
        )

    def test_comment_to_board(self):
        comment = Comment.objects.filter(board=self.board)
        self.assertEqual(comment.count(), 1)

    def test_get_comments(self):
        board_comments = self.board.comments
        self.assertEqual(len(board_comments), 1)
        board_comments.delete()
        board_comments = self.board.comments
        self.assertFalse(board_comments)

    def test_author_comment(self):
        new_user = User.objects.create(
            email="NewUser@email.com",
            date_of_birth="1988-03-20",
            username="UserName",
            password="Password"
        )
        #  Self.comment by author - this by new_user
        comment = Comment.objects.create(
            board=self.board,
            author=new_user,
            content="This comment is here because I am grateful for this test!"
        )
        self.assertTrue(self.comment.by_author)
        self.assertFalse(comment.by_board_author)

    def test_comment_count(self):
        self.assertEqual(self.user.comment_count, 1)
        Comment.objects.create(
            board=self.board,
            author=self.user,
            content="This comment is here because I am grateful for this test!"
        )
        self.assertEqual(self.user.comment_count, 2)
        all_comments = Comment.objects.all()
        all_comments.delete()
        self.assertEqual(self.user.comment_count, 0)

    def test_likes_count(self):
        newerUser = User.objects.create(
            email="newererUser@email.com",
            date_of_birth="1980-03-20",
            username="newAuth",
            password="nonAuthPassword"
        )
        evenNewerUser = User.objects.create(
            email="NewestestUser@email.com",
            date_of_birth="1980-03-20",
            username="NewestUserUnAuth",
            password="nonAuthPassword"
        )
        comment = self.comment
        self.assertEqual(comment.likes, 0)
        CommentLike.objects.create(
            comment=comment,
            author=newerUser
        )
        self.assertEqual(comment.likes, 1)
        CommentLike.objects.create(
            comment=comment,
            author=evenNewerUser
        )
        self.assertEqual(comment.likes, 2)
        evenNewerUser.delete()
        self.assertEqual(comment.likes, 1)

        # Check that bool returns True if comment is by the same author
        # as the boards itself
        self.assertTrue(comment.by_board_author)


class TopicTestCase(TestCase):

    def setUp(self) -> None:
        self.client = Client()
        self.topic = Topic.objects.create(
            title="Tests and testing",
            desc="All things about tests and the testing of such things"
        )
        self.user = User.objects.create(
            email="boardUser@email.com",
            date_of_birth="1980-03-20",
            username="UserUnAuth",
            password="nonAuthPassword"
        )
        self.announcement = Board.objects.create(
            author=self.user,
            title="Announcement number 1!",
            content="There will be an announcement here! Don't miss it",
        )
        self.board = Board.objects.create(
            author=self.user,
            title="This is the test title",
            desc="Obviously it is a test, it is only a test",
            content="This could go on and on, so i won't let it.",
            topic=self.topic
        )

    def test_total(self):
        self.assertEqual(self.topic.total(), 1)
        self.announcement.topic = self.topic
        self.announcement.save()
        self.assertEqual(self.topic.total(), 2)

    def test_topic_api(self):
        url = '/api/boards/topic/view'
        self.client.login(username="UserUnAuth", password="nonAuthPassword")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
