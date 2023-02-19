from django.db import models
from users.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    """Модель категорий"""
    name = models.CharField(max_length=100,
                            verbose_name='Категория')
    slug = models.SlugField(unique=True,
                            verbose_name='Относительный адрес категории')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель жанров"""
    name = models.CharField(max_length=50,
                            verbose_name='Жанр')
    slug = models.SlugField(unique=True,
                            verbose_name='Относительный адрес жанра')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель произведений"""
    name = models.CharField(max_length=50,
                            verbose_name='Произведение')
    year = models.PositiveIntegerField(verbose_name='Год выхода',
                                       db_index=True)
    description = models.CharField(max_length=200,
                                   verbose_name='Описание')
    genre = models.ManyToManyField(Genre,
                                   related_name='title',
                                   verbose_name='Жанр',
                                   blank=True)
    category = models.ForeignKey(Category,
                                 on_delete=models.SET_DEFAULT,
                                 related_name='title',
                                 verbose_name='Категория',
                                 blank=True,
                                 default=None
                                 )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель отзывов"""
    text = models.TextField(verbose_name='Содержание отзыва')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='review',
                               verbose_name='Автор')
    score = models.PositiveIntegerField(validators=(
        MinValueValidator(1, message='Оценка должна быть от 1 до 10'),
        MaxValueValidator(10, message='Оценка должна быть от 1 до 10')),
        verbose_name='Средняя оценка',
        blank=True)
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата и время отзыва')
    title = models.ForeignKey(Title,
                              on_delete=models.CASCADE,
                              related_name='review',
                              verbose_name='Произведение',
                              )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review_author'
            )
        ]
        ordering = ('-pub_date',)
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return self.text[:30]


class Comment(models.Model):
    """Модель комментариев к отзывам"""
    review = models.ForeignKey(Review,
                               on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Отзыв',
                               blank=True)

    text = models.TextField(verbose_name='Текст комментария')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Автор комментария')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата и время комментария')

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:30]
