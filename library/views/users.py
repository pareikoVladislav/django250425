from django.db.models.aggregates import Count
from rest_framework.generics import GenericAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from library.models import User
from library.serializers import UserListSerializer, UserCreateSerializer



class UserListCreateGenericView(ListCreateAPIView):
    queryset = User.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()

        context['include_related'] = self.request.query_params.get(
            'include_related', 'false'
        ).lower() == 'true'

        return context

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserListSerializer

        return UserCreateSerializer

    def list(self, request, *args, **kwargs):
        queryset = User.objects.annotate(
            posts_cnt=Count('posts')
        ).filter(posts_cnt__gt=0)

        serializer = self.get_serializer(queryset, many=True)

        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )
