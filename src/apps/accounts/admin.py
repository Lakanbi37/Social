from django.contrib import admin

# Register your models here.

from .models import UserProfile, UserGroup, Favourite, Member, Recommendation, Bookmark


class BookMarkInline(admin.TabularInline):
    model = Bookmark


class UserProfileAdmin(admin.ModelAdmin):
    inlines = [BookMarkInline]

    class Meta:
        model = UserProfile


admin.site.register(UserProfile, UserProfileAdmin)


class MemberInline(admin.TabularInline):
    model = Member


class UserGroupAdmin(admin.ModelAdmin):
    inlines = [MemberInline]

    class Meta:
        model = UserGroup


admin.site.register(Favourite)
admin.site.register(UserGroup, UserGroupAdmin)
admin.site.register(Member)
admin.site.register(Recommendation)
