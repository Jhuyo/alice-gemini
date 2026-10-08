import json
import os
from http.server import BaseHTTPRequestHandler
import google.generativeai as genai

# Настройка ключа
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel(
    model_name="gemini-3.5-flash",
    system_instruction=(
        "Ты голосовой ассистент в умной колонке Яндекс Станция. Называй себя нейрон"
        "Отвечай кратко, емко, без использования Markdown-разметки (не используй звездочки, решетки, жирный шрифт), "
        "так как твой ответ будет зачитан синтезатором речи."
    )
)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        data = json.loads(body.decode("utf-8"))

        request_data = data.get("request", {})
        command = request_data.get("command", "").strip()
        is_new_session = data.get("session", {}).get("new", False)

        if is_new_session and not command:
            reply = "Мозг подключен"
        else:
            try:
                response = model.generate_content(command)
                reply = response.text or "Ну емае"
            except Exception as e:
                reply = f"Ошибка: {str(e)[:100]}"

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
