from django.urls import path

from . import views


urlpatterns = [
    path("api/news/categories", views.CategoryListAPIView.as_view(), name="news-categories"),
    path("api/news/list", views.NewsListAPIView.as_view(), name="news-list"),
    path("api/news/detail", views.NewsDetailAPIView.as_view(), name="news-detail"),
]

