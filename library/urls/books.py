from django.urls import path, re_path

from library.views.books import (
    BookListCreateAPIView,
    BookRetrieveUpdateDestroyAPIView,
    BookListInRangeGenericView,
    # UserBookListGenericView
)

urlpatterns = [
    path('', BookListCreateAPIView.as_view()),
    # path('my/', UserBookListGenericView.as_view()),
    re_path(
        r'^(?P<date_from>\d{4}-\d{2}-\d{2})/(?P<date_to>\d{4}-\d{2}-\d{2})$',
        BookListInRangeGenericView.as_view()
    ),
    path('<int:book_id>/', BookRetrieveUpdateDestroyAPIView.as_view()),
]
