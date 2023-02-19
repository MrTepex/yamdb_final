from django.db.models import Avg
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenViewBase
from rest_framework.views import APIView

from reviews.models import Category, Genre, Title, Review
from users.models import User
from .permissions import (IsAdminOrSuperuser, IsAdminOrReadOnly,
                          IsAdminModeratorOwnerOrReadOnly,
                          )
from .serializers import (ReviewSerializer, CommentSerializer,
                          CategorySerializer, GenreSerializer,
                          TitleListSerializer, TitlePostSerializer,
                          UserSerializer, APITokenObtainSerializer,
                          UserSerializerSignUp)
from .filters import TitleFilter
from django.conf import settings


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(
        rating=Avg("review__score"),
    ).order_by("name")
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleListSerializer
        return TitlePostSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminModeratorOwnerOrReadOnly]

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        return Review.objects.filter(title=title)

    def perform_create(self, serializer):
        title_id = self.kwargs.get("title_id")
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAdminModeratorOwnerOrReadOnly]

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get("review_id"),
            title=self.kwargs.get("title_id")
        )
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get("title_id")
        review_id = self.kwargs.get("review_id")
        review = get_object_or_404(Review, id=review_id, title=title_id)
        serializer.save(author=self.request.user, review=review)


class CustomTokenObtainPairViewSet(TokenViewBase):
    serializer_class = APITokenObtainSerializer


class APISignUpViewSet(APIView):
    serializer_class = UserSerializerSignUp

    def send_code(self, user, email):
        token = default_token_generator.make_token(user)
        send_mail(
            'res',
            token,
            settings.ADDR_SENT_EMAIL,
            [email]
        )

    def post(self, request):
        serializer = UserSerializerSignUp(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        username = serializer.validated_data['username']
        is_registered = User.objects.filter(
            email=email, username=username)
        if not is_registered.exists():
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            self.send_code(user, email)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            user = get_object_or_404(User, email=email, username=username)
            self.send_code(user, email)
            response = {
                'error': 'Пользователь уже зарегистрирован в системе!'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    pagination_class = LimitOffsetPagination
    permission_classes = [IsAdminOrSuperuser]

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        permission_classes=(IsAuthenticated,)
    )
    def get(self, request):
        if request.method == 'GET':
            serializer = UserSerializer(request.user, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        role = serializer.validated_data.get('role')
        if (
            request.method == 'PATCH'
            and request.user.is_user
            and role is not None
        ):
            serializer = UserSerializer(request.user, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
