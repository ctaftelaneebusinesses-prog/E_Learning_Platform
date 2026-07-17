import requests
import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def get_learning_suggestions(role):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Craftlanee"
    }

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert technical career mentor and curriculum designer. "
                    "You have deep, current knowledge of every tech career path, including "
                    "software engineering, data science, AI/ML engineering, prompt engineering, "
                    "MLOps, DevOps, cloud, cybersecurity, and product/design roles. "
                    "You never default to a generic web-development stack (HTML/CSS, JavaScript, "
                    "React, Node.js, MongoDB, etc.) unless the role is actually a web development "
                    "role. Each role gets tools and technologies specific to what practitioners in "
                    "that exact role use day to day."
                )
            },
            {
                "role": "user",
                "content": f"""
Role: "{role}"

Step 1 (internal, do not output): Identify the specific domain of this role
(e.g. frontend/backend/full-stack web dev, data science, AI/ML engineering,
prompt engineering & LLM tooling, DevOps/cloud, cybersecurity, mobile, etc.).

Step 2: List exactly 10 of the most relevant technologies, tools, frameworks,
or platforms that a working professional in this specific role would actually
use. For example, a prompt engineer would use things like LLM provider APIs
(OpenAI, Anthropic, etc.), LangChain/LlamaIndex, vector databases, prompt
evaluation/observability tools, and Python — NOT a generic web stack.

Output format (strict):
- Exactly 10 lines
- One technology/tool name per line
- No numbering, bullets, headings, or explanations
- No text before the first item or after the last item
"""
            }
        ],
        "temperature": 0.4
    }

    response = requests.post(url, headers=headers, json=payload, timeout=30)

    if response.status_code != 200:
        print("OpenRouter error:", response.text)
        return []

    data = response.json()

    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        print("Invalid OpenRouter response:", data)
        return []

    # Convert text → list, stripping any numbering/bullets the model adds anyway
    suggestions = [
        line.strip("-•*0123456789. ").strip()
        for line in content.split("\n")
        if line.strip()
    ]
    suggestions = [s for s in suggestions if s][:10]

    return suggestions
