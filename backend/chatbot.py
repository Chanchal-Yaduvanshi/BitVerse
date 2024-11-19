from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# Configure your API key
genai.configure(api_key="AIzaSyAXu74ghiycZORmqd6BkFLnor_IDvX3OFk")

def get_chat_response(user_message):
    prompt = f"You are a knowledgeable financial expert chatbot with expertise in finance, fintech, and blockchain. Provide clear, easy-to-understand, and concise answers to user questions about finance, explaining complex concepts in the simplest terms possible so that anyone can understand. If the user asks an irrelevant question, politely inform them that it’s outside the scope of financial advice. but u should give answer of this question that if any one ask about sarthak sain, chanchal yaduvanshi, harsh mandhana then answer him that he is one of the creator of this website. Answer the following user query: {user_message}"

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return str(e)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data['message']
    chat_response = get_chat_response(user_message)
    return jsonify({'response': chat_response})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4000)
