from django.contrib import admin

from .admin_render import rendered_field
from .models import Company, Contact, EmailDraft, EmailTask, Knowledge


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name",)
    about_preview = rendered_field("about", fmt="markdown", label="About")
    exclude = ("about",)
    readonly_fields = ("about_preview",)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "company", "created_at")
    list_filter = ("company",)
    search_fields = ("first_name", "last_name", "email")
    autocomplete_fields = ("company",)
    story_preview = rendered_field("story", fmt="markdown", label="Story")
    exclude = ("story",)
    readonly_fields = ("story_preview",)


@admin.register(Knowledge)
class KnowledgeAdmin(admin.ModelAdmin):
    list_display = ("abstract", "created_at", "updated_at")
    search_fields = ("abstract", "content")
    ordering = ("abstract",)
    content_preview = rendered_field("content", fmt="markdown", label="Content")
    exclude = ("content",)
    readonly_fields = ("content_preview",)


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
    content_preview = rendered_field("content", fmt="html", label="Content (HTML)")
    exclude = ("content",)
    readonly_fields = ("content_preview",)
