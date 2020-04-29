import random

from apps.analytics.models import ProfileViews
from apps.notifications.signals import create_notification
from apps.posts.models import Privacy, Story
from core.utils.utils import create_slug, avatar_upload_location, upload_location
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.utils.translation import ugettext_lazy as _
from rest_framework.reverse import reverse_lazy as rf_lazy

# Create your models here.
User = get_user_model()
# accounts model

GROUP_TYPES = (
    (_('private'), _('Private')),
    (_('public'), _('Public')),

)


class UserProfileManager(models.Manager):
    use_for_related_fields = True

    def all(self):
        qs = self.get_queryset().all()
        try:
            if self.instance:
                qs = qs.exclude(user=self.instance)
        except:
            pass
        return qs

    def toggle_follow(self, user, to_toggle_user):
        user_profile, created = UserProfile.objects.get_or_create(user=user)  # (user_obj, true)
        if to_toggle_user in user_profile.following.all():
            user_profile.following.remove(to_toggle_user)
            added = False
        else:
            user_profile.following.add(to_toggle_user)
            added = True
        return added

    def is_following(self, user, followed_by_user):
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        if created:
            return False
        if followed_by_user in user_profile.following.all():
            return True
        return False

    def recommended(self, user, limit_to=10):
        print(user)
        profile = user.profile
        following = profile.following.all()
        following = profile.get_following()
        qs = self.get_queryset().exclude(user__in=following).exclude(id=profile.id).order_by("?")[:limit_to]
        return qs


class UserProfile(models.Model):
    PUBLIC = _('public')
    PRIVATE = _('private')
    COMPANY = _('company')
    ACCOUNT_TYPE = (
        (PUBLIC, _('Public')),
        (PRIVATE, _('Private')),
        (COMPANY, _('Company'))
    )
    account_type = models.CharField(max_length=30, choices=ACCOUNT_TYPE, default=PUBLIC)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='profile')  # user.profile
    following = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='followed_by')
    avatar = models.ImageField(upload_to=avatar_upload_location, null=True, blank=True)
    bookmarked_accounts = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                                 through="accounts.Bookmark",
                                                 through_fields=("profile", "user"),
                                                 blank=True,
                                                 related_name="bookmarked"
                                                 )
    bookmarked_groups = models.ManyToManyField("accounts.UserGroup", related_name="bookmarked", blank=True)
    privacy = models.OneToOneField("posts.Privacy", on_delete=models.SET_NULL, null=True)
    # user.profile.following -- users i follow
    # user.followed_by -- users that follow me -- reverse relationship

    objects = UserProfileManager()  # UserProfile.objects.all()

    # abc = UserProfileManager() # UserProfile.abc.all()

    class Meta:
        permissions = [("user_profile", _("Profile"))]

    def __str__(self):
        return f"{self.user.username}, {self.account_type}"

    def is_following(self, user):
        if user in self.following.all():
            return True
        return False

    def get_following_count(self):
        return self.following.all().count()

    def get_follower_count(self):
        return self.user.followed_by.all().count()

    def get_profile_views(self):
        view_model = ProfileViews.objects.get(profile=self)
        return view_model.count

    def get_following(self):
        users = self.following.all()  # User.objects.all().exclude(username=self.user.username)
        return users.exclude(username=self.user.username)

    def get_followers(self):
        users = self.user.followed_by.all()
        return users

    @property
    def posts(self):
        return self.user.posts.all()

    def get_follow_url(self):
        return rf_lazy("profiles:follow", kwargs={"username": self.user.username})

    def get_absolute_url(self):
        return rf_lazy("profiles:detail", kwargs={"username": self.user.username})

    def get_api_url(self, user):
        return rf_lazy('accounts-api:profile-detail', kwargs={"username": user.username})


# cfe = User.objects.first()
# User.objects.get_or_create() # (user_obj, true/false)
# cfe.save()

def post_save_user_receiver(sender, instance, created, *args, **kwargs):
    if created:
        new_profile = UserProfile.objects.get_or_create(user=instance)[0]
        privacy = Privacy.objects.create()
        new_profile.privacy = privacy
        new_profile.save()
        Story.objects.create(profile=new_profile)
        # celery + redis
        # deferred task


