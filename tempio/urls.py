from django.contrib import admin
from django.urls import include, path

from . import api, views

urlpatterns = [
    path("", views.index),
    path("upload/", views.upload),
    path("tag/<slug>/", views.index),
    path("admin/", admin.site.urls),
    path("<file_id>/", views.view),
    path("<file_id>/view/", views.download),
    path("<file_id>/download/", views.download, {"as_attachment": True}),
    path("api/", include([path("files/", api.FilesAPI.as_view()), path("files/<slug>/", api.FilesAPI.as_view())])),
]
