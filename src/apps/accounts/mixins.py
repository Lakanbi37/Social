from .models import UserProfile
from ..posts.models import Post, Story, Album


class ProfileObjectMixin(object):

    def __init__(self):
        self.request = None
        self.user = None

    @property
    def profile(self):
        profile = UserProfile.objects.get(user=self.request.user)
        self.user = profile.user
        return profile

    @property
    def get_posts(self):
        return Post.objects.filter_by_user(self.user)

    @property
    def get_viewable_stories(self):
        _stories = Story.objects.all().exclude(user=self.user)
        stories = []
        for story in _stories:
            if story.check_user(self.user):
                stories.append(story)
        return Story.objects.filter(id__in=[obj.id for obj in stories])

    @property
    def get_albums(self):
        return Album.objects.filter_by_user(self.user)
