import base64
import json

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.http import Http404, JsonResponse
from django.http.response import HttpResponseBase
from django.views.generic import View

from .models import File, Tag


class APIView(View):
    @property
    def json(self):
        if not hasattr(self, "_json_cache"):
            self._json_cache = json.loads(self.request.body) if self.request.body else {}
        return self._json_cache

    def param(self, name, python_type, default=None, method="GET"):
        data = getattr(self.request, method)
        try:
            return python_type(data[name])
        except Exception:
            return default

    def dispatch(self, request, *args, **kwargs):
        try:
            result = super().dispatch(request, *args, **kwargs)
            if isinstance(result, HttpResponseBase):
                return result
            return JsonResponse(result, json_dumps_params={"indent": 2})
        except (Http404, ObjectDoesNotExist):
            return JsonResponse({"error": "Record not found."}, status=404)
        except Exception as ex:
            return JsonResponse({"error": str(ex)}, status=500)


class FilesAPI(APIView):
    def get(self, request, *args, **kwargs):
        files = File.objects.filter(public=True).defer("content").order_by("-date_modified")
        if "slug" in kwargs:
            files = files.filter(tags__slug=kwargs["slug"])
        num = self.param("n", int, default=25)
        offset = self.param("o", int, default=0)
        tags = Tag.objects.filter(files__in=files).annotate(num_files=Count("files")).order_by("-num_files")
        return {
            "files": [
                {
                    "name": f.name,
                    "slug": f.slug,
                    "content_type": f.content_type,
                    "description": f.description,
                    "tags": [t.slug for t in f.tags.all()],
                    "date_created": f.date_created.isoformat(),
                    "width": f.width,
                    "height": f.height,
                    "download_url": request.build_absolute_uri(f.get_download_url()),
                    "thumbnail": base64.b64encode(f.thumbnail).decode("ascii") if f.thumbnail else None,
                }
                for f in files.prefetch_related("tags")[offset:num]
            ],
            "tags": [
                {"slug": t.slug, "num_files": t.num_files, "api_url": request.build_absolute_uri(t.get_api_url())}
                for t in tags
            ],
        }
