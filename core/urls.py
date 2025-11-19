"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from test_app.views import home_page
from library.views import (
    get_list_or_create,
    retrieve_book,
)


urlpatterns = [
    path('admin/', admin.site.urls),  # http://127.0.0.1:8000/admin/
    path('<str:user_name>/', home_page),  # http://127.0.0.1:8000

    # CRUD for Book
    path('api/v1/books/', get_list_or_create),
    path('api/v1/books/<int:book_id>/', retrieve_book),
]
