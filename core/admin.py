from django.contrib import admin
from django.db.models import OuterRef, Subquery

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
    list_display = ("created_at", "first_name", "last_name", "email", "company")
    list_filter = ("company",)
    search_fields = ("first_name", "last_name", "email")
    autocomplete_fields = ("company",)
    ordering = ("-created_at",)
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


class TaskLatestPerContactFilter(admin.SimpleListFilter):
    """Filter EmailDrafts by EmailTask, but show only the highest-version draft
    per contact within the selected task."""

    title = "task (latest per contact)"
    parameter_name = "task"

    def lookups(self, request, model_admin):
        return [(t.pk, str(t)) for t in EmailTask.objects.all()]

    def queryset(self, request, queryset):
        task_id = self.value()
        if not task_id:
            return queryset
        base = queryset.filter(task_id=task_id)
        latest_version = (
            EmailDraft.objects.filter(task_id=task_id, contact=OuterRef("contact"))
            .order_by("-version")
            .values("version")[:1]
        )
        return base.filter(version=Subquery(latest_version))


@admin.register(EmailDraft)
class EmailDraftAdmin(admin.ModelAdmin):
    list_display = ("created_at", "subject", "contact", "task", "status", "version")
    list_filter = ("status", TaskLatestPerContactFilter)
    search_fields = ("subject", "content")
    autocomplete_fields = ("contact", "task")
    pain_points_preview = rendered_field("pain_points", fmt="markdown", label="Pain points")
    content_preview = rendered_field("content", fmt="html", label="Content (HTML)")
    exclude = ("pain_points", "content")
    readonly_fields = ("pain_points_preview", "content_preview")
