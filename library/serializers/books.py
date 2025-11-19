from typing import Any

from django.db.models import Count
from rest_framework import serializers

from library.models import Book, User


class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'price',
            'publication_date'
        ]


class BookDetailedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class BookCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = (
            'title',
            'description',
            'category',
            'page_count',
            'publisher',
            'contributor',
            'author',
            'price'
        )

    def create(self, validated_data: dict[str, Any]) -> Book:
        contributor = validated_data.get('contributor')

        if not contributor:
            top_contributor = (
                Book.objects
                .values('contributor_id')
                .annotate(
                    books_count=Count('id')
                )
                .order_by('-books_count')
                .first()
            )['contributor_id']

            user = User.objects.get(pk=top_contributor)

            validated_data['contributor'] = user

        book = Book.objects.create(**validated_data)

        return book


class BookUpdateSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.0,
        write_only=True
    )

    discounted_percent = serializers.DecimalField(
        max_digits=4,
        decimal_places=2,  # 99.99
        required=False,
        write_only=True,
        help_text='Процент для построения скидки на книгу',
        min_value=0,
        max_value=99.99
    )

    class Meta:
        model = Book
        fields = (
            'title',
            'description',
            'category',
            'page_count',
            'publisher',
            'author',
            'price',
            'discounted_percent'
        )

    def update(self, instance: Book, validated_data: dict[str, Any]):
        discounted_percent = validated_data.pop('discounted_percent', None)

        if discounted_percent and ('price' in validated_data or instance.price is not None):
            price = validated_data.get('price') or instance.price

            discount_amount = price * ((100 - discounted_percent) / 100)  # discounted_percent = 80 => 0.8
            validated_data['discounted_price'] = discount_amount

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance
