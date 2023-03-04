
from django import forms
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Follow, Group, Post, User


class PostPagesTests(TestCase):
    """
    Класс тестирования html-страниц
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="StasBasov")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
            group=cls.group,
        )

        cls.comment = Comment.objects.create(
            text='Тестовый комментарий',
            post=cls.post,
            author=cls.user
        )

        cls.reverse_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': cls.group.slug}),
            reverse('posts:post_edit', kwargs={'post_id': cls.post.pk}),
            reverse('posts:post_create'),
            reverse('posts:post_detail', kwargs={'post_id': cls.post.pk}),
            reverse('posts:profile', kwargs={'username': cls.post.author}),
        ]
    cache.clear()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        self.templates_pages_names = {
            self.reverse_names[0]: 'posts/index.html',
            self.reverse_names[1]: 'posts/group_list.html',
            self.reverse_names[2]: 'includes/create_post.html',
            self.reverse_names[3]: 'includes/create_post.html',
            self.reverse_names[4]: 'posts/post_detail.html',
            self.reverse_names[5]: 'posts/profile.html',
        }
        for reverse_name, template in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(
                    reverse_name, follow=True
                )
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Список постов в шаблоне index равен ожидаемому контексту."""
        # Тестирование гостя
        cache.clear()
        response = self.guest_client.get(self.reverse_names[0])
        first_object = response.context['page_obj'][0]
        obj_data = {
            first_object.text: 'Тестовый пост',
            first_object.author: self.user,
            first_object.group: self.group,
        }
        for obj, data in obj_data.items():
            with self.subTest(obj=obj):
                self.assertEqual(obj, data)

        # Тестирование аворизованного пользователя
        response = self.authorized_client.get(self.reverse_names[1])
        first_obj = response.context['page_obj'][0]
        obj_data = {
            first_obj.text: 'Тестовый пост',
            first_obj.group: self.group,
            response.context['group']: self.group,
        }
        for obj, data in obj_data.items():
            with self.subTest(obj=obj):
                self.assertEqual(obj, data)

    def test_create_edit_show_correct_context(self):
        """Шаблон create_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.reverse_names[2])
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

        response = self.authorized_client.get(self.reverse_names[3])
        form_fields = {
            "text": forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

        """Шаблон post_detail сформирован с правильным контекстом"""
        response = self.guest_client.get(self.reverse_names[4])
        first_object = response.context.get('post')
        obj_data = {
            first_object.text: 'Тестовый пост',
            first_object.author: self.user,
        }
        for obj, data in obj_data.items():
            with self.subTest(obj=obj):
                self.assertEqual(obj, data)

        """Шаблон profile сформирован с правильным контекстом"""
        response = self.guest_client.get(self.reverse_names[5])
        first_object = response.context['page_obj'][0]
        obj_data = {
            first_object.text: 'Тестовый пост',
            first_object.author: self.user,
            first_object.group: self.group,
        }
        for obj, data in obj_data.items():
            with self.subTest(obj=obj):
                self.assertEqual(obj, data)

    def test_add_comment(self):
        """После успешной отправки комментарий появляется на странице поста."""
        response = self.authorized_client.get(self.reverse_names[4])
        count_comments = 1
        self.assertEqual(len(response.context['comments']), count_comments)
        first_object = response.context['comments'][0]
        comment_text = first_object.text
        self.assertTrue(comment_text, 'Тестовый текст')

    def test_cache_index(self):
        response = self.authorized_client.get(self.reverse_names[0])
        post = Post.objects.first()
        post.delete()
        response_cached = self.authorized_client.get(self.reverse_names[0])
        self.assertContains(response, post.text)
        self.assertContains(response_cached, post.text)
        self.assertEqual(response.content, response_cached.content)


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_follower = User.objects.create_user(
            username='follower',
            email='test_follower_@mail.ru',
            password='test_password')
        cls.user_following = User.objects.create_user(
            username='following',
            email='test_following_@mail.ru',
            password='test_password')
        cls.post = Post.objects.create(
            author=cls.user_following,
            text='Тестовая запись для тестирования')

        cls.reverse_names = [
            (reverse('posts:profile_follow',
                     kwargs={'username': cls.user_follower})),
            (reverse('posts:profile_unfollow',
                     kwargs={'username': cls.user_following})),
            (reverse('posts:follow_index')), ]

    def setUp(self):
        self.client_auth_follower = Client()
        self.client_auth_following = Client()
        self.client_auth_follower.force_login(self.user_follower)
        self.client_auth_following.force_login(self.user_following)

    def test_autorize_follow(self):
        """Авторизованный пользователь может
        подписываться на других пользователей и может
        удалять других пользователей из подписок.
        """
        self.follow_unflow_list = {self.reverse_names[0]:
                                   'posts/profile.html',
                                   self.reverse_names[1]:
                                   'posts/profile.html', }

        for reverse_name, template in self.follow_unflow_list.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client_auth_follower.get(
                    reverse_name, follow=True,
                )
                self.assertIsNotNone(Follow.objects.all().count())
                self.assertTemplateUsed(response, template)

    def test_subscription(self):
        """Новая запись появляется в ленте тех, кто на него подписан."""
        Follow.objects.create(user=self.user_follower,
                              author=self.user_following)
        response = self.client_auth_follower.get(self.reverse_names[2])
        post_text = response.context["page_obj"][0].text
        self.assertEqual(post_text, 'Тестовая запись для тестирования')

    def test_no_subscription(self):
        """Новая запись не появляется
        в ленте тех, кто не подписан."""
        Follow.objects.create(user=self.user_follower,
                              author=self.user_following)
        response = self.client_auth_following.get(self.reverse_names[2])
        self.assertNotIn('Тестовая запись для тестирования',
                         response.content.decode())
