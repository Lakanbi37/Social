from django.contrib import admin

# Register your models here.
from .models import ProfileViews, Tag


admin.site.register(ProfileViews)
admin.site.register(Tag)
