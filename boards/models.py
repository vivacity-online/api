from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from vivacity_api.settings import AUTH_USER_MODEL as User


def deactivate(obj):
    obj.is_active = False
    obj.removed_on_date = timezone.now().date()
    return True


class Topic(models.Model):
    title = models.CharField(max_length=250, default="", unique=True)
    desc = models.CharField(max_length=500, default="", blank=True)

    def total(self):
        all_of_topic = Board.objects.filter(topic=self).count()
        return all_of_topic

    def __str__(self):
        return self.title


TYPES = (
    (1, 'board'),
    (2, 'announcement'),
)


class Board(models.Model):
    # General  Board Information
    type = models.IntegerField(choices=TYPES, blank=True, default=1)
    created_on_date = models.DateTimeField(auto_now_add=True)
    published_on_date = models.DateTimeField(default=timezone.now)
    expires_on_date = models.DateTimeField(null=True, blank=True)
    removed_on_date = models.DateTimeField(null=True, blank=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="board_author",
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(blank=True, default=False)

    # Board Content
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name="topic",
        blank=True,
        null=True
    )
    title = models.CharField(max_length=250, default="")
    slug = models.SlugField(max_length=50, default="", blank=True, unique=True)
    desc = models.TextField(max_length=2500, default="", blank=True)
    content = models.TextField(max_length=25000, default="")

    # Board stats
    # TODO create stats class that can be associated with different models
    views = models.IntegerField(default=0)
    last_viewed_date = models.DateTimeField(null=True, blank=True)

    @property
    def likes(self):
        # Determine how many like the boards has
        board_likes = BoardLike.objects.filter(board=self).count()
        return board_likes

    @property
    def liked_by(self):
        # Gets all users who have liked the board
        likes = BoardLike.objects.filter(board=self)
        liked_by = [like.author for like in likes]
        return liked_by

    @property
    def comments(self):
        comments = Comment.objects.filter(board=self)
        return comments if comments.count() >= 1 else False

    def is_viewed(self, amount=None):
        #  Sets views +1 unless amount is set
        if (amount is not None) and (type(amount) == int):
            self.views += amount
        else:
            self.views += 1
        return self.views

    def activate(self):
        self.is_active = True
        self.published_on_date = timezone.now()

    def __str__(self):
        return f'{self.author} -> {self.slug}'

    def save(self, *args, **kwargs):
        if self.is_active:
            self.activate()
        if self.slug == "":
            self.slug = slugify(self.title)
        else:
            self.slug = slugify(self.slug)
        super(Board, self).save(*args, **kwargs)


class Comment(models.Model):
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="comment"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user",
        blank=True
    )

    title = models.CharField(max_length=200, blank=True, null=True)
    published_on_date = models.DateTimeField(blank=True, null=True, default=timezone.now)
    is_active = models.BooleanField(blank=True, default=False)
    content = models.TextField(max_length=2400, default="")

    @property
    def by_board_author(self):
        by_board_author = (self.board.author == self.author)
        return by_board_author

    @property
    def likes(self):
        comment_likes = CommentLike.objects.filter(comment=self).count()
        return comment_likes

    def __str__(self):
        return f'{self.author} - {self.board}'

    def save(self, *args, **kwargs):
        if self.author == self.board.author:
            self.by_author = True
        super(Comment, self).save(*args, **kwargs)


class Like(models.Model):
    class Meta:
        abstract = True

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_on_date = models.DateTimeField(auto_now_add=True)


class CommentLike(Like):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)


class BoardLike(Like):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)

# TODO Add AvatarLikes once Avatar component is up
# class AvatarLike(Like):
#     avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE)
