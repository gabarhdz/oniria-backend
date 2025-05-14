from django.contrib import admin
from .models import Community, Post, PostImage
# Register your models here.

admin.site.register(Community)
admin.site.register(Post)
admin.site.register(PostImage)
