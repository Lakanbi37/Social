import re
from decimal import Decimal as D
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from apps.comments.models import Comment
# Create your models here.
from apps.hashtags.signals import parsed_hashtags
from apps.notifications.signals import create_notification
from core.utils.utils import upload_location
from .managers import *

# Create your models here.

User = get_user_model()


class Privacy(models.Model):
    is_public = models.BooleanField(default=True)
    is_private = models.BooleanField(default=False)
    friends = models.BooleanField(default=False)
    exclude = models.ManyToManyField(User, blank=True, related_name="excluded_users")
    include = models.ManyToManyField(User, blank=True, related_name="included_users")

    def __str__(self):
        return str(self.id)


class Post(models.Model):
    USER = _('user')
    GROUP = _('group')
    POLL = _("poll")
    ACCOUNT_TYPE = (
        (USER, _('User')),
        (GROUP, _('Group')),
        (POLL, _("Poll"))
    )
    # The parent field is a related model to itself. When the original instance of this model is
    # shared it becomes a parent post while the newly created post becomes a child post associated with
    # the shared post which is the parent
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    # Designated whether or not an instance of this model is a parent post. we affirm that by
    # checking if the instant post has no parent post associated with it
    is_parent = models.BooleanField(default=False)
    # Type of post. this field helps distinguish between a user's post and a group post
    post_type = models.CharField(max_length=50, choices=ACCOUNT_TYPE, default=USER)
    # User and group associated with this post object
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL,
                             related_name="posts")
    group = models.ForeignKey('accounts.UserGroup', on_delete=models.SET_NULL, null=True, blank=True,
                              related_name="posts")
    # A comment on top of a posted photo or video. or just plain comment post with no
    # media attached to it
    content = models.TextField(null=True, blank=True)
    # Number of users that has liked this post. This field helps us keep track of
    # the number of likes a given post has for display
    liked = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='liked_posts')
    # Optional fields which shows what the user's mood is or what the user currently is doing at the
    # time the user is posting
    mood = models.CharField(help_text="What are you doing right now", verbose_name="Mood/Activity",
                            null=True,
                            blank=True,
                            max_length=400
                            )
    share_a_link = models.URLField(null=True, blank=True, verbose_name="Share a link", max_length=200)
    tags = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='PostTag',
        through_fields=('post', 'tagged_user'),
        related_name='tagged',
        blank=True)
    # This are the posted media files. (i.e) videos or photos or gif
    media = models.ManyToManyField('Media', blank=True, related_name="posts")
    # Location of the user in the post
    location = models.CharField(max_length=50, blank=True, null=True)
    # filter applied to the post. not really neccessary
    filter = models.CharField(max_length=30, blank=True, null=True, default='filter-normal')
    # The timestamp and updated fields keep tracks of the date the post was created or updated
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # If the post is a poll, There is a need to set the duration which the voting would last
    # after which users are no longer allowed to vote
    poll_expires = models.DateTimeField(null=True, blank=True)
    # For shared posts we get to know the type of share it is (i.e) if you are
    # sharing to users or a group or if you are not sharing to anybody at all
    # thus, there are four types of "Post Share"
    NO_SHARE = _("no_share")
    FEED_SHARE = _("feed_share")
    GROUP_SHARE = _("group_share")
    PAGE_SHARE = _("page_share")
    FRIEND_SHARE = _("friend_share")
    SHARE_CHOICES = (
        (NO_SHARE, _("Not a shared post")),
        (FEED_SHARE, _("Share on your Feeds")),
        (GROUP_SHARE, _("Share on a group")),
        (PAGE_SHARE, _("Share on a page")),
        (FRIEND_SHARE, _("Share on a friends Feeds")),
    )
    share_type = models.CharField(choices=SHARE_CHOICES, default=NO_SHARE, null=True, blank=True, max_length=60)
    # Designates whether or not this model has been shared with any of the options
    # provided
    is_share = models.BooleanField(default=False, verbose_name="Is a shared post ?")
    # if posts are being shared to users or pages we need to keep track of the user the post
    # is being shared to or the profile as the case may be. However if the post is being shared directly
    # to your own profile there would be no need to keep track of anything. thus this field can be null
    shared_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                    related_name="shared_post")
    # The group the post is being shared to if the share type is a group share. just like the previous field
    # this is just to keep track of the group being shared to
    shared_group = models.ForeignKey("accounts.UserGroup", null=True, blank=True,
                                     on_delete=models.SET_NULL, related_name="shared_post")

    objects = PostManager()

    class Meta:
        app_label = "posts"
        verbose_name = "Post"

    def __str__(self):
        if self.post_type == 'user':
            return f"{self.post_type}_post, ({self.user.username})"
        return f"{self.post_type}_post, ({self.group.admin.username})"

    def get_likes_count(self):
        return self.liked.all().count()

    def get_tags_count(self):
        return self.tags.all().count()

    @property
    def poll_votes(self):
        qs = self.poll_choices.all()
        _votes = 0
        for q in qs:
            _votes += int(q.votes.all().count())
        return _votes

    @property
    def poll_voters(self):
        queryset = self.poll_choices.all()
        voters = []
        for query in queryset:
            for user in query.votes.all():
                voters.append(user)
        print(voters)
        return voters

    def like_toggle(self, user):
        if user in self.liked.all():
            self.liked.remove(user)
            return False
        self.liked.add(user)
        return True

    @property
    def likes(self):
        return self.liked.all()

    def get_comment_count(self):
        return self.comments.all().count()

    @property
    def comments(self):
        return Comment.objects.filter_by_instance(self)

    def fetch_for_group(self, group):
        return self.objects.filter(group=group)

    def fetch_for_user(self, user):
        return self.objects.filter(user=user)


