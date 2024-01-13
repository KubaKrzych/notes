from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Note
from .forms import NoteForm
from .models import User, SharedNote
from .mixins import UserHasAccessToNoteMixin
from django.db.models import Q
from .utils import render_markdown_to_safe_html


class NoteListView(ListView):
    model = Note
    context_object_name = "notes"
    ordering = ["date_posted"]
    paginate_by = 5

    def get_queryset(self):
        current_user = self.request.user

        q_objects = Q(sharing_status="P")
        if self.request.user and self.request.user.is_authenticated:
            q_objects |= Q(user=current_user)
            q_objects |= Q(sharednote__shared_with=current_user)
        return Note.objects.filter(q_objects).distinct().order_by("-date_posted")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["heading"] = "Home page"
        return context


class SharedNoteListView(LoginRequiredMixin, NoteListView):
    def get_queryset(self):
        return (
            Note.objects.filter(
                Q(user=self.request.user) | Q(sharednote__shared_with=self.request.user)
            )
            .distinct()
            .order_by("-date_posted")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["heading"] = "Your notes and notes shared with you"
        return context


class NoteDetailView(UserHasAccessToNoteMixin, DetailView):
    model = Note
    context_object_name = "note"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        safe_content = render_markdown_to_safe_html(self.object.content)
        context = self.get_context_data(object=self.object)
        context["safe_content"] = safe_content
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        note = self.get_object()
        if "encryption_key" in request.POST:
            try:
                decrypted = note.decrypt_content(request.POST["encryption_key"])

                rendered_html = render_markdown_to_safe_html(decrypted)
                return JsonResponse({"decrypted": rendered_html}, status=200)
            except ValueError as e:
                return JsonResponse({"error": str(e)}, status=400)
        return JsonResponse({"error": "Invalid request"}, status=400)


class NoteCreateView(LoginRequiredMixin, CreateView):
    model = Note
    form_class = NoteForm
    template_name = "note/note_create.html"
    success_url = reverse_lazy("homepage")

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        note = self.object

        if note.encryption_status == "E" and form.cleaned_data["encryption_key"]:
            note.encrypt_content(form.cleaned_data["encryption_key"])
            note.save()

        if note.sharing_status == "S":
            usernames = form.clean_shared_with_users()
            for username in usernames:
                try:
                    user = User.objects.get(username=username)
                    SharedNote.objects.create(note=note, shared_with=user)
                except User.DoesNotExist:
                    messages.error(
                        self.request,
                        f"User {username} does not exist. Note was not shared with this user.",
                    )

        return response


def redirect_at_homepage(request):
    return redirect("/1")
