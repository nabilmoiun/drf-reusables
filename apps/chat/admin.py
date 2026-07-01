from django.contrib import admin

from apps.chat.forms import ConversationAdminForm
from apps.chat.models import Conversation, Attachment, Messaage

from apps.common.admin import BaseAdmin


@admin.register(Conversation)
class ConversationAdmin(BaseAdmin):
    list_display = ["__str__"]
    form = ConversationAdminForm
    

@admin.register(Attachment)
class AttachmentAdmin(BaseAdmin):
    list_display = ["__str__"]


@admin.register(Messaage)
class MessageAdmin(BaseAdmin):
    list_display = ["__str__"]
