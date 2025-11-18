from rest_framework import serializers

from library.models import Book

class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'price',
            'publication_date'
        ]