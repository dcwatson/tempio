import datetime
import io

from django.conf import settings
from django.db.models import Count, Q
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from PIL import Image, UnidentifiedImageError

from .models import File, Tag


def index(request, slug=None):
    File.cleanup()
    Tag.cleanup()
    files = File.objects.defer("content").order_by("-date_modified")
    if not request.user.is_superuser:
        files = files.filter(Q(public=True) | Q(owner=request.user))
    if slug:
        files = files.filter(tags__slug=slug)
    return render(
        request,
        "index.html",
        {
            "files": files[:50],
            "tags": Tag.objects.annotate(num_files=Count("files")).order_by("-num_files"),
            "slug": slug,
        },
    )


@csrf_exempt
@require_POST
def upload(request):
    upload = request.FILES["file"]
    if upload.size > settings.TEMPIO_MAX_SIZE:
        return JsonResponse({"error": "File too large."})
    content = upload.read()
    thumbnail = None
    width = None
    height = None
    expires = timezone.now() + datetime.timedelta(days=settings.TEMPIO_DEFAULT_EXPIRATION)
    if upload.content_type.startswith("image/"):
        try:
            im = Image.open(io.BytesIO(content))
            thumb = io.BytesIO()
            width, height = im.size
            im.thumbnail((200, 200))  # TODO: make this configurable
            im.save(thumb, "PNG")
            thumbnail = thumb.getvalue()
        except UnidentifiedImageError:
            pass
    f = File.objects.create(
        name=upload.name,
        content_type=upload.content_type,
        content=content,
        thumbnail=thumbnail,
        owner=request.user,
        date_expires=expires,
        width=width,
        height=height,
    )
    return JsonResponse({"url": f.get_absolute_url()})


def view(request, file_id):
    default_expires = timezone.now() + datetime.timedelta(days=settings.TEMPIO_DEFAULT_EXPIRATION)
    if file_id == "new":
        f = File(name="untitled.txt", content_type="text/plain", owner=request.user, date_expires=default_expires)
    else:
        f = get_object_or_404(File, slug=file_id)
    editable = (f.owner == request.user) or request.user.is_superuser
    if request.method == "POST":
        if editable:
            if "delete" in request.POST:
                f.delete()
            else:
                f.name = request.POST.get("name", f.name)
                f.description = request.POST.get("description", f.description)
                f.public = request.POST.get("public") == "1"
                if "content" in request.POST:
                    f.content = request.POST["content"].encode("utf-8")
                try:
                    expires = datetime.datetime.strptime(request.POST["expires"], "%Y-%m-%d").date()
                    if expires > datetime.date.today():
                        f.date_expires = timezone.now().replace(year=expires.year, month=expires.month, day=expires.day)
                except ValueError:
                    pass
                f.save()
                f.update_tags(request.POST.get("tags", ""))
        return redirect("/")
    return render(request, "view.html", {"file": f, "editable": editable})


def download(request, file_id, as_attachment=False):
    f = get_object_or_404(File, slug=file_id)
    if as_attachment:
        return FileResponse(io.BytesIO(f.content), as_attachment=True, filename=f.name, content_type=f.content_type)
    else:
        return HttpResponse(f.content, content_type=f.content_type)
