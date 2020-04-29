from apps.notifications.signals import create_notification


def create_notif(instance, recipient=None):
    notification = create_notification.send(
        sender=instance.__class__,
        _from=instance.user,
        _to=recipient,
        _type='mention_post',
        post=instance,
        message=f'{instance.user.username} mentioned you in a post',
        group=None,
        user=None
    )
    return notification
