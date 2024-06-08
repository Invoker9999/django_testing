from http import HTTPStatus

from .common import (
    BaseTestCase,
    NOTES_ADD,
    NOTES_DELETE,
    NOTES_DETAIL,
    NOTES_EDIT,
    NOTES_HOME,
    NOTES_LIST,
    NOTES_SUCCESS,
    USERS_LOGIN,
    USERS_LOGOUT,
    USERS_SIGNUP
)


class TestRoutes(BaseTestCase):

    def test_pages_availability_for_clients(self):
        urls_client_statuses = (
            (NOTES_HOME, self.client_anonymous, HTTPStatus.OK),
            (USERS_LOGIN, self.client_anonymous, HTTPStatus.OK),
            (USERS_LOGOUT, self.client_anonymous, HTTPStatus.OK),
            (USERS_SIGNUP, self.client_anonymous, HTTPStatus.OK),
            (NOTES_ADD, self.client_reader, HTTPStatus.OK),
            (NOTES_LIST, self.client_reader, HTTPStatus.OK),
            (NOTES_SUCCESS, self.client_reader, HTTPStatus.OK),
            (NOTES_EDIT, self.client_author, HTTPStatus.OK),
            (NOTES_DELETE, self.client_author, HTTPStatus.OK),
            (NOTES_DETAIL, self.client_author, HTTPStatus.OK),
            (NOTES_EDIT, self.client_reader, HTTPStatus.NOT_FOUND),
            (NOTES_DELETE, self.client_reader, HTTPStatus.NOT_FOUND),
            (NOTES_DETAIL, self.client_reader, HTTPStatus.NOT_FOUND),
        )

        for url, client, status in urls_client_statuses:
            with self.subTest(url=url, client=client, expected_result=status):
                self.assertEqual(client.get(url).status_code, status)

    def test_redirect_for_anonymous_client(self):
        urls_redirects = (
            (NOTES_ADD, f'{USERS_LOGIN}?next={NOTES_ADD}'),
            (NOTES_LIST, f'{USERS_LOGIN}?next={NOTES_LIST}'),
            (NOTES_SUCCESS, f'{USERS_LOGIN}?next={NOTES_SUCCESS}'),
            (NOTES_EDIT, f'{USERS_LOGIN}?next={NOTES_EDIT}'),
            (NOTES_DELETE, f'{USERS_LOGIN}?next={NOTES_DELETE}'),
            (NOTES_DETAIL, f'{USERS_LOGIN}?next={NOTES_DETAIL}'),
        )
        for url, redirect in urls_redirects:
            with self.subTest(url=url, expected_result=USERS_LOGIN):
                self.assertRedirects(
                    self.client_anonymous.get(url),
                    redirect
                )
