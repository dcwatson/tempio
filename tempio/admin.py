from django.contrib import admin

from .models import File, Tag


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "content_type", "public", "date_created")
    list_filter = ("public",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("slug",)
