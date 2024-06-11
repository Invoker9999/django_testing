from django.conf import settings

from news.forms import CommentForm


def test_max_10_news_on_homepage(client, news_home_url, list_news):
    """Количество новостей на главной странице — не более 10."""
    response = client.get(news_home_url)
    assert 'object_list' in response.context
    assert (
        client.get(news_home_url).context['object_list'].count()
    ) == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_sorted_by_freshness(client, news_home_url, list_news):
    """
    Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    response = client.get(news_home_url)
    assert 'object_list' in response.context
    all_dates = [
        news.date for news in (
            client.get(news_home_url).context['object_list']
        )
    ]
    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_sorted_chronologically(client, news_detail_url,
                                         list_comments):
    """
    Комментарии на странице отдельной новости отсортированы в
    хронологическом порядке: старые в начале списка, новые — в конце.
    """
    all_dates = [
        comment.created
        for comment
        in client.get(news_detail_url).context['news'].comment_set.all()
    ]
    assert all_dates == sorted(all_dates)


def test_anonymous_client_has_no_form(client, news_detail_url):
    """Анонимный клиент без формы."""
    assert 'form' not in client.get(news_detail_url).context


def test_authorized_client_has_form(client_reader, news_detail_url):
    """Авторизованный клиент с формой."""
    context = client_reader.get(news_detail_url).context
    assert 'form' in context
    assert isinstance(context['form'], CommentForm)
