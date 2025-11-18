from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from library.serializers import BookListSerializer
from library.models import Book


# @api_view(['GET', ])
# def get_all_books(request: Request):
#     data = [
#         {
#             "id": 1,
#             "title": "TEST TITLE 1"
#         },
#         {
#             "id": 2,
#             "title": "TEST TITLE 2"
#         },
#         {
#             "id": 3,
#             "title": "TEST TITLE 3"
#         },
#     ]
#
#     return Response(
#         data=data,
#         status=status.HTTP_200_OK
#     )


@api_view(['GET',])
def get_all_books(request: Request):
    data = Book.objects.all()  # <QuerySet [Book obj, Book obj, ...]>
    response = BookListSerializer(data, many=True)
    return Response(data=response.data,status=status.HTTP_200_OK)

