from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.core.paginator import Paginator

class CustomPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100
    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'total tasks': self.page.paginator.count,
            'total pages': self.page.paginator.num_pages,
            'results': data
        })