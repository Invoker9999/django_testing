from django.conf import settings
from django.urls import reverse

import pytest


@pytest.mark.django_db
def test_max_10_news_on_homepage(client, list_news):
    """Количество новостей на главной странице — не более 10."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_sorted_by_freshness(client, list_news):
    """
    Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    any_news = [test_news for test_news in object_list]
    sorted_news = sorted(any_news, key=lambda x: x.date, reverse=True)
    assert sorted_news == list_news


@pytest.mark.django_db
def test_comments_sorted_chronologically(client, news, list_comments):
    """
    Комментарии на странице отдельной новости отсортированы в
    хронологическом порядке: старые в начале списка, новые — в конце.
    """
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    any_comments = news.comment_set.all()
    assert any_comments[0].created < any_comments[1].created


@pytest.mark.parametrize(
    'parametrized_client, status',
    (
        (pytest.lazy_fixture('client'), False),  # type: ignore
        (pytest.lazy_fixture('author_client'), True),  # type: ignore
    ),
)
@pytest.mark.django_db
def test_comment_form_accessibility(parametrized_client, status, comment):
    """
    Анонимному пользователю недоступна форма для отправки комментария на
    странице отдельной новости, а авторизованному доступна.
    """
    url = reverse('news:detail', kwargs={'pk': comment.pk})
    response = parametrized_client.get(url)
    assert ('form' in response.context) is status
