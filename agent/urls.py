from django.urls import path
from agent import views

urlpatterns = [
    path("", views.home, name="home"),
    path("ai/", views.ai_query, name="ai_api"),
    path("chat/<int:chat_id>/", views.get_chat_messages, name="chat_messages"),
    path("chat-list/", views.chat_list, name="chat_list"),
    path("chat/<int:chat_id>/delete/", views.delete_chat, name="delete_chat"),
    path("chat/<int:chat_id>/rename/", views.rename_chat, name="rename_chat"),
]