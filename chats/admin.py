from django.contrib import admin

from chats.models import ChatSession, ChatSessionMessage, ChatSessionUser

# Register your models here.

admin.site.register(ChatSession)
admin.site.register(ChatSessionUser)
admin.site.register(ChatSessionMessage)
