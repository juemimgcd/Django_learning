from rest_framework import serializers

from .models import Comment, Note, Tag


class TagSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class CommentSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "author_name", 'content', 'created_at']


class NoteListSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username", read_only=True)
    tags = TagSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Note
        fields = [
            "id",
            "title",
            "author",
            "status",
            "tags",
            "created_at",
            "updated_at",
        ]


class NoteDetailSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username", read_only=True)
    tags = TagSimpleSerializer(many=True, read_only=True)
    comments = CommentSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Note
        fields = [
            "id",
            "title",
            "content",
            "author",
            "status",
            "tags",
            "comments",
            "created_at",
            "updated_at",
        ]


class NoteCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    content = serializers.CharField()
    status = serializers.ChoiceField(
        choices=Note.STATUS_CHOICES,
        required=False,
        default=Note.STATUS_DRAFT,
    )
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        default=list,
    )



class NoteUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200, required=False)
    content = serializers.CharField(required=False)
    status = serializers.ChoiceField(choices=Note.STATUS_CHOICES, required=False)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
    )



class NoteListQuerySerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=Note.STATUS_CHOICES,
        required=False
    )
    authorId = serializers.IntegerField(
        source="author_id",
        required=False,
        min_value=1
    )
    tagId = serializers.IntegerField(
        source="tag_id",
        required=False,
        min_value=1
    )
    keyword = serializers.CharField(
        required=False,
        allow_blank=False
    )
    ordering = serializers.ChoiceField(
        choices=[
            "created_at",
            "-created_at",
            "updated_at",
            "-updated_at",
            "title",
            "-title",
        ],
        required=False,
        default="-created_at"
    )
    page = serializers.IntegerField(
        required=False,
        min_value=1,
        default=1,
    )
    pageSize = serializers.IntegerField(
        source="page_size",
        required=False,
        min_value=1,
        max_value=20,
        default=5,
    )
