from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Category, Comment, Priority, Status, Tag, Ticket, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Администрирование пользователей и ролей."""

    list_display = ("username", "get_full_name", "email", "role", "is_staff")
    list_filter = ("role", "is_staff", "is_superuser")
    fieldsets = UserAdmin.fieldsets + (("Роль", {"fields": ("role",)}),)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "is_closed")
    list_editable = ("order", "is_closed")


@admin.register(Priority)
class PriorityAdmin(admin.ModelAdmin):
    list_display = ("name", "weight")
    list_editable = ("weight",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "assignee", "category", "status", "priority", "created_at")
    list_filter = ("status", "priority", "category")
    search_fields = ("title", "description")
    autocomplete_fields = ("category",)
    inlines = [CommentInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("ticket", "author", "is_internal", "created_at")
    list_filter = ("is_internal",)
