from flask import (Flask, request, jsonify)
import torch
from transformers import pipeline

app = Flask(__name__)

model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

pipe = pipeline("text-generation", model=model_name, torch_dtype=torch.bfloat16, device_map="auto")


@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return (
            jsonify({'error': 'No message provided'}), 400)
    messages = [
        {
            "role": "system", "content": "You are a friendly chatbot who answers shortly",
        }, {"role": "user", "content": user_message},
    ]
    prompt = pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    outputs = pipe(prompt, max_new_tokens=256, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)
    parts = outputs[0]["generated_text"].split("<|assistant|>")
    if len(parts) > 1:
        assistant_response = parts[1]
        lastdot = assistant_response.rfind('.')
        return jsonify({'response': assistant_response[:lastdot + 1]})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