post_save.connect(post_save_user_receiver, sender=settings.AUTH_USER_MODEL)


class GroupManager(models.Manager):

    def add_group(self, name, bio, _type, admin):
        obj = self.create(name=name, bio=bio, group_type=_type)
        obj.admin.add(admin)
        return obj


class UserGroup(models.Model):
    PUBLIC = _('public')
    PRIVATE = _('private')
    ACCOUNT_TYPE = (
        (PUBLIC, _('Public')),
        (PRIVATE, _('Private'))
    )
    name = models.CharField(max_length=30)
    slug = models.SlugField(blank=True, null=True)
    bio = models.TextField(null=True, blank=True)
    group_type = models.CharField(max_length=30, default=ACCOUNT_TYPE, choices=ACCOUNT_TYPE)
    admin = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='group_admin')
    avatar = models.ImageField(upload_to=upload_location)
    created = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Member',
        through_fields=('group', 'user'),
        related_name='member'
    )

    objects = GroupManager()

    class Meta:
        permissions = [("group_admin", _("Admin")), ("group_member", _("Group Member"))]

    def __str__(self):
        return self.name

    @property
    def posts(self):
        return self.posts.all()


def pre_save_reciever(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance, instance.name)


pre_save.connect(pre_save_reciever, sender=UserGroup)


class MemberModelManager(models.Manager):
    def add_member(self, group, member):
        member, created = self.model.objects.get_or_create(group=group, user=member)
        if not created:
            return False
        return member, created


class Member(models.Model):
    group = models.ForeignKey('accounts.UserGroup', related_name='group_member', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='group_user', on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = MemberModelManager()

    def __str__(self):
        return self.user.username

    def is_admin(self):
        pass


class FavouriteQueryset(models.query.QuerySet):
    def get_obj(self, user):
        qs, created = self.get_or_create(user=user)
        return qs

    def favourites(self, user):
        return sorted(self.get_obj(user).favourites.all(), key=lambda x: random.random)

    def favourited_by(self, user):
        return sorted(self.get_obj(user).favourited_by.all(), key=lambda x: random.random)


class FavouriteManager(models.Manager):

    def get_queryset(self):
        return FavouriteQueryset(self.model, using=self._db)

    def my_favourites(self, user):
        return self.get_queryset().favourites(user)

    def favourited_by(self, user):
        return self.get_queryset().favourited_by(user)


class Favourite(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    favourites = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='favourited_by')
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = FavouriteManager()

    def __str__(self):
        return self.user

    def __unicode__(self):
        return self.user

    def get_favourites(self):
        users = self.favourites.all()
        return users.exclude(username=self.user.username)

    def get_favourited_by(self):
        users = self.user.favourited_by.all()
        return users.exclude(username=self.user.username)

    def add_to_fav(self, user_id):
        user = User.objects.get(id=user_id)
        if user in self.favourites.all():
            self.favourites.remove(user)
            is_fav_user = False
        else:
            self.favourites.add(user)
            is_fav_user = True
        return is_fav_user


def create_notif(instance):
    notification = create_notification.send(
        sender=instance.__class__,
        _from=instance.recommend_by,
        _to=instance.recommend_to,
        _type='recommend',
        post=None,
        message=f'{instance.recommend_by.username} recommended {instance.recommended.username} to you',
        group=None,
        user=instance.recommended
    )
    return notification


class Recommendation(models.Model):
    recommend_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    recommend_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                     related_name='recommend_to')
    recommended = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                    related_name='recommended', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'user recommendation by {self.recommend_by} to {self.recommend_to}'


def recommendation_receiver(sender, instance, created, *args, **kwargs):
    if created:
        create_notif(instance)


post_save.connect(recommendation_receiver, sender=Recommendation)


class BookmarkManager(models.Manager):
    def bookmark(self, profile, user):
        bookmark = self.create(user=user, profile=profile)
        return bookmark


class Bookmark(models.Model):
    profile = models.ForeignKey("accounts.UserProfile", on_delete=models.CASCADE, related_name="bookmarks")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    objects = BookmarkManager()

    def __str__(self):
        return str(self.profile)