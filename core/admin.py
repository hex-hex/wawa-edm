from django.contrib import admin

from .admin_render import rendered_field
from .filters import latest_drafts_per_contact_for_task
from .models import Company, Contact, EmailDraft, EmailTask, Knowledge, KnowledgeTag

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
    list_display = ("created_at", "first_name", "last_name", "email", "company")
    list_filter = ("created_at",)
    search_fields = ("first_name", "last_name", "email")
    autocomplete_fields = ("company",)
    ordering = ("-created_at",)
    story_preview = rendered_field("story", fmt="markdown", label="Story")
    behavior_preview = rendered_field("behavior", fmt="markdown", label="Behavior")
    exclude = ("story", "behavior")
    readonly_fields = ("story_preview", "behavior_preview")


@admin.register(KnowledgeTag)
class KnowledgeTagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Knowledge)
class KnowledgeAdmin(admin.ModelAdmin):
    list_display = ("abstract", "created_at", "updated_at")
    list_filter = ("tags",)
    search_fields = ("abstract", "content")
    ordering = ("abstract",)
    filter_horizontal = ("tags",)
    content_preview = rendered_field("content", fmt="markdown", label="Content")
    exclude = ("content",)
    readonly_fields = ("content_preview",)


@admin.register(EmailTask)
class EmailTaskAdmin(admin.ModelAdmin):
    list_display = ("name", "target", "created_at")
    search_fields = ("name", "target")
    filter_horizontal = ("knowledges",)


class TaskLatestPerContactFilter(admin.SimpleListFilter):
    """Filter EmailDrafts by EmailTask, but show only the highest-version draft
    per contact within the selected task."""

    title = "task (latest per contact)"
    parameter_name = "task"

    def lookups(self, request, model_admin):
        return [(t.pk, str(t)) for t in EmailTask.objects.all()]

    def queryset(self, request, queryset):
        return latest_drafts_per_contact_for_task(queryset, self.value())


@admin.register(EmailDraft)
class EmailDraftAdmin(admin.ModelAdmin):
    list_display = ("created_at", "subject", "contact", "task", "status", "version")
    list_filter = ("status", TaskLatestPerContactFilter)
    search_fields = ("subject", "content")
    autocomplete_fields = ("contact", "task")
    filter_horizontal = ("knowledges",)
    pain_points_preview = rendered_field("pain_points", fmt="markdown", label="Pain points")
    content_preview = rendered_field("content", fmt="html", label="Content (HTML)")
    exclude = ("pain_points", "content")
    readonly_fields = ("pain_points_preview", "content_preview")
