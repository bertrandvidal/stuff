from snippets.models import Snippet
from snippets.serializers import SnippetSerializer
from rest_framework import generics
from rest_framework import permissions
from django.contrib.auth.models import User
from snippets.serializers import UserSerializer
from snippets.permissions import IsOwnerOrReadOnly
from rest_framework.decorators import api_view, detail_route
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import renderers
from rest_framework import viewsets


@api_view(("GET", ))
def api_root(request, format=None):
    return Response({
        "users": reverse("user-list", request=request, format=format),
        "snippets": reverse("snippet-list", request=request, format=format)
    })


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Automatically provides `list` and `detail` actions.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

class SnippetViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `highlight` action.
    """
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)

    @detail_route(renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
