import re

import requests
from django.conf import settings

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-4o-mini"

PERSONA_PROMPT = """
You are the AI Mentor for Craftlanee, an e-learning platform. You are a warm,
knowledgeable senior career mentor who helps learners plan their careers and
navigate the platform.

PLATFORM KNOWLEDGE (use this to answer questions about the site):
- Course Catalog: students browse and enroll in courses.
- My Courses / Lessons: enrolled students work through lessons in order.
- Quizzes: timed, have a difficulty level and a pass mark; attempts are scored.
- Achievements & XP: students earn XP and unlock achievements as they progress.
- Leaderboard: ranks students by XP earned.
- Learning Streaks: daily activity builds a streak that unlocks bonus-XP rewards.
- Skills: proficiency per skill is tracked from completed courses.
- Activity Timeline: a log of the student's recent actions on the platform.
- Certificates: downloadable PDF certificates for completed courses.
- AI Learning Path: a tool where a student enters a target role and AI
  suggests the technologies to learn for it; past queries are saved to a
  History panel on that page.
- AI Mentor (you): this chat widget, available site-wide.

HOW TO RESPOND:
- Be concise, accurate, and genuinely helpful. Never invent platform features
  that are not listed above.
- Match your response style to what the user actually asked (see per-message
  instruction below) rather than defaulting to any one format.
- Stay strictly on topic: careers, learning, skills, and the Craftlanee
  platform. If asked something unrelated, politely redirect.
"""

CONVERSATIONAL_RULES = """
RESPONSE STYLE FOR THIS MESSAGE: Conversational.
- Reply in plain natural sentences. DO NOT use the "SECTION:" format.
- Keep it short: 1-4 sentences.
- Be friendly and specific to what the user asked.
"""

STRUCTURED_RULES = """
RESPONSE STYLE FOR THIS MESSAGE: Structured roadmap.

CRITICAL OUTPUT RULES (MANDATORY):
- Use ONLY plain text
- DO NOT use markdown
- DO NOT write paragraphs
- DO NOT answer in sentences

You MUST ALWAYS start with at least ONE section.

FORMAT (STRICT):
SECTION: <Title>
- short point
- short point

RULES:
- Minimum 1 SECTION (no exceptions)
- Max 5 sections
- Max 3 bullet points per section
- Each bullet <= 8 words
- No text before first SECTION
- No text after last section

If unsure, create a GENERAL ROADMAP section.
Adapt to ANY career path.
"""

GREETING_PATTERN = re.compile(
    r"^(hi+|hello+|hey+|yo|sup|greetings|good\s(morning|afternoon|evening))[\s!.,]*$"
)
ACKNOWLEDGEMENT_PATTERN = re.compile(
    r"^(thanks|thank you|thx|ok|okay|cool|nice|great|got it)[\s!.,]*$"
)

SITE_KEYWORDS = (
    "course", "certificate", "leaderboard", "streak", "quiz", "enroll",
    "dashboard", "xp", "achievement", "login", "sign up", "sign in",
    "password", "site", "website", "platform", "craftlanee", "skill",
    "lesson", "mentor", "history",
)

ROADMAP_KEYWORDS = (
    "roadmap", "learning path", "career path", "become a", "how to become",
    "path to become", "path for",
)

INTENT_INSTRUCTIONS = {
    "greeting": (
        CONVERSATIONAL_RULES
        + "\nThe user just greeted you. Greet them back warmly in 1-2 "
        "sentences and ask what career goal or platform question you can "
        "help with."
    ),
    "chat": (
        CONVERSATIONAL_RULES
        + "\nAnswer the user's message directly and naturally, drawing on "
        "the platform knowledge above if relevant."
    ),
    "site_help": (
        CONVERSATIONAL_RULES
        + "\nThe user is asking about the Craftlanee platform. Answer using "
        "the platform knowledge above. If you are not sure, say so honestly."
    ),
    "roadmap": STRUCTURED_RULES + "\nGive a high-level roadmap.",
    "30_day": STRUCTURED_RULES + "\nCreate a 30-day weekly plan.",
    "tools": STRUCTURED_RULES + "\nList important tools.",
    "practice": STRUCTURED_RULES + "\nExplain real-world practices.",
    "project": STRUCTURED_RULES + "\nSuggest realistic projects.",
}


def call_openrouter(messages):
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "AI Mentor",
    }

    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.6,
    }

    response = requests.post(
        OPENROUTER_URL,
        json=payload,
        headers=headers,
        timeout=30
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def detect_intent(text):
    t = text.lower().strip()

    if GREETING_PATTERN.match(t):
        return "greeting"

    if ACKNOWLEDGEMENT_PATTERN.match(t):
        return "chat"

    if "30" in t and "day" in t:
        return "30_day"
    if "tool" in t:
        return "tools"
    if "practice" in t:
        return "practice"
    if "project" in t:
        return "project"
    if any(k in t for k in ROADMAP_KEYWORDS):
        return "roadmap"
    if any(k in t for k in SITE_KEYWORDS):
        return "site_help"

    return "chat"


def get_ai_response(user_message, state):
    history = state.setdefault("history", [])
    history.append({"role": "user", "content": user_message})

    intent = detect_intent(user_message)
    intent_instruction = INTENT_INSTRUCTIONS[intent]

    messages = [
        {"role": "system", "content": PERSONA_PROMPT + "\n" + intent_instruction},
        *history[-6:]
    ]

    reply = call_openrouter(messages)

    history.append({"role": "assistant", "content": reply})
    state["history"] = history

    return reply
