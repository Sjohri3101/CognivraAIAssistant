from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from agent.services.instruction_service import get_instruction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.http import require_POST
from agent.models import AIInstruction, Chat, Message
from .services.groq_service import chat
from django.contrib.auth.decorators import login_required
from accounts.models import UserProfile

@login_required
def home(request):

    chats = Chat.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "index.html",
        {
            "chats": chats
        }
    )

@login_required
@api_view(["POST"])
def ai_query(request):

    user_input = request.data.get("message", "").strip()
    chat_id = request.data.get("chat_id")
    profile, _ = UserProfile.objects.get_or_create(
    user=request.user
    )

    instruction = profile.assistant

    if instruction is None:
        instruction = AIInstruction.objects.get(name="default")

    if not user_input:
        return Response(
            {"error": "Message is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # -----------------------------------------
    # Get/Create Chat
    # -----------------------------------------

    if chat_id:
        try:
            chat_obj = get_object_or_404(Chat,id=chat_id,user=request.user)
        except Chat.DoesNotExist:
            chat_obj = Chat.objects.create(
                user=request.user,
                title=user_input[:50],
                instruction=instruction
            )
    else:
        chat_obj = Chat.objects.create(
            user=request.user,
            title=user_input[:50],
            instruction=instruction
        )

    # Update title only for new chats
    if not chat_obj.title:
        chat_obj.title = user_input[:50]
        chat_obj.save(update_fields=["title"])

    # -----------------------------------------
    # Save User Message
    # -----------------------------------------

    Message.objects.create(
        chat=chat_obj,
        role="user",
        content=user_input
    )

    # -----------------------------------------
    # Build Conversation History
    # -----------------------------------------

    messages = []

    # Optional system prompt
    system_prompt = (
        chat_obj.instruction.prompt_template
        if chat_obj.instruction
        else get_instruction()
    )

    messages.append({
        "role": "system",
        "content": system_prompt
    })

    history = (
        Message.objects
        .filter(chat=chat_obj)
        .order_by("created_at")
    )

    for msg in history:
        messages.append({
            "role": msg.role,
            "content": msg.content
        })

    # -----------------------------------------
    # Call Groq
    # -----------------------------------------

    try:
        bot_response = chat(messages)

    except Exception as ex:
        return Response(
            {
                "error": str(ex)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # -----------------------------------------
    # Save Bot Message
    # -----------------------------------------

    Message.objects.create(
        chat=chat_obj,
        role="assistant",
        content=bot_response
    )

    # -----------------------------------------
    # Response
    # -----------------------------------------

    return Response(
        {
            "chat_id": chat_obj.id,
            "response": bot_response
        }
    )


@login_required
def get_chat_messages(request, chat_id):

    messages = Message.objects.filter(
        chat_id=chat_id
    )

    data = []

    for message in messages:

        data.append(
            {
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at.strftime(
                    "%d-%m-%Y %H:%M"
                )
            }
        )

    return JsonResponse(
        data,
        safe=False
    )


@login_required
def chat_list(request):
    chats = Chat.objects.filter(user=request.user).order_by("-created_at")

    return render(
        request,
        "chat_history.html",
        {
            "chats": chats
        }
    )

@login_required
@require_POST
def delete_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)

    chat.delete()

    return JsonResponse({
        "success": True,
        "message": "Chat deleted successfully."
    })

@login_required
@require_POST
def rename_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)

    title = request.POST.get("title", "").strip()

    if not title:
        return JsonResponse({
            "success": False,
            "message": "Title is required."
        }, status=400)

    chat.title = title
    chat.save(update_fields=["title"])

    return JsonResponse({
        "success": True,
        "message": "Chat renamed successfully.",
        "title": chat.title
    })