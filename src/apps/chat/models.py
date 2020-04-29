from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from core.utils.utils import upload_location


class ThreadManager(models.Manager):
    def by_user(self, user):
        qlookup = Q(first=user) | Q(second=user)
        qlookup2 = Q(first=user) & Q(second=user)
        qs = self.get_queryset().filter(qlookup).exclude(qlookup2).distinct()
        return qs

    def get_or_new(self, user, other_username):  # get_or_create
        username = user.email
        if username == other_username:
            return None
        qlookup1 = Q(first__email=username) & Q(second__email=other_username)
        qlookup2 = Q(first__email=other_username) & Q(second__email=username)
        qs = self.get_queryset().filter(qlookup1 | qlookup2).distinct()
        if qs.count() == 1:
            return qs.first(), False
        elif qs.count() > 1:
            return qs.order_by('timestamp').first(), False
        else:
            Klass = user.__class__
            user2 = Klass.objects.get(email=other_username)
            if user != user2:
                obj = self.model(
                    first=user,
                    second=user2
                )
                obj.save()
                return obj, True
            return None, False


class Thread(models.Model):
    first = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_thread_first')
    second = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_thread_second')
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ThreadManager()

    def __str__(self):
        return self.room_group_name

    @property
    def room_group_name(self):
        return f'chat_{self.id}'

    # def broadcast(self, msg=None):
    #     if msg is not None:
    #         broadcast_msg_to_chat(
    #             msg, group_name=self.room_group_name, user='admin')
    #         return True
    #     return False


class ChatMessageQueryset(models.query.QuerySet):
    def unread(self):
        return self.filter(read=False)


class ChatMessageManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return ChatMessageQueryset(self.model, using=self._db)

    def unread(self):
        return self.get_queryset().unread()

    def read(self, thread, user):
        con = thread.chatmessage_set.unread()
        for c in con:
            if user != c.user:
                c.mark_read()
            else:
                pass

    def unread_mssg_count(self, user):
        unread = []
        chats = self.get_queryset()
        for c in chats:
            if user != c.user:
                if not c.read:
                    unread.append(c)
                else:
                    pass
            else:
                pass
        return unread.__len__()


class ChatMessage(models.Model):
    TEXT = _('text')
    STICKER = _('sticker')
    IMAGE = _('image')
    MESSAGE_TYPE = (
        (TEXT, _('Text')),
        (STICKER, _('Sticker')),
        (IMAGE, _('Image'))
    )
    message_type = models.CharField(
        max_length=120, choices=MESSAGE_TYPE, blank=True, null=True)
    thread = models.ForeignKey(
        Thread, null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             verbose_name='sender', on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True)
    media = models.FileField(upload_to=upload_location, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    objects = ChatMessageManager()

    def mark_read(self):
        self.read = True
        self.save()
