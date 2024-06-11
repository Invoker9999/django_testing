from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse

from news.models import Comment, News

TITLE = 'Заголовок'
TEXT_NEWS = 'Текст новости'
TEXT_COMMENT = 'Текст комментария'
NEWS = 'Новость'
TEXT = 'Текст'


@pytest.fixture(autouse=True)
def enable_db(db):
    """Доступ к базе данных для всех тестов без маркера 'django_db'."""
    pass


@pytest.fixture
def comment_delete_url(comment):
    """Страница удаления комментария."""
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def news_detail_url(news):
    """Конфигурация домащней страницы."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def comment_edit_url(comment):
    """Страница редактирования комментария."""
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def news_home_url():
    """Домашняя страница с новостями."""
    return reverse('news:home')


@pytest.fixture
def users_login_url():
    """Страница авторизации пользователя."""
    return reverse('users:login')


@pytest.fixture
def users_logout_url():
    """Страница выхода авторизованного пользователя."""
    return reverse('users:logout')


@pytest.fixture
def users_signup_url():
    """Страница регистрации нового пользователя."""
    return reverse('users:signup')


@pytest.fixture
def expected_for_comment_edit_url(comment_edit_url, users_login_url):
    return f'{users_login_url}?next={comment_edit_url}'


@pytest.fixture
def expected_for_comment_delete_url(comment_delete_url, users_login_url):
    return f'{users_login_url}?next={comment_delete_url}'


@pytest.fixture
def author(django_user_model):
    """Автор."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def client_author(author):
    """Автор-клиент."""
    client = Client()
    client.force_login(user=author)
    return client


@pytest.fixture
def reader(django_user_model):
    """Читатель."""
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def client_reader(reader):
    """Читатель пользователь."""
    client = Client()
    client.force_login(user=reader)
    return client


@pytest.fixture
def news():
    """Новость."""
    test_news = News.objects.create(
        title=TITLE,
        text=TEXT_NEWS,
        date=datetime.today(),
    )
    return test_news


@pytest.fixture
def comment(news, author):
    """Комментарий."""
    test_comment = Comment.objects.create(
        author=author,
        news=news,
        text=TEXT_COMMENT,
    )
    return test_comment


@pytest.fixture
def list_news():
    """Список новостей."""
    News.objects.bulk_create(
        News(
            title=f'{NEWS} {index}',
            text=TEXT_NEWS,
            date=datetime.today() - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def list_comments(news, author):
    """Список комментариев."""
    for index in range(2):
        Comment.objects.create(
            author=author,
            news=news,
            text=f'{TEXT} {index}',
        )
