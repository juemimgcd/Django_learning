import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Comment, Note, Tag
from .services import create_note, get_note_total, list_notes, update_note


User = get_user_model()


class NoteServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="secret123")
        self.tag_python = Tag.objects.create(name="python")
        self.tag_django = Tag.objects.create(name="django")

    def test_create_note_assigns_author_and_tags_from_tag_ids(self):
        note = create_note(
            author=self.user,
            validated_data={
                "title": "Service layer",
                "content": "Move ORM work out of the view.",
                "status": Note.STATUS_DRAFT,
                "tag_ids": [self.tag_python.id, self.tag_django.id],
            },
        )

        self.assertEqual(note.author, self.user)
        self.assertEqual(note.title, "Service layer")
        self.assertCountEqual(note.tags.values_list("name", flat=True), ["python", "django"])

    def test_update_note_changes_selected_fields_and_tags(self):
        note = Note.objects.create(
            author=self.user,
            title="Before",
            content="Old content",
            status=Note.STATUS_DRAFT,
        )
        note.tags.set([self.tag_python])

        updated_note = update_note(
            note=note,
            validated_data={
                "title": "After",
                "status": Note.STATUS_PUBLISHED,
                "tag_ids": [self.tag_django.id],
            },
        )

        self.assertEqual(updated_note.title, "After")
        self.assertEqual(updated_note.status, Note.STATUS_PUBLISHED)
        self.assertCountEqual(updated_note.tags.values_list("name", flat=True), ["django"])

    def test_list_notes_filters_with_skip_and_limit(self):
        other_user = User.objects.create_user(username="bob", password="secret123")

        first = Note.objects.create(
            author=self.user,
            title="Django services",
            content="First note",
            status=Note.STATUS_PUBLISHED,
        )
        second = Note.objects.create(
            author=self.user,
            title="Draft note",
            content="Second note",
            status=Note.STATUS_DRAFT,
        )
        third = Note.objects.create(
            author=other_user,
            title="Django testing",
            content="Third note",
            status=Note.STATUS_PUBLISHED,
        )
        first.tags.set([self.tag_python])
        second.tags.set([self.tag_django])
        third.tags.set([self.tag_python])

        items = list_notes(
            status=Note.STATUS_PUBLISHED,
            author_id=self.user.id,
            tag_id=self.tag_python.id,
            keyword="Django",
            skip=0,
            limit=5,
        )
        total = get_note_total(
            status=Note.STATUS_PUBLISHED,
            author_id=self.user.id,
            tag_id=self.tag_python.id,
            keyword="Django",
        )

        self.assertEqual(total, 1)
        self.assertEqual([note.id for note in items], [first.id])


class NoteApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="secret123")
        self.other_user = User.objects.create_user(username="bob", password="secret123")
        self.tag = Tag.objects.create(name="python")
        self.note = Note.objects.create(
            author=self.user,
            title="Serializer output",
            content="The response comes from serializers.",
            status=Note.STATUS_DRAFT,
        )
        self.note.tags.set([self.tag])
        Comment.objects.create(
            note=self.note,
            author_name="reader",
            content="Nice refactor",
        )

    def test_note_list_returns_fastapi_style_response(self):
        response = self.client.get(
            reverse("note-list"),
            {"page": 1, "pageSize": 10},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["code"], 200)
        self.assertEqual(payload["message"], "success")
        self.assertEqual(payload["data"]["total"], 1)
        self.assertEqual(payload["data"]["page"], 1)
        self.assertEqual(payload["data"]["pageSize"], 10)
        self.assertFalse(payload["data"]["hasMore"])
        self.assertEqual(payload["data"]["items"][0]["author"], "alice")
        self.assertEqual(payload["data"]["items"][0]["tags"][0]["name"], "python")

    def test_note_list_calculates_has_more_from_offset_and_total(self):
        for index in range(6):
            note = Note.objects.create(
                author=self.user,
                title=f"Note {index}",
                content="More results",
                status=Note.STATUS_PUBLISHED,
            )
            note.tags.set([self.tag])

        response = self.client.get(reverse("note-list"), {"page": 1, "pageSize": 2})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["code"], 200)
        self.assertEqual(payload["data"]["total"], 7)
        self.assertTrue(payload["data"]["hasMore"])
        self.assertEqual(payload["data"]["page"], 1)
        self.assertEqual(payload["data"]["pageSize"], 2)
        self.assertEqual(len(payload["data"]["items"]), 2)

    def test_note_create_uses_service_layer_flow(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("note-list"),
            data=json.dumps(
                {
                    "title": "Created note",
                    "content": "This went through the service layer.",
                    "status": Note.STATUS_PUBLISHED,
                    "tag_ids": [self.tag.id],
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertEqual(payload["code"], 201)
        self.assertEqual(payload["message"], "success")
        self.assertEqual(payload["data"]["title"], "Created note")
        self.assertEqual(payload["data"]["author"], "alice")
        self.assertEqual(payload["data"]["tags"][0]["name"], "python")

    def test_note_detail_returns_wrapped_success_response(self):
        response = self.client.get(reverse("note-detail", args=[self.note.id]))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["code"], 200)
        self.assertEqual(payload["message"], "success")
        self.assertEqual(payload["data"]["id"], self.note.id)
        self.assertEqual(payload["data"]["title"], self.note.title)

    def test_note_update_returns_wrapped_success_response(self):
        self.client.force_login(self.user)

        response = self.client.patch(
            reverse("note-detail", args=[self.note.id]),
            data=json.dumps({"title": "Updated title"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["code"], 200)
        self.assertEqual(payload["message"], "success")
        self.assertEqual(payload["data"]["title"], "Updated title")

    def test_note_delete_returns_wrapped_success_response(self):
        self.client.force_login(self.user)

        response = self.client.delete(reverse("note-detail", args=[self.note.id]))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["code"], 200)
        self.assertEqual(payload["message"], "success")
        self.assertIsNone(payload["data"])
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())

    def test_note_delete_requires_owner(self):
        self.client.force_login(self.other_user)

        response = self.client.delete(reverse("note-detail", args=[self.note.id]))

        self.assertEqual(response.status_code, 403)
        self.note.refresh_from_db()
