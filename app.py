import os
import csv
import logging
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from openai import OpenAI
from werkzeug.utils import secure_filename

# Setup
load_dotenv()
app = Flask(__name__)
logging.basicConfig(level=logging.INFO, filename='app.log')

# MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['shelby_creative']
games = db['games']
conversations = db['conversations']
knowledge_base = db['knowledge_base']

# OpenAI
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# RAG Function
def get_relevant_info(query):
    results = list(knowledge_base.find({'$text': {'$search': query}}, {'score': {'$meta': 'textScore'}}).sort([('score', {'$meta': 'textScore'})]).limit(1))
    return results[0]['content'] if results else ''

# Chat Response with Memory
def get_openai_response(messages, user_message):
    relevant_info = get_relevant_info(user_message)
    context = f"Context from Shelby Creative: {relevant_info}" if relevant_info else "No specific context available."
    full_message = [
        {"role": "system", "content": f"You are Thomas, an AI assistant for Shelby Creative. {context}"},
        *messages,
        {"role": "user", "content": user_message}
    ]
    response = openai_client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=full_message
    )
    return response.choices[0].message.content

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game/<name>')
def game(name):
    game_data = games.find_one({'name': name})
    if game_data:
        progress = game_data.get('progress', {'models': {'done': 0, 'total': 0}, 'scripts': {'done': 0, 'total': 0}, 'dungeons': {'done': 0, 'total': 0}})
        total_spent = game_data.get('total_spent', 0)
        payments = game_data.get('payments', [])
    else:
        progress = {'models': {'done': 0, 'total': 0}, 'scripts': {'done': 0, 'total': 0}, 'dungeons': {'done': 0, 'total': 0}}
        total_spent = 0
        payments = []
    return render_template('game.html', game_name=name, progress=progress, total_spent=total_spent, payments=payments)

@app.route('/chat')
def chat_page():
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        message = request.json.get('message')
        history = conversations.find_one({'_id': 'main'}) or {'messages': []}
        ai_response = get_openai_response(history['messages'][-10:], message)
        history['messages'].append({'role': 'user', 'content': message})
        history['messages'].append({'role': 'assistant', 'content': ai_response})
        conversations.update_one(
            {"_id": "main"},
            {"$set": {"messages": history['messages']}},
            upsert=True
        )
        return jsonify({'response': ai_response})
    except Exception as e:
        logging.error(f"Chat error: {str(e)}")
        return jsonify({'response': 'Sorry, something broke!'}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file uploaded', 400
    file = request.files['file']
    if file.filename == '':
        return 'No file selected', 400
    filename = secure_filename(file.filename)
    file_path = os.path.join('static/uploads', filename)
    os.makedirs('static/uploads', exist_ok=True)
    file.save(file_path)
    try:
        with open(file_path, newline='', encoding='utf-16') as csvfile:
            reader = csv.DictReader(csvfile)
            payments = list(reader)
            total_spent = sum(float(p.get('amount', 0)) for p in payments)
            game_name = request.form.get('game_name', 'Piece Quest')
            games.update_one(
                {"name": game_name},
                {"$set": {"payments": payments, "total_spent": total_spent}},
                upsert=True
            )
        return 'File uploaded successfully', 200
    except Exception as e:
        logging.error(f"Upload error: {str(e)}")
        return 'Error uploading file', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
