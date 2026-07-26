from django.contrib import admin
from .models import Chat, Message, AIInstruction


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = (
        "role",
        "content",
        "created_at",
    )


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "instruction",
        "created_at",
    )

    search_fields = (
        "title",
    )

    inlines = [
        MessageInline,
    ]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "chat",
        "role",
        "created_at",
    )

    search_fields = (
        "content",
    )

    list_filter = (
        "role",
    )


@admin.register(AIInstruction)
class AIInstructionAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
    )

    search_fields = (
        "name",
    )