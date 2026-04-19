# ruian_own.py — СВОЯ нейросеть. Никаких transformers. Никаких чужих моделей.

import json
import random
import math
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

# ========== МАТЕМАТИКА НЕЙРОСЕТИ ==========
def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def relu(x):
    return max(0, x)

def softmax(arr):
    exp_arr = [math.exp(x) for x in arr]
    s = sum(exp_arr)
    return [x / s for x in exp_arr]

# ========== ТВОЯ НЕЙРОСЕТЬ (С НУЛЯ) ==========
class RuIANNetwork:
    def __init__(self, input_size=100, hidden_size=256, output_size=100):
        # Инициализация весов (свои, не чужие)
        self.w1 = [[random.uniform(-0.5, 0.5) for _ in range(hidden_size)] for _ in range(input_size)]
        self.b1 = [0.0] * hidden_size
        self.w2 = [[random.uniform(-0.5, 0.5) for _ in range(output_size)] for _ in range(hidden_size)]
        self.b2 = [0.0] * output_size
        
        # Словарь для преобразования текста в числа
        self.vocab = {}
        self.reverse_vocab = []
        self.max_vocab_size = output_size
        
        # База знаний (для быстрых ответов)
        self.knowledge = {}
        
        # Обучаем базовым вещам
        self._init_basic_knowledge()
    
    def _init_basic_knowledge(self):
        """Базовые знания (как у человека — учим с детства)"""
        basic = [
            ("привет", "Привет! Я RuIAN, твоя нейросеть."),
            ("как дела", "У меня всё отлично! А у тебя?"),
            ("что ты умеешь", "Я умею учиться, запоминать и отвечать на вопросы. Спрашивай!"),
            ("помощь", "Чем могу помочь?"),
            ("спасибо", "Пожалуйста! Обращайся."),
            ("пока", "До свидания! Заходи ещё."),
            ("кто ты", "Я RuIAN — нейросеть, созданная с нуля без чужих моделей."),
            ("зачем ты", "Чтобы помогать тебе и учиться новому."),
        ]
        for q, a in basic:
            self.knowledge[q.lower()] = a
    
    def text_to_vector(self, text):
        """Превращает текст в вектор чисел (100 измерений)"""
        words = text.lower().split()[:20]
        vec = [0.0] * self.max_vocab_size
        for word in words:
            if word not in self.vocab:
                idx = len(self.vocab)
                if idx >= self.max_vocab_size:
                    idx = hash(word) % self.max_vocab_size
                self.vocab[word] = idx
                if len(self.reverse_vocab) <= idx:
                    self.reverse_vocab.append(word)
            vec[self.vocab[word]] += 1
        # Нормализация
        total = sum(vec)
        if total > 0:
            vec = [x / total for x in vec]
        return vec
    
    def forward(self, x):
        """Прямой проход по нейросети"""
        # Скрытый слой
        hidden = [0.0] * len(self.w1[0])
        for i in range(len(x)):
            for j in range(len(self.w1[0])):
                hidden[j] += x[i] * self.w1[i][j]
        for j in range(len(self.b1)):
            hidden[j] += self.b1[j]
            hidden[j] = relu(hidden[j])
        
        # Выходной слой
        output = [0.0] * len(self.w2[0])
        for i in range(len(hidden)):
            for j in range(len(self.w2[0])):
                output[j] += hidden[i] * self.w2[i][j]
        for j in range(len(self.b2)):
            output[j] += self.b2[j]
        
        return softmax(output)
    
    def train(self, x, target_idx, lr=0.01):
        """Обучение на одном примере"""
        # Прямой проход
        hidden = [0.0] * len(self.w1[0])
        for i in range(len(x)):
            for j in range(len(self.w1[0])):
                hidden[j] += x[i] * self.w1[i][j]
        for j in range(len(self.b1)):
            hidden[j] += self.b1[j]
            hidden[j] = relu(hidden[j])
        
        output = [0.0] * len(self.w2[0])
        for i in range(len(hidden)):
            for j in range(len(self.w2[0])):
                output[j] += hidden[i] * self.w2[i][j]
        for j in range(len(self.b2)):
            output[j] += self.b2[j]
        
        # Softmax
        exp_o = [math.exp(o) for o in output]
        sum_exp = sum(exp_o)
        probs = [e / sum_exp for e in exp_o]
        
        # Ошибка
        error = [0.0] * len(probs)
        for i in range(len(probs)):
            error[i] = probs[i] - (1.0 if i == target_idx else 0.0)
        
        # Обратное распространение
        # Обновляем w2 и b2
        for i in range(len(hidden)):
            for j in range(len(self.w2[0])):
                self.w2[i][j] -= lr * error[j] * hidden[i]
        for j in range(len(self.b2)):
            self.b2[j] -= lr * error[j]
        
        # Обновляем w1 и b1
        hidden_error = [0.0] * len(hidden)
        for i in range(len(hidden)):
            for j in range(len(error)):
                hidden_error[i] += error[j] * self.w2[i][j]
        
        for i in range(len(x)):
            for j in range(len(self.w1[0])):
                if hidden[j] > 0:
                    self.w1[i][j] -= lr * hidden_error[j] * x[i]
        for j in range(len(self.b1)):
            if hidden[j] > 0:
                self.b1[j] -= lr * hidden_error[j]
    
    def think(self, text):
        """Генерация ответа"""
        text_lower = text.lower()
        
        # Сначала проверяем базу знаний
        for key, response in self.knowledge.items():
            if key in text_lower:
                return response
        
        # Если нет — генерируем через нейросеть
        vec = self.text_to_vector(text)
        probs = self.forward(vec)
        
        # Выбираем самый вероятный токен
        best_idx = max(range(len(probs)), key=lambda i: probs[i])
        if best_idx < len(self.reverse_vocab):
            response = self.reverse_vocab[best_idx]
            if len(response) < 3:
                return "Интересный вопрос! Расскажи подробнее."
            return f"Я думаю, что это связано с '{response}'. Расскажи ещё?"
        
        return "Понял! Расскажи подробнее, я учусь."
    
    def learn(self, question, answer):
        """Обучаем нейросеть на паре вопрос-ответ"""
        self.knowledge[question.lower()] = answer
        
        # Добавляем в словарь новые слова
        for word in question.lower().split():
            if word not in self.vocab:
                idx = len(self.vocab)
                if idx >= self.max_vocab_size:
                    idx = hash(word) % self.max_vocab_size
                self.vocab[word] = idx
                if len(self.reverse_vocab) <= idx:
                    self.reverse_vocab.append(word)
        
        # Обучаем нейросеть
        vec = self.text_to_vector(question)
        words = answer.lower().split()
        if words:
            target_word = words[0]
            if target_word not in self.vocab:
                idx = len(self.vocab)
                if idx >= self.max_vocab_size:
                    idx = hash(target_word) % self.max_vocab_size
                self.vocab[target_word] = idx
                if len(self.reverse_vocab) <= idx:
                    self.reverse_vocab.append(target_word)
            self.train(vec, self.vocab[target_word], lr=0.05)
        
        self.save()
        return True
    
    def save(self):
        """Сохраняем нейросеть"""
        data = {
            'w1': self.w1,
            'b1': self.b1,
            'w2': self.w2,
            'b2': self.b2,
            'vocab': self.vocab,
            'reverse_vocab': self.reverse_vocab,
            'knowledge': self.knowledge
        }
        with open('ruian_brain.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load(self):
        """Загружаем нейросеть"""
        if os.path.exists('ruian_brain.json'):
            with open('ruian_brain.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.w1 = data['w1']
            self.b1 = data['b1']
            self.w2 = data['w2']
            self.b2 = data['b2']
            self.vocab = data['vocab']
            self.reverse_vocab = data['reverse_vocab']
            self.knowledge = data['knowledge']
            return True
        return False

# ========== СОЗДАЁМ НЕЙРОСЕТЬ ==========
ruian = RuIANNetwork()
ruian.load()  # Загружаем, если есть сохранённая

# ========== HTTP СЕРВЕР ==========
class RuIANHandler(BaseHTTPRequestHandler):
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
                'knowledge_size': len(ruian.knowledge),
                'vocab_size': len(ruian.vocab)
            }).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/chat':
            length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(length).decode())
            message = data.get('message', '')
            response = ruian.think(message)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'response': response}).encode())
        
        elif self.path == '/learn':
            length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(length).decode())
            question = data.get('question', '')
            answer = data.get('answer', '')
            ruian.learn(question, answer)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'learned'}).encode())
        
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    port = 8000
    server = HTTPServer(('127.0.0.1', port), RuIANHandler)
    print(f"""
╔════════════════════════════════════════════════╗
║      🧠 RuIAN — СВОЯ НЕЙРОСЕТЬ 🧠             ║
╠════════════════════════════════════════════════╣
║  Запущена на: http://localhost:{port}          ║
║  База знаний: {len(ruian.knowledge)} фраз       ║
║  Словарь: {len(ruian.vocab)} слов              ║
║                                                ║
║  НИКАКИХ ЧУЖИХ МОДЕЛЕЙ. ТВОЯ. С НУЛЯ.         ║
╚════════════════════════════════════════════════╝
    """)
    server.serve_forever()

if __name__ == '__main__':
    run_server()
