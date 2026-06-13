from django.contrib import admin

from .models import Company, Contact, EmailDraft, EmailTask, Knowledge


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


@admin.register(Knowledge)
class KnowledgeAdmin(admin.ModelAdmin):
    list_display = ("abstract", "created_at", "updated_at")
    search_fields = ("abstract", "content")
    ordering = ("abstract",)


@admin.register(EmailTask)
class EmailTaskAdmin(admin.ModelAdmin):
    list_display = ("name", "target", "created_at")
    search_fields = ("name", "target")
    filter_horizontal = ("knowledges",)


@admin.register(EmailDraft)
class EmailDraftAdmin(admin.ModelAdmin):
    list_display = ("title", "contact", "status", "version", "created_at")
    list_filter = ("status",)
    search_fields = ("title", "content")
    autocomplete_fields = ("contact",)
