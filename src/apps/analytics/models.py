from django.db import models
from django.conf import settings


# Create your models here.

class ProfileViewsManager(models.Manager):
    def add_views(self, user, profile):
        obj, created = self.model.objects.get_or_create(profile=profile)
        if user in obj.viewers.all():
            print('you have already viewed this profile')
            pass
        elif user == obj.profile.user:
            print('do not defraud us')
            pass
        else:
            obj.viewers.add(user)
            obj.count += 1
            obj.save()
        return obj


class ProfileViews(models.Model):
    viewers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    profile = models.ForeignKey('accounts.UserProfile', on_delete=models.CASCADE, related_name='profile')
    count = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = ProfileViewsManager()

    def __str__(self):
        return f"{self.profile} - {self.count} views"

    def __unicode__(self):
        return f"{self.profile} - {self.count}"


class Tag(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tag = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.tag

