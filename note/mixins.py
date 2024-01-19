from django.core.exceptions import PermissionDenied
from .models import SharedNote


class UserHasAccessToNoteMixin:
    def dispatch(self, request, *args, **kwargs):
        note = self.get_object()

        if note.sharing_status == "P":
            return super().dispatch(request, *args, **kwargs)

        if note.user == request.user:
            return super().dispatch(request, *args, **kwargs)

        if SharedNote.objects.filter(note=note, shared_with=request.user).exists():
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied
