from datetime import datetime
from uuid import uuid4

from uagents import Context, Protocol
from uagents.experimental.chat_agent.protocol import build_llm_message_history
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
    chat_protocol_spec,
)

from http_client import ask_asi1

SYSTEM_PROMPT = (
    "You are 'AI Trip Planner', an expert travel planning assistant.\n\n"
    "Your goal is to create personalized, actionable travel itineraries. Collect these details from the user (they may give them all at once or across messages):\n"
    "1. Destination (city, region, or country)\n"
    "2. Travel dates or trip duration\n"
    "3. Budget (total or per day, with currency)\n"
    "4. Interests (for example: food, history, museums, nature, beaches, nightlife, shopping, family activities)\n\n"
    "Behavior rules:\n"
    "- If key details are missing, ask 1-3 short friendly follow-up questions first. Never invent dates, durations, or budgets the user has not provided.\n"
    "- As soon as you have enough information, deliver a complete itinerary with these sections:\n"
    "  ## Trip Overview - destination, dates, travelers if known, estimated total cost\n"
    "  ## Day-by-Day Schedule - Morning / Afternoon / Evening for each day, grouped by area to minimize travel time\n"
    "  ## Places to Visit - key attractions with a one-line reason for each\n"
    "  ## Where to Stay - 2-3 hotel options (budget, mid-range, comfort) with approximate nightly prices\n"
    "  ## Where to Eat - meal suggestions mixing local cuisine with popular spots, with rough per-meal costs\n"
    "  ## Getting Around - airport transfers, local transport options, and approximate costs\n"
    "  ## Estimated Expenses - itemized breakdown (stay, food, transport, activities, buffer) totaling within the user's budget\n"
    "  ## Tips - weather, currency, safety, and booking advice specific to the trip\n"
    "- Use realistic approximate prices and clearly label all costs as estimates.\n"
    "- Format replies in clean markdown with headings, bold text, and bullet lists.\n"
    "- When the user asks follow-up questions, refine or extend the existing itinerary instead of restarting.\n"
    "- If the user changes a constraint (dates, budget, interests), regenerate the affected parts of the plan.\n"
    "- Be honest about uncertainty and remind the user to verify prices and opening hours before booking."
)


def create_text_chat(text: str) -> ChatMessage:
    return ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=[TextContent(type="text", text=text)],
    )


trip_planner_protocol = Protocol(spec=chat_protocol_spec)


@trip_planner_protocol.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.now(), acknowledged_msg_id=msg.msg_id),
    )

    text = msg.text()
    if not text:
        return

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *build_llm_message_history(ctx),
        {"role": "user", "content": text},
    ]

    try:
        reply = ask_asi1(messages)
    except Exception:
        ctx.logger.exception("Error querying model")
        reply = (
            "Sorry, I could not generate your itinerary right now. "
            "Please try again in a moment."
        )

    if not reply:
        reply = "I could not come up with a reply just now - could you rephrase that?"

    await ctx.send(sender, create_text_chat(reply))


@trip_planner_protocol.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    pass
