from rest_framework.generics import CreateAPIView


class CreateListModelMixin(CreateAPIView):

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get('data', {}), list):
            kwargs["many"] = True
        return super(CreateListModelMixin, self).get_serializer(*args, **kwargs)
