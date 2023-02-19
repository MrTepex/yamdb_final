from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (APISignUpViewSet, CategoryViewSet, CommentViewSet,
                    CustomTokenObtainPairViewSet, GenreViewSet,
                    ReviewViewSet, TitleViewSet, UserViewSet)

v1_router = DefaultRouter()
v1_router.register(r'v1/categories', CategoryViewSet, basename='categories')
v1_router.register(r'v1/genres', GenreViewSet, basename='genres')
v1_router.register(r'v1/titles', TitleViewSet, basename='titles')
v1_router.register(r'v1/titles/(?P<title_id>\d+)/reviews', ReviewViewSet,
                   basename='reviews')
v1_router.register(
    r'v1/titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments')
v1_router.register(r'v1/users', UserViewSet, basename='users')

auth_patterns = [
    path('signup/', APISignUpViewSet.as_view()),
    path('token/', CustomTokenObtainPairViewSet.as_view()),
]
urlpatterns = [
    path('', include(v1_router.urls)),
    path('v1/auth/', include(auth_patterns)),
]
