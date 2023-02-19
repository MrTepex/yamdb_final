from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title
from users.models import User


class ReviewsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'text', 'pub_date', 'score')
    search_fields = ('author', 'text',)
    list_filter = ('author', 'text', 'score')
    list_editable = ('text',)
    empty_value_display = '-пусто-'


admin.site.register(User)
admin.site.register(Review, ReviewsAdmin)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Genre)
admin.site.register(Title)