def create_notif(recipient, instance, type_='mention_post', message=""):
    notification = create_notification.send(
        sender=instance.__class__,
        _from=instance.user,
        _to=recipient,
        _type=type_,
        post=instance,
        message=message,
        group=None,
        user=None
    )
    return notification


def post_save_receiver(sender, instance, created, *args, **kwargs):
    # if created:
    # notify a user
    user_regex = r'@(?P<username>[\w.@+-]+)'
    reg_users = []
    # mentions
    usernames = re.findall(user_regex, instance.content)
    # send notification to user here.
    for user in usernames:
        try:
            _user = User.objects.get(username=user)
            reg_users.append(_user)
        except Exception as e:
            print(str(e))
            pass
    [create_notif(user, instance, message=f'{instance.user.username} mentioned you in a post') for user in reg_users]

    hash_regex = r'#(?P<hashtag>[\w\d-]+)'
    hashtags = re.findall(hash_regex, instance.content)
    parsed_hashtags.send(sender=instance.__class__, hashtag_list=hashtags)
    # send hashtag signal to user here.


post_save.connect(post_save_receiver, sender=Post)


class PostTag(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    tagged_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tagged_user} tagged in {self.post}"

    def __unicode__(self):
        return f"{self.tagged_user} tagged in {self.post}"


def post_tag_post_save_receiver(sender, instance, created, *args, **kwargs):
    if created:
        create_notif(instance.tagged_user, instance.post.user, "tag", f'{instance.user.username} tagged you in his '
                                                                      f'recent post')


post_save.connect(post_tag_post_save_receiver, sender=PostTag)


class Story(models.Model):
    profile = models.OneToOneField("accounts.UserProfile", on_delete=models.CASCADE)
    media = models.ManyToManyField("Media", blank=True, related_name="stories")
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = StoryManager()

    class Meta:
        verbose_name = "Story"
        verbose_name_plural = "Stories"
        app_label = "posts"

    def __str__(self):
        return self.profile

    def check_user(self, user):
        privacy = self.profile.privacy
        if privacy.is_public:
            return True
        elif privacy.is_private:
            return False
        elif user in privacy.include.all():
            return True
        elif user in privacy.exclude.all():
            return False
        return False

    def add_story(self, files):
        if not files:
            raise ValidationError({"files": "Story must have media files associated"})
        print(f"submitted files: {files}")
        if isinstance(files, list):
            media = [self.media.add(file) for file in files]
            print(f"processed files: {media}")
        else:
            self.media.add(files)
        print(f"submitted files: {files}", f"processed files: {media}")
        return files


class Media(models.Model):
    POST = _("post")
    ALBUM = _("album")
    STORY = _("story")
    MEDIA_CHOICES = (
        (POST, _("Post")),
        (ALBUM, _("Album")),
        (STORY, _("Story"))
    )
    media_type = models.CharField(choices=MEDIA_CHOICES, max_length=30, default=STORY)
    file = models.FileField(upload_to=upload_location, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    background = models.CharField(max_length=150, null=True)
    tag = models.ManyToManyField(settings.AUTH_USER_MODEL, through="MediaTag",
                                 through_fields=("media", "user"), related_name="media_tags")
    feelings = models.CharField(max_length=200, null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    emoji = models.ImageField(null=True, blank=True, upload_to=upload_location)
    filter = models.CharField(max_length=120, default="filter-normal")
    timestamp = models.DateTimeField(auto_now_add=True)
    can_share = models.BooleanField(default=True)

    class Meta:
        app_label = "posts"

    def __str__(self):
        return str(self.id)


class MediaTag(models.Model):
    media = models.ForeignKey(Media, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.media


class Album(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="albums")
    photos = models.ManyToManyField(Media, blank=True, related_name="albums")
    name = models.CharField(max_length=120, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(null=True, blank=True, max_length=200)
    date = models.DateTimeField(auto_now_add=False, auto_now=False)
    tagged_users = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                          through="AlbumTag",
                                          through_fields=("album", "user"))
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=True)
    privacy = models.OneToOneField(Privacy, on_delete=models.SET_NULL, null=True)

    objects = AlbumManager()

    class Meta:
        app_label = "posts"

    def __str__(self):
        return str(self.user)


class AlbumTag(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.album)


class PollsManager(models.Manager):

    def get_queryset(self):
        return PollQuerySet(self.model, using=self._db)

    def calculate(self, poll_id):
        poll = self.get(id=poll_id)
        total_votes = poll.post.poll_votes
        try:
            return int(poll.votes.count()) / total_votes * 100
        except ZeroDivisionError:
            return 0

    def vote(self, poll_id, user):
        try:
            poll = self.get(id=poll_id)
        except Exception:
            raise ValidationError({"poll": "Poll does not exist"})
        post = poll.post
        if user not in post.poll_voters:
            poll.votes.add(user)
            poll.save()
            return True
        return False

    def add_poll_choice(self, choice, post_id=None):
        if post_id is not None:
            try:
                post = Post.objects.get(id=post_id)
            except Exception as e:
                raise ValidationError({"post": "Post does not exist"})
        else:
            raise ValidationError({"post": "This field is required"})
        poll_choice = self.create(post=post, choice=choice)
        return poll_choice


class PollChoice(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="poll_choices")
    choice = models.CharField(max_length=150)
    votes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    objects = PollsManager()

    def __str__(self):
        return f"{str(self.post)} - {self.choice}"

    def voted(self, user):
        return bool(user in self.votes.all())
