from rest_framework import mixins, viewsets


class OnlyListViewset(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    pass
