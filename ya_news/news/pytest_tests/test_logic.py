from http import HTTPStatus

from django.urls import reverse

import pytest

from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from conftest import TEXT_COMMENT


@pytest.mark.django_db
def test_no_anon_comment(client, news, new_comment_text):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', kwargs={'pk': news.pk})
    client.post(url, data=new_comment_text)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_user_comment(author, author_client, news, new_comment_text):
    """Авторизованный пользователь может отправить комментарий."""
    url = reverse('news:detail', kwargs={'pk': news.pk})
    author_client.post(url, data=new_comment_text)
    comment = Comment.objects.get()
    assert Comment.objects.count() == 1
    assert comment.text == new_comment_text['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_comment_with_banned_words_fails(author_client, news):
    """
    Если комментарий содержит запрещённые слова, он не будет опубликован,
    а форма вернёт ошибку.
    """
    clean_text_data = {
        'text': f'Тестовый текст, {BAD_WORDS[0]}, последующий текст'
    }
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = author_client.post(url, data=clean_text_data)
    assertFormError(response, form='form', field='text', errors=WARNING)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_user_edit_comment(author_client, news, comment,
                                  new_comment_text):
    """Авторизованный пользователь может редактировать свои комментарии."""
    news_url = reverse('news:detail', kwargs={'pk': news.pk})
    comment_url = reverse('news:edit', kwargs={'pk': comment.pk})
    response = author_client.post(comment_url, data=new_comment_text)
    assertRedirects(response, news_url + '#comments')
    comment.refresh_from_db()
    assert comment.text == new_comment_text['text']


@pytest.mark.django_db
def test_author_user_cannot_edit_comment(admin_client, comment,
                                         new_comment_text):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    comment_url = reverse('news:edit', kwargs={'pk': comment.pk})
    response = admin_client.post(comment_url, data=new_comment_text)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == TEXT_COMMENT


@pytest.mark.django_db
def test_author_user_delete_comment(author_client, news, comment):
    """Авторизованный пользователь может удалять свои комментарии."""
    news_url = reverse('news:detail', kwargs={'pk': news.pk})
    comment_url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = author_client.delete(comment_url)
    assertRedirects(response, news_url + '#comments')
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_user_cannot_delete_comment(admin_client, comment):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    comment_url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = admin_client.delete(comment_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
