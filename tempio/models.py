import base64
import datetime
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count
from django.template.defaultfilters import filesizeformat
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.text import slugify


def random_key():
    for attempt in range(5):
        key = get_random_string(7)
        if not File.objects.filter(slug=key).exists():
            return key
    raise RuntimeError("Could not generate a unique slug")


class Tag(models.Model):
    slug = models.SlugField()

    @classmethod
    def cleanup(cls):
        cls.objects.annotate(count=Count("files")).filter(count=0).delete()

    def __str__(self):
        return self.slug

    def get_absolute_url(self):
        return "/tag/{}/".format(self.slug)

    def get_api_url(self):
        return "/api/files/{}/".format(self.slug)


class File(models.Model):
    slug = models.SlugField(unique=True, default=random_key)
    name = models.CharField(max_length=200, blank=True)
    content_type = models.CharField(max_length=250)
    content = models.BinaryField()
    thumbnail = models.BinaryField(null=True, blank=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="files", on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True, related_name="files")
    date_created = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(auto_now=True)
    date_expires = models.DateTimeField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    public = models.BooleanField(default=True)

    @classmethod
    def cleanup(cls):
        cls.objects.filter(date_expires__lt=timezone.now()).delete()
        # Remove transient users periodically.
        User = get_user_model()
        cutoff = timezone.now() - datetime.timedelta(days=settings.TEMPIO_USER_EXPIRATION)
        User.objects.annotate(num_files=Count("files")).filter(date_joined__lt=cutoff, num_files=0).delete()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "/{}/".format(self.slug)

    def get_view_url(self):
        return "{}view/".format(self.get_absolute_url())

    def get_download_url(self):
        return "{}download/".format(self.get_absolute_url())

    @property
    def is_image(self):
        return self.content_type.startswith("image/")

    @property
    def is_text(self):
        return self.content_type.startswith("text/") or "sql" in self.content_type

    @property
    def extension(self):
        name, ext = os.path.splitext(self.name)
        return ext[1:]

    @property
    def template(self):
        if self.is_image:
            return "image.html"
        elif self.is_text:
            return "text.html"
        else:
            return "file.html"

    @property
    def tag_text(self):
        return " ".join(t.slug for t in self.tags.order_by("slug")) if self.pk else ""

    def text(self):
        return self.content.decode("utf-8", "replace") if not self.is_image else ""

    def thumbnail_data(self):
        return (
            "data:image/png;base64,{}".format(base64.b64encode(self.thumbnail).decode("ascii"))
            if self.thumbnail
            else ""
        )

    def properties(self):
        props = {
            "Created": self.date_created,
            "Expires": self.date_expires or "Never",
            "Size": filesizeformat(len(self.content)),
            "Type": self.content_type,
        }
        if self.width:
            props["Width"] = self.width
        if self.height:
            props["Height"] = self.height
            # import exifread
            # tags = exifread.process_file(io.BytesIO(self.content), details=False)
            #  print(tags)
        return props

    def update_tags(self, text):
        tags = []
        for tag in text.split():
            tags.append(Tag.objects.get_or_create(slug=slugify(tag))[0])
        self.tags.set(tags)
        delete_ids = []
        for t in Tag.objects.annotate(num_files=Count("files")):
            if t.num_files == 0:
                delete_ids.append(t.pk)
        Tag.objects.filter(pk__in=delete_ids).delete()
