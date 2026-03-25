from django.contrib import admin

from .models import Category, News


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "sort_order")
    ordering = ("sort_order", "id")


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "views", "publish_time")
    list_filter = ("category",)
    search_fields = ("title", "description", "content")

