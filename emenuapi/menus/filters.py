from django_filters import rest_framework as filters


class MenuFilter(filters.FilterSet):
    created = filters.IsoDateTimeFromToRangeFilter()
    updated = filters.IsoDateTimeFromToRangeFilter()
