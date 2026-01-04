from datetime import datetime, timedelta
import os
from flask import Flask, render_template, request, make_response
import config
from openai import OpenAI


API_KEY = config.API_KEY or os.getenv("OPENAI_API_KEY", "")
client = OpenAI(api_key=API_KEY) if API_KEY else OpenAI()

app = Flask(__name__)

DEMO_LIMITS = {
    "per_ip_daily": 5,
    "global_daily": 50,
    "cooldown_seconds": 15,
}
MAX_TOKENS = 256
MAX_HISTORY = 12
LIMIT_MESSAGE = "Public demo limit reached. Please try again later or run locally."

rate_state = {
    "day": None,
    "global_count": 0,
    "ip_counts": {},
    "ip_last_request": {},
}
conversations = {}


def _utc_day():
    return datetime.utcnow().strftime("%Y-%m-%d")


def _reset_daily_limits_if_needed():
    today = _utc_day()
    if rate_state["day"] != today:
        rate_state["day"] = today
        rate_state["global_count"] = 0
        rate_state["ip_counts"] = {}
        rate_state["ip_last_request"] = {}


def _seconds_until_tomorrow():
    now = datetime.utcnow()
    tomorrow = (now + timedelta(days=1)).date()
    midnight = datetime.combine(tomorrow, datetime.min.time())
    return max(1, int((midnight - now).total_seconds()))


def _get_client_ip():
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.remote_addr or "unknown"


def _check_rate_limits(ip_address):
    _reset_daily_limits_if_needed()
    now = datetime.utcnow()

    last_request = rate_state["ip_last_request"].get(ip_address)
    if last_request:
        elapsed = (now - last_request).total_seconds()
        if elapsed < DEMO_LIMITS["cooldown_seconds"]:
            retry_after = max(1, int(DEMO_LIMITS["cooldown_seconds"] - elapsed))
            return False, retry_after

    ip_count = rate_state["ip_counts"].get(ip_address, 0)
    if ip_count >= DEMO_LIMITS["per_ip_daily"]:
        return False, _seconds_until_tomorrow()
    if rate_state["global_count"] >= DEMO_LIMITS["global_daily"]:
        return False, _seconds_until_tomorrow()

    rate_state["ip_counts"][ip_address] = ip_count + 1
    rate_state["global_count"] += 1
    rate_state["ip_last_request"][ip_address] = now
    return True, None


def _rate_limit_response(retry_after):
    response = make_response(LIMIT_MESSAGE, 429)
    if retry_after:
        response.headers["Retry-After"] = str(retry_after)
    return response
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    user_text = request.args.get("msg", "").strip()
    if not user_text:
        return make_response("Please provide a message.", 400)

    if not API_KEY and not os.getenv("OPENAI_API_KEY"):
        return make_response("Server misconfigured. Missing OPENAI_API_KEY.", 500)

    ip_address = _get_client_ip()
    allowed, retry_after = _check_rate_limits(ip_address)
    if not allowed:
        return _rate_limit_response(retry_after)

    model_engine = "gpt-3.5-turbo"
    history = conversations.setdefault(ip_address, [])
    history.append({"role": "user", "content": user_text})
    history[:] = history[-MAX_HISTORY:]

    try:
        response = client.chat.completions.create(
            model=model_engine,
            messages=history,
            max_tokens=MAX_TOKENS,
        )
    except Exception:
        history.pop()
        return make_response("Upstream error. Please try again.", 500)

    ai_response = response.choices[0].message.content
    history.append({"role": "assistant", "content": ai_response})
    history[:] = history[-MAX_HISTORY:]
    return str(ai_response)


@app.route("/clear", methods=["POST"])
def clear_chat():
    ip_address = _get_client_ip()
    conversations.pop(ip_address, None)
    return ("", 204)



if __name__ == "__main__":
    app.run()
