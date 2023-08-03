from django.urls import include, path
from rest_framework import routers

from api.views import (FavoriteView, FollowGetView, FollowView,
                       FoodgramUserViewSet, IngredientViewSet, RecipeViewSet,
                       ShoppingCartDownload, ShoppingCartView, TagViewSet)

router = routers.DefaultRouter()
router.register('users/subscriptions', FollowGetView, 'subscriptions')
router.register('users', FoodgramUserViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet, 'recipes')
router.register('ingredients', IngredientViewSet)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('recipes/<int:id>/favorite/', FavoriteView.as_view()),
    path('recipes/<int:id>/shopping_cart/', ShoppingCartView.as_view()),
    path('recipes/download_shopping_cart/', ShoppingCartDownload.as_view()),
    path('recipes/download_shopping_cart/', ShoppingCartDownload.as_view()),
    path('users/<int:id>/subscribe/', FollowView.as_view()),
    path('', include(router.urls)),
]
