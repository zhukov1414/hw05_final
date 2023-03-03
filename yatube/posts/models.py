from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.deletion import CASCADE

User = get_user_model()


class Group(models.Model):
    title = models.CharField("Название", max_length=200)
    slug = models.SlugField("Ссылка", max_length=18, unique=True)
    description = models.TextField("Описание", max_length=250)

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts')
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        related_name='posts',
        on_delete=models.SET_NULL)

    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self) -> str:
        return self.text[:settings.COUNT_POSTS]

    class Meta():
        ordering = ['-pub_date']


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    author = models.ForeignKey(
        User,
        on_delete=CASCADE,
        related_name="comments"
    )
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ("-created",)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=CASCADE,
        related_name="follower"
    )
    author = models.ForeignKey(
        User,
        on_delete=CASCADE,
        related_name="following"
    )

    def __str__(self):
        return self.text

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("user", "author"),
                name="unique_pair"
            ),
        ]
