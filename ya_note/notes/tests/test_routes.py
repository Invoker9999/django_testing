from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Класс TestRoutes предназначен для тестирования маршрутов"""

    TITLE = 'Заголовок'
    TEXT = 'Текст'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Пользователь')
        cls.author_user = User.objects.create(username='Автор пользователь')
        cls.note = Note.objects.create(
            author=cls.user,
            title=cls.TITLE,
            text=cls.TEXT,
        )

    def setUp(self):
        self.user_client = Client()
        self.user_client.force_login(self.user)
        self.author_user_client = Client()
        self.author_user_client.force_login(self.author_user)

    def test_anonymous_user_page_access(self):
        """
        Главная страница доступна анонимному пользователю.
        Страницы регистрации пользователей,
        входа в учётную запись и выхода из неё доступны всем пользователям.
        """
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.user_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_user_page_access(self):
        """
        Аутентифицированному пользователю доступна страница со списком заметок
        notes/, страница успешного добавления заметки done/,
        страница добавления новой заметки add/.
        """
        urls = (
            'notes:list',
            'notes:success',
            'notes:add',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.user_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_access_for_different_user_types(self):
        """
        Страницы отдельной заметки, удаления и редактирования заметки доступны
        только автору заметки.
        Если на эти страницы попытается зайти другой пользователь —
        вернётся ошибка 404.
        """
        users_statuses = (
            (self.user_client, HTTPStatus.OK),
            (self.author_user_client, HTTPStatus.NOT_FOUND),
        )
        urls = (
            'notes:detail',
            'notes:edit',
            'notes:delete',
        )
        for user, status in users_statuses:
            for name in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_page_redirects(self):
        """
        При попытке перейти на страницу списка заметок,
        страницу успешного добавления записи, страницу добавления заметки,
        отдельной заметки, редактирования или удаления заметки анонимный
        пользователь перенаправляется на страницу логина.
        """
        login_url = reverse('users:login')
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
