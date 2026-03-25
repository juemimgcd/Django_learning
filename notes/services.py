from django.db import transaction

from .models import Note, Tag


def list_notes(
        status=None,
        author_id=None,
        tag_id=None,
        keyword=None,
        ordering="-created_at",
        skip=0,
        limit=5,
):
    queryset = Note.objects.select_related("author").prefetch_related("tags")

    if status:
        queryset = queryset.filter(status=status)

    if author_id:
        queryset = queryset.filter(author_id=author_id)

    if tag_id:
        queryset = queryset.filter(tags__id=tag_id)

    if keyword:
        queryset = queryset.filter(title__icontains=keyword)

    if limit <= 0:
        return []

    return list(queryset.distinct().order_by(ordering)[skip: skip + limit])


def get_note_total(
        status=None,
        author_id=None,
        tag_id=None,
        keyword=None,
):
    queryset = Note.objects.all()

    if status:
        queryset = queryset.filter(status=status)

    if author_id:
        queryset = queryset.filter(author_id=author_id)

    if tag_id:
        queryset = queryset.filter(tags__id=tag_id)

    if keyword:
        queryset = queryset.filter(title__icontains=keyword)

    return queryset.distinct().count()



def get_note(*, note_id):
    return (
        Note.objects.select_related("author")
        .prefetch_related("tags")
        .get(pk=note_id)
    )


def get_note_detail(*, note_id):
    return (
        Note.objects.select_related("author")
        .prefetch_related("tags", "comments")
        .get(pk=note_id)
    )


@transaction.atomic
def create_note(*, author, validated_data):
    payload = dict(validated_data)
    tag_ids = payload.pop("tag_ids", None)
    tags = payload.pop("tags", None)

    if tags is None:
        tags = Tag.objects.filter(id__in=tag_ids or [])

    note = Note.objects.create(author=author, **payload)

    if tags:
        note.tags.set(tags)

    return get_note(note_id=note.pk)


@transaction.atomic
def update_note(*, note, validated_data):
    payload = dict(validated_data)
    tag_ids = payload.pop("tag_ids", None)
    tags = payload.pop("tags", None)

    if tags is None and tag_ids is not None:
        tags = Tag.objects.filter(id__in=tag_ids)

    updated = False
    for field, value in payload.items():
        setattr(note, field, value)
        updated = True

    if updated:
        note.save()

    if tags is not None:
        note.tags.set(tags)

    return get_note(note_id=note.pk)


def delete_note(*, note):
    note.delete()
