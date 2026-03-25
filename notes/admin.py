from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import Comment, Note, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "status", "created_at")
    list_filter = ("status", "created_at", "tags")
    search_fields = ("title", "content")
    filter_horizontal = ("tags",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "author_name", "note", "created_at")
    search_fields = ("author_name", "content")