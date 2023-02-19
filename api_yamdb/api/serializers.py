from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class ValueFromViewKeyWordArgumentsDefault:
    requires_context = True

    def __init__(self, context_key):
        self.key = context_key

    def __call__(self, serializer_field):
        return serializer_field.context.get('view').kwargs.get(self.key)

    def __repr__(self):
        return '%s()' % self.__class__.__name__


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(default=serializers.CurrentUserDefault(),
                              slug_field='username',
                              read_only=True)
    title = serializers.HiddenField(
        default=ValueFromViewKeyWordArgumentsDefault('title_id'))

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title')
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('author', 'title')
            )
        ]


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug',)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug',)


class TitleListSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True,
                            read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(required=False)

    class Meta:
        model = Title
        fields = ('id', 'genre', 'category', 'rating', 'name', 'year',
                  'description',)


class TitlePostSerializer(serializers.ModelSerializer):
    genre = SlugRelatedField(slug_field='slug',
                             many=True,
                             queryset=Genre.objects.all())
    category = SlugRelatedField(slug_field='slug',
                                queryset=Category.objects.all())

    class Meta:
        model = Title
        fields = ('id', 'genre', 'category', 'name', 'year',
                  'description',)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        model = User


class UserSerializerSignUp(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email'
        )

    def validate(self, value):
        errors = []
        username = value.get('username')
        email = value.get('email')
        if username.lower() == 'me':
            errors.append('Нельзя использовать "me" для username')
        if username.lower() == email.lower():
            errors.append('username не должен совпадать с email')
        if errors:
            raise serializers.ValidationError(errors)
        return value


class APITokenObtainSerializer(serializers.Serializer):

    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user).access_token

    def validate(self, attrs):
        request = self.context.get('request')
        authenticate_kwargs = {
            'request': request,
            'username': request.data.get('username'),
            'confirmation_code': request.data.get('confirmation_code'),
        }
        if request.data.get('username') is None:
            raise serializers.ValidationError('Необходимо указать username')
        user = get_object_or_404(User, username=request.data.get('username'))
        confirmation_code = request.data.get('confirmation_code')
        res = default_token_generator.check_token(user, confirmation_code)
        if not res:
            raise serializers.ValidationError('Неверный код подтверждения')
        self.user = authenticate(**authenticate_kwargs)
        return {'token': str(self.get_token(user))}
