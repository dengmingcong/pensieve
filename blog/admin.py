from django.contrib import admin

from .models import Blog, BlogAuthor, BlogComment, Tag



admin.site.register(Blog)
admin.site.register(BlogAuthor)
admin.site.register(BlogComment)
admin.site.register(Tag)
