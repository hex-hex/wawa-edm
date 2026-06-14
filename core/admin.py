from django.contrib import admin

from .admin_render import rendered_field
from .models import Company, Contact, EmailDraft, EmailTask, Knowledge

admin.site.site_header = "Wawa EDM"
admin.site.site_title = "Wawa EDM Admin"
admin.site.index_title = "Campaign workspace"


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
    behavior_preview = rendered_field("behavior", fmt="markdown", label="Behavior")
    exclude = ("story", "behavior")
    readonly_fields = ("story_preview", "behavior_preview")


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
    list_display = ("created_at", "title", "contact", "task", "status", "version")
    list_filter = ("status", "task")
    search_fields = ("title", "content")
    autocomplete_fields = ("contact", "task")
    pain_points_preview = rendered_field("pain_points", fmt="markdown", label="Pain points")
    content_preview = rendered_field("content", fmt="html", label="Content (HTML)")
    exclude = ("pain_points", "content")
    readonly_fields = ("pain_points_preview", "content_preview")
