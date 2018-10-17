from django.contrib import admin
from django.urls import path

from . import views


urlpatterns = [
    path('', views.index),
    path('upload/', views.upload),
    path('tag/<slug>/', views.index),
    path('admin/', admin.site.urls),
    path('<file_id>/', views.view),
    path('<file_id>/download/', views.download),
]
