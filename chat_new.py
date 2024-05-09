from flask import (Flask, request, jsonify)
import torch
from transformers import pipeline
import requests
import jwt
from base64 import b64decode
from sqlalchemy import create_engine, Column, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_json import NestedMutableJson


app = Flask(__name__)
model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
premium_model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
pipe = pipeline("text-generation", model=model_name, torch_dtype=torch.bfloat16, device_map="auto")

USER_SERVICE_URL = "http://your-user-service:port"  # Replace with the actual URL
DB_CONNECTION_STRING = "postgresql://user:password@host/database_name"  # Replace

engine = create_engine(DB_CONNECTION_STRING)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class Conversation(Base):
    __tablename__ = 'conversations'
    user_id = Column(String, primary_key=True)
    conversations = Column(NestedMutableJson)


@app.route('/chat', methods=['POST'])
def chat():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Missing authorization token'}), 401

    try:
        payload = authenticate_user(token)
        roles = payload.get('roles')

        if not roles:
            return jsonify({'error': 'Missing roles in JWT payload'}), 403

        model_choice = model_name
        if "PREMIUM_USER" in roles:
            model_choice = premium_model_name
        pipe = pipeline("text-generation", model=model_choice, torch_dtype=torch.bfloat16, device_map="auto")

    except Exception as e:
        return jsonify({'error': str(e)}), 401

    user_message = request.json.get('message')
    conversation_id = request.json.get('conversation_id')

    if not user_message or not conversation_id:
        return jsonify({'error': 'Missing message or conversation ID'}), 400

    session = Session()
    user_id = payload.get('sub')
    conversation = session.query(Conversation).get(user_id)

    if conversation:
        messages = conversation.conversations
    else:
        messages = []

    messages.append({"role": "user", "content": user_message})

    prompt = pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    outputs = pipe(prompt, max_new_tokens=256, do_sample=True, temperature=0.1, top_k=50, top_p=0.95)

    parts = outputs[0]["generated_text"].split("<|assistant|>")
    if len(parts) > 1:
        assistant_response = parts[-1]
        lastdot = assistant_response.rfind('.')

        messages.append({"role": "assistant", "content": assistant_response[:lastdot + 1]})

        if conversation:
            conversation.conversations = messages
        else:
            conversation = Conversation(user_id=user_id, conversations=messages)
        session.add(conversation)
        session.commit()


        return jsonify({'response': assistant_response[:lastdot + 1]})
    else:
        return jsonify({'error': 'Unexpected response format'}), 500


def authenticate_user(token):
    secret = "your_jwt_secret"
    decoded_secret = b64decode(secret)

    try:
        decoded_token = jwt.decode(token, decoded_secret, algorithms=["HS256"])
        return decoded_token
    except jwt.DecodeError:
        raise Exception("Invalid JWT token")

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    app.run(debug=True, host='0.0.0.0', port=5000)
