from http import HTTPStatus

from django.test import Client, TestCase

from ..models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="HasNoName")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
        )

        cls.urls = ['/',
                    '/create/',
                    f'/group/{cls.group.slug}/',
                    f'/profile/{cls.user.username}/',
                    f'/posts/{cls.post.pk}/',
                    f'/posts/{cls.post.pk}/edit/',
                    '/follow/', ]

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_error_page_404(self):
        """Несуществующая страница вернет код 404"""
        response = self.guest_client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            self.urls[0]: 'posts/index.html',
            self.urls[1]: 'includes/create_post.html',
            self.urls[2]: 'posts/group_list.html',
            self.urls[3]: 'posts/profile.html',
            self.urls[4]: 'posts/post_detail.html',
            self.urls[5]: 'includes/create_post.html',
            self.urls[6]: 'posts/follow.html',
        }

        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_post_id_edit_url_exists_at_author(self):
        """Страницы доступные только автору."""
        url_names = {
            self.urls[5]: 'includes/create_post.html',
            self.urls[1]: 'includes/create_post.html',
            self.urls[6]: 'posts/follow.html',
        }
        for address, template in url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)
