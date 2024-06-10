from http import HTTPStatus

from pytils.translit import slugify

from .common import (
    BaseTestCase,
    NOTES_ADD,
    NOTES_DELETE,
    NOTES_EDIT,
    NOTES_SUCCESS,
)
from notes.forms import WARNING
from notes.models import Note


class TestNoteCreation(BaseTestCase):

    def base_check_create_note(self, form, expected_slug):
        notes = set(Note.objects.all())
        self.client_author.post(NOTES_ADD, data=form)
        notes = set(Note.objects.all()).difference(notes)
        self.assertEqual(len(notes), 1)
        note = notes.pop()
        self.assertEqual(note.title, form['title'])
        self.assertEqual(note.text, form['text'])
        self.assertEqual(note.author, self.author)
        self.assertEqual(note.slug, expected_slug)

    def test_anonymous_client_cant_create_note(self):
        notes = set(Note.objects.all())
        self.assertEqual(
            self.client_anonymous.post(
                NOTES_ADD,
                data=self.form_data
            ).status_code,
            HTTPStatus.FOUND
        )
        self.assertEqual(set(Note.objects.all()), notes)

    def test_client_can_create_note(self):
        self.base_check_create_note(self.form_data, self.form_data['slug'])

    def test_create_note_with_slug_is_none(self):
        self.base_check_create_note(
            self.form_empty_data,
            slugify(self.form_empty_data['title'])
        )

    def test_create_note_with_repeat_slug(self):
        notes = set(Note.objects.all())
        self.assertEqual(
            self.client_author.post(
                NOTES_ADD,
                data=self.form_repeat_data
            ).context.get('form').errors['slug'][0],
            self.form_repeat_data['slug'] + WARNING
        )
        self.assertEqual(set(Note.objects.all()), notes)

    def test_client_cant_edit_note_of_another_client(self):
        note_before = Note.objects.count()
        response = self.client_reader.post(
            NOTES_EDIT,
            data=self.form_new_data
        )
        self.assertEqual(Note.objects.count(), note_before)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.author, self.note.author)
        self.assertEqual(note.slug, self.note.slug)

    def test_client_cant_delete_note_of_another_client(self):
        note_before = Note.objects.count()
        response = self.client_reader.delete(NOTES_DELETE)
        self.assertEqual(Note.objects.count(), note_before)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter(id=self.note.id).exists())
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.author, self.note.author)
        self.assertEqual(note.slug, self.note.slug)

    def test_author_can_edit_note(self):
        response = self.client_author.post(
            NOTES_EDIT,
            data=self.form_new_data
        )
        self.assertRedirects(response, NOTES_SUCCESS)
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.title, self.form_new_data['title'])
        self.assertEqual(note.text, self.form_new_data['text'])
        self.assertEqual(note.author, self.note.author)
        self.assertEqual(note.slug, self.form_new_data['slug'])

    def test_author_can_delete_note(self):
        notes_count = Note.objects.count()
        response = self.client_author.delete(NOTES_DELETE)
        self.assertRedirects(response, NOTES_SUCCESS)
        self.assertEqual(notes_count - Note.objects.count(), 1)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())
