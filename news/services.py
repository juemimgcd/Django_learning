from django.db.models import F

from .models import Category, News


def list_categories(*, skip=0, limit=20):
    if limit <= 0:
        return []
    return list(Category.objects.all().order_by("sort_order", "id")[skip: skip + limit])


def list_news(*, category_id, skip=0, limit=10):
    if limit <= 0:
        return []
    return list(
        News.objects.filter(category_id=category_id)
        .order_by("-publish_time", "-id")[skip: skip + limit]
    )


def get_news_total(*, category_id):
    return News.objects.filter(category_id=category_id).count()


def get_news_detail(*, news_id):
    return News.objects.filter(id=news_id).first()


def increase_news_views(*, news_id):
    News.objects.filter(id=news_id).update(views=F("views") + 1)


def get_related_news(*, category_id, news_id, limit=5):
    return list(
        News.objects.filter(category_id=category_id)
        .exclude(id=news_id)
        .order_by("-views", "-publish_time")[:limit]
    )

