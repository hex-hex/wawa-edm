import django_filters
from django.db.models import Q

from .models import Company, Contact


class CompanyFilter(django_filters.FilterSet):
    about_empty = django_filters.BooleanFilter(
        method="filter_about_empty",
        label="about is null or blank",
    )

    class Meta:
        model = Company
        fields = []

    def filter_about_empty(self, queryset, name, value):
        if value is None:
            return queryset
        empty = Q(about__isnull=True) | Q(about__exact="")
        return queryset.filter(empty) if value else queryset.exclude(empty)


class ContactFilter(django_filters.FilterSet):
    story_empty = django_filters.BooleanFilter(
        method="filter_story_empty",
        label="story is null or blank",
    )

    class Meta:
        model = Contact
        fields = ["priority", "gender"]

    def filter_story_empty(self, queryset, name, value):
        if value is None:
            return queryset
        empty = Q(story__isnull=True) | Q(story__exact="")
        return queryset.filter(empty) if value else queryset.exclude(empty)
