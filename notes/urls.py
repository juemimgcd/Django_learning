from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("health/", views.health, name="health"),
    path("ping/", views.ping, name="ping"),
    path("api/notes/", views.NoteListAPIView.as_view(), name="note-list"),
    path("api/notes/<int:pk>/", views.NoteDetailAPIView.as_view(), name="note-detail"),
]
