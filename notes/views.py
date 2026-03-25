from django.http import HttpResponse, JsonResponse
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from .permissions import IsAuthorOrReadOnly
from .responses import success_response
from .serializers import (
    NoteCreateSerializer,
    NoteDetailSerializer,
    NoteListQuerySerializer,
    NoteListSerializer,
    NoteUpdateSerializer,
)
from .services import (
    create_note,
    delete_note,
    get_note_detail,
    get_note_total,
    list_notes,
    update_note,
)



# Create your views here.
def home(request):
    return HttpResponse("Welcome to StudyNotes")


def health(request):
    return HttpResponse("OK")


def ping(request):
    return JsonResponse({"message": "pong"})


class NoteListAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self,request):
        query_serializer = NoteListQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        page = query_serializer.validated_data["page"]
        page_size = query_serializer.validated_data["page_size"]
        offset = (page - 1) * page_size

        filters = {
            "status": query_serializer.validated_data.get("status"),
            "author_id": query_serializer.validated_data.get("author_id"),
            "tag_id": query_serializer.validated_data.get("tag_id"),
            "keyword": query_serializer.validated_data.get("keyword"),
            "ordering": query_serializer.validated_data.get("ordering"),
        }

        items = list_notes(skip=offset, limit=page_size, **filters)
        total = get_note_total(
            status=filters["status"],
            author_id=filters["author_id"],
            tag_id=filters["tag_id"],
            keyword=filters["keyword"],
        )

        serializer = NoteListSerializer(items, many=True)
        has_more = (offset + len(items)) < (total or 0)
        return success_response(
            data={
                "items": serializer.data,
                "total": total or 0,
                "page": page,
                "pageSize": page_size,
                "hasMore": has_more,
            }
        )

    def post(self, request):
        serializer = NoteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        note = create_note(
            author=request.user,
            validated_data=serializer.validated_data,
        )
        output = NoteDetailSerializer(note)
        return success_response(data=output.data, status_code=status.HTTP_201_CREATED)


class NoteDetailAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_object(self, pk):
        note = get_note_detail(note_id=pk)
        self.check_object_permissions(self.request, note)
        return note

    def get(self, request, pk):
        note = self.get_object(pk)
        return success_response(data=NoteDetailSerializer(note).data)

    def patch(self, request, pk):
        note = self.get_object(pk)
        serializer = NoteUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        note = update_note(note=note, validated_data=serializer.validated_data)
        return success_response(data=NoteDetailSerializer(note).data)

    def delete(self, request, pk):
        note = self.get_object(pk)
        delete_note(note=note)
        return success_response(data=None)
