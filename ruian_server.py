# ruian_server.py — твоя собственная нейросеть
import json
import random
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

# ========== ТВОЯ НЕЙРОСЕТЬ ==========
class RuIAN:
    def __init__(self):
        self.brain = {}
        self.responses = {}
        self.load()
        self._init_defaults()
    
    def _init_defaults(self):
        default_responses = {
            "привет": "Привет! Я RuIAN, твоя нейросеть.",
            "как дела": "У меня всё отлично! А у тебя?",
            "что ты умеешь": "Я умею учиться, запоминать и отвечать на вопросы.",
            "помощь": "Чем могу помочь?",
            "спасибо": "Пожалуйста!",
            "пока": "До свидания!",
            "кто ты": "Я RuIAN — нейросеть, созданная с нуля.",
        }
        self.responses.update(default_responses)
    
    def think(self, text):
        text_lower = text.lower()
        for key, response in self.responses.items():
            if key in text_lower:
                return response
        return "Интересный вопрос! Расскажи подробнее, я учусь."
    
    def save(self):
        data = {'responses': self.responses, 'brain': self.brain}
        with open('ruian_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load(self):
        if os.path.exists('ruian_data.json'):
            with open('ruian_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.responses = data.get('responses', {})
                self.brain = data.get('brain', {})

ruian = RuIAN()

# ========== СЕРВЕР ==========
class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'active',
                'knowledge_size': len(ruian.responses)
            }).encode())
    
    def do_POST(self):
        if self.path == '/chat':
            length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(length))
            response = ruian.think(data.get('message', ''))
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'response': response}).encode())

print("""
╔════════════════════════════════════════╗
║     RuIAN — твоя нейросеть запущена   ║
╠════════════════════════════════════════╣
║  http://localhost:8000                 ║
║  Своя нейросеть. Без чужих моделей.   ║
╚════════════════════════════════════════╝
""")
HTTPServer(('127.0.0.1', 8000), Handler).serve_forever()
