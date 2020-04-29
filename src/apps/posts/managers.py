import datetime as dt
from django.db import models
from django.utils.translation import ugettext_lazy as _
from rest_framework.serializers import ValidationError
from rest_framework.generics import get_object_or_404
from core.loading import get_model

FEED_SHARE = _("feed_share")
GROUP_SHARE = _("group_share")
PAGE_SHARE = _("page_share")
FRIEND_SHARE = _("friend_share")


class PostQuerySet(models.QuerySet):

    def filter_by_user(self, user):
        return self.filter(user=user)

    def filter_by_group(self, group):
        return self.filter(group=group)

    def get_shared_posts(self):
        return self.filter(is_shared=True)


class PostManager(models.Manager):

    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)

    def filter_by_user(self, user):
        return self.get_queryset().filter_by_user(user)

    def filter_by_group(self, group):
        return self.get_queryset().filter_by_group(group)

    def shared_posts(self):
        return self.get_queryset().get_shared_posts()

    def create_poll_post(self, user, content, link="", location=""):
        post = self.create(
            post_type="poll",
            user=user,
            content=content,
            location=location,
            share_a_link=link
        )
        return post

    def create_user_post(self, user, content, share_type, mood, link,
                         location, parent_id=None, files=None,
                         is_share=False, shared_user=None, ):
        if files is None:
            files = []
        post = self.model(
            post_type='user',
            user=user,
            content=content,
            mood=mood,
            location=location,
            share_a_link=link
        )
        if parent_id is not None:
            try:
                parent = get_object_or_404(self.model, id=parent_id)  # self.model.get(id=parent_id)
                post.parent = parent
            except Exception as e:
                raise ValidationError({"parent": "Parent post does not exist"})
        if is_share:
            post.is_share = is_share
            if share_type == FEED_SHARE:
                post.share_type = FEED_SHARE
            elif share_type == FRIEND_SHARE or share_type == PAGE_SHARE:
                post.share_type = share_type
                if shared_user is None:
                    raise ValidationError({"share_to": "You have not selected any user to share the post to"})
                post.shared_user = shared_user
            else:
                raise ValidationError({"share_type": "Share type is invalid"})

        new_post_media = list([post.media.add(file) for file in files if files is not []])
        post.save()
        for file in post.media.all():
            file.media_type = "post"
            file.save()
        print(new_post_media)
        return post

    def create_group_post(self, user, group, content, share_type, mood, link,
                          location, parent_id=None, files=None,
                          is_share=False, ):
        if files is None:
            files = []
        if group is None:
            raise ValidationError({"group": "This group field is required"})
        if not user.has_perm("group_member", group):
            raise ValidationError({"user": "Insufficient permission"})
        post = self.model(
            post_type='group',
            user=user,
            group=group,
            content=content,
            mood=mood,
            share_a_link=link,
            location=location
        )
        if parent_id is not None:
            try:
                parent = get_object_or_404(self.model, id=parent_id)  # self.model.get(id=parent_id)
                post.parent = parent
                post.is_parent = True
            except Exception as e:
                raise ValidationError({"parent": "The post no longer exist"})
        if is_share:
            post.is_share = is_share
            if share_type == GROUP_SHARE:
                post.share_type = share_type
                post.shared_group = group
            else:
                raise ValidationError({"share_type": "Share type is invalid"})
        new_post_files = list([post.media.add(file) for file in files if files is not []])
        post.save()
        for file in post.media.all():
            file.media_type = "post"
            file.save()
        print(new_post_files)
        return post


class StoryQuerySet(models.QuerySet):

    def all(self):
        return self.filter(created__lte=dt.timedelta(hours=24))


class StoryManager(models.Manager):

    def get_queryset(self):
        return StoryQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().all()


class AlbumQuerySet(models.QuerySet):

    def filter_by_date(self, date):
        return self.filter(date=date)

    def published(self):
        return self.filter(published=True)

    def filter_by_user(self, user):
        return self.filter(user=user)


class AlbumManager(models.Manager):

    def get_queryset(self):
        return AlbumQuerySet(self.model, using=self._db)

    def add_album(self, user, privacy, published, name="", description="", location="", date=None,  photos=None):
        if photos is None:
            photos = []
        album = self.model(user=user, name=name, description=description,
                           location=location, date=date, published=published)
        album.privacy = privacy
        new_photos = list([album.photos.add(photo) for photo in photos if photos is not []])
        for file in album.photos.all():
            file.media_type = "album"
            file.save()
        print(new_photos)
        album.save()
        return album

    def published(self):
        return self.get_queryset().published()

    def filter_by_date(self, date):
        return self.get_queryset().filter_by_date(date)

    def filter_by_user(self, user):
        return self.get_queryset().filter_by_user(user)


class PollQuerySet(models.QuerySet):

    def filter_by_post(self, post):
        return self.filter(post=post)



