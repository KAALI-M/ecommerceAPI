from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    # default number of items per page
    page_size = 10
    
    # Allow the client to set the page size with a query parameter
    page_size_query_param = 'page_size'
    
    # maximum number of items per page to avoid overload
    max_page_size = 100
    
    # query parameter for navigating to a specific page
    page_query_param = 'page'