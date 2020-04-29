from django.dispatch import Signal

create_notification = Signal(providing_args=['_from', '_to', '_type', 'message', 'post', 'group', 'user'])