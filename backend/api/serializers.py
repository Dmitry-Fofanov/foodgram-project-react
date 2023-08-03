from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Follow, Ingredient, Recipe, RecipeIngredient, Tag,
                            User)


class FoodgramUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        read_only_fields = fields

    def get_is_subscribed(self, user):
        if hasattr(user, 'is_subscribed'):
            return user.is_subscribed
        return Follow.objects.filter(
            user=self.context['request'].user,
            author=user,
        ).exists()


class FoodgramUserWithRecipesSerializer(FoodgramUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = FoodgramUserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )
        read_only_fields = fields

    def get_recipes(self, user):
        recipes = user.recipes.all()
        limit = self.context['request'].query_params.get('recipes_limit')
        if limit:
            try:
                recipes = recipes[:int(limit)]
            except ValueError:
                pass
        return RecipeShortSerializer(recipes, many=True).data

    def get_recipes_count(self, user):
        if hasattr(user, 'recipes_count'):
            return user.recipes_count
        return user.recipes.count()


class FoodgramUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount',
        )


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = FoodgramUserSerializer()
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipeingredient_set',
    )
    is_favorited = serializers.BooleanField(
        default=False,
    )
    is_in_shopping_cart = serializers.BooleanField(
        default=False,
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )


class RecipePostSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance = super().create(validated_data)
        for data in ingredients:
            RecipeIngredient(
                recipe=instance,
                ingredient=data['ingredient'],
                amount=data['amount'],
            ).save()

        return instance

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)

        if ingredients:
            instance.ingredients.clear()
            for data in ingredients:
                RecipeIngredient(
                    recipe=instance,
                    ingredient=data['ingredient'],
                    amount=data['amount'],
                ).save()

        return instance


class RecipeShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
