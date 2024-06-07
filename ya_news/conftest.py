from datetime import datetime, timedelta

import pytest

from django.conf import settings
from django.utils import timezone


from news.models import News, Comment

NEW_TEXT = 'Новый текст'
TITLE = 'Заголовок'
TEXT_NEWS = 'Текст новости'
TEXT_COMMENT = 'Текст комментария'
NEWS = 'Новость'
TEXT = 'Текст'


@pytest.fixture
def new_comment_text():
    """Новый текст комментария"""
    return {'text': NEW_TEXT}


@pytest.fixture
def author(django_user_model):
    """Автор"""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    """Автор-клиент"""
    client.force_login(author)
    return client


@pytest.fixture
def news():
    """Новости"""
    test_news = News.objects.create(
        title=TITLE,
        text=TEXT_NEWS,
        date=datetime.today(),
    )
    return test_news


@pytest.fixture
def comment(news, author):
    """Комментарий"""
    test_comment = Comment.objects.create(
        author=author,
        news=news,
        text=TEXT_COMMENT,
    )
    return test_comment


@pytest.fixture
def list_news():
    """Список новостей"""
    today, news_list = datetime.today(), []
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE):
        test_news = News.objects.create(
            title=f'{NEWS} {index}',
            text=TEXT_NEWS,
        )
        test_news.date = today - timedelta(days=index)
        test_news.save()
        news_list.append(test_news)
    return news_list


@pytest.fixture
def list_comments(news, author):
    """Список комментариев"""
    now, comment_list = timezone.now(), []
    for index in range(2):
        test_comment = Comment.objects.create(
            author=author,
            news=news,
            text=f'{TEXT} {index}',
        )
        test_comment.created = now + timedelta(days=index)
        test_comment.save()
        comment_list.append(test_comment)
    return comment_list
