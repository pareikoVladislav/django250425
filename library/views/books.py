from datetime import datetime

from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import (
    BasePermission,
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    IsAdminUser
)

from library.models import Book
from library.serializers import (
    BookListSerializer,
    BookDetailedSerializer,
    BookCreateSerializer,
    BookUpdateSerializer
)
from library.permissions.book import IsOwnerOrReadOnly



# class UserBookListGenericView(ListAPIView):
#     serializer_class = BookListSerializer
#
#     def get_queryset(self):
#         qs = Book.objects.filter(
#             contributor=self.request.user
#         )
#
#         return qs

class BookViewSet(ModelViewSet):
    # serializer_class = BookListSerializer
    queryset = Book.objects.all()

    def get_permissions(self):
        if any(act in self.action for act in {'retrieve', 'update', 'partial_update', 'destroy'}):
            return [IsOwnerOrReadOnly()]
        return super().get_permissions()

    def get_serializer_class(self):
        if 'list' in self.action or 'get_user_books' in self.action:
            return BookListSerializer
        if 'retrieve' in self.action:
            return BookDetailedSerializer
        if 'create' in self.action:
            return BookCreateSerializer
        return BookUpdateSerializer

    @action(methods=['get',], detail=False, url_path='my')
    # api/v1/books/
    # api/v1/books/^[\d a-z]*$
    # api/v1/books/my/
    def get_user_books(self, request):
        qs = self.get_queryset()

        qs = qs.filter(
            contibutor=request.user
        )

        serializer = self.get_serializer(qs, many=True)

        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )






class BookListInRangeGenericView(ListAPIView):
    serializer_class = BookListSerializer

    def get_queryset(self):
        date_format = "%Y-%m-%d"  # 2025-01-01

        # '2025-01-01' -> datetime.strptime() -> datetime(2025, 1, 1, 0, 0, 0) -> .date() -> datetime(2025, 1, 1)
        start = datetime.strptime(self.kwargs['date_from'], date_format).date()
        end = datetime.strptime(self.kwargs['date_to'], date_format).date()

        qs = Book.objects.filter(
            publication_date__range=[start, end]
        )

        return qs

class BookListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get_filtered_queryset(self, query_params):
        # queryset = model.objects.all()  # SELECT * FROM books;
        queryset = Book.objects.all()  # SELECT * FROM books;

        author_last_name = query_params.get('last_name')
        author_first_name = query_params.get('first_name')

        if author_last_name:
            queryset = queryset.filter(
                author__last_name=author_last_name
            )  # SELECT * FROM books WHERE author_last_name = 'author_last_name';

        if author_first_name:
            queryset = queryset.filter(
                author__first_name=author_first_name
            )

        return queryset

    def get(self, request: Request) -> Response:
        print("="*100)
        print(request.user)
        print("="*100)

        books = self.get_filtered_queryset(request.query_params)
        books_dto = BookListSerializer(books, many=True)

        return Response(
            data=books_dto.data,
            status=status.HTTP_200_OK
        )

    def post(self, request: Request) -> Response:
        # DTO
        # D  - ata
        # T  - ransfer
        # O  - bject
        book_dto = BookCreateSerializer(data=request.data)

        if not book_dto.is_valid():
            return Response(
                data=book_dto.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            book_dto.save()
        except Exception as exc:
            return Response(
                data={"error": f"Ошибка при сохранении книги: {str(exc)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            data=book_dto.data,
            status=status.HTTP_201_CREATED
        )


class BookRetrieveUpdateDestroyAPIView(APIView):
    def get_object(self, book_id: int):
        return Book.objects.get(pk=book_id)

    def get(self, request: Request, book_id: int) -> Response:
        try:
            book = self.get_object(book_id)
        except Book.DoesNotExist:
            return Response(
                data={"error": f"Книга с id={book_id} не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )

        book_dto = BookDetailedSerializer(book)

        return Response(
            data=book_dto.data, # {...}
            status=status.HTTP_200_OK
        )

    def put(self, request: Request, book_id: int) -> Response:
        try:
            book = self.get_object(book_id)  # <Book object (pk=333)>
        except Book.DoesNotExist:
            return Response(
                data={"error": f"Книга с id={book_id} не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )

        book_dto = BookUpdateSerializer(
            instance=book,
            data=request.data,
        )

        if not book_dto.is_valid():
            return Response(
                data=book_dto.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            book_dto.save()
        except Exception as exc:
            return Response(
                data={"error": f"Ошибка при обновлении книги: {str(exc)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            data=book_dto.data,
            status=status.HTTP_200_OK
        )

    def patch(self, request: Request, book_id: int) -> Response:
        try:
            book = self.get_object(book_id)  # <Book object (pk=333)>
        except Book.DoesNotExist:
            return Response(
                data={"error": f"Книга с id={book_id} не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )

        book_dto = BookUpdateSerializer(
            instance=book,
            data=request.data,
            partial=True
        )

        if not book_dto.is_valid():
            return Response(
                data=book_dto.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            book_dto.save()
        except Exception as exc:
            return Response(
                data={"error": f"Ошибка при обновлении книги: {str(exc)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            data=book_dto.data,
            status=status.HTTP_200_OK
        )

    def delete(self, request: Request, book_id: int) -> Response:
        try:
            book = self.get_object(book_id)
        except Book.DoesNotExist:
            return Response(
                data={"error": f"Книга с id={book_id} не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            book.delete()
        except Exception as exc:
            return Response(
                data={"error": f"Ошибка при удалении книги: {str(exc)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            data={},
            status=status.HTTP_204_NO_CONTENT
        )


#
# @api_view(['GET', 'POST'])
# def get_list_or_create(request: Request) -> Response:
#     if request.method == 'GET':
#         # Чтобы получить список объектов, нужно эти объекты как-то достать.
#         # Для этого мы обращаемся к базе и просим: "Дай все книги, что у тебя есть".
#         books = Book.objects.all()
#
#         # Сырые объекты базы — тяжелые и неповоротливые.
#         # Вернуть их клиенту мы не можем. Поэтому попросим сериализатор
#         # аккуратно превратить каждую книгу в обычный словарик.
#         books_dto = BookListSerializer(books, many=True)
#
#         # Теперь у нас есть простой список данных — можно смело отправлять клиенту.
#         return Response(
#             data=books_dto.data,
#             status=status.HTTP_200_OK
#         )
#     elif request.method == 'POST':
#         # Новая книга приходит в виде набора данных.
#         # Сериализатор проверяет: всё ли заполнено, всё ли выглядит правдиво.
#         book_dto = BookCreateSerializer(data=request.data)
#
#         # Сначала убеждаемся, что данные не вызывают вопросов.
#         if not book_dto.is_valid():
#             # Если что-то не так, сразу честно говорим об этом клиенту.
#             return Response(
#                 data=book_dto.errors,
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         try:
#             # Если всё хорошо — сохраняем книгу в базу.
#             # В этот момент она становится "настоящей", живущей в таблице.
#             book_dto.save()
#         except Exception as exc:
#             # Но если база вдруг перехватит нас за рукав, мы сообщим о проблеме.
#             return Response(
#                 data={"error": f"Ошибка при сохранении книги: {str(exc)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
#
#         # В противном случае всё гуд и мы, наконец, говорим — книга создана.
#         return Response(
#             data=book_dto.data,
#             status=status.HTTP_201_CREATED
#         )
#
#
# @api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
# def retrieve_book(request: Request, book_id: int) -> Response:
#     if request.method == 'GET':
#         try:
#             # Здесь мы пытаемся найти книгу по её номеру.
#             # Если книги нет — база честно скажет: "Такой не существует"(це будет ошибка DoesNotExists).
#             book = Book.objects.get(pk=book_id)
#         except Book.DoesNotExist:
#             # В этом случае мы сообщим клиенту, что искать дальше бессмысленно.
#             return Response(
#                 data={"error": f"Книга с id={book_id} не найдена"},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#
#         # Одну книгу тоже нужно “упростить”, прежде чем отдавать её наружу.
#         book_dto = BookDetailedSerializer(book)
#
#         # И только теперь отправляем читателю простой и чистый словарь.
#         return Response(
#             data=book_dto.data,
#             status=status.HTTP_200_OK
#         )
#
#     elif request.method in ('PUT', 'PATCH'):
#         # PUT — это "переписать всё заново".
#         # PATCH — "подправить чуть-чуть".
#         partial = False if request.method == 'PUT' else True
#
#         try:
#             # Для начала найдём ту самую книгу, которую хотим поменять.
#             book = Book.objects.get(pk=book_id)  # <Book object (pk=333)>
#         except Book.DoesNotExist:
#             # Если её нет — не получится обновить то, чего нет.
#             return Response(
#                 data={"error": f"Книга с id={book_id} не найдена"},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#
#         # Передаём и старый объект, и новые данные сериализатору,
#         # который аккуратно обновит всё, что нужно. А так же говорим, что обновление будет, возможно, частичным (partial = True \ False)
#         book_dto = BookUpdateSerializer(instance=book, data=request.data, partial=partial)
#
#         # Проверяем, что клиент не прислал что-то странное или неуместное.
#         if not book_dto.is_valid():
#             return Response(
#                 data=book_dto.errors,
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         try:
#             # Если всё хорошо — сохраняем изменения в базе.
#             book_dto.save()
#         except Exception as exc:
#             # Иногда база может быть против — тогда об этом стоит сообщить.
#             return Response(
#                 data={"error": f"Ошибка при обновлении книги: {str(exc)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
#
#         # Возвращаем обновлённую книгу обратно клиенту.
#         return Response(
#             data=book_dto.data,
#             status=status.HTTP_200_OK
#         )
#
#     elif request.method == 'DELETE':
#         try:
#             # Чтобы удалить книгу, её сначала нужно найти.
#             book = Book.objects.get(pk=book_id)
#         except Book.DoesNotExist:
#             # Если книги нет, говорим от этом клиенту
#             return Response(
#                 data={"error": f"Книга с id={book_id} не найдена"},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#
#         try:
#             # Если книга найдена — спокойно удаляем её из базы.
#             book.delete()
#         except Exception as exc:
#             # Но база иногда может возмутиться (например, из-за связей).
#             return Response(
#                 data={"error": f"Ошибка при удалении книги: {str(exc)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
#
#         # 204 — это “всё прошло успешно, но возвращать нам нечего”.
#         return Response(
#             data={},
#             status=status.HTTP_204_NO_CONTENT
#         )
