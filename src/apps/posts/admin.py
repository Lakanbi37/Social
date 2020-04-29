from django.contrib import admin

# Register your models here.
from .models import Post, Story, PostTag, Album, Media


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', '__str__', 'owner', 'liked', 'tags', 'filter')

    class Meta:
        model = Post
        fields = ['post_type', 'user', 'group', 'description',
                  'liked', 'tags', 'media', 'location', 'filter']

    def owner(self, obj):
        if obj.user:
            return obj.user
        return obj.group

    def liked(self, obj):
        return obj.get_likes_count()

    def tags(self, obj):
        return obj.get_tags_count()


admin.site.register(Post, PostAdmin)

# admin.site.register(Post)
admin.site.register(Story)
admin.site.register(Album)
admin.site.register(Media)
admin.site.register(PostTag)
