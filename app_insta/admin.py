from app_insta.models import Comment, Image, Profile, Relation
from django.contrib import admin
from .models import Image, Profile, Comment, Relation

# Register your models here.
admin.site.register(Image)
admin.site.register(Profile)
admin.site.register(Comment)
admin.site.register(Relation)