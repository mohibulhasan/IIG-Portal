  
import django_filters
from django_filters import DateFilter, CharFilter

from .models import *

class InterfaceFilter(django_filters.FilterSet):
	#start_date = DateFilter(field_name="date_created", lookup_expr='gte')
	des = CharFilter(field_name="interface_description", lookup_expr='icontains')
	note = CharFilter(field_name='interface_name', lookup_expr='icontains')


	class Meta:
		model = InterfaceInfo
		fields = '__all__'
		exclude = ['interface_graph','interface_name','interface_description']