import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from .services import get_ai_response


@csrf_exempt
@login_required
def chat_with_mentor(request):
    if request.method == "POST":
        data = json.loads(request.body)
        message = data.get("message", "").strip()

        request.session.setdefault("mentor_state", {})

        reply = get_ai_response(message, request.session["mentor_state"])

        request.session.modified = True

        return JsonResponse({"reply": reply})
