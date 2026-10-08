import json
import os
from http.server import BaseHTTPRequestHandler
from google import genai

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        data = json.loads(body.decode("utf-8"))

        request_data = data.get("request", {})
        command = request_data.get("command", "").strip()
        is_new_session = data.get("session", {}).get("new", False)

        if is_new_session and not command:
            reply = "Мозг включен"
        else:
            try:
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=(
                        "Ты голосовой ассистент в колонке Яндекс Станция. "
                        "Отвечай кратко, емко, без Markdown-разметки (без звездочек и решеток), "
                        f"так как твой ответ будет зачитан голосом. Запрос: {command}"
                    ),
                )
                reply = response.text or "Не удалось получить ответ."
            except Exception:
                reply = "Ну пиздец."

        result = {
            "response": {
                "text": reply,
                "end_session": False
            },
            "version": "1.0"
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))
