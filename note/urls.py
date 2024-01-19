from django.urls import path
from . import views

# Create your views here.
urlpatterns = [
    path("", views.redirect_at_homepage, name="homepage"),
    path("<int:pk>", views.NoteListView.as_view(), name="notes-list"),
    path("note/<int:pk>/", views.NoteDetailView.as_view(), name="note-detail"),
    path("create/", views.NoteCreateView.as_view(), name="note-create"),
    path(
        "profile/",
        views.SharedNoteListView.as_view(),
        name="profile",
    ),
]
