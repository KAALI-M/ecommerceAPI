from rest_framework import viewsets, permissions
from discounts.models import Discount
from discounts.discountsAPI.serializers import DiscountSerializer
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from .pagination import CustomPagination
from django_filters.rest_framework import FilterSet
import django_filters
from django.db.models import Q


class ModelPermissions(permissions.DjangoModelPermissions):

    def has_permission(self, request, view):
        #all users can view discounts even if they are not authenticated
        user = request.user
        if  request.method == 'GET':
                    return True
        #only authenticated users having the right permissions can add, update and delete discounts
        elif user and user.is_authenticated: 
            match request.method :
                case 'POST': 
                    return user.has_perm('discounts.add_discount')
                case 'PUT'|'PATCH':
                    return user.has_perm('discounts.change_discount')
                case 'DELETE':
                    return user.has_perm('discounts.delete_discount')
        return False
    
class ProductFilter(FilterSet):   
    included_date = django_filters.DateFilter(method='filter_by_date_range', label='Date included in discount range')
    def filter_by_date_range(self, queryset, name, value):
        # Filters where `field1 <= entered_date` and `field2 >= entered_date`
        return queryset.filter(Q(start_date__lte=value) & Q(end_date__gte=value))
    class Meta:
        model = Discount
        fields = ['included_date']    

class DiscountViewSet(viewsets.ModelViewSet):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [ModelPermissions]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ProductFilter
    pagination_class = CustomPagination

    # exemple of query :http://127.0.0.1:8000/api/discounts/?included_date=2024-11-01
