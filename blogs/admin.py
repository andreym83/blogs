from django.contrib import admin

from blogs.models import Post, Subscriber, Read

admin.site.register(Post)
admin.site.register(Subscriber)
admin.site.register(Read)
