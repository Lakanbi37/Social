import secrets
from django.utils import timezone
from django.utils.text import slugify
today = timezone.datetime.today().strftime('%Y-%m-%d')
mins = timezone.datetime.today().strftime('%H:%M:%S.%f')
secs = timezone.datetime.today().strftime('%H:%M')


def create_slug(instance, field, new_slug=None):
    slug = slugify(field)
    if new_slug is not None:
        slug = new_slug
    model = instance.__class__
    qs = model.objects.filter(slug=slug).order_by("-id")
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" % (slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug


def generate(size=5):
    return secrets.token_hex(size)


def avatar_upload_location(instance, filename):
    return f"{instance.user.username}/media/profile/profile_pic_{filename}"


video_extensions = ["mp4", "avi", "m4v", "mkv"]
photo_extension = ["jpg", "png", "jpeg", "gif"]


def upload_location(instance, filename):
    file, extension = filename.split(".")
    file_prefix = ""
    if extension in video_extensions:
        file_prefix = "video"
    elif extension in photo_extension:
        file_prefix = "photo"
    if instance.media_type == "post":
        location = f"posts/{today}/{file_prefix}_post/{secs}_{file}_{mins}.{extension}"
    elif instance.media_type == "album":
        location = f"albums/{today}/{file_prefix}_Album/{secs}_{file}_{mins}.{extension}"
    else:
        location = f"stories/{today}/{file_prefix}_story/{secs}_{file}_{mins}.{extension}"
    return location


def media_upload_location(instance, filename):
    # filebase, extension = filename.split(".")
    # return "%s/%s.%s" %(instance.id, instance.id, extension)
    model = instance.__class__
    try:
        new_id = model.objects.order_by("id").last().id + 1
    except:
        new_id = generate(10)
    """
    instance.__class__ gets the model. We must use this method because the model is defined below.
    Then create a queryset ordered by the "id"s of each object, 
    Then we get the last object in the queryset with `.last()`
    Which will give us the most recently created Model instance
    We add 1 to it, so we get what should be the same id as the model we are creating.
    """
    return f"instamedia_{new_id}/{filename}"
    # "%s/%s" % (new_id, filename)
