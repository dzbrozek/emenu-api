from django_filters import rest_framework as filters


class MenuFilter(filters.FilterSet):
    created = filters.IsoDateTimeFromToRangeFilter(field_name='created')
    updated = filters.IsoDateTimeFromToRangeFilter(field_name='updated')
