from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

app_name='app_insta'

urlpatterns=[
    path('', views.feed, name='feed'),
] 
if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_URL) 