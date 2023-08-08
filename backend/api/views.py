from http import HTTPStatus

from django.db.models import Count, Exists, OuterRef, Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api import exceptions
from api.mixins import OnlyListViewset
from api.serializers import (FoodgramUserWithRecipesSerializer,
                             IngredientSerializer, RecipePostSerializer,
                             RecipeSerializer, RecipeShortSerializer,
                             TagSerializer)
from recipes.models import (Favorite, Follow, Ingredient, Recipe, ShoppingCart,
                            Tag, User)


class FoodgramUserViewSet(UserViewSet):
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        is_subscribed = user.following.filter(
            author=OuterRef('id'),
        )
        queryset = queryset.annotate(
            is_subscribed=Exists(is_subscribed),
        )
        return queryset


class TagViewSet(ReadOnlyModelViewSet):
    pagination_class = None
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = Recipe.objects.prefetch_related(
            'recipeingredient_set__ingredient',
            'tags',
        )
        data = self.request.query_params

        if data.get('is_favorited'):
            if data['is_favorited'] == '0':
                queryset = queryset.exclude(
                    favorited_by=self.request.user.id
                )
            else:
                queryset = queryset.filter(
                    favorited_by__in=(self.request.user.id,),
                )

        if data.get('is_in_shopping_cart'):
            if data['is_in_shopping_cart'] == '0':
                queryset = queryset.exclude(
                    in_shopping_cart=self.request.user.id
                )
            else:
                queryset = queryset.filter(
                    in_shopping_cart__in=(self.request.user.id,),
                )

        if data.get('author'):
            try:
                int(data['author'])
            except ValueError:
                return Recipe.objects.none()
            queryset = queryset.filter(author=data['author'])

        if data.get('tags'):
            queryset = queryset.filter(tags__slug__in=data.getlist('tags'))

        user = self.request.user

        is_favorited = user.favorite_set.filter(
            recipe=OuterRef('id'),
        )
        is_in_shopping_cart = user.shoppingcart_set.filter(
            recipe=OuterRef('id'),
        )
        queryset = queryset.annotate(
            is_favorited=Exists(is_favorited),
            is_in_shopping_cart=Exists(is_in_shopping_cart),
        ).all()
        return queryset

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipePostSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        instance_serializer = RecipeSerializer(
            instance,
            context={'request': request},
        )
        return Response(instance_serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        instance_serializer = RecipeSerializer(
            instance,
            context={'request': request},
        )
        return Response(instance_serializer.data)


class IngredientViewSet(ReadOnlyModelViewSet):
    pagination_class = None
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    def get_queryset(self):
        name = self.request.query_params.get('name')
        if name:
            return Ingredient.objects.filter(name__istartswith=name).all()
        return Ingredient.objects.all()


class FlagView(APIView):
    model = None
    duplicate_exception = None
    doesnt_exist_exception = None
    target_model = Recipe
    target_serializer = RecipeShortSerializer
    target_name = 'recipe'

    def get_target(self, id):
        return get_object_or_404(self.target_model, id=id)

    def post(self, request, id):
        target = self.get_target(id)
        user = request.user
        if self.model.objects.filter(
            user=user,
            **{self.target_name: target},
        ).exists():
            raise self.duplicate_exception()
        self.model(
            user=user,
            **{self.target_name: target},
        ).save()
        return Response(
            self.target_serializer(
                target,
                context={'request': request},
            ).data,
            status=HTTPStatus.CREATED,
        )

    def delete(self, request, id):
        target = self.get_target(id)
        user = request.user
        if not self.model.objects.filter(
            user=user,
            **{self.target_name: target},
        ).exists():
            raise self.doesnt_exist_exception()
        self.model.objects.get(
            user=user,
            **{self.target_name: target},
        ).delete()
        return Response(
            status=HTTPStatus.NO_CONTENT,
        )


class FavoriteView(FlagView):
    model = Favorite
    duplicate_exception = exceptions.AlreadyFavoriteException
    doesnt_exist_exception = exceptions.NotFavoriteException


class ShoppingCartView(FlagView):
    model = ShoppingCart
    duplicate_exception = exceptions.AlreadyInShoppingCart
    doesnt_exist_exception = exceptions.NotInCartException


class ShoppingCartDownload(APIView):
    def get(self, request):
        ingredients = Ingredient.objects.filter(
            recipes__in_shopping_cart=self.request.user.id,
        ).annotate(amount=Sum('recipeingredient__amount'))

        shopping_cart = '\n'.join(
            f'{i.name}, {i.amount} {i.measurement_unit}'
            for i in ingredients
        ) + '\n'
        response = HttpResponse(
            shopping_cart,
            content_type='text/plain',
        )
        response['Content-Disposition'] = (
            'attachment; filename=ShoppingCart.txt'
        )
        return response


class FollowView(FlagView):
    model = Follow
    duplicate_exception = exceptions.AlreadyFollowingException
    doesnt_exist_exception = exceptions.NotFollowingException
    target_model = User
    target_serializer = FoodgramUserWithRecipesSerializer
    target_name = 'author'


class FollowGetView(OnlyListViewset):
    model = User
    serializer_class = FoodgramUserWithRecipesSerializer

    def get_queryset(self):
        queryset = User.objects.prefetch_related(
            'recipes',
        )
        queryset = queryset.filter(followers__user__in=(self.request.user,))
        queryset = queryset.annotate(recipes_count=Count('recipes'))
        return queryset
