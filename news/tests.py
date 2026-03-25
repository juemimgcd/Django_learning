from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APITestCase

from .models import Category, News


class NewsApiTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Tech", sort_order=1)
        self.other_category = Category.objects.create(name="Sports", sort_order=2)
        self.news_one = News.objects.create(
            title="Django launches",
            description="Framework update",
            content="Detailed content",
            author="OpenAI",
            category=self.category,
            views=3,
            publish_time=timezone.now(),
        )
        self.news_two = News.objects.create(
            title="Another tech story",
            description="Another description",
            content="Another content",
            author="Reporter",
            category=self.category,
            views=8,
            publish_time=timezone.now() - timedelta(hours=1),
        )
        self.news_other = News.objects.create(
            title="Sports story",
            description="Sports description",
            content="Sports content",
            author="Sports reporter",
            category=self.other_category,
            views=5,
            publish_time=timezone.now() - timedelta(days=1),
        )

    def test_categories_endpoint_returns_sorted_list(self):
        response = self.client.get("/api/news/categories", {"skip": 0, "limit": 10})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["code"], 200)
        self.assertEqual(len(response.data["data"]), 2)
        self.assertEqual(response.data["data"][0]["name"], "Tech")

    def test_news_list_returns_paginated_data(self):
        response = self.client.get(
            "/api/news/list",
            {"categoryId": self.category.id, "page": 1, "pageSize": 1},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["total"], 2)
        self.assertEqual(response.data["data"]["page"], 1)
        self.assertEqual(response.data["data"]["pageSize"], 1)
        self.assertTrue(response.data["data"]["hasMore"])
        self.assertEqual(len(response.data["data"]["items"]), 1)

    def test_news_list_rejects_invalid_page_size(self):
        response = self.client.get(
            "/api/news/list",
            {"categoryId": self.category.id, "page": 1, "pageSize": 0},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("pageSize", response.data)

    def test_news_detail_returns_detail_related_and_increments_views(self):
        before_views = self.news_one.views

        response = self.client.get("/api/news/detail", {"id": self.news_one.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["detail"]["id"], self.news_one.id)
        self.assertEqual(len(response.data["data"]["related"]), 1)
        self.assertEqual(response.data["data"]["related"][0]["id"], self.news_two.id)

        self.news_one.refresh_from_db()
        self.assertEqual(self.news_one.views, before_views + 1)

    def test_news_detail_returns_404_when_missing(self):
        response = self.client.get("/api/news/detail", {"id": 9999})

        self.assertEqual(response.status_code, 404)

