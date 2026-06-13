from django.contrib import admin

from .models import Company, Contact


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "company", "created_at")
    list_filter = ("company",)
    search_fields = ("first_name", "last_name", "email")
    autocomplete_fields = ("company",)
