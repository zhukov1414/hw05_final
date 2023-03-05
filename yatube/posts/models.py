from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.deletion import CASCADE

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    slug = models.SlugField(max_length=18, unique=True, verbose_name="Ссылка")
    description = models.TextField(max_length=250, verbose_name="Описание")

    class Meta():
        ordering = ("-pk",)
        verbose_name_plural = "Группы"

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name="Текст")
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор")

    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        related_name="posts",
        on_delete=models.SET_NULL,
        verbose_name="Группа")

    image = models.ImageField(
        "Картинка",
        upload_to="posts/",
        blank=True
    )

    class Meta():
        ordering = ['-pub_date']
        verbose_name_plural = 'Посты'

    def __str__(self) -> str:
        return f"{self.text[:settings.COUNT_POSTS]}"


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Посты',
    )
    author = models.ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    text = models.TextField(verbose_name='Текст')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created',)
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.text} created {self.created}'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=CASCADE,
        related_name="following",
        verbose_name='Автор',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("user", "author"),
                name="unique_pair"
            ),
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f"{self.user.username} follows {self.author.username}"
