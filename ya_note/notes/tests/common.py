from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


NOTE_SLUG = 'Slug'

NOTES_ADD = reverse('notes:add')
NOTES_DELETE = reverse('notes:delete', args=(NOTE_SLUG,))
NOTES_DETAIL = reverse('notes:detail', args=(NOTE_SLUG,))
NOTES_EDIT = reverse('notes:edit', args=(NOTE_SLUG,))
NOTES_HOME = reverse('notes:home')
NOTES_LIST = reverse('notes:list')
NOTES_SUCCESS = reverse('notes:success')

USERS_LOGIN = reverse('users:login')
USERS_LOGOUT = reverse('users:logout')
USERS_SIGNUP = reverse('users:signup')


User = get_user_model()


class BaseTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='У. Черчиль')
        cls.client_author = Client()
        cls.client_author.force_login(user=cls.author)

        cls.reader = User.objects.create(username='Читатель заметки')
        cls.client_reader = Client()
        cls.client_reader.force_login(user=cls.reader)

        cls.client_anonymous = Client()

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Просто текст.',
            slug=NOTE_SLUG,
            author=cls.author,
        )

        cls.form_data = {
            'title': 'Заголовок 1',
            'text': 'Просто текст.',
            'slug': 'Slug_1',
        }

        cls.form_new_data = {
            'title': 'Новый заголовок',
            'text': 'Просто новый текст.',
            'slug': 'New_slug',
        }

        cls.form_empty_data = {
            'title': 'Заголовок EMPTY',
            'text': 'Просто текст EMPTY.',
            'slug': '',
        }

        cls.form_repeat_data = {
            'title': 'Заголовок INITIAL',
            'text': 'Просто текст INITIAL.',
            'slug': NOTE_SLUG,
        }
