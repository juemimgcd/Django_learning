from rest_framework.exceptions import NotFound
from rest_framework.views import APIView

from common.responses import success_response

from .serializers import (
    CategoryQuerySerializer,
    CategorySerializer,
    NewsDetailQuerySerializer,
    NewsDetailSerializer,
    NewsListQuerySerializer,
    NewsListSerializer,
    RelatedNewsSerializer,
)
from .services import (
    get_news_detail,
    get_news_total,
    get_related_news,
    increase_news_views,
    list_categories,
    list_news,
)


class CategoryListAPIView(APIView):
    def get(self, request):
        query_serializer = CategoryQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        categories = list_categories(**query_serializer.validated_data)
        serializer = CategorySerializer(categories, many=True)
        return success_response(data=serializer.data)


class NewsListAPIView(APIView):
    def get(self, request):
        query_serializer = NewsListQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        category_id = query_serializer.validated_data["category_id"]
        page = query_serializer.validated_data["page"]
        page_size = query_serializer.validated_data["page_size"]
        offset = (page - 1) * page_size

        news_items = list_news(category_id=category_id, skip=offset, limit=page_size)
        total = get_news_total(category_id=category_id)
        has_more = (offset + len(news_items)) < (total or 0)

        serializer = NewsListSerializer(news_items, many=True)
        return success_response(
            data={
                "items": serializer.data,
                "total": total or 0,
                "page": page,
                "pageSize": page_size,
                "hasMore": has_more,
            }
        )


class NewsDetailAPIView(APIView):
    def get(self, request):
        query_serializer = NewsDetailQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        news_id = query_serializer.validated_data["news_id"]
        detail = get_news_detail(news_id=news_id)
        if detail is None:
            raise NotFound("not found")

        increase_news_views(news_id=news_id)
        detail.refresh_from_db()
        related = get_related_news(category_id=detail.category_id, news_id=detail.id)

        return success_response(
            data={
                "detail": NewsDetailSerializer(detail).data,
                "related": RelatedNewsSerializer(related, many=True).data,
            }
        )

