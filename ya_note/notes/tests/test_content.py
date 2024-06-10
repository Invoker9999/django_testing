from notes.forms import NoteForm
from notes.models import Note

from .common import (
    BaseTestCase,
    NOTE_SLUG,
    NOTES_ADD,
    NOTES_EDIT,
    NOTES_LIST,
)


class TestListNotes(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.notes = Note.objects.bulk_create(
            Note(
                title=f'Заголовок {index}',
                text='Просто текст.',
                slug=NOTE_SLUG + f'{index}',
                author=cls.author,
            )
            for index in range(4)
        )

    def test_notes_one_author(self):
        response = self.client_author.get(NOTES_LIST)
        self.assertIn('object_list', response.context)
        notes = self.client_author.get(NOTES_LIST).context['object_list']
        self.assertIn(self.note, notes)
        self.assertEqual(list(notes).count(self.note), 1)
        note = notes.get(id=self.note.id)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.author, self.note.author)
        self.assertEqual(note.slug, self.note.slug)

    def test_notes_not_available_for_another_author(self):
        self.assertNotIn(
            self.note,
            self.client_reader.get(NOTES_LIST).context['object_list']
        )

    def test_form_include_page(self):
        urls = (NOTES_ADD, NOTES_EDIT)
        for url in urls:
            with self.subTest(url=url):
                context = self.client_author.get(url).context
                self.assertIn('form', context)
                self.assertIsInstance(context['form'], NoteForm)
