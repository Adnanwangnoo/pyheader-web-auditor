from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import requests
import json
import os

load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

SECURITY_HEADERS = [
    {"name": "Content-Security-Policy",       "abbr": "CSP",  "critical": True},
    {"name": "Strict-Transport-Security",      "abbr": "HSTS", "critical": True},
    {"name": "X-Frame-Options",               "abbr": "XFO",  "critical": True},
    {"name": "X-Content-Type-Options",        "abbr": "XCTO", "critical": False},
    {"name": "Referrer-Policy",               "abbr": "RP",   "critical": False},
    {"name": "Permissions-Policy",            "abbr": "PP",   "critical": False},
    {"name": "X-XSS-Protection",              "abbr": "XSP",  "critical": False},
    {"name": "Cross-Origin-Embedder-Policy",  "abbr": "COEP", "critical": False},
    {"name": "Cross-Origin-Opener-Policy",    "abbr": "COOP", "critical": False},
    {"name": "Cross-Origin-Resource-Policy",  "abbr": "CORP", "critical": False},
]


@app.route("/")
def index():
    return render_template("index.html", headers=SECURITY_HEADERS)


@app.route("/fetch-headers", methods=["POST"])
def fetch_headers():
    data = request.get_json()
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    if not url.startswith("http"):
        url = "https://" + url
    try:
        resp = requests.get(
            url, timeout=8, allow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 SecurityHeaderAuditor/1.0"}
        )
        headers = dict(resp.headers)
        formatted = "\n".join(f"{k}: {v}" for k, v in headers.items())
        return jsonify({"headers": formatted, "status": resp.status_code, "url": resp.url})
    except requests.exceptions.SSLError:
        return jsonify({"error": "SSL certificate error for this domain"}), 400
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Could not connect to that URL"}), 400
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timed out after 8 seconds"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    headers_text = data.get("headers", "").strip()
    if not headers_text:
        return jsonify({"error": "No headers provided"}), 400

    header_names = [h["name"] for h in SECURITY_HEADERS]
    header_json_template = ",\n    ".join(
        f'"{h}": {{"present": true/false, "value": "<value or null>", "analysis": "<1-2 sentence analysis>"}}'
        for h in header_names
    )

    prompt = f"""You are a senior web security engineer. Analyze these HTTP response headers for security best practices.

HTTP Headers to analyze:
---
{headers_text}
---

Respond ONLY with valid JSON (absolutely no markdown, no backticks, no preamble, no explanation):
{{
  "score": <integer 0-100 based on security posture>,
  "summary": "<2-sentence plain-English overall assessment>",
  "headers": {{
    {header_json_template}
  }},
  "recommendations": [
    "<most important fix with example value>",
    "<second most important fix>",
    "<third fix>"
  ]
}}"""

    try:
        resp = requests.post(
            GEMINI_URL,
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.1, "maxOutputTokens": 2000}
            },
            timeout=30
        )
        result = resp.json()

        # Extract text from Gemini response
        raw = result["candidates"][0]["content"]["parts"][0]["text"].strip()

        # Strip any accidental markdown fences
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.split("```")[0]

        parsed = json.loads(raw.strip())
        return jsonify({"result": parsed})

    except json.JSONDecodeError as e:
        return jsonify({"error": f"Failed to parse AI response: {str(e)}"}), 500
    except KeyError:
        return jsonify({"error": "Unexpected response from Gemini API. Check your API key."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
