from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.
from .signals import create_notification

TYPE_CHOICES = (
    (_('post'), _('Post')),
    (_('follow'), _('Follow')),
    (_('like'), _('Like')),
    (_('mention_post'), _('Mention Post')),
    (_('mention_comment'), _('Mention Comment')),
    (_('new con'), _('New Con')),
    (_('invite'), _('Invite')),
    (_('change_admin'), _('Change Admin')),
    (_('recommend'), _('Recommend')),
    (_('add_grp_member'), _('Add Group Member')),
    (_('favourites'), _('Favourites')),
    (_('comment'), _('Comment')),
    (_('shared_your_post'), _('Shared Your Post')),
    (_('share'), _('Share')),
    (_('tag'), _('Tag'))
)


class NotificationQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(active=True)

    def inactive(self):
        return self.filter(active=False)

    def unread(self):
        return self.filter(read=False)


class NotificationManager(models.Manager):
    def get_queryset(self):
        return NotificationQuerySet(self.model, using=self._db)

    def get_notifications(self, user):
        return self.get_queryset().filter(active=True).filter(to_user=user)

    def unread_notifs(self, user):
        return self.get_queryset().unread().filter(active=True).filter(to_user=user)

    def unread_notifs_count(self, user):
        return self.unread_notifs(user).count()


class Notification(models.Model):
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='post')
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='from_user', on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='to_user', on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='recomended_user', blank=True, null=True)
    post = models.ForeignKey('posts.Post', blank=True, null=True, on_delete=models.CASCADE)
    group = models.ForeignKey('accounts.UserGroup', blank=True, null=True, on_delete=models.CASCADE)
    read = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    objects = NotificationManager()

    def __str__(self):
        return self.type

    def __unicode__(self):
        return self.type

    def mark_read(self):
        self.read = True
        self.save()

    def clear_notifs(self):
        self.active = False
        self.save()


def create_notification_reciever(sender, _from, _to, _type, message, post, group, user, *args, **kwargs):
    _notif = Notification()
    _notif.type = _type
    _notif.from_user = _from
    _notif.to_user = _to
    if message is not None:
        _notif.message = message
    if user is not None:
        _notif.user = user
    if post is not None:
        _notif.post = post
    if group is not None:
        _notif.group = group
    _notif.save()


create_notification.connect(create_notification_reciever)
