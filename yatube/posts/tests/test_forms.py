import shutil
import tempfile

from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings
from posts.forms import PostForm
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Group, Post, User


class PostFormTests(TestCase):
    @classmethod
    def setUp(self):
        super().setUpClass()
        self.user = User.objects.create(username="NoName")
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Описание группы'
        )

        self.post = Post.objects.create(
            text='Тестовая запись',
            author=self.user,
            group=self.group
        )
        self.form = PostForm()
        cache.clear()
    
    @classmethod
    # Удаление временной папки
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()


    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        cache.clear()
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(
            response, reverse("posts:profile",
                              kwargs={"username": self.user.username})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=PostFormTests.group,
                author=PostFormTests.user,
            ).exists()
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit(self):
        """Форма изменяет запись в Post."""
        self.post = Post.objects.create(
            author=self.user,
            text="Тестовый текст",
        )
        self.group = Group.objects.create(
            title="Тестовая группа",
            slug="slug",
            description="Тестовое описание",
        )
        posts_count = Post.objects.count()
        form_data = {"text": "Изменяем текст", "group": self.group.id}
        response = self.authorized_client.post(
            reverse("posts:post_edit", args=({self.post.id})),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse("posts:post_detail",
                              kwargs={"post_id": self.post.id})
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                group=PostFormTests.group,
                author=PostFormTests.user,
            ).exists()
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
