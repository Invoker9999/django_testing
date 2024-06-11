from http import HTTPStatus

import pytest

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

BAD_WORD_DATA = {'text': 'Текст, {bad_word}, остаток текста'}
FORM_DATA = {'text': 'Текст комментария'}
FORM_NEW_DATA = {'text': 'Новый текст комментария'}


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_by_bad_words(client_author, bad_word, news_detail_url):
    """
    Проверка на запрещенные слова,
    в случае их присутствия форма вернет ошибку.
    """
    comments_before = Comment.objects.count()
    BAD_WORD_DATA['text'] = BAD_WORD_DATA['text'].format(bad_word=bad_word)
    response = client_author.post(
        news_detail_url,
        data=BAD_WORD_DATA
    )
    assert response.context['form'].errors['text'][0] == WARNING
    assert Comment.objects.count() == comments_before


def test_anonymous_client_cant_create_comment(client,
                                              news_detail_url):
    """
    Проверка на невозможность анонимного пользователя
    отправить комментарий.
    """
    comments_before = Comment.objects.count()
    response = client.post(news_detail_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == comments_before


def test_client_can_create_comment(client_reader,
                                   reader,
                                   news,
                                   news_detail_url):
    """
    Проверка на возможность создания комментария
    авторизованным пользователем.
    """
    comments_before = Comment.objects.count()
    reader_id = reader.id
    response = client_reader.post(news_detail_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == comments_before + 1
    Comment.objects.all().delete
    comment_new = Comment.objects.get(id=reader_id)
    assert comment_new.text == FORM_DATA['text']
    assert comment_new.news == news
    assert comment_new.author == reader


def test_author_can_edit_own_comment(client_author,
                                     comment_edit_url,
                                     comment):
    """Проверка на возможность редактирования комментария автору."""
    comments_before = Comment.objects.count()
    assert client_author.post(
        comment_edit_url,
        data=FORM_NEW_DATA
    ).status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == comments_before
    comment_edit = Comment.objects.get(id=comment.id)
    assert comment_edit.text == FORM_NEW_DATA['text']
    assert comment_edit.news == comment.news
    assert comment_edit.author == comment.author


def test_author_can_delete_own_comment(client_author,
                                       comment_delete_url,
                                       comment):
    """Проверка на возможность удаления своего комментария автору."""
    comments_before = Comment.objects.count()
    assert client_author.post(
        comment_delete_url
    ).status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == comments_before - 1
    assert not Comment.objects.filter(pk=comment.pk).exists()


def test_reader_cant_edit_authors_comment(client_reader,
                                          comment_edit_url,
                                          comment):
    """Проверка на невозможность редактирования комментария читателем."""
    comments_before = Comment.objects.count()
    assert client_reader.post(
        comment_edit_url,
        data=FORM_NEW_DATA
    ).status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_before
    comment_cant_edit = Comment.objects.latest('id')
    assert comment_cant_edit.text == comment.text
    assert comment_cant_edit.news == comment.news
    assert comment_cant_edit.author == comment.author


def test_reader_cant_delete_authors_comment(client_reader,
                                            comment_delete_url,
                                            comment):
    """Проверка на невозможность удаления комментария читателем."""
    comments_before = Comment.objects.count()
    assert client_reader.post(
        comment_delete_url
    ).status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_before
    comment_cant_delete = Comment.objects.latest('id')
    assert comment_cant_delete.text == comment.text
    assert comment_cant_delete.news == comment.news
    assert comment_cant_delete.author == comment.author
