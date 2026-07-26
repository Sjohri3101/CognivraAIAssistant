import logging

from agent.models import AIInstruction

logger = logging.getLogger(__name__)


DEFAULT_PROMPT = """
You are an intelligent AI Assistant.

Your responsibilities are:

- Answer user questions accurately and naturally.
- Maintain context throughout the conversation.
- Provide clear, concise, and helpful responses.
- Explain technical concepts with examples whenever appropriate.
- Generate code when requested.
- Format responses using Markdown when it improves readability.
- Use bullet points, numbered lists, and tables where appropriate.
- If you do not know an answer, say so instead of making up information.
- Never fabricate facts or references.
- Keep responses professional, friendly, and conversational.

Guidelines:

- Understand the user's intent from the conversation history.
- Remember previous messages within the current chat.
- If the user asks a follow-up question, answer it using previous context.
- For programming questions, provide complete and executable examples whenever possible.
- When returning JSON, return only valid JSON.
- When generating code, wrap it inside proper Markdown code blocks.
"""


def get_instruction(name="default"):
    """
    Return the system instruction stored in the database.
    Falls back to DEFAULT_PROMPT if no custom instruction exists.
    """
    try:
        instruction = AIInstruction.objects.filter(name=name).first()

        if instruction and instruction.prompt_template:
            return instruction.prompt_template.strip()

    except Exception:
        logger.exception("Unable to fetch AI instruction.")

    return DEFAULT_PROMPT


def save_instruction(name, prompt):
    """
    Create or update a system instruction.
    """
    return AIInstruction.objects.update_or_create(
        name=name,
        defaults={
            "prompt_template": prompt.strip()
        }
    )[0]


def list_instructions():
    """
    Return all available instructions.
    """
    return AIInstruction.objects.all().order_by("name")


def delete_instruction(name):
    """
    Delete an instruction by name.
    """
    AIInstruction.objects.filter(name=name).delete()


def instruction_exists(name):
    """
    Check whether an instruction exists.
    """
    return AIInstruction.objects.filter(name=name).exists()