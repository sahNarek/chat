import torch
from transformers import pipeline



class LlmModel:
    """_summary_
    """
    def __init__(self, model_name: str) -> None:
        """_summary_

        Args:
            model_name (str): _description_
        """
        self.pipe = pipeline("text-generation", model=model_name, torch_dtype=torch.bfloat16, device_map="auto")
        self.messages = [
            {
                "role": "system", "content": "You are a friendly chatbot who answers shortly",
            }
        ]
    
    def build_user_message(self, user_message: str):
        """_summary_

        Args:
            user_message (str): _description_
        """
        return [{"role": "user", "content": user_message}]

    
    def generate(self, user_prompt: str, previous_messages: list):
        """_summary_

        Args:
            user_prompt (str): _description_
            previous_messages (list): _description_
        """
        user_message = self.build_user_message(user_prompt)
        messages_to_pass = self.messages + previous_messages + user_message
        prompt = self.pipe.tokenizer.apply_chat_template(messages_to_pass, tokenize=False, add_generation_prompt=True)
        outputs = self.pipe(prompt, max_new_tokens=256, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)
        parts = outputs[0]["generated_text"].split("<|assistant|>")
        if len(parts) > 1:
            assistant_response = parts[1]
            lastdot = assistant_response.rfind('.')
            return assistant_response[:lastdot + 1]
        return "Unexpected response format"